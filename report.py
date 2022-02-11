from flask import Flask, Blueprint, render_template, request, session, redirect, url_for, send_from_directory, send_file
from flask_database import db
from create_report import CreateRep_Table, create_rep
from create_report import create_rep
from user_report import user_rep
from job_report import job_report
import datetime
import os

report_file = Blueprint('report_file', __name__, template_folder='templates', static_folder='static')

app = Flask(__name__)
app.secret_key = ';jadsfjjmLFNDCJGRLsdlCHasFAFFSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
#
UPLOAD_FOLDER = '/static/reports'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER





@report_file.route('/<string:org_name>/ContractReports', methods=["POST", "GET"])
def contract_report(org_name):
    if session.get('UserId'):
        if session["RoleId"] > 2:
            # cnt = 8
            filename = "JobReport" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".xlsx"
            job_report(session["OrgId"], filename)
            uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            # create_rep(session["OrgId"])
            print(uploads)
            return redirect(url_for('report_file.return_files', org_name=session["OrgName"], filename=filename))
        else:
            if session["RoleId"] > 1:
                error = 'You are not an Admin'
                return render_template('dashboard.html', Error=error)
            else:
                error = 'You are not an Admin'
                return render_template('Workers.html', Error=error)
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org.html', Error=error)

@report_file.route('/<string:org_name>/<path:filename>')
def return_files(org_name, filename):
    try:
        return send_file('./static/reports/{}'.format(filename),attachment_filename='{}'.format(filename), as_attachment=True)
    except Exception as e:
        return str(e)


@report_file.route('/<string:org_name>/UserReports', methods=["POST", "GET"])
def user_report(org_name):
    if session.get('UserId'):
        if session["RoleId"] > 2:
            # cnt = 8
            filename = "UserReport_" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".xlsx"
            user_rep(session["OrgId"], filename)
            uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            # create_rep(session["OrgId"])
            print(uploads)
            return redirect(url_for('report_file.return_files1', org_name=session["OrgName"], filename=filename))

        else:
            if session["RoleId"] > 1:
                error = 'You are not an Admin'
                return render_template('dashboard.html', Error=error)
            else:
                error = 'You are not an Admin'
                return render_template('Workers.html', Error=error)
    else:
        if session.get('OrgId'):
            error = 'You are not logged in'
            return render_template('index.html', Error=error)
        else:
            error = 'You are not logged in'
            return render_template('login_org.html', Error=error)

@report_file.route('/<string:org_name>/<path:filename>')
def return_files1(org_name, filename):
    try:
        return send_file('./static/reports/{}'.format(filename), attachment_filename='{}'.format(filename),
                         as_attachment=True)
    except Exception as e:
        return str(e)
