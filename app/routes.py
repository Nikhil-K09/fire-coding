from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime
from . import mongo

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
import base64
import os
import requests
from flask import request, jsonify
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime

@main.route('/submit', methods=['POST'])
@login_required
def submit():
    data = request.get_json()
    code = data.get('code')
    lang_id = int(data.get('lang'))
    input_data = data.get('input', '')
    expected_output = data.get('expected_output', '')
    problem_id = data.get('problem_id')

    # fetch problem
    try:
        problem = mongo.db.problems.find_one({"_id": ObjectId(problem_id)})
    except Exception:
        return jsonify({"status":"Error", "output":"Invalid problem ID"})

    if not problem:
        return jsonify({"status":"Error", "output":"Problem not found"})

    # Save submission as Pending
    sub_doc = {
        "user_id": current_user.id,
        "problem_id": problem_id,
        "problem_title": problem['title'],
        "lang": lang_id,
        "lang_name": {54:"C++",71:"Python 3",62:"Java",50:"C",51:"C#",46:"Bash"}.get(lang_id, "Unknown"),
        "code": code,
        "input": input_data,
        "expected_output": expected_output,
        "status": "Pending",
        "stdout": "",
        "submitted_at": datetime.utcnow()
    }
    sub_id = mongo.db.submissions.insert_one(sub_doc).inserted_id

    # Call Judge0
    try:
        url = os.getenv("JUDGE0_URL")  # make sure it's in .env
        key = os.getenv("JUDGE0_KEY")
        host = os.getenv("JUDGE0_HOST")

        headers = {"Content-Type": "application/json"}
        if key and host:
            headers["x-rapidapi-key"] = key
            headers["x-rapidapi-host"] = host

        payload = {
            "source_code": base64.b64encode(code.encode()).decode(),
            "language_id": lang_id,
            "stdin": base64.b64encode(input_data.encode()).decode(),
            "expected_output": base64.b64encode(expected_output.encode()).decode() if expected_output else None,
            "redirect_stderr_to_stdout": True
        }

        r = requests.post(url + "?base64_encoded=true&wait=true", json=payload, headers=headers)
        result = r.json()

        # decode outputs
        stdout = base64.b64decode(result.get("stdout","").encode()).decode() if result.get("stdout") else ""
        compile_output = base64.b64decode(result.get("compile_output","").encode()).decode() if result.get("compile_output") else ""
        stderr = base64.b64decode(result.get("stderr","").encode()).decode() if result.get("stderr") else ""

        final_output = ""
        if compile_output: final_output += f"Compile output:\n{compile_output}\n\n"
        if stdout: final_output += f"{stdout}\n"
        if stderr: final_output += f"{stderr}\n"

        status_desc = result.get("status", {}).get("description", "Unknown")

        # Update DB with real result
        mongo.db.submissions.update_one(
            {"_id": sub_id},
            {"$set": {"status": status_desc, "stdout": final_output}}
        )

        return jsonify({
            "status": status_desc,
            "output": final_output,
            "submission_id": str(sub_id)
        })

    except Exception as e:
        mongo.db.submissions.update_one(
            {"_id": sub_id},
            {"$set": {"status": "Error", "stdout": str(e)}}
        )
        return jsonify({"status":"Error", "output": str(e), "submission_id": str(sub_id)})
