import os
import os.path
from flask import Flask, Blueprint, render_template,request,session,redirect,url_for
from werkzeug.utils import secure_filename
from flask_database import db
from models import Contracts, ContractItems
from load_jobs import contract_data
import datetime
import pymssql

import json
import threading
from create_report import create_rep, CreateRep_Table

host = "197.189.232.50"
username = "FE-User"
password = "Fourier.01"
database = "PGAluminium"
conn = pymssql.connect(host, username, password, database)
cursor = conn.cursor()

contracts_file = Blueprint('contracts_file',__name__,template_folder='templates',static_folder='static')

UPLOAD_FOLDER = 'static/reports'
ALLOWED_EXTENSIONS = set(['xlsx'])

app = Flask(__name__)
app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Items Page
@contracts_file.route('/<string:org_name>/Worker/<int:user_id>', methods=["POST", "GET"])
def worker(org_name, user_id):
    if user_id == session["UserId"]:
        
        Confirmation = ""

        fast_assign = db.engine.execute("""
                                        Select
                                        i.ContractItemId, i.ActivityStatusId, i.LineReferenceNumber, i.Description,
                                        i.AssignedUserId, c.Description  as 'Contract', c.ContractReference,
                                        c.DueDate, a.Status, a.isActivityEnd, a.isCancelled, i.TemplateId
                                        from ContractItems i
                                        join Contracts c on
                                        c.ContractId = i.ContractId
                                        join ActivityStatuses a on
                                        a.StatusId=i.ActivityStatusId join Activities p on a.ActivityId = p.ActivityId
                                        where i.OrgId = {} and
                                        DueDate >= DATEADD(DAY, -90, GETDATE()) and c.ActivityStatusId <> (select Ast.StatusId from ActivityStatuses Ast join Activities Act on Ast.ActivityId = Act.ActivityId where Act.Level = 1 and Act.OrgId = {} and Ast.isCancelled = 1)
                                        order by i.LineReferenceNumber DESC
                                        """.format(session["OrgId"], session["OrgId"])).fetchall()
        print(fast_assign)

        base_activities_data = db.engine.execute("""
                                                 select distinct
                                                 a.OrgId, a.ActivityId, a.Activity, s.BgColor, s.isCancelled, s.IsActive, a.Prerequisite, t.TemplateId
                                                 from Activities a
                                                 left join ActivityStatuses s on
                                                 s.ActivityId = a.ActivityId
                                                 left join TemplateActivities t on t.ActivityId = a.ActivityId
                                                 where a.Level = 2 and a.OrgId = {} and a.IsActive = 1
                                                 """.format(session["OrgId"])).fetchall()

        templates = db.engine.execute("Select * from Templates where OrgId = {}".format(session['OrgId'])).fetchall()
        templates = list(templates)
        activity_template = db.engine.execute("Select * from TemplateActivities where OrgId = {}".format(session['OrgId'])).fetchall()

        db.session.commit()
        if request.method == "POST":
            if request.form['UpdateStatus'] == "Start":
                new_act = request.form["StatusName1"] + " Start"
            elif request.form['UpdateStatus'] == "Complete":
                new_act = request.form["StatusName1"] + " Complete"
            if "Cancelled" in new_act:
                new_act = "Cancelled"
                new_stat_id = db.engine.execute("SELECT Ast.StatusId FROM ActivityStatuses Ast join Activities Act on Act.ActivityId = Ast.ActivityId WHERE Ast.Status = '{}' and Act.Level = 2 and Ast.OrgId = {}".format(new_act, session["OrgId"])).first()
            else:
                new_stat_id = db.engine.execute("SELECT Ast.StatusId FROM ActivityStatuses Ast join Activities Act on Act.ActivityId = Ast.ActivityId WHERE Ast.Status = '{}' and Act.Level = 2 and Ast.OrgId = {}".format(new_act, session["OrgId"])).first()
            ciie = request.form["CIIE1"]
            
            db.engine.execute("""
                              Update ContractItems
                              Set ActivityStatusId = {}, AssignedUserId = {}, UserId = {}
                             where ContractItemId = {} and OrgId = {} 
                             """.format(new_stat_id[0], session["UserId"], session["UserId"], ciie, session["OrgId"]))
            db.session.commit()

            return redirect(url_for('contracts_file.worker', org_name=session["OrgName"], user_id=session["UserId"],base_activities_data=base_activities_data))

        return render_template('AdminItem.html', templates=templates, activity_template=activity_template, fast_assign=fast_assign, user_id=user_id, base_activities_data=base_activities_data, Confirmation=Confirmation)
    else:
        error = 'You do not have authorisation to view this page'
        return render_template('AdminContracts.html', Error=error)


#Contracts Page
@contracts_file.route('/<string:org_name>/ManageContracts', methods=["POST", "GET"])
def manage_contracts(org_name):
    if session.get('UserId'):
        if session["RoleId"] > 0:
            #filename = "DynamicReport_"+str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))+".xlsx"

            #sp = db.engine.execute("ReportContracts {}".format(session["OrgId"])).fetchall()

            sp = db.engine.execute("""
                                    [JobsView] {}
                                    """.format(session['OrgId'])).fetchall()

            now = datetime.datetime.utcnow()

            today_date = datetime.datetime.now()
            today_date_str = today_date.strftime("%Y-%m-%d")

            if request.method == "POST":
                if request.form["AddContracts"] == "Add Job":
                    Contracts_Add = Contracts(OrgId = session["OrgId"], ContractReference = request.form["CRef"], Description = request.form["CDes"], Timestamp=now, OrderedDate = request.form["ODate"], ContactPerson = request.form["CusName"], Value = request.form["VName"], ContactNumber1 = request.form["CStatus"], DueDate = request.form["CDate"], AssignedUserId = session['UserId'], Notes = request.form["CNotes"])
                    for i in sp:
                        if i[2] == request.form["CRef"]:
                            error = 'This Job Number already exists'
                            return render_template('AdminContract.html', sp=sp, Error=error, today_date=today_date_str)
                    db.session.add(Contracts_Add)
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contracts', org_name=session["OrgName"]))
                elif request.form["AddContracts"] == "Save Job":
                    Contract_Edit = Contracts.query.get(request.form["ECID"])
                    Contract_Edit.ContractReference = request.form["ECRef"]
                    Contract_Edit.Description = request.form["ECDes"]
                    Contract_Edit.ContactPerson = request.form["ECusName"]
                    Contract_Edit.DueDate = request.form["ECDate"]
                    Contract_Edit.OrderedDate = request.form["EODate"]
                    Contract_Edit.Notes = request.form["ECNotes"]
                    Val = request.form["VEName"]
                    Contract_Edit.Value = float(Val)
                    Contract_Edit.ContactNumber1 = request.form["ECStatus"]
                    check_ref = db.engine.execute(
                        "Select ContractReference from Contracts where OrgId = {} and ContractId != {}".format(
                            session['OrgId'], request.form["ECID"])).fetchall()
                    for i in check_ref:
                        if i[0] == Contract_Edit.ContractReference:
                            error = 'This Job Number already exists'
                            return render_template('AdminContract.html', sp=sp, Error=error, today_date=today_date_str)

                    if request.form["ECStatus"] == 'Complete':
                        db.engine.execute("""
                                          Update ContractItems
                                          Set Description = 'Completed', UserId = {}
                                          where ContractId = {} and OrgId = {} and Description != 'Completed'
                                          """.format(session["UserId"], request.form["ECID"], session["OrgId"]))
                        db.engine.execute(
                            """Update ActivityProgress Set Progress = 100 where ContractId = {} and OrgId = {}""".format(
                                request.form["ECID"], session["OrgId"]))
                        db.session.commit()
                        return redirect(url_for('contracts_file.manage_contracts', org_name=session["OrgName"]))

                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contracts', org_name=session["OrgName"]))
                elif request.form["AddContracts"] == "Delete":
                    db.engine.execute("""
                                        Insert into JobLog (JobId, [Job Number], UserId, OrgId, Timestamp)
                                        values ({}, '{}', {}, {}, GETDATE())
                                        """.format(request.form["ECID1"], request.form["ECRef1"], session['UserId'], session['OrgId']))
                    db.engine.execute("""
                                      Delete from Contracts
                                      where ContractId = {} and OrgId = {} 
                                      """.format(request.form["ECID1"], session["OrgId"]))

                    db.engine.execute("""
                                      Delete from ContractItems
                                      where ContractId = {} and OrgId = {} 
                                      """.format(request.form["ECID1"], session["OrgId"]))

                    db.engine.execute("""
                                      Delete from ContractItemHistory
                                      where ContractId = {} and OrgId = {} 
                                      """.format(request.form["ECID1"], session["OrgId"]))
                    db.engine.execute("""
                                      Delete from ActivityProgress
                                      where ContractId = {} and OrgId = {} 
                                      """.format(request.form["ECID1"], session["OrgId"]))

                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contracts', org_name=session["OrgName"]))
                elif request.form["AddContracts"] == "Upload":
                    #contract_names = db.engine.execute("Select ContractId from Contracts where ContractReference = '{}'".format(request.form["ConRef1"])).first()
                    #check_items = db.engine.execute("Select * from ContractItems c left join Contracts n on n.ContractId = c.ContractId where c.ContractId = {}".format(contract_names[0])).fetchall()
                    #try:
                    if 'file' not in request.files:
                        error = 'Please select a new file'
                        return render_template('AdminContract.html', Error=error)
                    file = request.files['file']
                    if file.filename == '':
                        error = 'Please select a new file'
                        return render_template('AdminContract.html', Error=error)
                    if file and allowed_file(file.filename):
                        filename = "1_" + secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                        contract_data(file_name=os.path.join(app.config['UPLOAD_FOLDER'], filename), orgid=session["OrgId"], userid=session["UserId"])['Items']
                        #contract_data(file_name=os.path.join(app.config['UPLOAD_FOLDER'], filename),orgid=session["OrgId"], userid=session["UserId"])
                        return redirect(url_for('contracts_file.manage_contracts', org_name=org_name))
                    else:
                        error = 'Please select the correct file'
                        return render_template('AdminContract.html', Error=error, today_date=today_date_str)

                    error = 'Your file is incorrect. Please remove all formulas and delete empty rows'
                    return render_template('AdminContract.html', Error=error)
            return render_template('AdminContract.html', sp=sp, now=now)
        else:
            error = 'You are not an Admin'
            return render_template('AdminContract.html', Error=error)
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index_1.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org_2.html', Error=error)


# CI Page
@contracts_file.route('/<string:org_name>/<string:contract_name>/ContractItems', methods=["POST", "GET"])
def manage_contract_items(org_name, contract_name):
    if session.get('UserId'):
        if session["RoleId"] > 0:
            templates = db.engine.execute(
                "Select * from Templates where OrgId = {}".format(session['OrgId'])).fetchall()

            contract_data = db.engine.execute("""
                                                SELECT
                                                c.ContractId, c.Description, c.DueDate, c.ContractReference, c.ContactPerson, c.ContactNumber1 
                                                FROM Contracts c
                                                where c.ContractReference = '{}' and c.OrgId = {}
                                              """.format(contract_name, session["OrgId"])).first()

            activity_on_hold = db.engine.execute("""
                                                Select a.activity from Contracts c
                                                join ContractItems ci on c.ActivityHold = ci.ContractItemId
                                                join JobActivities a on ci.LineReferenceNumber = a.ActivityId
                                                where c.ContractReference = '{}' and c.OrgId = {}
                                                """.format(contract_name, session["OrgId"])).first()

            act_data = db.engine.execute("""
                                        Select ci.ContractItemId, ci.ContractId, ci.LineReferenceNumber, ci.Description, a.Progress,
                                        ci.Timestamped, c.DueDate, u1.Username, u2.UserName as Worker, j.Activity, j.IsQC, j.[Order]
                                        from ContractItems ci join Contracts c on ci.ContractId = c.ContractId
                                        join Users u1 on ci.AssignedUserId = u1.UserId
                                        left join Users u2 on ci.UserId = u2.UserId
                                        join ActivityProgress a on ci.ContractItemId = a.ContractItemId 
                                        join JobActivities j on ci.TemplateId = j.ActivityId
                                        where ci.OrgId = {} and ci.ContractId = {}
                                        order by j.[Order] asc
                                        """.format(session['OrgId'], contract_data[0])).fetchall()

            completion_rate = db.engine.execute("""
                                                select Count(a.Progress) from ContractItems ci
                                                join ActivityProgress a on ci.ContractItemId = a.ContractItemId
                                                where ci.OrgId = {} and ci.ContractId = {} and a.Progress = 0
                                                """.format(session['OrgId'], contract_data[0])).first()

            jobact = db.engine.execute("Select * from JobActivities where OrgId = {} order by [Order] asc".format(session['OrgId'])).fetchall()

            now = datetime.date.today()

            if request.method == "POST":
                if request.form["ContractItems"] == "Add Activities":

                    session['addacts'] = request.form.getlist("Act")
                    conid = contract_data[0]
                    description = 'Created'
                    for i in session['addacts']:

                        db.engine.execute("""
                                          Insert into ContractItems (OrgId, ContractId, LineReferenceNumber,TemplateId, Description, Timestamped, DateAdded, UserId, AssignedUserId, Progress)
                                          values ({}, {}, '{}', {}, '{}', {}, {}, {}, {}, {})
                                          """.format(session['OrgId'], conid, i, int(i), description, now, now, session['UserId'], session['UserId'], 0))

                        db.engine.execute("Update ContractItems Set Description = 'Started', UserId = {} where ContractId = {} and LineReferenceNumber = 1 and OrgId = {} and Description != 'Started'".format(session['UserId'], conid, session['OrgId']))


                    db.engine.execute("""                                    
                                        INSERT INTO ActivityProgress 
                                        SELECT OrgId, ContractItemId, Progress, ContractId FROM ContractItems
                                        WHERE OrgId = {} and ContractId = {} and NOT EXISTS(SELECT * 
                                                         FROM ActivityProgress 
                                                         WHERE (ContractItems.ContractItemId=ActivityProgress.ContractItemId)
                                                         )
                                        """.format(session['OrgId'], conid))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"], contract_name=contract_name))

                elif request.form["ContractItems"] == "Place Job On Hold":

                    db.engine.execute(
                        """
                        Update Contracts
                        Set ContactNumber1 = 'On Hold', StartedHold = GETDATE(), ActivityHold = {}
                        where ContractId = {} and OrgId = {}
                        """.format(request.form["OnHoldAct"], request.form["ContractId"], session['OrgId']))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"],
                                            contract_name=contract_name))

                elif request.form["ContractItems"] == "Complete Hold":

                    db.engine.execute(
                        """
                        Update Contracts
                        Set ContactNumber1 = 'Start', CompletedHold = GETDATE()
                        where ContractId = {} and OrgId = {}
                        """.format(request.form["ContractHoldId"], session['OrgId']))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"],
                                            contract_name=contract_name))

                elif request.form["ContractItems"] == "Confirm":
                    db.engine.execute(
                        """
                        Update ContractItems 
                        Set Description = 'On Hold', OnHold = 1, StartedHold = {}, UserId = {}
                        where ContractItemId = {} and OrgId = {}
                        """.format(now, session['UserId'], request.form["OnHoldAct"], session['OrgId']))
                    db.engine.execute(
                        """
                        Update Contracts
                        Set ContactNumber1 = 'On Hold', StartedHold = '{}' 
                        where ContractId = {} and OrgId = {}
                        """.format(now, request.form["ContractId"], session['OrgId']))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"],
                                            contract_name=contract_name))

                elif request.form["ContractItems"] == "Update":
                    db.engine.execute(
                        """
                        Update ActivityProgress 
                        Set Progress = {} 
                        where ContractItemId = {} and OrgId = {}
                        """.format(request.form["myProg"], request.form["ActSelect"], session['OrgId']))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"],
                                            contract_name=contract_name))

                elif request.form["ContractItems"] == "Delete":

                    db.engine.execute("""
                                      Delete from ContractItems
                                      where ContractItemId = {} and OrgId = {} 
                                      """.format(request.form["ActSelect1"], session["OrgId"]))

                    db.engine.execute("""
                                      Delete from ContractItemHistory
                                      where ContractItemId = {} and OrgId = {} 
                                      """.format(request.form["ActSelect1"], session["OrgId"]))
                    db.engine.execute("""
                                      Delete from ActivityProgress
                                      where OrgId = {} and ContractItemId = {} 
                                      """.format(session["OrgId"], request.form["ActSelect1"]))

                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"],
                                            contract_name=contract_name))

                elif request.form["ContractItems"] == "Start":
                    action = 'Started'
                    db.engine.execute(
                        """
                        Update ContractItems Set Description = '{}', UserId = {} where ContractItemId = {} and OrgId = {}
                        """.format(action, session['UserId'], request.form["CIIE"], session['OrgId']))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"],
                                            contract_name=contract_name))

                elif request.form["ContractItems"] == "Complete":
                    action = 'Completed'
                    db.engine.execute(
                        """
                        Update ContractItems Set Description = '{}', UserId = {} where ContractItemId = {} and OrgId = {}
                        """.format(action, session['UserId'], request.form["CIIE"], session['OrgId']))
                    db.session.commit()
                    return redirect(url_for('contracts_file.manage_contract_items', org_name=session["OrgName"],
                                            contract_name=contract_name))

            return render_template('AdminItemManage.html', contract_name=contract_name,
                                    contract_data=contract_data, act_data=act_data, jobact=jobact, completion_rate=completion_rate, now=now, activity_on_hold=activity_on_hold)
        else:
            error = 'You are not an Admin'
            return render_template('index_1.html', Error=error)
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index_1.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org_2.html', Error=error)
