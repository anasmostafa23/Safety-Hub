import random
import json
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Audit, Response
import os
import numpy as np

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
SITE_COUNT = 15
DAYS_BACK = 180  # 6 months of data

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

# Define realistic response probabilities for each keyword
RESPONSE_PROBABILITIES = {
    # People category
    "competency_certified/компетентность_и_сертификация": {"Yes": 0.85, "No": 0.10, "N/A": 0.05},
    "medically_fit/медицинская_подготовка": {"Yes": 0.95, "No": 0.03, "N/A": 0.02},
    "supervisor_available/наличие_руководителя": {"Yes": 0.90, "No": 0.08, "N/A": 0.02},
    "high_risk_procedure_team/работы_повышенной_опасности": {"Yes": 0.80, "No": 0.15, "N/A": 0.05},
    
    # Equipment category
    "tools_inspected/проверка_инструментов": {"Yes": 0.75, "No": 0.20, "N/A": 0.05},
    "equipment_certified/сертификация_оборудования": {"Yes": 0.70, "No": 0.25, "N/A": 0.05},
    "defective_equipment_removed/удаление_неисправного_оборудования": {"Yes": 0.65, "No": 0.30, "N/A": 0.05},
    "ppe_available_condition/наличие_и_состояние_сиз": {"Yes": 0.80, "No": 0.15, "N/A": 0.05},
    
    # Environment category
    "emergency_exits_marked/аварийные_выходы": {"Yes": 0.85, "No": 0.10, "N/A": 0.05},
    "work_area_hazard_free/отсутствие_опасностей": {"Yes": 0.60, "No": 0.35, "N/A": 0.05},
    "hazardous_materials_stored/хранение_опасных_материалов": {"Yes": 0.75, "No": 0.20, "N/A": 0.05},
    "adequate_lighting/освещение": {"Yes": 0.70, "No": 0.20, "N/A": 0.10}  # Higher N/A for indoor/outdoor variation
}

# Add some site-specific variations
def get_site_variation(site_id):
    """Make some sites better/worse than others"""
    site_num = int(site_id.split("-")[1])
    if site_num % 5 == 0:  # 20% of sites are problematic
        return {"Yes": -0.15, "No": +0.15, "N/A": 0.0}
    elif site_num % 3 == 0:  # 20% of sites are excellent
        return {"Yes": +0.10, "No": -0.10, "N/A": 0.0}
    else:
        return {"Yes": 0.0, "No": 0.0, "N/A": 0.0}

# Add some engineer-specific variations
def get_engineer_variation(engineer_id):
    """Make some engineers more thorough than others"""
    if engineer_id % 10 == 0:  # 10% are strict
        return {"Yes": -0.10, "No": +0.10, "N/A": 0.0}
    elif engineer_id % 5 == 0:  # 20% are lenient
        return {"Yes": +0.15, "No": -0.15, "N/A": 0.0}
    else:
        return {"Yes": 0.0, "No": 0.0, "N/A": 0.0}

def weighted_random_response(keyword, site_id, engineer_id):
    """Get a realistic response based on keyword probabilities with site/engineer variations"""
    base_probs = RESPONSE_PROBABILITIES[keyword]
    site_effect = get_site_variation(site_id)
    engineer_effect = get_engineer_variation(engineer_id)
    
    # Apply variations
    adjusted_probs = {
        "Yes": max(0, min(1, base_probs["Yes"] + site_effect["Yes"] + engineer_effect["Yes"])),
        "No": max(0, min(1, base_probs["No"] + site_effect["No"] + engineer_effect["No"])),
        "N/A": base_probs["N/A"]  # Keep N/A constant for simplicity
    }
    
    # Normalize probabilities
    total = sum(adjusted_probs.values())
    normalized_probs = {k: v/total for k, v in adjusted_probs.items()}
    
    # Select response
    choices = list(normalized_probs.keys())
    probs = list(normalized_probs.values())
    return np.random.choice(choices, p=probs)

# --- Step 1: Generate Users ---
print("Generating users...")
users = []
for i in range(NUM_USERS):
    full_name = fake.name()
    user = User(full_name=full_name)
    users.append(user)
session.add_all(users)
session.commit()

# --- Step 2: Generate Audits and Responses ---
print("Generating audits and responses...")
start_date = datetime.now() - timedelta(days=DAYS_BACK)

for audit_num in range(NUM_AUDITS):
    if audit_num % 100 == 0:
        print(f"Generated {audit_num} audits...")
    
    user = random.choice(users)
    site_id = f"SITE-{random.randint(1, SITE_COUNT):03}"
    
    # Create timestamp with more audits during work hours
    hour = random.choices(
        [8,9,10,11,12,13,14,15,16,17,18,19],  # Work hours 8am-7pm
        weights=[1,3,5,7,8,6,7,8,7,5,3,1]     # More audits mid-morning and mid-afternoon
    )[0]
    minute = random.randint(0, 59)
    timestamp = fake.date_time_between(start_date=start_date, end_date="now")
    timestamp = timestamp.replace(hour=hour, minute=minute)
    
    audit = Audit(user_id=user.telegram_id, site_id=site_id, timestamp=timestamp)
    session.add(audit)
    session.commit()

    # Select questions - more likely to select from all categories
    selected_questions = random.sample(flat_questions, k=min(12, len(flat_questions)))
    
    responses = []
    for q in selected_questions:
        response = weighted_random_response(
            q['keyword'],
            site_id,
            user.telegram_id
        )
        
        responses.append(Response(
            audit_id=audit.id,
            category=q['category'],
            question=q["question_en"],
            question_ru=q["question_ru"],
            keyword=q["keyword"],
            response=response
        ))

    session.add_all(responses)
    session.commit()

print(f"✅ Successfully inserted:")
print(f"- {NUM_USERS} users")
print(f"- {NUM_AUDITS} audits")
print(f"- Approximately {NUM_AUDITS * len(selected_questions)} responses")
session.close()
