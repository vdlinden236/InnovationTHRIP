import os
from flask import Flask, request, session, redirect, url_for, render_template, make_response, abort
from flask_sqlalchemy import SQLAlchemy

from users import users_file
from report import report_file
from surveys import surveys_file
from gamification import gamification_file
import Socket_Updates
from Socket_Updates import execute_update
from knowledge import snags_file
from flask_compress import Compress
from flask_socketio import SocketIO
from flask_caching import Cache
from flask_database import db
#from flask_socketio import SocketIO, emit
import threading
import urllib.parse
import os
import pyodbc
import pymssql
import pdfkit
import eventlet
eventlet.monkey_patch()

UPLOAD_FOLDER = '/static/reports'
ALLOWED_EXTENSIONS = set(['xlsx'])
#create app
app = Flask(__name__)

app.jinja_env.cache = {}
app.jinja_env.auto_reload = False
#all pyy files that is called from app.py
app.register_blueprint(users_file)
app.register_blueprint(surveys_file)
app.register_blueprint(gamification_file)
app.register_blueprint(report_file) #not used
app.register_blueprint(snags_file) #not used

app.secret_key = ';jfjjmLFNDCJGRLsdlCHSA'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SQLALCHEMY_TRACK_MODIFICATIONS = False
socketio = SocketIO(app, async_mode = 'eventlet')


COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500
Compress(app)


@app.template_filter()
def currencyFormat(value):
    value = float(value)
    return "${:,.2f}".format(value)


@app.errorhandler(403)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(503)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


def configure_app(app):
    Compress(app)


@socketio.on('connect', namespace='/Update_Survey')
def client_connect():
    print("Client Connected")

#submit survey - in the background
@socketio.on('SurveyPage', namespace='/Update_Survey')
def handle_update(json_data):
    survey_id = json_data['survey_id']
    results = json_data['results']
    comments = json_data['comments']
#Calls SocketUpdate.py with execute_update - from survey_questions.htm button submit
    t = threading.Thread(target=execute_update, args=(survey_id, session["UserId"], session["OrgId"], results, comments))
    t.start()

#configure_app(app)
#socketio.run(app)

app.run(debug=True)