import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

# Basic stats
st.markdown("### Summary Statistics")
num_audits = len(audits)
num_users = session.query(User).count()
num_sites = len(set(a.site_id for a in audits))

st.write(f"**Total audits:** {num_audits}")
st.write(f"**Unique users:** {num_users}")
st.write(f"**Unique sites:** {num_sites}")

# Load audits and users for filtering
all_audits = audits
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
    session.close()
    st.stop()

# Flatten responses for filtered audits
responses = []
for audit in filtered_audits:
    rs = session.query(Response).filter_by(audit_id=audit.id).all()
    responses.extend(rs)

df = pd.DataFrame([{
    "Audit ID": r.audit_id,
    "Category": r.category,
    "Keyword": r.keyword,
    "Question": r.question,
    "Response": r.response,
    "Timestamp": next(a.timestamp for a in filtered_audits if a.id == r.audit_id)
} for r in responses])

# Show audit selection and details
st.subheader("Select an Audit to View Details")
audit_options = [
    f"{audit.id} | {audit.user.full_name} | {audit.site_id} | {audit.timestamp.strftime('%Y-%m-%d %H:%M')}"
    for audit in filtered_audits
]
selected = st.selectbox("Audit", audit_options)
selected_id = int(selected.split(" | ")[0])
audit = session.query(Audit).get(selected_id)

st.subheader("Audit Details")
st.write(f"**Full Name:** {audit.user.full_name}")
st.write(f"**Site ID:** {audit.site_id}")
st.write(f"**Timestamp:** {audit.timestamp}")

audit_responses = df[df["Audit ID"] == selected_id].copy()
st.dataframe(audit_responses[["Category", "Keyword", "Question", "Response"]])

# Insights and charts
st.markdown("---")
st.subheader("Insights and Charts")

# Response distribution pie chart
response_counts = df["Response"].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(response_counts, labels=response_counts.index, autopct="%1.1f%%", startangle=140)
ax1.axis("equal")
st.pyplot(fig1)

# Responses by category bar chart
cat_counts = df.groupby(["Category", "Response"]).size().unstack(fill_value=0)
st.bar_chart(cat_counts)

# Audits over time (number of audits per day)
audit_dates = pd.Series([a.timestamp.date() for a in filtered_audits])
audits_over_time = audit_dates.value_counts().sort_index()
st.line_chart(audits_over_time)

# Optional: Response distribution per category stacked bar chart
st.markdown("##### Response Distribution per Category")
fig2, ax2 = plt.subplots(figsize=(10, 6))
cat_counts.plot(kind='bar', stacked=True, ax=ax2)
ax2.set_ylabel("Count")
ax2.set_xlabel("Category")
ax2.set_title("Response Counts by Category and Response")
st.pyplot(fig2)

session.close()
