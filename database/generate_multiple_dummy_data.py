import random
import json
import os
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
from models import Base, User, Audit, Response

# --------------------------
# Configuration
# --------------------------
fake = Faker()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "safetyhub.db")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates")

NUM_USERS = 50
NUM_AUDITS = 1200
SITE_COUNT = 15
DAYS_BACK = 180

engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)
session = Session()


# --------------------------
# Load multiple templates
# --------------------------
def load_all_templates():
    """Load all template JSON files inside the templates directory."""
    templates = []
    for fname in os.listdir(TEMPLATES_DIR):
        if fname.endswith(".json"):
            path = os.path.join(TEMPLATES_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                templates.append({
                    "name": os.path.splitext(fname)[0],
                    "data": data
                })
    if not templates:
        raise FileNotFoundError("No templates found in templates directory.")
    return templates


TEMPLATES = load_all_templates()

# --------------------------
# Flatten questions
# --------------------------
def flatten_template(template_json):
    """Flatten a checklist JSON into a list of questions with category metadata."""
    flat = []
    for category in template_json["categories"]:
        cat_name = category["name"]
        for q in category["questions"]:
            q_copy = q.copy()
            q_copy["category"] = cat_name
            flat.append(q_copy)
    return flat


# --------------------------
# Response probability setup
# --------------------------
DEFAULT_PROBS = {
    "Yes": 0.8,
    "No": 0.15,
    "N/A": 0.05
}

# Small variations per template type
TEMPLATE_MODIFIERS = {
    "template1_full_bilingual": {"Yes": 0.0, "No": 0.0, "N/A": 0.0},
    "template2_environment": {"Yes": -0.05, "No": +0.05, "N/A": 0.0},
    "template3_electrical": {"Yes": +0.05, "No": -0.05, "N/A": 0.0},
    "template4_construction": {"Yes": -0.10, "No": +0.10, "N/A": 0.0},
}


def get_site_variation(site_id):
    site_num = int(site_id.split("-")[1])
    if site_num % 5 == 0:
        return {"Yes": -0.15, "No": +0.15, "N/A": 0.0}
    elif site_num % 3 == 0:
        return {"Yes": +0.10, "No": -0.10, "N/A": 0.0}
    else:
        return {"Yes": 0.0, "No": 0.0, "N/A": 0.0}


def get_engineer_variation(engineer_id):
    if engineer_id % 10 == 0:
        return {"Yes": -0.10, "No": +0.10, "N/A": 0.0}
    elif engineer_id % 5 == 0:
        return {"Yes": +0.15, "No": -0.15, "N/A": 0.0}
    else:
        return {"Yes": 0.0, "No": 0.0, "N/A": 0.0}


def weighted_random_response(template_name, site_id, engineer_id):
    """Return probabilistic Yes/No/N/A depending on site, engineer, and template effects."""
    probs = DEFAULT_PROBS.copy()
    t_mod = TEMPLATE_MODIFIERS.get(template_name, {"Yes": 0, "No": 0, "N/A": 0})
    s_mod = get_site_variation(site_id)
    e_mod = get_engineer_variation(engineer_id)

    adjusted = {
        "Yes": max(0, min(1, probs["Yes"] + t_mod["Yes"] + s_mod["Yes"] + e_mod["Yes"])),
        "No": max(0, min(1, probs["No"] + t_mod["No"] + s_mod["No"] + e_mod["No"])),
        "N/A": probs["N/A"]
    }
    total = sum(adjusted.values())
    norm = {k: v / total for k, v in adjusted.items()}

    return np.random.choice(list(norm.keys()), p=list(norm.values()))


# --------------------------
# User generation
# --------------------------
print("👥 Generating users...")
users = []
for i in range(NUM_USERS):
    u = User(full_name=fake.name())
    users.append(u)
session.add_all(users)
session.commit()

# --------------------------
# Audit + Response generation
# --------------------------
print("📋 Generating audits and responses...")
start_date = datetime.now() - timedelta(days=DAYS_BACK)

for idx in range(NUM_AUDITS):
    if idx % 100 == 0:
        print(f"→ Generated {idx}/{NUM_AUDITS} audits...")

    user = random.choice(users)
    site_id = f"SITE-{random.randint(1, SITE_COUNT):03}"

    # Pick a random template
    chosen_template = random.choice(TEMPLATES)
    template_name = chosen_template["name"]
    flat_qs = flatten_template(chosen_template["data"])

    # Create timestamp weighted toward work hours
    hour = random.choices(
        [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
        weights=[1, 3, 5, 8, 10, 7, 6, 4, 3, 1]
    )[0]
    minute = random.randint(0, 59)
    timestamp = fake.date_time_between(start_date=start_date, end_date="now")
    timestamp = timestamp.replace(hour=hour, minute=minute)

    audit = Audit(
        user_id=user.telegram_id,
        site_id=site_id,
        timestamp=timestamp
    )
    session.add(audit)
    session.commit()

    # Select subset of questions
    selected = random.sample(flat_qs, k=min(10, len(flat_qs)))

    responses = []
    for q in selected:
        ans = weighted_random_response(template_name, site_id, user.telegram_id)
        responses.append(Response(
            audit_id=audit.id,
            category=q.get("category", "Unknown"),
            question=q.get("question_en", q.get("question", "Unknown Question")),
            question_ru=q.get("question_ru", ""),
            keyword=q.get("keyword", q.get("key", q.get("id", "unknown_keyword"))),
            response=ans
        ))

    session.add_all(responses)
    session.commit()

print("✅ Generation complete!")
print(f"- Templates used: {[t['name'] for t in TEMPLATES]}")
print(f"- {NUM_USERS} users created")
print(f"- {NUM_AUDITS} audits inserted")
session.close()
