from flask import Flask, render_template, request, jsonify
import os
from typing import Dict, Any

from criteria import get_preset_criteria, PRESET_CRITERIA
from models import Criterion
import mock_data
from scoring_api import score_resume # Added import for scoring_api

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "resume-scorer-secret"

@app.route("/")
def index():
    return render_template("index.html", criteria=get_preset_criteria())

@app.route("/resumes")
def list_resumes():
    return render_template("resume_list.html", resumes=mock_data.get_mock_resumes())

@app.route("/scoring/<resume_id>")
def scoring_result(resume_id):
    resume = mock_data.get_resume_by_id(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404 #Added error handling
    return render_template("scoring_result.html", resume=resume, criteria=get_preset_criteria())

@app.route("/criteria/editor")
def criteria_editor():
    return render_template("criteria_editor.html", criteria=get_preset_criteria())

@app.route("/api/criteria/<criteria_id>")
def get_criteria(criteria_id):
    preset_criteria = get_preset_criteria()
    if criteria_id not in preset_criteria:
        return jsonify({"error": "Criteria not found"}), 404
    return jsonify(preset_criteria[criteria_id])

@app.route("/api/criteria", methods=["POST"])
def create_criteria():
    criteria = request.json
    try:
        name = criteria.get("name")
        if not name:
            raise ValueError("Criteria name is required")
            
        root_criterion = Criterion(**criteria.get("root_criterion", {}))
        
        # Add to preset criteria (in memory for now)
        criteria_id = name.lower().replace(" ", "_")
        PRESET_CRITERIA[criteria_id] = {
            "name": name,
            "weights": {},  # Initialize with empty weights
            "structure": {}  # Initialize with empty structure
        }
        
        return jsonify({"id": criteria_id, "name": name})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/score", methods=["POST"])
def score():
    request_data = request.json
    try:
        resume_id = request_data.get("resume_id")
        criteria_id = request_data.get("criteria_id")

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)