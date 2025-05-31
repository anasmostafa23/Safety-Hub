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

# Load audits and users for filtering
all_audits = session.query(Audit).join(User).order_by(Audit.timestamp.desc()).all()

site_ids = sorted(list(set(audit.site_id for audit in all_audits)))
names = sorted(list(set(audit.user.full_name for audit in all_audits)))

st.sidebar.header("🔎 Filter Audits")

selected_site = st.sidebar.selectbox("Filter by Site ID", ["All"] + site_ids)
selected_name = st.sidebar.selectbox("Filter by Full Name", ["All"] + names)
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

filtered_audits = all_audits

if selected_site != "All":
    filtered_audits = [a for a in filtered_audits if a.site_id == selected_site]

if selected_name != "All":
    filtered_audits = [a for a in filtered_audits if a.user.full_name == selected_name]

filtered_audits = [a for a in filtered_audits if start_date <= a.timestamp.date() <= end_date]


if not filtered_audits:
    st.warning("No audits match your filters.")
else:
    audit_options = [
        f"{audit.id} | {audit.user.full_name} | {audit.site_id} | {audit.timestamp.strftime('%Y-%m-%d %H:%M')}"
        for audit in filtered_audits
    ]
    selected = st.selectbox("Select an audit to view details", audit_options)
    
    # Parse selected audit ID
    selected_id = int(selected.split(" | ")[0]) 
    audit = session.query(Audit).get(selected_id)

    st.subheader("Audit Details")
    st.write(f"**Full Name:** {audit.user.full_name}")
    st.write(f"**Site ID:** {audit.site_id}")
    st.write(f"**Timestamp:** {audit.timestamp}")

    st.subheader("Responses")
    responses = session.query(Response).filter_by(audit_id=audit.id).all()

    df = pd.DataFrame([{
        "Category": r.category,
        "Keyword": r.keyword , 
        "Question": r.question,
        "Response": r.response
    } for r in responses])

    st.dataframe(df)


session.close()
