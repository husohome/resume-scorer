import os
from flask import Flask, render_template, request, jsonify
import logging
import mock_data
from criteria import get_preset_criteria, PRESET_CRITERIA
from scoring_api import score_resume
from database import db

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

@app.route('/rankings')
def show_rankings():
    criteria = get_preset_criteria()
    return render_template("ranked_results.html", 
                         criteria=criteria, 
                         ranked_resumes=[], 
                         selected_criteria=None)

@app.route('/api/rank', methods=['POST'])
def rank_resumes():
    try:
        data = request.json
        criteria_id = data.get('criteria_id')
        
        # Get all resumes
        resumes = mock_data.get_mock_resumes()
        
        # Get selected criteria
        preset_criteria = get_preset_criteria().get(criteria_id)
        if not preset_criteria:
            return jsonify({"error": "Criteria not found"}), 404
            
        criteria = preset_criteria['root_criterion']
        
        # Score each resume
        scored_resumes = []
        for resume in resumes.values():
            try:
                results = score_resume(resume['non_personal'], criteria)
                resume_with_score = {**resume, 'score': results['final_score']}
                scored_resumes.append(resume_with_score)
            except Exception as e:
                app.logger.error(f"Error scoring resume {resume['id']}: {str(e)}")
                continue
        
        # Sort by score in descending order
        ranked_resumes = sorted(scored_resumes, key=lambda x: x['score'], reverse=True)
        
        return jsonify(ranked_resumes)
    except Exception as e:
        app.logger.error(f"Error ranking resumes: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/criteria/editor')
def criteria_editor():
    return render_template("criteria_editor.html", criteria=get_preset_criteria())

@app.route('/api/criteria', methods=['POST'])
def create_criteria():
    try:
        data = request.json
        criteria_name = data.get('name')
        root_criterion = data.get('root_criterion')
        
        # Add the new criteria to the preset criteria
        criteria_id = f"custom_{len(get_preset_criteria())}"
        PRESET_CRITERIA[criteria_id] = {
            "name": criteria_name,
            "root_criterion": root_criterion
        }
        
        return jsonify({"id": criteria_id, "message": "Criteria created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/criteria/<criteria_id>')
def get_criteria(criteria_id):
    criteria = get_preset_criteria().get(criteria_id)
    if not criteria:
        return jsonify({"error": "Criteria not found"}), 404
    return jsonify(criteria)

@app.route('/api/score', methods=['POST'])
def score():
    try:
        request_data = request.json
        resume_id = request_data.get('resume_id')
        criteria_id = request_data.get('criteria_id')
        
        resume = mock_data.get_resume_by_id(resume_id)
        if not resume:
            return jsonify({"error": "Resume not found"}), 404
            
        preset_criteria = get_preset_criteria().get(criteria_id)
        if not preset_criteria:
            return jsonify({"error": "Criteria not found"}), 404
            
        criteria = preset_criteria['root_criterion']
        results = score_resume(resume['non_personal'], criteria)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scoring/<resume_id>')
def scoring_result(resume_id):
    resume = mock_data.get_resume_by_id(resume_id)
    criteria = get_preset_criteria()
    return render_template('scoring_result.html', resume=resume, criteria=criteria)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
