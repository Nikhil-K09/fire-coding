import os
import json
from app import create_app, mongo

app = create_app()

with app.app_context():
    db = mongo.db
    path = os.path.join(os.path.dirname(__file__), 'db', 'seed_problems.json')
    with open(path, 'r', encoding='utf-8') as f:
        problems = json.load(f)

    updated = 0
    inserted = 0

    for p in problems:
        slug = p.get('slug')
        if not slug:
            continue

        result = db.problems.update_one(
            {'slug': slug},   # filter by slug
            {'$set': p},      # update all fields
            upsert=True       # insert if not found
        )

        if result.matched_count > 0:
            updated += 1  # existing document was updated
        else:
            inserted += 1  # new document inserted

    print(f"Seed complete. Inserted {inserted} new problem(s), Updated {updated} existing problem(s).")
