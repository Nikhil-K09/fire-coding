from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime
from . import mongo
from .judge0 import run_code   # <<< Add this
import base64
import os
import requests


main = Blueprint('main', __name__)

# Home page: list of problems
@main.route('/')
def index():
    problems = list(mongo.db.problems.find({}, {"title":1, "difficulty":1}))
    for p in problems:
        p['_id'] = str(p['_id'])
    return render_template('index.html', problems=problems)


# Problem page
@main.route('/problem/<problem_id>')
def problem(problem_id):
    try:
        prob = mongo.db.problems.find_one({"_id": ObjectId(problem_id)})
    except Exception:
        abort(404)

    if not prob:
        abort(404)

    prob['_id'] = str(prob['_id'])
    return render_template('problem.html', problem=prob)


# Profile page: show submissions
@main.route('/profile')
@login_required
def profile():
    subs = list(mongo.db.submissions.find({"user_id": current_user.id}).sort("submitted_at", -1))
    for s in subs:
        s['_id'] = str(s['_id'])
        s['submitted_at'] = s['submitted_at'].strftime("%Y-%m-%d %H:%M:%S")
    return render_template('profile.html', submissions=subs)


# Submit code (runs Judge0 API)
# in routes.py
# routes.py

@main.route('/submit', methods=['POST'])
@login_required
def submit():
    data = request.get_json()
    code = data.get('code')
    lang_id = int(data.get('lang'))
    problem_id = data.get('problem_id')

    problem = mongo.db.problems.find_one({"_id": ObjectId(problem_id)})
    if not problem:
        return jsonify({"status":"Error","stdout":"Problem not found"})

    # Single test case
    test_case = problem.get("test_case", {})
    input_data = str(test_case.get("input",""))
    expected_output = str(test_case.get("output","")).strip()

    try:
        # call Judge0 synchronously
        result = run_code(code, lang_id, input_data)
        stdout = str(result.get("stdout","")).strip()
        stderr = str(result.get("stderr","")).strip()
        status_judge = result.get("status",{}).get("description","Unknown")

        # compare output
        test_case_status = "Success" if stdout == expected_output else "Failed"

    except Exception as e:
        stdout = ""
        stderr = str(e)
        test_case_status = "Error"

    # save submission
    mongo.db.submissions.insert_one({
        "user_id": current_user.id,
        "problem_id": problem_id,
        "problem_title": problem['title'],
        "lang": lang_id,
        "lang_name": {54:"C++",71:"Python 3",62:"Java"}.get(lang_id, "Unknown"),
        "code": code,
        "submitted_at": datetime.utcnow(),
        "test_case_result": {
            "status": test_case_status,
            "stdout": stdout,
            "stderr": stderr
        }
    })

    return jsonify({
        "status": test_case_status,
        "stdout": stdout,
        "stderr": stderr
    })

  