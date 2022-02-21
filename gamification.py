import pdfkit 
import jinja2
from pdfkit.api import configuration
import pyodbc
from flask import Flask, make_response, send_from_directory, Blueprint, render_template, request, session, redirect, url_for, flash
from flask_database import db
from datetime import timedelta
import pdfkit
from datetime import datetime
from datetime import date
from passlib.hash import sha256_crypt
from threading import Thread
from itsdangerous import URLSafeTimedSerializer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import json 


print()

gamification_file = Blueprint('gamification_file', __name__, template_folder='templates', static_folder='static')

app = Flask(__name__)

app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# mail = Mail(app)

WTF_CSRF_ENABLED = True
# -----------------------------------------remove org3 with org - find and replace 
@gamification_file.route('/<string:org_name>/Dashboardg', methods=['GET', 'POST'])
def dashboardg(org_name):
    if session.get('UserId'):
        allprob = db.execute("Select problemID, userID, name, description from [thrip].[problemstatements] where OrgID = {} and IsActive = 'Yes' ".format(session['OrgId'])).fetchall()
        allinnov = db.execute("Select innovationID, userID, name, description from [thrip].[innovation] where OrgID = {} ".format(session['OrgId'])).fetchall()
       
        users = db.execute("Select * from [thrip].[orgusers] where OrgID = {} and userID = {}".format(session['OrgId'], session['UserId'])).fetchone()
        if request.method == "POST":
            if (request.form["topotw"] == "Schedule Brainstorming Session") :
                datesched = request.form["datesched"]
                timesched =  request.form["timesced"]
                subject =  request.form["subject"]
                meetlink = request.form["meetlink"]
                author = db.execute("select firstname, surname, email from [thrip].[orgusers] where OrgID = {} and userID = {}".format(session["OrgId"], session['UserId'])).fetchone() 
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
                        'email_topproblem.html',
                        confirm_url=confirm_url,  timesched = timesched, datesched = datesched, author = author, meetlink = meetlink, subject = subject, username = username, )

                    message = Mail(
                        from_email='vdlinden@fourier.co.za',
                        to_emails=emailuser[0],
                        subject='You are invited!',
                        html_content=html)
                    try:
                        sg = SendGridAPIClient('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')
                        response = sg.send(message)
                        print(response.status_code)
                        print(response.body)
                        print(response.headers)
                    except Exception as e:
                        print(e.args)
                
                return render_template('AdminDash.html',allprob = allprob, allinnov = allinnov, org_name=session["OrgName"],users=users )
            if (request.form["topotw"] == "Send Views Mail ") :
                selprob =  db.execute("select userID, name, description from [thrip].[problemstatements] where problemId = {}".format(request.form["selprob"])).fetchone()
                viewmail =  request.form["emailviews"]
                username =  db.execute("select firstname, email from [thrip].[orgusers3] where userID = {}".format(selprob[0])).fetchone()
                   
                author = db.execute("select firstname, surname, email from [thrip].[orgusers] where OrgID = {} and userID = {}".format(session["OrgId"], session['UserId'])).fetchone() 
                
            
                confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            
                confirm_url = url_for(
                    'users_file.confirm_email',
                    token=confirm_serializer.dumps(username[1], salt='email-confirmation-salt'),
                    _external=True)

                html = render_template(
                    'email_toprank.html',
                    confirm_url=confirm_url,  selprob = selprob, viewmail = viewmail, author = author, username = username, )

                message = Mail(
                    from_email='vdlinden@fourier.co.za',
                    to_emails=username[1],
                    subject = 'Feedback on your problem',
                    html_content=html)
                try:
                    sg = SendGridAPIClient('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')
                    response = sg.send(message)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as e:
                    print(e.args)
            
            return render_template('AdminDash.html',allprob = allprob, allinnov = allinnov, org_name=session["OrgName"],users=users )

            
          
        return render_template('AdminDash.html',allprob = allprob, allinnov = allinnov, org_name=session["OrgName"], users=users) 
    else:
        error = 'You are not logged in'
        return render_template('login.html', Error=error)

@gamification_file.route('/<string:org_name>/.download', methods=['GET', 'POST'])
def download(org_name):
   # dynamic html to pdf with variable passing  - install wkhtmltopdf - pip pdfkit jinja2, os , 
   # add if statement to get innovation pdf here 
    Problems = db.execute(
            "Select p.*, h.description as 'Horizon' from [thrip].[problemstatements] p join [thrip].[horisons] h on p.[horisonID] = h.[horisonID] where p.OrgID = {}".format(
                session['OrgId'])).fetchall()

    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "templates/test.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(Problems = Problems )
    html_file = open('test.html', 'w')
    html_file.write(outputText)
    html_file.close()
    #return outputText

    file = "name.pdf"
    name = "names"
    pdfkit.from_file('test.html',  'name.pdf' )
    workingdir = os.path.abspath(os.getcwd())
    return send_from_directory(workingdir, file)
   
@gamification_file.route('/<string:org_name>/.report', methods=['GET', 'POST'])
def report(org_name):
    test = 1
    active_problems_user = db.execute(
            "Select count(*) from [thrip].[problemstatements] where OrgID = {} and userID = {} and IsActive = 'Yes'".format(session['OrgId'],session['UserId'])).fetchall()
    active_problems = db.execute(
            "Select count(*) from [thrip].[problemstatements] where OrgID = {} and IsActive = 'Yes'".format(session['OrgId'])).fetchall()
    innovations_user = db.execute(
            "select count(*) from [thrip].[innovation] where OrgID = {} and userID = {}".format(session['OrgId'],session['UserId'])).fetchall()
   
    # closed_problems = db.execute(
    #         "Select count(*) from [thrip].[problemstatements] where OrgID = {} and IsActive = 'No'".format(session['OrgId'])).fetchall()
    innovations = db.execute(
            "select count(*) from [thrip].[innovation] where OrgID = {}".format(session['OrgId'])).fetchall()
    ratingsrate_user = db.execute(
            "select count(*) from [thrip].[problemratings] where OrgID = {} and userID ={}".format(session['OrgId'], session['UserId'])).fetchall()
    ratingsrate = db.execute(
            "select count(*) from [thrip].[problemratings] where OrgID = {} ".format(session['OrgId'])).fetchall()
#    display all the orgs in db amount of innov rabnks anf probs for graph 
    allprobs = db.execute(
            "Select count(*) from [thrip].[problemstatements] where not OrgID = '0'").fetchall()
    allinnov = db.execute(
            "Select count(*) from [thrip].[innovation] where not OrgID = '0'").fetchall()
    allranks = db.execute(
            "Select count(*) from [thrip].[problemratings] where not OrgID = '0'").fetchall()
    allorg = [allprobs,allinnov, allranks]
    org = [active_problems, innovations, ratingsrate ]
    user = [active_problems_user,innovations_user,ratingsrate_user]
   

    return render_template('gamification_report.html', allranks = allranks, allinnov=allinnov, allprobs=allprobs, ratingsrate_user = ratingsrate_user, ratingsrate = ratingsrate, innovations = innovations, innovations_user = innovations_user, active_problems = active_problems, active_problems_user = active_problems_user, test = test)

            # 
