import os
import json
from app import create_app, mongo

app = create_app()

with app.app_context():
    db = mongo.db
    path = os.path.join(os.path.dirname(__file__), 'db', 'seed_problems.json')
    with open(path, 'r', encoding='utf-8') as f:
        problems = json.load(f)

    inserted = 0
    for p in problems:
        slug = p.get('slug')
        if slug and db.problems.find_one({'slug': slug}):
            continue
        db.problems.insert_one(p)
        inserted += 1

    print(f"Seed complete. Inserted {inserted} new problem(s).")
