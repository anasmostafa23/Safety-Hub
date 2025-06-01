import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Audit, Response, Base
import seaborn as sns
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
    "Timestamp": audit.timestamp,
    "site_id": audit.site_id,
    "full_name": audit.user.full_name
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


tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Global Site Insights",
    "📍 Per Site Insights",
    "🧑‍🔧 Global Engineer Insights",
    "👤 Individual Engineer Insights"
])

with tab1:
    st.header("🌍 Global Keyword Answer Frequencies")
    
    global_counts = df.groupby(["Keyword", "Response"]).size().unstack(fill_value=0)
    global_percent = global_counts.div(global_counts.sum(axis=1), axis=0) * 100

    st.subheader("Frequency")
    st.dataframe(global_counts)

    st.subheader("Percentage (%)")
    st.dataframe(global_percent.round(2))



with tab2:
    st.header("📍 Site-Level Insights")

    site_selected = st.selectbox("Select a Site", sorted(df["site_id"].unique()))
    site_df = df[df["site_id"] == site_selected]
    
    site_counts = site_df.groupby(["Keyword", "Response"]).size().unstack(fill_value=0)
    site_percent = site_counts.div(site_counts.sum(axis=1), axis=0) * 100

    st.subheader(f"Frequencies for {site_selected}")
    st.dataframe(site_counts)

    st.subheader(f"Percentage (%) for {site_selected}")
    st.dataframe(site_percent.round(2))

    fig, ax = plt.subplots(figsize=(10, 5))
    site_counts.plot(kind="bar", stacked=True, ax=ax)
    st.pyplot(fig)

with tab3:
    st.header("🧑‍🔧 Global Engineer Insights")

    engineer_df = df.groupby("full_name").agg(
        total_audits=("Audit ID", "nunique"),
        sites_visited=("site_id", "nunique")
    ).reset_index()

    st.dataframe(engineer_df)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=engineer_df, x="full_name", y="total_audits", ax=ax)
    ax.set_title("Total Audits per Engineer")
    st.pyplot(fig)

with tab4:
    st.header("👤 Individual Engineer Keyword Performance")

    engineer_selected = st.selectbox("Choose Engineer", sorted(df["full_name"].unique()))
    engineer_data = df[df["full_name"] == engineer_selected]

    st.write(f"Total audits: {engineer_data['Audit ID'].nunique()}")
    st.write(f"Sites visited: {engineer_data['site_id'].nunique()}")

    for site in engineer_data["site_id"].unique():
        st.subheader(f"📍 Site: {site}")

        site_visits = engineer_data[engineer_data["site_id"] == site]
        site_kw = site_visits.groupby(["Keyword", "Response"]).size().unstack(fill_value=0)
        site_kw_percent = site_kw.div(site_kw.sum(axis=1), axis=0) * 100

        st.markdown("**Keyword Answer Ratio**")
        st.dataframe(site_kw_percent.round(2))

        # Compare to global for this site
        site_global = df[df["site_id"] == site].groupby(["Keyword", "Response"]).size().unstack(fill_value=0)
        site_global_percent = site_global.div(site_global.sum(axis=1), axis=0) * 100

        st.markdown("**Compared to Global Site Averages**")
        st.dataframe(site_global_percent.round(2))

session.close()
