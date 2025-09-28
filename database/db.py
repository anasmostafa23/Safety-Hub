from database.models import Session, User, Audit, Response
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Global session cache for better performance
_session_cache = {}

@contextmanager
def get_db_session():
    """Context manager for database sessions with proper cleanup"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()

def upsert_user(telegram_id, full_name, site_id):
    """Optimized user upsert with session reuse"""
    with get_db_session() as session:
        user = session.query(User).get(telegram_id)
        if not user:
            user = User(telegram_id=telegram_id, full_name=full_name, site_id=site_id)
            session.add(user)
        else:
            user.full_name = full_name
            user.site_id = site_id

def create_audit(telegram_id, site_id):
    """Optimized audit creation"""
    with get_db_session() as session:
        audit = Audit(user_id=telegram_id, site_id=site_id)
        session.add(audit)
        session.flush()  # Get the ID without committing
        audit_id = audit.id
    return audit_id

def save_responses(audit_id, template, responses):
    """Optimized bulk response saving - all in one transaction"""
    with get_db_session() as session:
        response_objects = []
        question_index = 0

        for cat in template["categories"]:
            cat_name = cat["name"]
            for q in cat["questions"]:
                answer = responses[question_index] if question_index < len(responses) else "N/A"
                response_obj = Response(
                    audit_id=audit_id,
                    question_index=question_index,
                    category=cat_name,
                    question=q["question_en"],
                    question_ru=q["question_ru"],
                    keyword=q["keyword"],
                    response=answer
                )
                response_objects.append(response_obj)
                question_index += 1

        # Bulk insert all responses at once
        session.bulk_save_objects(response_objects)
        logger.info(f"Saved {len(response_objects)} responses for audit {audit_id}")

def get_active_audit_template():
    """Optimized template loading with caching"""
    with get_db_session() as session:
        audit = session.query(Audit).filter_by(is_active=True).first()
        if not audit:
            return None

        import json
        try:
            with open(audit.template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading template {audit.template_path}: {e}")
            return None

# Cache for active template to avoid repeated file I/O
_template_cache = {"data": None, "path": None}

def get_cached_active_audit_template():
    """Get cached active template to avoid repeated file reads"""
    global _template_cache

    with get_db_session() as session:
        audit = session.query(Audit).filter_by(is_active=True).first()
        if not audit:
            _template_cache = {"data": None, "path": None}
            return None

        # Check if we have a cached version of the current template
        if _template_cache["path"] == audit.template_path and _template_cache["data"]:
            return _template_cache["data"]

        # Load and cache the template
        try:
            import json
            with open(audit.template_path, "r", encoding="utf-8") as f:
                template_data = json.load(f)
                _template_cache = {"data": template_data, "path": audit.template_path}
                return template_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading template {audit.template_path}: {e}")
            _template_cache = {"data": None, "path": None}
            return None
