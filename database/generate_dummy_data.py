import random
import json
from datetime import datetime
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Audit, Response
import os

def load_template():
    TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../templates/template1_full_bilingual.json")
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
fake = Faker()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "safetyhub.db")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()

# Configuration
NUM_USERS = 50
NUM_AUDITS = 1000
RESPONSE_CHOICES = ["Yes", "No", "N/A"]

# Load real checklist template
template = load_template()

# Flatten questions with category included
flat_questions = []
for category in template["categories"]:
    category_name = category["name"]
    for q in category["questions"]:
        q_copy = q.copy()
        q_copy['category'] = category_name
        flat_questions.append(q_copy)

# --- Step 1: Generate Users ---
users = []
for _ in range(NUM_USERS):
    full_name = fake.name()
    user = User(full_name=full_name)
    users.append(user)
session.add_all(users)
session.commit()

# --- Step 2: Generate Audits and Responses ---
for _ in range(NUM_AUDITS):
    user = random.choice(users)
    site_id = f"SITE-{random.randint(1, 15):03}"
    timestamp = fake.date_time_between(start_date="-60d", end_date="now")

    audit = Audit(user_id=user.telegram_id, site_id=site_id, timestamp=timestamp)
    session.add(audit)
    session.commit()

    selected_questions = random.sample(flat_questions, k=min(12, len(flat_questions)))  # up to 12 unique questions
    responses = []

    for q in selected_questions:
        responses.append(Response(
            audit_id=audit.id,
            category=q['category'],
            question=q["question_en"],
            question_ru=q["question_ru"],
            keyword=q["keyword"],
            response=random.choice(RESPONSE_CHOICES)
        ))

    session.add_all(responses)
    session.commit()

print(f"✅ Inserted {NUM_USERS} users, {NUM_AUDITS} audits, and {NUM_AUDITS * len(selected_questions)} responses.")
session.close()
