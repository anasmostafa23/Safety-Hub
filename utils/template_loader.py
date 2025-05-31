# safetyhub_bot/utils/template_loader.py

import json
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../templates/template1_full_bilingual.json")

def load_template():
    
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_keywords_from_template(json_path='template1_full_bilingual.json'):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    keywords = []
    for category in data['categories']:
        for q in category['questions']:
            keywords.append({
                'keyword': q['keyword'],
                'question_en': q['question_en'],
                'question_ru': q['question_ru'],
                'category': category['name']
            })
    return keywords