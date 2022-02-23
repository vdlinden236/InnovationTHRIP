import os
import os.path

from flask import Flask, Blueprint, render_template, request, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_database import db
from load_jobs import contract_data

import pymssql

import json
import threading
from create_report import create_rep, CreateRep_Table

import pdfkit
from flask import Flask, make_response, Blueprint, render_template, request, session, redirect, url_for, flash
from flask_database import db
from datetime import timedelta
from datetime import datetime
from datetime import date
from passlib.hash import sha256_crypt
from threading import Thread
from itsdangerous import URLSafeTimedSerializer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



surveys_file = Blueprint('surveys_file', __name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = 'static/reports'
ALLOWED_EXTENSIONS = set(['xlsx'])

app = Flask(__name__)
app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Display amounts of comleted and list of organisation availble surveys.
@surveys_file.route('/<string:org_name>/Surveys', methods=["POST", "GET"])
def surveys(org_name):
    if session.get('UserId'):
        surveys = db.execute("""select q.name, q.description, q.surveyID, q.startDate, q.endDate from [thrip].[surveys] q 
                                                left join [thrip].[orgsurvey] g on q.surveyID = g.surveyID where g.OrgID = {} """.format(session['OrgId'])).fetchall()

        user_surveys = db.execute("Select * from [thrip].[usersurveys] where OrgID = {} and UserID = {}".format(session['OrgId'], session['UserId'])).fetchall()
        user_count = db.execute("Select count(*) from [thrip].[usersurveys] where OrgID = {} and UserID = {}".format(session['OrgId'], session['UserId'])).fetchone()
        survey_count = db.execute("Select count(*) from [thrip].[orgsurvey] where OrgID = {}".format(session['OrgId'], session['UserId'])).fetchone()
        question_count = db.execute("Select count(*) from [thrip].[questions11] where OrgID = {}".format(session['OrgId'], session['UserId'])).fetchone()
        return render_template('surveys.html', surveys=surveys, user_surveys=user_surveys, user_count=user_count, survey_count=survey_count, question_count=question_count)
    else:
        error = 'You are not logged in'
        return render_template('login.html', Error=error)

#Display questions in groups
@surveys_file.route('/<string:org_name>/<int:survey_id>/Questions', methods=["POST", "GET"])
def survey_questions(org_name, survey_id):
    if session.get('UserId'):
        categories = db.execute("""select * from [thrip].[questiongroups]
                                         where OrgID = {} and surveyID = {}""".format(session['OrgId'], survey_id)).fetchall()
        questions = db.execute("""select q.OrgId, q.questionID, q.surveyID, q.questionGroupID, q.name as 'Questions', g.name, q.OptionType from [thrip].[questions11] q 
                                        left join [thrip].[questiongroups] g on q.questionGroupID = g.questionGroupID where q.OrgID = {} and q.surveyID = {}""".format(session['OrgId'], survey_id)).fetchall()

        if request.method == "POST":
            question_id = 1
            for i in questions:
                option = request.form.getlist('{}'.format(i[1]))
                print(option)
                answer = option
                print(question_id)
#insert the survey answer in selection tb
                db.execute("""
                                    Insert into [thrip].[selections]
                                    (OrgID, userID, orgsurveyID, optionID, questionID)
                                    values ({}, {}, {}, {}, {})
                                    """.format(session['OrgId'], session['UserId'], survey_id, answer[0], question_id))
                question_id += 1
            db.commit()
            return render_template('survey_questions.html', questions=questions, categories=categories)

        return render_template('survey_questions.html', questions=questions, categories=categories)

    else:
        error = 'You are not logged in'
        return render_template('login.html', Error=error)


# Get a report from a surveyID
# @surveys_file.route('/<string:org_name>/Report', methods=["POST", "GET"])
#def report(org_name):
#    if session.get('UserId'):
#       report = db.execute(
#            "Select * from [thrip].[selections] where OrgID = {}".format(
#                session['OrgId'])).fetchall()
#        return render_template('SurveyReport.html',  report=report)
#    else:
#        errors = 'You are not logged in'
#        return render_template('login.html', Error=errors)
#
#    if request.method == "POST":
#            return redirect(url_for('surveys_file.report', org_name=session["OrgName"]))
#            return render_template('SurveyReport.html', SurveyId=SurveyId)
#    else:
#            error = 'You are not logged in'
#            return render_template('login.html', Error=error)

#Add a problem to a userid
@surveys_file.route('/<string:org_name>/Problems', methods=["POST", "GET"])
def problems(org_name):
    if session.get('UserId'):
        test = "all"
        problems = db.execute(
            "Select p.*, h.description as 'Horizon' from [thrip].[problemstatements] p join [thrip].[horisons] h on p.[horisonID] = h.[horisonID] where p.qtype = 'Problem' AND p.OrgID = {}".format(session['OrgId'])).fetchall()
        Complaints = db.execute(
            "Select p.*, h.description as 'Horizon' from [thrip].[problemstatements] p join [thrip].[horisons] h on p.[horisonID] = h.[horisonID] where p.qtype = 'Complaint' AND p.OrgID = {}".format(
                session['OrgId'])).fetchall()
        Ideas = db.execute(
            "Select p.*, h.description as 'Horizon' from [thrip].[problemstatements] p join [thrip].[horisons] h on p.[horisonID] = h.[horisonID] where p.qtype = 'Idea' AND p.OrgID = {}".format(
                session['OrgId'])).fetchall()
        Problems = db.execute(
            "Select p.*, h.description as 'Horizon' from [thrip].[problemstatements] p join [thrip].[horisons] h on p.[horisonID] = h.[horisonID] where p.OrgID = {}".format(
                session['OrgId'])).fetchall()

        active_problems = db.execute(
            "Select count(*) from [thrip].[problemstatements] where OrgID = {} and IsActive = 'Yes'".format(session['OrgId'])).fetchall()
        closed_problems = db.execute(
            "Select count(*) from [thrip].[problemstatements] where OrgID = {} and IsActive = 'No'".format(session['OrgId'])).fetchall()
        innovations = db.execute(
            "select count(*) from [thrip].[innovation] where OrgID = {}".format(session['OrgId'])).fetchall()

        problem_rating = db.execute("""   SELECT
                                            problemID, sum(rating) / COUNT(rating) as 'Rating', count(rating) as 'Total'
                                            FROM[thrip].[problemratings]
                                            where OrgID = {}
                                            group by problemID""".format(session['OrgId'])).fetchall()

        user_problem_rating = db.execute("""
                                            SELECT p.OrgID, p.problemratingID, u.firstname, u.surname, p.problemID, p.rating, p.feedback 
                                            FROM [thrip].[problemratings] p
                                            join [thrip].[orgusers] u on p.userID = u.userID
                                            where p.OrgID = {}""".format(session['OrgId'])).fetchall()

        if request.method == "POST":
            if request.form["problems"] == "Submit Problem":

                try:
                    f = request.files['file']
                    date = datetime.date.today()
                    f.filename = str(date) + "_" + f.filename
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    db.execute("""
                                                  Insert into [thrip].[problemstatements] 
                                                  (OrgId, userID, name, description, orgFunctionName, timestamp, isActive, horisonID, attatchedFile, qtype) 
                                                  values 
                                                  ({}, {}, '{}', '{}', '{}', GETDATE(), 'Yes', {}, '{}', {}')
                                                  """.format(session['OrgId'], session['UserId'],
                                                             request.form["PName"], request.form["UDesc"],
                                                             request.form["UFunc"], request.form["UTime"],
                                                             secure_filename(f.filename), request.form["Utype"] ))

                    db.commit()
                    cps = db.execute("select gcpsi from [thrip].[gamification] where userID ={}".format( session['UserId'])).fetchone()
                    cps = cps[0] + int(request.form["UTime"]) 
                    db.execute("""
                                UPDATE [thrip].[gamification] 
                                        SET gcpsi = '{}' where userID = {}
                                        """.format(cps, session["UserId"]))    
                    db.commit()
                    if (request.form["passvar"]=="1"):
                      return redirect(url_for('users_file.AdminDashboard', org_name=session["OrgName"]))
                    else:  
                      return redirect(url_for('surveys_file.problems', org_name=session["OrgName"]))

                except:

                    db.execute("""
                              Insert into [thrip].[problemstatements] 
                              (OrgId, userID, name, description, orgFunctionName, timestamp, isActive, horisonID, qtype) 
                              values 
                              ({}, {}, '{}', '{}', '{}', GETDATE(), 'Yes', '{}', '{}')
                              """.format(session['OrgId'], session['UserId'],
                                         request.form["PName"], request.form["UDesc"],
                                         request.form["UFunc"], request.form["UTime"], request.form["Utype"]))

                    db.commit()
                    cps = db.execute("select gcpsi from [thrip].[gamification] where userID ={}".format( session['UserId'])).fetchone()
                    cps = cps[0] + int(request.form["UTime"]) 
                    db.execute("""
                                UPDATE [thrip].[gamification] 
                                        SET gcpsi = '{}' where userID = {}
                                        """.format(cps, session["UserId"]))    
                    db.commit()
                    if (request.form["passvar"]=="1"):
                      return redirect(url_for('users_file.dashboard', org_name=session["OrgName"]))
                    else:  
                      return redirect(url_for('surveys_file.problems', org_name=session["OrgName"]))

            elif request.form["problems"] == "Edit Problem":
                db.execute("""
                                  UPDATE [thrip].[problemstatements] 
                                  SET name = '{}', description = '{}', orgFunctionName = '{}', horisonID = {}, qtype = '{}' where problemID = {}
                                  """.format(request.form["EName"], request.form["EDesc"],
                                             request.form["EFunc"], request.form["ETime"], request.form["Etype"], request.form["probID"]))
                db.commit()
                return redirect(url_for('surveys_file.problems', org_name=session["OrgName"]))

            if request.form["problems"] == "View Type":
                intype = request.form["InType"]
                if intype == "Complaints":
                    return render_template('problems.html', org_name=session["OrgName"], intype=intype,
                                           Problems=Complaints,
                                           active_problems=active_problems[0], closed_problems=closed_problems[0],
                                           innovations=innovations[0], problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating)

                elif intype == "Problems" :
                    return render_template('problems.html', org_name=session["OrgName"], intype=intype,
                                           Problems=problems,
                                           active_problems=active_problems[0], closed_problems=closed_problems[0],
                                           innovations=innovations[0], problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating)

                elif intype == "Ideas":
                    return render_template('problems.html', org_name=session["OrgName"], intype=intype,
                                           Problems=Ideas, Ideas=Ideas, Complaints=Complaints,
                                           active_problems=active_problems[0], closed_problems=closed_problems[0],
                                           innovations=innovations[0], problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating)

                else:
                    return render_template('problems.html', org_name=session["OrgName"], intype = intype, Problems=Problems, active_problems=active_problems[0], closed_problems=closed_problems[0], innovations=innovations[0], problem_rating=problem_rating, user_problem_rating=user_problem_rating )

        return render_template('problems.html', test = test, intype = session['type'] , Problems=Problems,Ideas=Ideas,Complaints=Complaints, active_problems=active_problems[0], closed_problems=closed_problems[0], innovations=innovations[0], problem_rating=problem_rating, user_problem_rating=user_problem_rating)
    else:
        error = 'You are not logged in'
        return render_template('login.html', Error=error)


@surveys_file.route('/problems/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)


@surveys_file.route('/<string:org_name>/Innovations', methods=["POST", "GET"])
def innovations(org_name):
    if session.get('UserId'):
        inHR = db.execute(
            "Select i.*, p.name as 'ProbName',p.orgFunctionName as Department from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where  p.orgFunctionName= 'HR' AND i.OrgID = {} ".format(session['OrgId'])).fetchall()
        inFin = db.execute(
            "Select i.*, p.name as 'ProbName',p.orgFunctionName as Department from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where  p.orgFunctionName= 'Finance' AND i.OrgID = {} ".format(
                session['OrgId'])).fetchall()
        inMan = db.execute(
            "Select i.*, p.name as 'ProbName',p.orgFunctionName as Department from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where  p.orgFunctionName= 'Management' AND i.OrgID = {} ".format(
                session['OrgId'])).fetchall()
        inProd = db.execute(
            "Select i.*, p.name as 'ProbName',p.orgFunctionName as Department from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where  p.orgFunctionName= 'Production' AND i.OrgID = {} ".format(
                session['OrgId'])).fetchall()
        inIT = db.execute(
            "Select i.*, p.name as 'ProbName' ,p.orgFunctionName as Department from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where  p.orgFunctionName= 'IT' AND i.OrgID = {} ".format(
                session['OrgId'])).fetchall()
        inEng = db.execute(
            "Select i.*, p.name as 'ProbName' ,p.orgFunctionName as Department from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where  p.orgFunctionName= 'Engineering' AND i.OrgID = {} ".format(
                session['OrgId'])).fetchall()

        innovations = db.execute(
            "Select i.*, p.name as 'ProbName', p.orgFunctionName as Department  from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where i.OrgID = {}".format(session['OrgId'])).fetchall()
        active_innovations = db.execute(
            "select count(*) from [thrip].[innovation] where OrgID = {}".format(session['OrgId'])).fetchall()
        actions_campaigns = db.execute(
            "select sum(campaignID), sum(actionID) from [thrip].[innovation] where OrgID = {}".format(session['OrgId'])).fetchall()
        # Need to be changes to gateproblemstatements
        # problems = db.execute(
        #     "Select * from [thrip].[gateproblemstatements] where OrgID = {}".format(session['OrgId'])).fetchall()
       
        problems = db.execute(
            "Select * from [thrip].[problemstatements] where OrgID = {}".format(session['OrgId'])).fetchall()
        active_problems = db.execute(
            "Select count(*) from [thrip].[problemstatements] where OrgID = {} and IsActive = 'Yes'".format(session['OrgId'])).fetchall()
        innovperprob = active_innovations[0][0] // active_problems[0][0]
        if request.method == "POST":
          if request.form["problems"] == "Submit Innovation":
            try:
                f = request.files['file']
#program can break here due to file formats. beperk users to spefici formats
                date = datetime.date.today()
                f.filename = str(date) + "_" + f.filename
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                db.execute("""
                                  Insert into [thrip].[innovation] 
                                  (OrgId, userID, problemID, name, description, horisonID, campaignID, innovationStatusTypeID, actionID, [businessCaseFile]) 
                                  values 
                                  ({}, {}, {}, '{}', '{}', '{}', {}, 'In Creation', 0, '{}')
                                  """.format(session['OrgId'], session['UserId'],
                                             request.form["UProb"], request.form["Innov"],
                                             request.form["UDesc"], request.form["UTime"], request.form["Camp"], secure_filename(f.filename)))
                db.commit()
                cps = db.execute("select gcpsi from [thrip].[gamification] where userID ={}".format( session['UserId'])).fetchone()
                cps = cps[0] + int(request.form["UTime"]) 
                db.execute("""
                                  UPDATE [thrip].[gamification] 
                                SET gcpsi = '{}' where userID = {}
                                """.format(cps, session["UserId"]))    
                db.commit()
                
                return redirect(url_for('surveys_file.innovations', org_name=session["OrgName"]))
            except:
                db.execute("""
                          Insert into [thrip].[innovation] 
                          (OrgId, userID, problemID, name, description, horisonID, campaignID, innovationStatusTypeID, actionID) 
                          values 
                          ({}, {}, {}, '{}', '{}', '{}', {}, 'In Creation', 0)
                          """.format(session['OrgId'], session['UserId'],
                                     request.form["UProb"], request.form["Innov"],
                                     request.form["UDesc"], request.form["UTime"],
                                     request.form["Camp"]))
                db.commit()
                cps = db.execute("select gcpsi from [thrip].[gamification] where userID ={}".format( session['UserId'])).fetchone()
                cps = cps[0] + int(request.form["UTime"]) 
                db.execute("""
                                  UPDATE [thrip].[gamification] 
                                SET gcpsi = '{}' where userID = {}
                                """.format(cps,session["UserId"]))    
                db.commit()
                return redirect(url_for('surveys_file.innovations', org_name=session["OrgName"]))
          elif request.form["problems"] == "Edit Problem":
              db.execute("""
                                UPDATE [thrip].[problemstatements] 
                                SET name = '{}', description = '{}', orgFunctionName = '{}', horisonID = {}, qtype = '{}' where problemID = {}
                                """.format(request.form["EName"], request.form["EDesc"],
                                           request.form["EFunc"], request.form["ETime"], request.form["Etype"],
                                           request.form["probID"]))
              db.commit()
              return redirect(url_for('surveys_file.problems', org_name=session["OrgName"]))
          if request.form["problems"] == "Rate Problem":
              db.execute("""
                                Insert into [thrip].[problemratings]
                                (OrgId, userID, problemID, rating, feedback, options, email) 
                                values 
                                ({}, {}, {}, {}, '{}', '1', 'smithm@fourier.co.za')
                                """.format(session['OrgId'], session['UserId'], request.form["UProb"],
                                           request.form["rating1"], request.form["UFeed"]))
              db.commit()
              cps = db.execute("select gcpsi from [thrip].[gamification] where userID ={}".format( session['UserId'])).fetchone()
              cps = cps[0] + int(request.form["rating1"]) 
              db.execute("""
                           UPDATE [thrip].[gamification] 
                                SET gcpsi = '{}' where userID = {}
                                """.format(cps, session["UserId"]))    
              db.commit()
            #   if (request.form["passvar"]=="1"):
            #           return redirect(url_for('users_file.AdminDashboard', org_name=session["OrgName"]))
            #   else:  
            #           return redirect(url_for('surveys_file.problems', org_name=session["OrgName"]))
              return redirect(url_for('users_file.AdminDashboard', org_name=session["OrgName"]))
          
                #  Email + options can be removed from both th einnovation and problem ratings tables
          elif request.form["problems"] == "Rate Innovation":
              db.execute("""
                                Insert into [thrip].[innovationratings]
                                (OrgId, userID, innovationID, rating, feedback, options, email) 
                                values 
                                ({}, {}, {}, {}, '{}', '1', 'smithm@fourier.co.za')
                                """.format(session['OrgId'], session['UserId'], request.form["UProb"],
                                           request.form["rating1"], request.form["UFeed"]))
              db.commit()
              cps = db.execute("select gcpsi from [thrip].[gamification] where userID ={}".format( session['UserId'])).fetchone()
              cps = cps[0] + int(request.form["rating1"]) 
              db.execute("""
                           UPDATE [thrip].[gamification] 
                                SET gcpsi = '{}' where userID = {}
                                """.format(cps, session["UserId"]))    
              db.commit()
              return redirect(url_for('surveys_file.problems', org_name=session["OrgName"]))    
          elif request.form["problems"] == "Select Department":
              department = request.form["Depart"]
              if department == "HR":
                return render_template('innovations.html', innovations=inHR,innovperprob=innovperprob, active_problems=active_problems, active_innovations=active_innovations[0], actions_campaigns=actions_campaigns[0], problems=problems)
              elif department == "Finance":
                return render_template('innovations.html', innovations=inFin, innovperprob=innovperprob, active_problems=active_problems, active_innovations=active_innovations[0],
                                   actions_campaigns=actions_campaigns[0], problems=problems)
              elif department == "Management":
                return render_template('innovations.html', innovations=inMan, innovperprob=innovperprob, active_problems=active_problems, active_innovations=active_innovations[0],
                                   actions_campaigns=actions_campaigns[0], problems=problems)
              elif department == "Production":
                return render_template('innovations.html', innovations=inProd,innovperprob=innovperprob, active_problems=active_problems,  active_innovations=active_innovations[0],
                                   actions_campaigns=actions_campaigns[0], problems=problems)
              elif department == "IT":
                return render_template('innovations.html', innovations=inIT,innovperprob=innovperprob, active_problems=active_problems,  active_innovations=active_innovations[0],
                                   actions_campaigns=actions_campaigns[0], problems=problems)
              else:
                return render_template('innovations.html',innovperprob=innovperprob, active_problems=active_problems,  innovations=innovations,
                                             active_innovations=active_innovations[0],
                                             actions_campaigns=actions_campaigns[0], problems=problems)

        return render_template('innovations.html',innovperprob=innovperprob, active_problems=active_problems,  innovations=innovations, active_innovations=active_innovations[0], actions_campaigns=actions_campaigns[0], problems=problems)
    else:
        error = 'You are not logged in'
        return render_template('login.html', Error=error)



@surveys_file.route('/<string:org_name>/Gatekeeper ', methods=["POST", "GET"])
def gatekeeper(org_name):
    if session.get('UserId'):
        gateiHR = db.execute(
              "Select * from [thrip].[problemstatements] where orgFunctionName = 'HR' AND OrgID = {}".format(session['OrgId'])).fetchall()
        gateiFin = db.execute(
              "Select * from [thrip].[problemstatements] where orgFunctionName = 'Finance' AND OrgID = {}".format(
                  session['OrgId'])).fetchall()
        gateiMan = db.execute(
              "Select * from [thrip].[problemstatements] where orgFunctionName = 'Management' AND OrgID = {}".format(
                  session['OrgId'])).fetchall()
        gateiProd = db.execute(
              "Select * from [thrip].[problemstatements] where orgFunctionName = 'Production' AND OrgID = {}".format(
                  session['OrgId'])).fetchall()
        gateiIT = db.execute(
              "Select * from [thrip].[problemstatements] where orgFunctionName = 'IT' AND OrgID = {}".format(
                  session['OrgId'])).fetchall()
        testotw = "896"
         
        problemnotgatelist = db.execute(
              "Select p.problemID, g.problemID as 'GateID' from [thrip].[problemstatements] p join [thrip].[gateinputs] g on p.[problemID] <> g.[problemID] where p.OrgID = {}".format(
                  session['OrgId'])).fetchall()
        problemnotgateid = []
        test = []
        for i in problemnotgatelist:
               test.append(i)
        problemnotgateid1 = [item[1] for item in problemnotgatelist]       
        problemnotgateid = tuple(problemnotgateid1)
        problemnotgate =  db.execute(
            "Select * from [thrip].[problemstatements] where problemID NOT IN {}  AND OrgID = {}".format( (problemnotgateid) , session['OrgId'])).fetchall()
      
        gatePS = db.execute(
            "Select * from [thrip].[gateproblemstatements] where PSStatus = 'Active' AND OrgID = {}".format(session['OrgId'])).fetchall()
        
        active_innovations = db.execute(
            "select count(*) from [thrip].[innovation] where OrgID = {}".format(session['OrgId'])).fetchall()
        active_inputs = db.execute(
            "select count(*) from [thrip].[problemstatements] where OrgID = {}".format(session['OrgId'])).fetchall()
        active_problemstaments = db.execute(
            "select count(*) from [thrip].[gateproblemstatements] where OrgID = {}".format(session['OrgId'])).fetchall()
        test = "0"  

       # problemtest = "Select i.* from [thrip].[problemstatements] i join [thrip].[problemstatements] p on i.problemID = p.problemID where  p.problemID != {} ".survey_id)).fetchall()
        #"""select q.OrgId, q.questionID, q.surveyID, q.questionGroupID, q.name as 'Questions', g.name, q.OptionType from [thrip].[questions11] q
       #                                         left join [thrip].[questiongroups] g on q.questionGroupID = g.questionGroupID where q.OrgID = {} and q.surveyID = {}""".format(session['OrgId'], survey_id)).fetchall()

        #add here where id not in gate table
        problems = db.execute(
            "Select * from [thrip].[problemstatements] where OrgID = {}".format(session['OrgId'])).fetchall()
        problem_rating = db.execute("""   SELECT
                                                   problemID, sum(rating) / COUNT(rating) as 'Ratings', count(rating) as 'Total'
                                                   FROM[thrip].[problemratings]
                                                   where OrgID = {}
                                                   group by problemID""".format(session['OrgId'])).fetchall()

        user_problem_rating = db.execute("""
                                                   SELECT p.OrgID, p.problemratingID, u.firstname, u.surname, p.problemID, p.rating, p.feedback 
                                                   FROM [thrip].[problemratings] p
                                                   join [thrip].[orgusers] u on p.userID = u.userID
                                                   where p.OrgID = {}""".format(session['OrgId'])).fetchall()

        if request.method == "POST":
          
          if request.form["problems"] == "Submit Problem Statement":
            try:
                
                db.execute("""
                                  Insert into [thrip].[gateproblemstatements] 
                                  ( OrgId,  name, description, orgFunctionName, PSStatus, PSScore) 
                                  values 
                                  ('{}', {}, '{}', '{}', '{}', '{}')
                                  """.format(session['OrgId'],
                                              request.form["PSName"],
                                             request.form["UDesPS"], request.form["UFunPS"], request.form["StatPS"], request.form["UPSScore"]))
                db.commit()
                return redirect(url_for('surveys_file.gatekeeper', org_name=session["OrgName"]))
            except:
                preprobID = request.form.getlist('UPSS')
                db.execute("""
                          Insert into [thrip].[gateproblemstatements] 
                                  (OrgId,  name, description, orgFunctionName, PSStatus, PSScore) 
                                  values 
                                  ( {}, '{}', '{}', '{}', '{}', '{}')
                                  """.format(session['OrgId'], request.form["PSName"], request.form["UDesPS"], request.form["UFunPS"], request.form["StatPS"], request.form["UPSScore"]))
                db.commit()
                return redirect(url_for('surveys_file.gatekeeper', org_name=session["OrgName"]))
          elif request.form["problems"] == "Edit Problem Statement":
              #preprobID = request.form.getlist('EPS')
              OGStatus = db.execute("Select PSStatus from[thrip].[gateproblemstatements]  where gateproblemID = {}".format(request.form["gateprobID"])).fetchall()
                               
                                             
              db.execute("""
                                UPDATE [thrip].[gateproblemstatements] 
                                  SET name = '{}', description = '{}', orgFunctionName = '{}', PSStatus = '{}', PSScore = '{}' where gateproblemID = '{}'
                                  """.format(request.form["EPSName"], request.form["EDesPS"], request.form["EFunPS"], request.form["EStatPS"], request.form["EPSScore"], request.form["gateprobID"]))
              db.commit()
              useridprob = "test"
              NewStatus = request.form["EStatPS"]
              username = ""
              emailuser = ""
              if OGStatus[0][0] != NewStatus :
                    useridprob =   db.execute("select p.userID, p.problemID from [thrip].[problemstatements] p join [thrip].[gateinputs] u on p.[problemID] = u.[problemID] where u.gateproblemID = {}".format(request.form["gateprobID"])).fetchall()

                    
                    tempbadge =[]
                    for i in useridprob :
                        tempbadge = i
                        username = db.execute("select firstname from [thrip].[orgusers] where UserId = {}".format(tempbadge[0])).fetchone()
                        emailuser = db.execute("select email from [thrip].[orgusers] where UserId = {}".format(tempbadge[0])).fetchone()
                        probname = db.execute("select name, description from [thrip].[problemstatements] where problemID = {}".format(tempbadge[1])).fetchone()
                      
                        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                    
                        confirm_url = url_for(
                            'users_file.confirm_email',
                            token=confirm_serializer.dumps(emailuser[0], salt='email-confirmation-salt'),
                            _external=True)

                        html = render_template(
                            'email_problemclosed.html',
                            confirm_url=confirm_url, score = tempbadge[1], badgename = tempbadge[0], username = username, probname = probname[0], probdes = probname[1] )

                        message = Mail(
                            from_email='vdlinden@fourier.co.za',
                            to_emails=emailuser[0],
                            subject='Your problem is solved!',
                            html_content=html)
                        try:
                            sg = SendGridAPIClient('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')
                            response = sg.send(message)
                            print(response.status_code)
                            print(response.body)
                            print(response.headers)
                        except Exception as e:
                            print(e.args)


              #return redirect(url_for('surveys_file.gatekeeper', org_name=session["OrgName"], useridprob = useridprob))
              return render_template('gatekeeper.html',problem_rating=problem_rating, OGStatus = OGStatus[0][0], NewStatus = NewStatus,
                                           user_problem_rating=user_problem_rating, useridprob = useridprob, username = username, emailuser = emailuser, gatePS = gatePS, problems=problems, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0])
             
          elif request.form["problems"] == "Select Department":
              department = request.form["Depart"]
              if department == "HR":
                return render_template('gatekeeper.html', problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating, gatePS = gatePS, problems=gateiHR, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0])
              elif department == "Finance":
                return render_template('gatekeeper.html',problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating, gatePS = gatePS, problems=gateiFin, active_innovations = active_innovations[0],
                                   active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0])
              elif department == "Management":
                return render_template('gatekeeper.html',problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating, gatePS = gatePS, problems=gateiMan,
                                   active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0])
              elif department == "Production":
                return render_template('gatekeeper.html',problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating, gatePS = gatePS, problems=gateiProd,
                                       active_innovations=active_innovations[0], active_inputs=active_inputs[0], active_problemstaments=active_problemstaments[0])
              elif department == "IT":
                return render_template('gatekeeper.html',problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating, gatePS = gatePS, problems=gateiIT, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0])
              else:
                return render_template('gatekeeper.html', problem_rating=problem_rating,
                                           user_problem_rating=user_problem_rating, gatePS = gatePS, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0], problems=problems)
          elif request.form["problems"] == "Link Survey Inputs":
                probleminputs = request.form["inprob"]
                db.execute("""Insert into [thrip].[gateinputs] ( problemID, gateproblemID) values ('{}', '{}')""".format(
                  probleminputs, request.form["PSin"]))
                db.commit()
                return redirect(url_for('surveys_file.gatekeeper', org_name=session["OrgName"]))
        #  ------REMEMBER TO FIND AND REPLACE ORGUSERS3 WITH ORGUSERS - TEST DATA WITH REAL DATA -------------------------------------------------------------------------
          elif request.form["problems"] == "Send mails":
            # user_email = "nanetvdl@gmail.com"
            if request.form["Com"] == "AllCommunication":
                test = "All com"        

                return render_template('gatekeeper.html',problem_rating=problem_rating,
                                            user_problem_rating=user_problem_rating, gatePS = gatePS, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0], problems=problems, problemnotgate = problemnotgate, problemnotgateid=problemnotgateid, test = test )
            elif request.form["Com"] == "InactiveUsers":
                    test = "InactiveUsers" 
                    userIDs = db.execute("select userID from [thrip].[orgusers3] where OrgID = {}".format(session["OrgId"])).fetchall()

                    todaydate= datetime.now()
                    for i in userIDs:
                      usertime = db.execute("select time from [thrip].[orgusers3] where UserID = {}".format(i[0])).fetchone()
                      
                      date_time_obj = datetime.strptime(usertime[0], '%Y-%m-%d')
                      difference = (todaydate - date_time_obj ).days 
                      if   (difference > 3) :   
                        username = db.execute("select firstname from [thrip].[orgusers3] where UserId = {}".format(i[0])).fetchone()
                        emailuser = db.execute("select email from [thrip].[orgusers3] where UserId = {}".format(i[0])).fetchone()
                    
                        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                    
                        confirm_url = url_for(
                            'users_file.confirm_email',
                            token=confirm_serializer.dumps(emailuser[0], salt='email-confirmation-salt'),
                            _external=True)

                        html = render_template(
                            'email_inactiveuser.html',
                            confirm_url=confirm_url, difference = difference, username = username)

                        message = Mail(
                            from_email='vdlinden@fourier.co.za',
                            to_emails=emailuser[0],
                            subject='We miss you !',
                            html_content=html)
                        try:
                            sg = SendGridAPIClient('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')
                            response = sg.send(message)
                            print(response.status_code)
                            print(response.body)
                            print(response.headers)
                        except Exception as e:
                            print(e.args)
                    return render_template('gatekeeper.html',problem_rating=problem_rating,
                                            user_problem_rating=user_problem_rating, gatePS = gatePS, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0], problems=problems, problemnotgate = problemnotgate, problemnotgateid=problemnotgateid, test = test )
            elif request.form["Com"] == "HighImportanceInput":
                    test = "HighImportanceInput"        
                    #get the problemsID and find the top 5 and save only the name (first element in list)  
                    gateproblemstatementID = db.execute("select name, PSScore from [thrip].[gateproblemstatements] where OrgID = {}".format(session["OrgId"])).fetchall()
                    top5probname = []
                    top5prob = sorted(gateproblemstatementID, key = lambda x: x[1], reverse = True)[:5]
                    
                    for i in top5prob:
                        top5probname.append(i[0])
                   
                    userIDs = db.execute("select userID from [thrip].[orgusers3] where OrgID = {}".format(session["OrgId"])).fetchall()

                    for i in userIDs:
                        username = db.execute("select firstname from [thrip].[orgusers3] where UserId = {}".format(i[0])).fetchone()
                        emailuser = db.execute("select email from [thrip].[orgusers3] where UserId = {}".format(i[0])).fetchone()
                    
                        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                    
                        confirm_url = url_for(
                            'users_file.confirm_email',
                            token=confirm_serializer.dumps(emailuser[0], salt='email-confirmation-salt'),
                            _external=True)

                        html = render_template(
                            'email_top5prob.html',
                            confirm_url=confirm_url, top5probname = top5probname, username = username)

                        message = Mail(
                            from_email='vdlinden@fourier.co.za',
                            to_emails=emailuser[0],
                            subject='Top 5 Problems need YOUR help !',
                            html_content=html)
                        try:
                            sg = SendGridAPIClient('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')
                            response = sg.send(message)
                            print(response.status_code)
                            print(response.body)
                            print(response.headers)
                        except Exception as e:
                            print(e.args)
                    return render_template('gatekeeper.html',problem_rating=problem_rating,
                                                    user_problem_rating=user_problem_rating, gatePS = gatePS, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0], problems=problems, problemnotgate = problemnotgate, problemnotgateid=problemnotgateid, test = test )
            elif request.form["Com"] == "CloseTobadge":
                    test = "CloseTobadge"        
                    #get the problemsID and find the top 5 and save only the name (first element in list)  
                    gamscores = db.execute("select p.userID, p.gcpsi from [thrip].[gamification] p join [thrip].[orgusers] u on p.[userID] = u.[userID] where u.OrgID = {}".format(session["OrgId"])).fetchall()

                            #"Select p.problemID, g.problemID from [thrip].[problemstatements] p join [thrip].[gateinputs] g on p.[problemID] <> g.[problemID] where p.OrgID = {}".format(session['OrgId'])).fetchall()
                    badgelist = []
                    for i in gamscores:
                        #close to badge 1 (near 50)
                      if (i[1]< 50) and (i[1]>30):
                        badgelist.append(["50 Score", i[0], i[1]])
                        
                        #close to badge 2 (near 100)
                      if (i[1]< 100) and (i[1]>70):
                        badgelist.append(["100 Score", i[0], i[1]]) 
                        
                        #close to badge 3 (near 150)
                      if (i[1]< 150) and (i[1]>120):
                        badgelist.append(["150 Score", i[0], i[1]])
                         
                    
                    tempbadge =[]
                    for i in badgelist :
                        tempbadge = i
                        userids = tempbadge[1]
                       
                        #userids = int(userid)
                        username = db.execute("select firstname from [thrip].[orgusers3] where UserId = {}".format(tempbadge[1])).fetchone()
                        emailuser = db.execute("select email from [thrip].[orgusers3] where UserId = {}".format(tempbadge[1])).fetchone()

                        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                    
                        confirm_url = url_for(
                            'users_file.confirm_email',
                            token=confirm_serializer.dumps(emailuser[0], salt='email-confirmation-salt'),
                            _external=True)

                        html = render_template(
                            'email_closetobadge.html',
                            confirm_url=confirm_url, score = tempbadge[1], badgename = tempbadge[0], username = username )

                        message = Mail(
                            from_email='vdlinden@fourier.co.za',
                            to_emails=emailuser[0],
                            subject='Congratulations your close to your next achievement.',
                            html_content=html)
                        try:
                            sg = SendGridAPIClient('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')
                            response = sg.send(message)
                            print(response.status_code)
                            print(response.body)
                            print(response.headers)
                        except Exception as e:
                            print(e.args)
                    return render_template('gatekeeper.html', badgelist = badgelist, badgename = tempbadge, username = username, emailuser = emailuser,
                        problem_rating=problem_rating,user_problem_rating=user_problem_rating, gatePS = gatePS, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0], problems=problems, problemnotgate = problemnotgate, problemnotgateid=problemnotgateid, test = test )
            elif request.form["Com"] == "TimeBasedChallenge":
                    test = "TimeBasedChallenge"        
                    # request.form["UDesPS"]
                    timetbchal = request.form["tbchaltime"]
                    gateid =  request.form["probtbchal"]
                    gateprobname =  db.execute("select name, description from [thrip].[gateproblemstatements] where gateproblemID = {}".format(gateid)).fetchone()
                   
                    userIDs = db.execute("select userID from [thrip].[orgusers3] where OrgID = {}".format(session["OrgId"])).fetchall()

                    for i in userIDs:
                        username = db.execute("select firstname from [thrip].[orgusers3] where UserId = {}".format(i[0])).fetchone()
                        emailuser = db.execute("select email from [thrip].[orgusers3] where UserId = {}".format(i[0])).fetchone()
                    
                        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                    
                        confirm_url = url_for(
                            'users_file.confirm_email',
                            token=confirm_serializer.dumps(emailuser[0], salt='email-confirmation-salt'),
                            _external=True)

                        html = render_template(
                            'email_timebasedchallenge.html',
                            confirm_url=confirm_url, gateprobname = gateprobname, timetbchal = timetbchal, username = username, )

                        message = Mail(
                            from_email='vdlinden@fourier.co.za',
                            to_emails=emailuser[0],
                            subject='Time Challenge to Innovate !',
                            html_content=html)
                        try:
                            sg = SendGridAPIClient('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')
                            response = sg.send(message)
                            print(response.status_code)
                            print(response.body)
                            print(response.headers)
                        except Exception as e:
                            print(e.args)
                    return render_template('gatekeeper.html',problem_rating=problem_rating,
                                                    user_problem_rating=user_problem_rating, gatePS = gatePS, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0], problems=problems, problemnotgate = problemnotgate, problemnotgateid=problemnotgateid, test = test )
         
                 
          return render_template('gatekeeper.html',problem_rating=problem_rating,
                                            user_problem_rating=user_problem_rating, gatePS = gatePS, active_innovations=active_innovations[0],  active_inputs = active_inputs[0], active_problemstaments = active_problemstaments[0], problems=problems, problemnotgate = problemnotgate, problemnotgateid=problemnotgateid, test = test )

        else:
           return render_template('gatekeeper.html',problem_rating=problem_rating,
                                user_problem_rating=user_problem_rating, gatePS = gatePS, active_innovations=active_innovations[0],
                                        active_inputs=active_inputs[0], active_problemstaments=active_problemstaments[0],
                                        problems=problems, problemnotgate = problemnotgate,problemnotgateid=problemnotgateid)
    
    else:
        error = 'You are not logged in'
        return render_template('login.html', Error=error)

@surveys_file.route('/innovations/<path:filename>', methods=['GET', 'POST'])
def download_innovate(filename):
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)


@surveys_file.route('/<string:org_name>/Analysis', methods=["POST", "GET"])
def analysis(org_name):
    if session.get('UserId'):
        analysis = db.execute("Select * from [thrip].[analysis] where OrgID = {}".format(session['OrgId'])).fetchall()
        return render_template('analysis.html', analysis=analysis)
    else:
        error = 'You are not logged in'
        return render_template('login.html', Error=error)
