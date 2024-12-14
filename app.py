import os
from flask import Flask, render_template, request, jsonify
from models import db
import logging
import mock_data
from criteria import get_preset_criteria
from scoring_api import score_resume

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "resume-scorer-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///resumes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html', criteria=get_preset_criteria())

@app.route('/resumes')
def list_resumes():
    resumes = mock_data.get_mock_resumes()
    return render_template('resume_list.html', resumes=resumes)

@app.route('/api/score', methods=['POST'])
def score():
    data = request.json
    resume_id = data.get('resume_id')
    criteria_id = data.get('criteria_id')
    weights = data.get('weights', {})
    
    # Get resume data
    resume = mock_data.get_resume_by_id(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    # Get criteria
    criteria = get_preset_criteria()[criteria_id]
    if not criteria:
        return jsonify({"error": "Criteria not found"}), 404
    
    # Update weights if provided
    if weights:
        criteria['weights'].update(weights)
    
    # Get scoring results
    results = score_resume(resume['non_personal'], criteria)
    
    return jsonify(results)

@app.route('/scoring/<resume_id>')
def scoring_result(resume_id):
    resume = mock_data.get_resume_by_id(resume_id)
    criteria = get_preset_criteria()
    return render_template('scoring_result.html', resume=resume, criteria=criteria)

with app.app_context():
    db.create_all()
