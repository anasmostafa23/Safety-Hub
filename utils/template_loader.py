# safetyhub_bot/utils/template_loader.py

import json
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../templates/template1_full_bilingual.json")

def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
