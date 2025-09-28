# safetyhub_bot/utils/template_loader.py

import json
import os

def load_keywords_from_template(json_path):
    """Load keywords from a template file path"""
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
