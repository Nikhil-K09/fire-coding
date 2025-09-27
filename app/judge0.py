import os
import requests
from dotenv import load_dotenv

load_dotenv()

JUDGE0_URL = os.getenv('JUDGE0_URL')
JUDGE0_KEY = os.getenv('JUDGE0_KEY')
JUDGE0_HOST = os.getenv('JUDGE0_HOST')


def run_code(source_code, language_id, stdin='', expected_output=None, wait=True, timeout=60):
    """Call Judge0 and return JSON result. Uses RapidAPI headers if JUDGE0_KEY/JUDGE0_HOST are set.

    - source_code: string
    - language_id: int (Judge0 language id)
    - stdin: string
    - expected_output: optional string
    - wait: if True, request wait=true to get result synchronously
    """
    if not JUDGE0_URL:
        raise RuntimeError('JUDGE0_URL not configured in environment')

    params = {'base64_encoded': 'false'}
    if wait:
        params['wait'] = 'true'

    headers = {'Content-Type': 'application/json'}
    if JUDGE0_KEY and JUDGE0_HOST:
        # RapidAPI-style hosted Judge0
        headers['x-rapidapi-key'] = JUDGE0_KEY
        headers['x-rapidapi-host'] = JUDGE0_HOST

    payload = {
        'source_code': source_code,
        'language_id': int(language_id),
        'stdin': stdin,
        'redirect_stderr_to_stdout': True,
    }
    if expected_output is not None:
        payload['expected_output'] = expected_output

    resp = requests.post(JUDGE0_URL, params=params, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
