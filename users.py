import pdfkit
import pyodbc
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

print()

users_file = Blueprint('users_file', __name__, template_folder='templates', static_folder='static')

app = Flask(__name__)

app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# mail = Mail(app)

WTF_CSRF_ENABLED = True


def send_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    confirm_url = url_for(
        'users_file.confirm_email',
        token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
        _external=True)

    html = render_template(
        'email_confirmation.html',
        confirm_url=confirm_url)

    message = Mail(
        from_email='vdlinden@fourier.co.za',
        to_emails=user_email,
        subject='Validate Account',
        html_content=html)
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.args)


def send_password_reset_email(user_email):
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    password_reset_url = url_for(
        'users_file.reset_with_token',
        token=password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
        _external=True)

    html = render_template(
        'password_reset_email.html',
        password_reset_url=password_reset_url)

    message = Mail(
        from_email='vdlinden@fourier.co.za',
        to_emails=user_email,
        subject='Reset Password',
        html_content=html)
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.args)


@users_file.route('/', methods=["POST", "GET"])
def login_org():
    if session.get('UserId'):
         timesf = date.today()
        #  ----------------------------------------------------------------------
         db.execute("""
                                UPDATE [thrip].[orgusers] 
                                  SET times = '{}' where userID = '{}'
                                  """.format(timesf, session['UserId'] ))
         db.commit()
         oftheweek1 = db.execute(
                "select gtopprob, gtopinnov, gtoprank, gbadge1, gbadge2, gbadge3, gbadge4, gbadge5, gbadge6, gbadge7, gbadge8 from [thrip].[gamification] where userID= {}".format(newuser[2])).fetchone()
         session['OftheWeek'] = oftheweek1[0]
         session['OftheWeeki'] = oftheweek1[1]
         session['OftheWeekr'] = oftheweek1[2]
         session['gbadge10'] = oftheweek1[3]
         session['gbadge50'] = oftheweek1[4]
         session['gbadge100'] = oftheweek1[5]
         session['gbadgeprob'] = oftheweek1[6]
         session['gbadgeinnov'] = oftheweek1[7]
         session['gbadgerank'] = oftheweek1[8]
         session['gbadgecal'] = oftheweek1[9]
         session['gbadgetime'] = oftheweek1[10]  
          #  ----------------------------------------------------------------------
         return redirect(url_for('users_file.dashboard', org_name=session["OrgName"]))
    else:

        if request.method == "POST":
            newuser = db.execute(
                """select o.organisationName, u.OrgID, u.userID, u.firstname, u.admin, u.password, u.surname, 
                u.verified from [thrip].[orgusers] u join [thrip].[organisations] o on u.OrgId = o.OrgId where 
                u.email = '{}'""".format(
                    request.form["Email"])).fetchone()
            
            oftheweek1 = db.execute(
                "select gtopprob, gtopinnov, gtoprank, gbadge1, gbadge2, gbadge3, gbadge4, gbadge5, gbadge6, gbadge7, gbadge8 from [thrip].[gamification] where userID= {}".format(newuser[2])).fetchone()
            
            if sha256_crypt.verify(request.form["Pswd"], newuser[5]):
                session['OrgId'] = newuser[1]
                session['type'] = 'All'
                session['OrgName'] = newuser[0].replace(" ", "_")
                session['UserId'] = newuser[2]
                session['UserName'] = newuser[3]
                session['Admin'] = newuser[4]
                session['logged_in'] = 1
                session['Surname'] = newuser[6]
                session['Verified'] = newuser[7]
                session['OftheWeek'] = oftheweek1[0]
                session['OftheWeeki'] = oftheweek1[1]
                session['OftheWeekr'] = oftheweek1[2]
                session['gbadge10'] = oftheweek1[3]
                session['gbadge50'] = oftheweek1[4]
                session['gbadge100'] = oftheweek1[5]
                session['gbadgeprob'] = oftheweek1[6]
                session['gbadgeinnov'] = oftheweek1[7]
                session['gbadgerank'] = oftheweek1[8]
                session['gbadgecal'] = oftheweek1[9]
                session['gbadgetime'] = oftheweek1[10]
                print(session['OrgId'])

                return redirect(url_for('users_file.dashboard', org_name=session["OrgName"]))

            else:
                error = 'Your password is incorrect'
                return render_template('login.html', Error=error)

        return render_template('login.html')


@users_file.route('/signup', methods=["POST", "GET"])
def signup():
    if session.get('UserId'):
        return redirect(url_for('users_file.dashboard', org_name=session["OrgName"]))
    else:

        orgs = db.execute("SELECT * FROM [thrip].[organisations]").fetchall()

        if request.method == "POST":

            useremail = db.execute("select email from [thrip].[orgusers] where OrgId = {}".format(request.form["Organisation"])).fetchall()

            for i in range(0, len(useremail)):
                if request.form["Email"] == useremail[i][0]:
                    Error = "This email already exists"
                    return render_template('register.html', Error=Error)
            timesd = date.today()    
            db.execute("""
                              Insert into [thrip].[orgusers] 
                              (OrgId, firstname, surname, gender, language, qualification, department, email, verified, token, password, admin, status, times) 
                              values 
                              ({}, '{}', '{}', '', '', '', '', '{}', 0, 0, '{}', 'No', 1, '{}')
                              """.format(request.form["Organisation"], request.form["FName"], request.form["Surname"], request.form["Email"], sha256_crypt.encrypt(request.form["Pswd"]), timesd))

            db.commit()
            confirm = "User added successfully"
            send_confirmation_email(request.form["Email"])
            newuser = db.execute(
                "select o.organisationName, u.userID, u.admin, u.surname, u.verified from [thrip].[orgusers] u join [thrip].[organisations] o on u.OrgId = o.OrgId where u.OrgId = {} and u.email = '{}'".format(request.form["Organisation"], request.form["Email"])).fetchone()
           
           
            oftheweek1 = db.execute(
                "select gtopprob,gtopinnov, gtoprank, gbadge1, gbadge2, gbadge3, gbadge4, gbadge5, gbadge6, gbadge7, gbadge8  from [thrip].[gamification] where userID= {}".format(newuser[1])).fetchone()
            #create session variables after log in (times == today()), gtopinnov, gtoprank,
            session['OrgId'] = request.form["Organisation"]
            session['OrgName'] = newuser[0]
            session['type'] = 'All'
            session['UserId'] = newuser[1]
            session['UserName'] = request.form["FName"]
            session['Admin'] = newuser[2]
            session['Verified'] = newuser[4]
            session['logged_in'] = 1
            session['Surname'] = newuser[3]
            session['OftheWeek'] = oftheweek1[0]
            session['OftheWeeki'] = oftheweek1[1]
            session['OftheWeekr'] = oftheweek1[2]
            session['gbadge10'] = oftheweek1[3]
            session['gbadge50'] = oftheweek1[4]
            session['gbadge100'] = oftheweek1[5]
            session['gbadgeprob'] = oftheweek1[6]
            session['gbadgeinnov'] = oftheweek1[7]
            session['gbadgerank'] = oftheweek1[8]
            session['gbadgecal'] = oftheweek1[9]
            session['gbadgetime'] = oftheweek1[10]
          
            if session['Verified'] == 0:
                return render_template('verification.html', org=orgs)
            else:
                return redirect(url_for('users_file.dashboard', org_name=session["OrgName"]))

        return render_template('register.html', org=orgs)


@users_file.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('users.login'))

    db.execute("Update [thrip].[orgusers] set verified = 1 where email = '{}'".format(email))
    db.commit()

    flash('Thank you for confirming your email address!')

    return redirect(url_for('users_file.dashboard', org_name=session["OrgName"]))


@users_file.route('/ResetPassword', methods=["POST", "GET"])
def reset_password():

    if request.method == "POST":
        email = request.form["emailpass"]
        session['EMailReset'] = request.form["emailpass"]
        send_password_reset_email(email)
        return redirect(url_for('users_file.login_org'))

    return render_template('reset_password.html')


@users_file.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):

    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    if request.method == "POST":
        db.execute("""
                          Update [thrip].[orgusers] 
                          set password = '{}'
                          where email = '{}'
                          """.format(sha256_crypt.encrypt(request.form["password"]), session['EMailReset']))
        session.pop('EMailReset')
        db.commit()

        return redirect(url_for('users_file.login_org'))

    return render_template('reset_password_with_token.html', token=token)


@users_file.route('/<string:org_name>/Dashboard', methods=['GET', 'POST','HEAD'])
def dashboard( org_name):
    if session.get('UserId'):
        allprob = db.execute("Select problemID, userID, name, description, orgFunctionName, qtype from [thrip].[problemstatements] where OrgID = {} and IsActive = 'Yes' ".format(session['OrgId'])).fetchall()
        allfinprob = db.execute("Select problemID, userID, name, description, orgFunctionName, qtype from [thrip].[problemstatements] where OrgID = {} and IsActive = 'Yes' and orgFunctionName = 'Finance' ".format(session['OrgId'])).fetchall()
        allinnov = db.execute(
            "Select i.*, p.name as 'ProbName', p.orgFunctionName as Department  from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where i.OrgID = {}".format(session['OrgId'])).fetchall()
        allfininnov = db.execute(
            "Select i.*, p.name as 'ProbName', p.orgFunctionName as Department  from [thrip].[innovation] i join [thrip].[problemstatements] p on i.problemID = p.problemID where i.OrgID = {} and p.orgFunctionName = 'Finance'".format(session['OrgId'])).fetchall()
        
        users = db.execute("Select * from [thrip].[orgusers] where OrgID = {} and userID = {}".format(session['OrgId'], session['UserId'])).fetchone()
        oftheweek1 = db.execute(
                "select gtopprob, gtopinnov, gtoprank, gbadge1, gbadge2, gbadge3, gbadge4, gbadge5, gbadge6, gbadge7, gbadge8 from [thrip].[gamification] where userID= {}".format(session['UserId'])).fetchone()
        session['OftheWeek'] = oftheweek1[0]
        session['OftheWeeki'] = oftheweek1[1]
        session['OftheWeekr'] = oftheweek1[2]
        session['gbadge10'] = oftheweek1[3]
        session['gbadge50'] = oftheweek1[4]
        session['gbadge100'] = oftheweek1[5]
        session['gbadgeprob'] = oftheweek1[6]
        session['gbadgeinnov'] = oftheweek1[7]
        session['gbadgerank'] = oftheweek1[8]
        session['gbadgecal'] = oftheweek1[9]
        session['gbadgetime'] = oftheweek1[10]  
        
         
      
        if request.method == "POST":
          
            db.execute("""
                                Update [thrip].[orgusers]
                                set firstname = '{}', surname = '{}', gender = '{}', language = '{}', qualification = '{}', department = '{}'
                                where OrgID = {} and userID = {}
                                """.format(request.form["Name"], request.form["Surname"], request.form["Gender"], request.form["Language"], request.form["Qualification"], request.form["Department"], session['OrgId'], session['UserId']))
            db.commit()
        
        return render_template('AdminDash.html', allinnov = allinnov, allprob = allprob, org_name=session["OrgName"],  users=users)
        # else:
        #     return render_template('AdminDash.html', allfinprob = allfinprob, allinnov = allinnov, allprob = allfinprob, org_name=session["OrgName"],  users=users)
        
    else:
        error = 'You are not logged in'
        return render_template('login.html', Error=error)

#Determine if user is an admin and display admin tab
@users_file.route('/<string:org_name>/AdminDashboard', methods=["POST", "GET"])
def manage_users(org_name):
    if session.get('UserId'):
        users = db.execute(
            "Select * from [thrip].[orgusers] where OrgID = {}".format(session['OrgId'])).fetchall()
        avOrg= db.execute(
            "Select * from [thrip].[organisations]") .fetchall()
        avSurv = db.execute(
            "Select * from [thrip].[surveys]") .fetchall()

        #add here more var to pass
        return render_template('AdminUser.html', users=users, avOrg = avOrg, avSurv = avSurv )
        error = 'You are not logged in'
        return render_template('login.html', Error=error)

#display survey report and share variables
@users_file.route('/AdminUser', methods=["POST", "GET"])
def LinkOS():
      if request.method == "POST":
          if request.form["LinkOS"] == "Link Survey to Organisation":
              db.execute("""Insert into [thrip].[orgsurvey] ( OrgId, surveyID) values ('{}', '{}')""".format(request.form["avOrgan"], request.form["avSu"]))

              db.commit()
              return redirect(url_for('users_file.manage_users',org_name=session["OrgName"] ))


          if  request.form['LinkOS'] == "Submit Organisation":

                db.execute("""Insert into [thrip].[organisations] ( organisationName, description, URL) values ('{}', '{}', '{}')""".format(request.form["OName"], request.form["ODesc"],request.form["OURL"]))

                db.commit()
                return redirect(url_for('users_file.manage_users',org_name=session["OrgName"]))

          if request.form['LinkOS'] == "Submit Survey":
              # retuns values inserted to create new survey

              # SStart = request.form["SStart"]
              # SEnd = request.form["SEnd"]
              SDesc = "m"
              # SCatAm =request.form["SCatAm"]
              SName = request.form["SName"]
              db.execute(
                  """Insert into [thrip].[surveys] (name, description, startDate, endDate) values ('{}', '{}', '{}','{}')""".format(
                     SName, request.form["SDesc"], request.form["SStart"], request.form["SEnd"]))
              db.commit()

              #surveysID = db.execute("select surveyID from [thrip].[surveys] where description = {}".format(
              #    SDesc)).fetchall()
              #print(surveysID)

              #categories = request.form["SCatm"]
              #questions = request.
              #for i in categories :
                  #db.execute(
                   #   """Insert into [thrip].[questiongroups] ( surveyID, name, sequenceNum) values ('{}', '{}', '{}')""".format(
                    #      surveysID, request.form["i.categories"], i))
                  #db.commit()
               #   print(i)
              return redirect(url_for('users_file.manage_users', org_name=session["OrgName"]))



          else:
                error = 'You are not logged in'
                return render_template('login.html', Error = error)

#display survey report and share variables ------------remove this batch
@users_file.route('/AdminUser', methods=["POST", "GET"])
def Surveyadd():
      if request.method == "POST":
          #retuns values inserted to create new survey
            #SName = request.form["SName"]
            #SStart = request.form["SStart"]
           # SEnd = request.form["SEnd"]
           ## SDesc = request.form["SDesc"]
           # SCatAm =request.form["SCatAm"]
            return render_template('SurveyReport.html' )

      else:
        error = 'You are not logged in'
        return render_template('login.html', Error = error)


#called when user logs out clears all session variables
@users_file.route('/Logout', methods=['GET', 'POST'])
def logout():
#clear session variables
    if session.get('UserId'):
        session.pop('UserId')
        session.pop('type')
        session.pop('UserName')
        session.pop('OrgId')
        session.pop('OrgName')
        session.pop('Admin')
        session.pop('logged_in')
        session.pop('Surname')
        session.pop('Verified')
        # session.pop('OftheWeek') 
      
        return redirect(url_for('users_file.login_org'))
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('login.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login.html', Error=error)


@users_file.route('/Admin', methods=['GET', 'POST'])
def admin():
    if session['OrgId'] == 2:
        orgs = db.engine.execute("Select * From Organisations").fetchall()
        users = db.engine.execute("""SELECT distinct
                                             o.Name as 'Org', u.UserId, u.UserName, u.IsActive, u.PIN, u.OrgId, r.RoleId, n.RoleName
                                             FROM Users u
                                             left join UserRoles r on
                                             u.UserId=r.UserId
                                             left join Roles n on
                                             n.RoleId=r.RoleId
                                             left join Organisations o on
                                             o.OrgId = u.OrgId
                                             order by OrgId""").fetchall()

        acts = db.execute(
            "Select a.ActivityId, a.Activity, o.Name, a.Level From Activities a left join Organisations o on o.OrgId = a.OrgId order by Level").fetchall()

        if request.method == "POST":

            # Add Organisation
            if request.form["admin"] == "Add Organisation":

                Orgs = db.engine.execute("select Name from Organisations").fetchall()
                OrgsEmails = db.engine.execute("select Email from Organisations").fetchall()

                for i in range(0, len(Orgs)):
                    if request.form["OName"] == Orgs[i][0]:
                        Error = "This organisation is already created"
                        return render_template('admin.html', orgs=orgs, Error=Error)

                for i in range(0, len(Orgs)):
                    if request.form["OEmail"] == OrgsEmails[i][0]:
                        Error = "This Email has already been used"
                        return render_template('admin.html', orgs=orgs, Error=Error)

                db.engine.execute("""
                                  Insert into Organisations 
                                  (Name, IsActive, Password, Email) 
                                  values 
                                  ('{}', 1, '{}', '{}')
                                  """.format(request.form["OName"], sha256_crypt.encrypt(request.form["OPass"]),
                                             request.form["OEmail"]))
                db.session.commit()
                Confirm = "Organisation added successfully"

                # return render_template('admin.html', orgs=orgs, Confirm=Confirm)
                return redirect(url_for('users_file.admin', orgs=orgs))


            # Add User
            elif request.form["admin"] == "Add User":

                if len(request.form["UP"]) != 4:
                    Error = "The PIN needs to be 4 digits long"
                    return render_template('admin.html', orgs=orgs, Error=Error)

                Users = db.engine.execute(
                    "Select UserName, PIN from Users where OrgId = {}".format(request.form["UO"])).fetchall()

                for i in range(0, len(Users)):
                    if request.form["UN"] == Users[i][0]:
                        Error = "This user name is already being used"
                        return render_template('admin.html', orgs=orgs, Error=Error)
                    elif int(request.form["UP"]) == Users[i][1]:
                        Error = "This pin is already being used"
                        return render_template('admin.html', orgs=orgs, Error=Error)

                db.engine.execute("""
                                  Insert into Users 
                                  (UserName, PIN, IsActive, OrgId) 
                                  values 
                                  ('{}', {}, 1, {})
                                  """.format(request.form["UN"], int(request.form["UP"]), int(request.form["UO"])))
                db.session.commit()

                user = db.engine.execute(
                    "Select UserId from Users where UserName = '{}' and OrgId = {} and PIN = {}".format(
                        request.form["UN"], int(request.form["UO"]), int(request.form["UP"]))).fetchall()

                db.engine.execute("""
                                  Insert into UserRoles 
                                  (UserId, RoleId) 
                                  values 
                                  ({}, {})
                                  """.format(user[0][0], int(request.form["UR"])))

                db.session.commit()

                # return render_template('admin.html', orgs=orgs, Users=Users)
                return redirect(url_for('users_file.admin', orgs=orgs))
            # Add Activity

            elif request.form["admin"] == "Add Activity":
                # check for duplicate activities first
                ActivityCheck = db.engine.execute(
                    """Select Activity from Activities where OrgId = {} and Level = {}""".format(request.form["Aorg"],
                                                                                                 int(request.form[
                                                                                                         "Alevel"]))).fetchall()
                for i in range(0, len(ActivityCheck)):
                    if request.form["Aname"] == ActivityCheck[i][0]:
                        Error = "This activity already exists"
                        return render_template('admin.html', orgs=orgs, Error=Error)

                db.engine.execute("""
                                  Insert into Activities 
                                  (OrgId, Activity, IsActive, Level) 
                                  values 
                                  ({}, '{}', 1, {})
                                  """.format(request.form["Aorg"], request.form["Aname"], int(request.form["Alevel"])))

                db.session.commit()

                actid = db.engine.execute("""
                                          Select ActivityId from Activities 
                                          where OrgId = {} and Activity = '{}' and Level = {}
                                          """
                                          .format(request.form["Aorg"], request.form["Aname"],
                                                  int(request.form["Alevel"]))).first()

                if request.form["Aname"] != "Cancelled":
                    DefaultValue = 1
                    DefaultCheck = db.engine.execute(
                        """Select s.Status, s.IsDefault from Activities a inner join ActivityStatuses s on a.ActivityId = s.ActivityId where a.Level = 2 and a.OrgId = {} and s.IsDefault = 1""".format(
                            request.form["Aorg"])).fetchone()

                    if DefaultCheck is not None:
                        DefaultValue = 0

                    sequence = 0
                    seqnum = db.engine.execute(
                        """Select SequenceNumber from ActivityStatuses WHERE OrgId = {} ORDER BY StatusId DESC""".format(
                            request.form["Aorg"])).fetchone()
                    if seqnum is not None:
                        sequence = seqnum[0]

                    db.engine.execute("""
                                      Insert into ActivityStatuses 
                                      (OrgId, SequenceNumber, Status, ActivityId, IsActive, IsDefault, IsCancelled, isActivityStart, isActivityEnd, BgColor) 
                                      values 
                                      ({}, {}, '{}', {}, {}, {}, {}, {}, {}, '{}')
                                      """.format(request.form["Aorg"], sequence + 1, request.form["Aname"] + " Start",
                                                 actid[0], 1, DefaultValue, request.form["ACan"], 1, 0, '122854'))

                    db.session.commit()

                    db.engine.execute("""
                                      Insert into ActivityStatuses 
                                      (OrgId, SequenceNumber, Status, ActivityId, IsActive, IsDefault, IsCancelled, isActivityStart, isActivityEnd, BgColor) 
                                      values 
                                      ({}, {}, '{}', {}, {}, {}, {}, {}, {}, '{}')
                                      """.format(request.form["Aorg"], sequence + 2,
                                                 request.form["Aname"] + " Complete", actid[0], 1, 0,
                                                 request.form["ACan"], 0, 1, '122854'))

                    db.session.commit()

                else:
                    sequence = 0
                    seqnum = db.engine.execute(
                        """Select SequenceNumber from ActivityStatuses WHERE OrgId = {} ORDER BY StatusId DESC""".format(
                            request.form["Aorg"])).fetchone()
                    if seqnum is not None:
                        sequence = seqnum[0]

                    db.engine.execute("""
                                      Insert into ActivityStatuses 
                                      (OrgId, SequenceNumber, Status, ActivityId, IsActive, IsDefault, IsCancelled, isActivityStart, isActivityEnd, BgColor) 
                                      values 
                                      ({}, {}, '{}', {}, {}, {}, {}, {}, {}, '{}')
                                      """.format(request.form["Aorg"], sequence + 1, request.form["Aname"], actid[0], 1,
                                                 0, request.form["ACan"], 0, 1, 'f44336'))

                    db.session.commit()

                return redirect(url_for('users_file.admin'))
        return render_template('admin.html', orgs=orgs, users=users, acts=acts)
    else:
        error = 'You are not an Admin'
        return render_template('index_1.html', Error=error)
