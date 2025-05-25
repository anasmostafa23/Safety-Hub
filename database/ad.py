from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Audit, User

engine = create_engine("sqlite:///safetyhub.db")
Session = sessionmaker(bind=engine)
session = Session()

audits = session.query(Audit).join(User).all()
print(f"Found {len(audits)} audits.")
for audit in audits:
    print(audit.id, audit.user.full_name, audit.timestamp)

session.close()
