# dashboard.py

import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Audit, Response, Base
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "safetyhub.db")
engine = create_engine(f"sqlite:///{db_path}")


# Setup database connection
Session = sessionmaker(bind=engine)
session = Session()


# Fetch all audits
audits = session.query(Audit).join(User).order_by(Audit.timestamp.desc()).all()
st.title("Safetyhub Audit Dashboard")
st.write("Number of audits found:", len(audits))


if not audits:
    st.warning("No audits found.")
else:
    audit_options = [
        f"{audit.id} | {audit.user.full_name} | {audit.site_id} | {audit.timestamp.strftime('%Y-%m-%d %H:%M')}"
        for audit in audits
    ]
    selected = st.selectbox("Select an audit to view details", audit_options)

    # Parse selected audit ID
    selected_id = int(selected.split(" | ")[0]) 
    audit = session.query(Audit).get(selected_id)

    st.subheader("Audit Details")
    st.write(f"**Full Name:** {audit.user.full_name}")
    st.write(f"**Site ID:** {audit.user.site_id}")
    st.write(f"**Timestamp:** {audit.timestamp}")

    st.subheader("Responses")
    responses = session.query(Response).filter_by(audit_id=audit.id).all()

    df = pd.DataFrame([{
        "Category": r.category,
        "Question": r.question,
        "Response": r.response
    } for r in responses])

    st.dataframe(df)

session.close()
