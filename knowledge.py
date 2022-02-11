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


@snags_file.route('/<string:org_name>/InnovationCapability', methods=["POST", "GET"])
def innov_capab(org_name):

    return render_template('innov_capab.html')

@snags_file.route('/<string:org_name>/InnovationDirection', methods=["POST", "GET"])
def TIInnovDirec(org_name):

    return render_template('TIInnovDirec.html')

@snags_file.route('/<string:org_name>/TypesInnovations', methods=["POST", "GET"])
def TITypes(org_name):

    return render_template('TITypes.html')

@snags_file.route('/<string:org_name>/InnovationStrategy', methods=["POST", "GET"])
def TIStrategy(org_name):

    return render_template('TIStrategy.html')

@snags_file.route('/<string:org_name>/InnovationOverview', methods=["POST", "GET"])
def TIInnovOver(org_name):

    return render_template('TIInnovOver.html')

@snags_file.route('/<string:org_name>/InnovationBarrier', methods=["POST", "GET"])
def TIInnovBarr(org_name):

    return render_template('TIInnovBarr.html')

@snags_file.route('/<string:org_name>/StategicIntent', methods=["POST", "GET"])
def TIStat(org_name):
    return render_template('TIStat.html')

@snags_file.route('/<string:org_name>/SInnovationCapability', methods=["POST", "GET"])
def TSInnovCap(org_name):
    return render_template('TSInnovCap.html')

@snags_file.route('/<string:org_name>/DSRedesign', methods=["POST", "GET"])
def DSReDesScor(org_name):
    return render_template('DSReDesScor.html')

@snags_file.route('/<string:org_name>/DSBalScore', methods=["POST", "GET"])
def DSBalScore(org_name):
    return render_template('DSBalScore.html')

@snags_file.route('/<string:org_name>/DInnovationMan', methods=["POST", "GET"])
def DIInnovman(org_name):
    return render_template('DIInnovman.html')

@snags_file.route('/<string:org_name>/DSPillars', methods=["POST", "GET"])
def DSPillar(org_name):
    return render_template('DSPillar.html')

@snags_file.route('/<string:org_name>/DTypicalProcess', methods=["POST", "GET"])
def DITypicalPro(org_name):
    return render_template('DITypicalPro.html')

@snags_file.route('/<string:org_name>/DInnovationProcess', methods=["POST", "GET"])
def DIProcess(org_name):
    return render_template('DIProcess.html')

@snags_file.route('/<string:org_name>/SBalancedScorecard', methods=["POST", "GET"])
def TSBalSco(org_name):
    return render_template('TSBalSco.html')

@snags_file.route('/<string:org_name>/SRedesignScorecard', methods=["POST", "GET"])
def TSReSco(org_name):
    return render_template('TSReSco.html')

@snags_file.route('/<string:org_name>/StrategicPillars', methods=["POST", "GET"])
def TSPill(org_name):
    return render_template('TSPill.html')

@snags_file.route('/<string:org_name>/InnovationCapabilityManagement', methods=["POST", "GET"])
def innov_capab_mng(org_name):
    return render_template('innov_capab_man.html')


@snags_file.route('/<string:org_name>/StrategicPillars', methods=["POST", "GET"])
def strat_pillars(org_name):
    return render_template('strat_pillars.html')


@snags_file.route('/<string:org_name>/SurveyMethodology', methods=["POST", "GET"])
def survey_method(org_name):
    return render_template('survey_meth.html')


@snags_file.route('/<string:org_name>/ImplementationLevers', methods=["POST", "GET"])
def implement_levers(org_name):
    return render_template('implement_levers.html')