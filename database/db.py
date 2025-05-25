from database.models import Session, User, Audit, Response


def upsert_user(telegram_id, full_name, site_id):
    session = Session()
    user = session.query(User).get(telegram_id)
    if not user:
        user = User(telegram_id=telegram_id, full_name=full_name, site_id=site_id)
        session.add(user)
    else:
        user.full_name = full_name
        user.site_id = site_id
    session.commit()
    session.close()


def create_audit(telegram_id, site_id):
    session = Session()
    audit = Audit(user_id=telegram_id, site_id=site_id)  # Pass site_id here
    session.add(audit)
    session.commit()
    audit_id = audit.id
    session.close()
    return audit_id


def save_responses(audit_id, template, responses):
    session = Session()
    question_index = 0
    for cat in template["categories"]:
        cat_name = cat["name"]
        for q in cat["questions"]:
            answer = responses[question_index] if question_index < len(responses) else "N/A"
            session.add(Response(
                audit_id=audit_id,
                question_index=question_index,
                category=cat_name,
                question=q["question_en"],
                response=answer
            ))
            question_index += 1
    session.commit()
    session.close()
