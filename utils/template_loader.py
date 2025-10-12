# safetyhub_bot/utils/template_loader.py

import json
import os
from .template_manager import get_active_template, initialize_default_template

def load_template():
    """Load the currently active template."""

    # Initialize default template if none is active
    initialize_default_template()

    template = get_active_template()
    if template is None:
        raise FileNotFoundError("No active template found. Please contact an administrator.")

    return template

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
