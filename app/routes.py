from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from datetime import datetime
from . import mongo
from .judge0 import run_code
import pytz

main = Blueprint('main', __name__)

# ================== HOME PAGE ==================
@main.route('/')
def index():
    problems = list(mongo.db.problems.find({}, {"title":1, "difficulty":1}))
    for p in problems:
        p['_id'] = str(p['_id'])
    return render_template('index.html', problems=problems)


# ================== PROBLEM PAGE ==================
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


# ================== PROFILE ROUTES ==================
@main.route('/profile')
@login_required
def my_profile():
    # Ensure profile exists
    profile = mongo.db.profiles.find_one({"user_id": current_user.id})
    if not profile:
        mongo.db.profiles.insert_one({
            "user_id": current_user.id,
            "username": current_user.username,
            "solved_count": 0,
            "solved_dates": []
        })
    return redirect(url_for('main.user_profile', username=current_user.username))


@main.route('/profile/<username>')
@login_required
def user_profile(username):
    # Fetch user profile
    profile = mongo.db.profiles.find_one({"username": username})
    if not profile:
        abort(404)

    # Fetch submissions
    subs = list(mongo.db.submissions.find({"username": username}).sort("submitted_at", -1))
    for s in subs:
        s['_id'] = str(s['_id'])
        s['submitted_at'] = s['submitted_at'].strftime("%Y-%m-%d %H:%M:%S")

    solved_dates = profile.get("solved_dates", [])
    solved_count = len(solved_dates)

    return render_template(
        "profile.html",
        username=profile["username"],
        solved_count=solved_count,
        solved_dates=solved_dates,
        submissions=subs
    )

# ================== SUBMIT CODE ==================
@main.route('/submit', methods=['POST'])
@login_required
def submit():
    data = request.get_json()
    code = data.get('code')
    lang_id = int(data.get('lang'))
    problem_id = data.get('problem_id')

    # Fetch problem
    problem = mongo.db.problems.find_one({"_id": ObjectId(problem_id)})
    if not problem:
        return jsonify({"status": "Error", "error": "Problem not found"})

    test_case = problem.get("test_case", {})
    input_data = str(test_case.get("input", ""))
    expected_output = str(test_case.get("output", "")).strip()

    # Run code using Judge0
    try:
        result = run_code(code, lang_id, input_data)
        stdout = str(result.get("stdout", "")).strip()
        stderr = str(result.get("stderr", "")).strip()
        status = "Accepted" if stdout == expected_output else "Rejected"
    except Exception as e:
        stdout = ""
        stderr = str(e)
        status = "Error"

    # Local timestamp
    local_tz = pytz.timezone("Asia/Kolkata")
    local_time = datetime.now(local_tz)

    # Save submission
    submission_doc = {
        "user_id": current_user.id,
        "username": current_user.username,
        "problem_id": problem_id,
        "problem_title": problem['title'],
        "lang": lang_id,
        "lang_name": {54:"C++", 71:"Python 3", 62:"Java"}.get(lang_id,"Unknown"),
        "code": code,
        "submitted_at": local_time,
        "test_case_result": {
            "status": status,
            "stdout": stdout,
            "stderr": stderr
        }
    }
    mongo.db.submissions.insert_one(submission_doc)

    # Update solved problems and profile
    if status == "Accepted":
        solved_entry = mongo.db.solved.find_one({
            "user_id": current_user.id,
            "problem_id": problem_id
        })

        if not solved_entry:
            # Insert first solved entry
            mongo.db.solved.insert_one({
                "user_id": current_user.id,
                "username": current_user.username,
                "problem_id": problem_id,
                "title": problem['title'],
                "solved_at": local_time
            })

            # Update profile collection
            profile = mongo.db.profiles.find_one({"user_id": current_user.id})
            if not profile:
                mongo.db.profiles.insert_one({
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "solved_count": 1,
                    "solved_dates": [local_time.date().isoformat()]
                })
            else:
                mongo.db.profiles.update_one(
                    {"user_id": current_user.id},
                    {
                        "$inc": {"solved_count": 1},
                        "$addToSet": {"solved_dates": local_time.date().isoformat()}
                    }
                )

    return jsonify({
        "status": status,
        "stdout": stdout,
        "expected": expected_output,
        "error": stderr,
        "submitted_at": local_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    })

@main.route('/ide')
@login_required
def ide():
    return render_template('ide.html')

@main.route('/ide_submit', methods=['POST'])
@login_required
def ide_submit():
    data = request.get_json()
    code = data.get("code")
    lang_id = int(data.get("lang_id"))
    input_data = data.get("input", "")

    try:
        result = run_code(code, lang_id, input_data)
        stdout = str(result.get("stdout", "") or "")
        stderr = str(result.get("stderr", "") or "")
        status = "Accepted" if stdout else "Error"
    except Exception as e:
        stdout = ""
        stderr = str(e)
        status = "Error"

    return jsonify({
        "status": status,
        "stdout": stdout,
        "stderr": stderr
    })
