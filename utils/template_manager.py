# utils/template_manager.py
import os
import json
from typing import List, Dict, Optional

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates")
ACTIVE_TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), "../templates/active_template.json")

def get_available_templates() -> List[Dict]:
    """Get list of all available templates with metadata."""
    templates = []
    if not os.path.exists(TEMPLATES_DIR):
        return templates

    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.json') and not filename.startswith('active_template'):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)

                # Extract basic info
                template_info = {
                    'filename': filename,
                    'name': template_data.get('template_name', filename),
                    'categories_count': len(template_data.get('categories', [])),
                    'questions_count': sum(len(cat.get('questions', []))
                                         for cat in template_data.get('categories', [])),
                    'filepath': filepath
                }
                templates.append(template_info)
            except (json.JSONDecodeError, KeyError):
                # Skip invalid template files
                continue

    return templates

def get_active_template() -> Optional[Dict]:
    """Get the currently active template."""
    if not os.path.exists(ACTIVE_TEMPLATE_FILE):
        return None

    try:
        with open(ACTIVE_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            active_data = json.load(f)
            template_filename = active_data.get('active_template')

            if template_filename:
                template_path = os.path.join(TEMPLATES_DIR, template_filename)
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        pass

    return None

def set_active_template(template_filename: str) -> bool:
    """Set the active template by filename."""
    if not template_filename.endswith('.json'):
        template_filename += '.json'

    template_path = os.path.join(TEMPLATES_DIR, template_filename)
    if not os.path.exists(template_path):
        return False

    # Create active template config
    active_config = {
        'active_template': template_filename,
        'set_at': str(os.times())  # timestamp for tracking
    }

    try:
        with open(ACTIVE_TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(active_config, f, indent=2)
        return True
    except Exception:
        return False

def get_template_info(filename: str) -> Optional[Dict]:
    """Get detailed information about a specific template."""
    if not filename.endswith('.json'):
        filename += '.json'

    filepath = os.path.join(TEMPLATES_DIR, filename)
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            template_data = json.load(f)

        return {
            'filename': filename,
            'name': template_data.get('template_name', filename),
            'categories': template_data.get('categories', []),
            'categories_count': len(template_data.get('categories', [])),
            'questions_count': sum(len(cat.get('questions', []))
                                 for cat in template_data.get('categories', [])),
            'filepath': filepath
        }
    except (json.JSONDecodeError, KeyError):
        return None

def initialize_default_template():
    """Initialize with a default template if none is active."""
    if get_active_template() is None:
        # Try to use template1_full_bilingual.json as default
        default_template = "template1_full_bilingual.json"
        if os.path.exists(os.path.join(TEMPLATES_DIR, default_template)):
            set_active_template(default_template)
            return True
    return False
