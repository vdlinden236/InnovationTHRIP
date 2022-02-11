import os
from flask import Flask, Blueprint, render_template,request,session,redirect,url_for
from werkzeug.utils import secure_filename
from flask_database import db
import datetime
#from datetime import datetime

snags_file = Blueprint('snags_file',__name__,template_folder='templates',static_folder='static')

UPLOAD_FOLDER_1 = 'static/images'
ALLOWED_EXTENSIONS = set(['png, jpgd'])

app = Flask(__name__)
app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_1

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@snags_file.route('/<string:org_name>/Scanner', methods=["POST", "GET"])
def snags(org_name):
    user_act = db.engine.execute("""
                                Select a.Activity from Users u
                                join JobActivities a on
                                a.ActivityId = u.Activity
                                where u.UserId = {}
                                """.format(session['UserId'])).first()

    if request.method == "POST":

        CurrentStatus = db.engine.execute("""
                                            Select ci.Description, ci.ContractItemId from ContractItems ci 
                                            join JobActivities a on ci.TemplateId = a.ActivityId
                                            join Contracts c on c.ContractId = ci.ContractId
                                            where a.Activity = '{}' and ci.OrgId = {} and c.ContractReference = '{}'
                                            """.format(request.form["UserAct"], session['OrgId'], request.form["JobNumber"])).first()

        Status = CurrentStatus[0]

        if Status == 'Created':
            NewStatus = 'Started'
            db.engine.execute(
                """Update ContractItems Set Description = '{}', UserId = {} where ContractItemId = {} and OrgId = {}""".format(
                    NewStatus, session['UserId'], CurrentStatus[1], session['OrgId']))
            db.session.commit()
        elif Status == 'Started':
            NewStatus = 'Completed'
            db.engine.execute(
                """Update ContractItems Set Description = '{}', UserId = {} where ContractItemId = {} and OrgId = {}""".format(
                    NewStatus, session['UserId'], CurrentStatus[1], session['OrgId']))
            db.engine.execute(
                """Update ActivityProgress Set Progress = 100 where ContractItemId = {} and OrgId = {}""".format(
                    CurrentStatus[1], session['OrgId']))
            db.session.commit()
        else:
            Error = 'This activity is complete'
            return render_template('upload_snags.html', user_act=user_act[0], Error=Error)

        return redirect(url_for('users_file.logout'))
    return render_template('upload_snags.html', user_act=user_act[0])
