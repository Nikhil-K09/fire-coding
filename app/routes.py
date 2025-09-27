from flask import Blueprint, render_template, request, jsonify, abort
from . import mongo
from .judge0 import run_code
from bson.objectid import ObjectId
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    problems = list(mongo.db.problems.find({}, {'title': 1, 'difficulty': 1}))
    for p in problems:
        p['_id'] = str(p['_id'])
    return render_template('index.html', problems=problems)


@main.route('/problem/<problem_id>')
def problem(problem_id):
    try:
        prob = mongo.db.problems.find_one({'_id': ObjectId(problem_id)})
    except Exception:
        abort(404)

    if not prob:
        abort(404)

    # convert ObjectId to string for templates
    prob['_id'] = str(prob['_id'])
    return render_template('problem.html', problem=prob)


@main.route('/submit', methods=['POST'])
def submit():
    data = request.get_json(force=True)
    code = data.get('code')
    lang = data.get('lang')
    stdin = data.get('input', '')
    expected_output = data.get('expected_output')
    problem_id = data.get('problem_id')

    if not code or not lang:
        return jsonify({'error': 'code and lang are required'}), 400

    # call Judge0 synchronously (wait=true) to simplify the prototype
    result = run_code(code, int(lang), stdin, expected_output, wait=True)

    # store submission
    mongo.db.submissions.insert_one({
        'problem_id': problem_id,
        'code': code,
        'lang': lang,
        'stdin': stdin,
        'result': result,
        'created_at': datetime.utcnow()
    })

    return jsonify(result)


@main.route('/submissions')
def submissions():
    subs = list(mongo.db.submissions.find().sort('created_at', -1).limit(100))
    for s in subs:
        s['_id'] = str(s['_id'])
        s['created_at'] = s.get('created_at').isoformat() if s.get('created_at') else ''
    return render_template('submissions.html', submissions=subs)
