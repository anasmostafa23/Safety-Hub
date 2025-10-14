import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Audit, Response, Base
import seaborn as sns
import os
import numpy as np
import squarify
from math import pi
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "safetyhub.db")
engine = create_engine(f"sqlite:///{db_path}")

# Setup database connection
Session = sessionmaker(bind=engine)
session = Session()

# Fetch all data
audits = session.query(Audit).join(User).order_by(Audit.timestamp.desc()).all()
users = session.query(User).all()

st.title("Safetyhub Audit Dashboard")

# Load all responses into a DataFrame
@st.cache_data
def load_all_responses():
    responses = []
    for audit in audits:
        rs = session.query(Response).filter_by(audit_id=audit.id).all()
        for r in rs:
            responses.append({
                "Audit ID": r.audit_id,
                "Category": r.category,
                "Keyword": r.keyword,
                "Question": r.question,
                "Response": r.response,
                "Timestamp": audit.timestamp,
                "site_id": audit.site_id,
                "full_name": audit.user.full_name,
                "title": audit.title

            })
    return pd.DataFrame(responses)

df = load_all_responses()

# Calculate global answer frequencies and percentages
@st.cache_data
def calculate_global_stats(df):
    global_counts = df.groupby(["Keyword", "Response"]).size().unstack(fill_value=0)
    global_percent = global_counts.div(global_counts.sum(axis=1), axis=0) * 100
    return global_counts, global_percent

global_counts, global_percent = calculate_global_stats(df)

# Calculate site-level stats
@st.cache_data
def calculate_site_stats(df):
    site_counts = df.groupby(["site_id", "Keyword", "Response"]).size().unstack(fill_value=0)
    site_percent = site_counts.div(site_counts.sum(axis=1), axis=0) * 100
    return site_counts, site_percent

site_counts, site_percent = calculate_site_stats(df)

# Calculate engineer stats
@st.cache_data
def calculate_engineer_stats(df):
    # Basic engineer metrics
    engineer_metrics = df.groupby("full_name").agg(
        total_audits=("Audit ID", "nunique"),
        sites_visited=("site_id", "nunique"),
        unique_sites=("site_id", lambda x: list(x.unique()))
    ).reset_index()
    
    # Site visits per engineer
    engineer_site_visits = df.groupby(["full_name", "site_id"]).size().reset_index(name="visits")
    
    # Engineer keyword performance
    engineer_kw = df.groupby(["full_name", "Keyword", "Response"]).size().unstack(fill_value=0)
    engineer_kw_percent = engineer_kw.div(engineer_kw.sum(axis=1), axis=0) * 100
    
    return engineer_metrics, engineer_site_visits, engineer_kw, engineer_kw_percent

engineer_metrics, engineer_site_visits, engineer_kw, engineer_kw_percent = calculate_engineer_stats(df)

# Filtering sidebar
st.sidebar.header("🔎 Filter Data")
selected_template = st.sidebar.selectbox("Filter by Audit Template", ["All"] + sorted(df["title"].dropna().unique().tolist()))
selected_site = st.sidebar.selectbox("Filter by Site ID", ["All"] + sorted(df["site_id"].unique().tolist()))
selected_name = st.sidebar.selectbox("Filter by Engineer", ["All"] + sorted(df["full_name"].unique().tolist()))
start_date = st.sidebar.date_input("Start Date", value=df["Timestamp"].min())
end_date = st.sidebar.date_input("End Date", value=df["Timestamp"].max())

# Apply filters
filtered_df = df.copy()
if selected_template != "All":
    filtered_df = filtered_df[filtered_df["title"] == selected_template]
if selected_site != "All":
    filtered_df = filtered_df[filtered_df["site_id"] == selected_site]
if selected_name != "All":
    filtered_df = filtered_df[filtered_df["full_name"] == selected_name]
filtered_df = filtered_df[(filtered_df["Timestamp"].dt.date >= start_date) &
                          (filtered_df["Timestamp"].dt.date <= end_date)]

if filtered_df.empty:
    st.warning("No data matches your filters.")
    session.close()
    st.stop()

# Summary statistics
st.markdown("### 📊 Summary Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Audits", len(filtered_df["Audit ID"].unique()))
col2.metric("Unique Engineers", len(filtered_df["full_name"].unique()))
col3.metric("Unique Sites", len(filtered_df["site_id"].unique()))

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Global Insights", 
    "📍 Site Insights",
    "👤 Individual Engineer",
    "📝 Individual Audits"
])

with tab1:
    st.header("Global Keyword Performance")
    
    global_counts = df.groupby(["Keyword", "Response"]).size().unstack(fill_value=0)
    global_percent = global_counts.div(global_counts.sum(axis=1), axis=0) * 100

    st.subheader("Frequency")
    st.dataframe(global_counts)

    st.subheader("Percentage (%)")
    st.dataframe(global_percent.round(2))
    # Only keep the heatmap as requested
    st.subheader("Keyword Performance Heatmap")
    st.write("Percentage of Yes/No/NA responses for each keyword")
    
    # Get filtered global stats
    filtered_global_counts, filtered_global_percent = calculate_global_stats(filtered_df)
    
    # Display as heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(filtered_global_percent, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax)
    ax.set_title("Response Percentage by Keyword")
    st.pyplot(fig)

with tab2:
    st.header("🏗️ Site Insights")
    
    # Site selector at the top
    if selected_site == "All":
        site = st.selectbox("Select a Site", sorted(filtered_df["site_id"].unique()))
    else:
        site = selected_site
    
    site_data = filtered_df[filtered_df["site_id"] == site]
    
    # --- Site Overview Section ---
    st.subheader(f"📌 {site} - Detailed Analysis")
    
    # Key metrics row
   # --- Compact Overview Metrics ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Audits", len(site_data["Audit ID"].unique()))

    compliance_rate = (site_data['Response'] == 'Yes').mean() * 100
    m2.metric("Compliance", f"{compliance_rate:.1f}%", 
            delta=f"Δ{compliance_rate - global_percent['Yes'].mean():.1f}%")

    m3.metric("Engineers", len(site_data["full_name"].unique()))

    # Handle the "Most Common Issue" metric with proper truncation
    primary_issue = (site_data[site_data['Response']=='No']['Keyword'].value_counts().index[0] 
                    if 'No' in site_data['Response'].values else 'None')

    # Solution 1: Truncate with tooltip
    m4.markdown(f"""
    <div title="{primary_issue if len(primary_issue) > 20 else ''}">
        <div style="font-size: 14px; color: #808495">Most Common Issue</div>
        <div style="font-size: 20px; margin-top: 4px">
            {primary_issue[:18] + '...' if len(primary_issue) > 20 else primary_issue}
        </div>
    </div>
    """, unsafe_allow_html=True)


    site_tab1, site_tab2 = st.tabs([
        "📈 Trends & Patterns",
        "⚠️ Issue Analysis"
    ])
    
    with site_tab1:
        # Temporal trends (from previous detail_tab1)
        st.markdown("#### 🕒 Compliance Trend")
        monthly_compliance = site_data[site_data['Response']=='Yes'].groupby(
            site_data['Timestamp'].dt.to_period('M')
        ).size() / site_data.groupby(site_data['Timestamp'].dt.to_period('M')).size() * 100
        
        fig, ax = plt.subplots(figsize=(10, 4))
        monthly_compliance.plot(kind='line', marker='o', ax=ax, label='Site Compliance')
        ax.axhline(y=global_percent['Yes'].mean(), color='r', linestyle='--', 
                  label='Global Average')
        ax.set_title(f"Monthly Compliance Trend")
        ax.set_ylabel("Compliance Rate (%)")
        ax.legend()
        st.pyplot(fig)
        
       
    
    
    
    with site_tab2:
        # Issue analysis (from previous detail_tab3)
        st.markdown("#### 🚨 Issue Frequency")
        
        # Monthly issues
        monthly_issues = site_data[site_data['Response']=='No'].groupby(
            site_data['Timestamp'].dt.to_period('M')).size()
        
        fig, ax = plt.subplots(figsize=(10, 4))
        monthly_issues.plot(kind='bar', ax=ax, color='orange')
        ax.set_title("Monthly Issue Count")
        ax.set_xlabel("")
        st.pyplot(fig)
         # Issue breakdown - Simplified single plot version
        st.markdown("#### 🔎 Top 5 Problem Areas")

        # Get top 5 issues
        issue_keywords = site_data[site_data['Response']=='No']['Keyword'].value_counts().nlargest(5)

        if not issue_keywords.empty:
            fig, ax = plt.subplots(figsize=(10, 4))  # Adjusted for better proportions
            
            # Create horizontal bar plot
            issue_keywords.sort_values().plot(
                kind='barh', 
                ax=ax, 
                color='#ff6666',  # Slightly brighter red for emphasis
                edgecolor='darkred',
                width=0.7  # Makes bars slightly thinner
            )
            
            # Add value labels on each bar
            for i, v in enumerate(issue_keywords.sort_values()):
                ax.text(v + 0.5, i, str(v), color='darkred', fontweight='bold')
            
            ax.set_title("Most Frequent Safety Issues", pad=20, fontsize=14)
            ax.set_xlabel("Number of Occurrences", labelpad=10)
            ax.set_ylabel("")
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            st.pyplot(fig)
        else:
            st.success("🎉 No safety issues found for this site!")     
            
      

    
with tab3:
    st.header("👤 Individual Engineer Insights")
    
    if selected_name == "All":
        engineer = st.selectbox("Select Engineer", sorted(filtered_df["full_name"].unique()))
    else:
        engineer = selected_name
    
    engineer_data = filtered_df[filtered_df["full_name"] == engineer]
    
    st.subheader(f"Engineer Profile: {engineer}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Audits", len(engineer_data["Audit ID"].unique()))
    col2.metric("Sites Visited", len(engineer_data["site_id"].unique()))
    
    # Calculate engineer's overall compliance rate
    compliance_rate = (engineer_data['Response'] == 'Yes').mean() * 100
    col3.metric("Overall Compliance", f"{compliance_rate:.1f}%", 
               delta=f"{(compliance_rate - global_percent['Yes'].mean()):.1f}% vs global avg")
    
    # --- Performance Comparison Section ---
    st.subheader("Performance Benchmarking")
    
    # Create tabs for different comparison views
    comp_tab1, comp_tab2, comp_tab3 = st.tabs(["Peer Groups", "Trend Analysis", "Keyword Performance"])
    
    with comp_tab1:
        st.markdown("**Comparison Against Peer Groups**")
        
        # Create peer groups based on activity level
        if engineer_metrics['total_audits'].nunique() > 1:
                engineer_metrics['peer_group'] = pd.qcut(
                engineer_metrics['total_audits'],
                q=4,
                labels=['Low Activity', 'Moderate Activity', 'High Activity', 'Top Performers'],
                duplicates='drop'  # <-- also ensures unique bin edges
        )
        else:
                # fallback: everyone in the same group
                engineer_metrics['peer_group'] = 'Uniform Activity'

        
        # Get current engineer's group
        current_group = engineer_metrics.loc[
            engineer_metrics['full_name'] == engineer, 'peer_group'].values[0]
        
        st.write(f"{engineer} is in the **{current_group}** peer group "
                f"(based on audit volume)")
        
        # Show comparison within peer group
        peer_data = engineer_metrics[engineer_metrics['peer_group'] == current_group]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Audit count comparison
        sns.barplot(
            data=peer_data.sort_values('total_audits', ascending=False),
            y='full_name',
            x='total_audits',
            ax=ax1,
            palette=['red' if x == engineer else 'gray' for x in peer_data['full_name']]
        )
        ax1.set_title(f"Audit Count Comparison\n({current_group} Group)")
        ax1.set_xlabel("Number of Audits")
        
        # Compliance rate comparison
        peer_compliance = []
        for peer in peer_data['full_name']:
            peer_responses = filtered_df[filtered_df['full_name'] == peer]['Response']
            peer_compliance.append((peer_responses == 'Yes').mean() * 100)
        
        peer_data['compliance_rate'] = peer_compliance
        sns.barplot(
            data=peer_data.sort_values('compliance_rate', ascending=False),
            y='full_name',
            x='compliance_rate',
            ax=ax2,
            palette=['red' if x == engineer else 'gray' for x in peer_data['full_name']]
        )
        ax2.axvline(x=global_percent['Yes'].mean(), color='green', linestyle='--', 
                   label='Global Avg')
        ax2.set_title(f"Compliance Rate Comparison\n({current_group} Group)")
        ax2.set_xlabel("Compliance Rate (%)")
        ax2.legend()
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with comp_tab2:
        st.markdown("**Performance Trend Over Time**")
        
        # Monthly compliance trend
        monthly = engineer_data.groupby([
            engineer_data['Timestamp'].dt.to_period('M'),
            'Response'
        ]).size().unstack().fillna(0)
        monthly_pct = monthly.div(monthly.sum(axis=1), axis=0) * 100
        
        fig, ax = plt.subplots(figsize=(10, 4))
        monthly_pct['Yes'].plot(
            kind='line', 
            marker='o', 
            ax=ax, 
            label=engineer
        )
        
        # Add peer group average for context
        if 'peer_group' in locals():
            peer_group_avg = filtered_df[
                filtered_df['full_name'].isin(peer_data['full_name'])
            ].groupby([
                filtered_df['Timestamp'].dt.to_period('M'),
                'Response'
            ]).size().unstack().fillna(0)
            peer_group_avg_pct = peer_group_avg.div(peer_group_avg.sum(axis=1), axis=0) * 100
            peer_group_avg_pct['Yes'].plot(
                kind='line', 
                linestyle='--', 
                ax=ax, 
                label=f'{current_group} Avg'
            )
        
        ax.axhline(y=global_percent['Yes'].mean(), color='green', linestyle=':', 
                  label='Global Avg')
        ax.set_title("Monthly Compliance Rate Trend")
        ax.set_ylabel("Compliance Rate (%)")
        ax.legend()
        st.pyplot(fig)
        
        # Audit frequency over time
        st.markdown("**Audit Activity Over Time**")
        audit_freq = engineer_data.groupby(
            engineer_data['Timestamp'].dt.to_period('M')
        ).size()
        
        fig, ax = plt.subplots(figsize=(10, 3))
        audit_freq.plot(kind='bar', ax=ax)
        ax.set_title("Monthly Audit Count")
        ax.set_xlabel("")
        st.pyplot(fig)
    
    with comp_tab3:
        st.markdown("**Keyword-Specific Performance**")
        
        # Calculate engineer's keyword compliance
        eng_kw = engineer_data.groupby(['Keyword', 'Response']).size().unstack().fillna(0)
        eng_kw_pct = eng_kw.div(eng_kw.sum(axis=1), axis=0) * 100
        
        # Compare to global averages
        comparison = pd.DataFrame({
            'Engineer': eng_kw_pct['Yes'],
            'Global': global_percent['Yes']
        }).dropna()
        
        # Sort by performance gap
        comparison['Difference'] = comparison['Engineer'] - comparison['Global']
        comparison = comparison.sort_values('Difference')
        
        # Split into top and bottom performing keywords
        st.write("**Areas of Strength**")
        top_keywords = comparison.nlargest(3, 'Difference')
        if not top_keywords.empty:
            cols = st.columns(len(top_keywords))
            for i, (kw, row) in enumerate(top_keywords.iterrows()):
                cols[i].metric(
                    label=kw,
                    value=f"{row['Engineer']:.1f}%",
                    delta=f"+{row['Difference']:.1f}% vs global",
                    delta_color="normal"
                )
        else:
            st.warning("No significant areas of strength identified")
        
        st.write("**Areas Needing Improvement**")
        bottom_keywords = comparison.nsmallest(3, 'Difference')
        if not bottom_keywords.empty:
            cols = st.columns(len(bottom_keywords))
            for i, (kw, row) in enumerate(bottom_keywords.iterrows()):
                cols[i].metric(
                    label=kw,
                    value=f"{row['Engineer']:.1f}%",
                    delta=f"{row['Difference']:.1f}% vs global",
                    delta_color="inverse"
                )
        else:
            st.info("No significant areas needing improvement")
        
        # Detailed keyword view
        st.markdown("**Detailed Keyword Performance**")
        selected_kw = st.selectbox(
            "Select keyword to analyze:",
            options=sorted(comparison.index.tolist())
        )
        
        kw_data = engineer_data[engineer_data['Keyword'] == selected_kw]
        kw_responses = kw_data['Response'].value_counts(normalize=True) * 100
        
        fig, ax = plt.subplots(figsize=(8, 3))
        kw_responses.plot(kind='bar', ax=ax)
        ax.set_title(f"Response Distribution for '{selected_kw}'")
        ax.set_ylabel("Percentage")
        st.pyplot(fig)

with tab4:
    st.header("📝 Audit Inspector")
    
    # Fetch filtered audits based on current filters
    filtered_audits = session.query(Audit).join(User).filter(
        Audit.timestamp.between(start_date, end_date + timedelta(days=1))
    )

    if selected_template != "All":
        filtered_audits = filtered_audits.filter(Audit.title == selected_template)
    if selected_site != "All":
        filtered_audits = filtered_audits.filter(Audit.site_id == selected_site)
    if selected_name != "All":
        filtered_audits = filtered_audits.filter(User.full_name == selected_name)
    
    filtered_audits = filtered_audits.order_by(Audit.timestamp.desc()).all()
    
    if not filtered_audits:
        st.warning("No audits match your filters")
        session.close()
        st.stop()
    
    # Audit selection dropdown
    audit_options = [
        f"{audit.id} | {audit.user.full_name} | {audit.site_id} | {audit.timestamp.strftime('%Y-%m-%d %H:%M')}"
        for audit in filtered_audits
    ]
    
    selected = st.selectbox(
        "Select an audit to inspect:",
        options=audit_options,
        key="audit_selector"  # Important for unique key
    )
    
    # Parse selected audit
    selected_id = int(selected.split(" | ")[0])
    audit = session.query(Audit).get(selected_id)
    
    # Audit metadata
    st.subheader("Audit Metadata")
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        st.metric("Auditor", audit.user.full_name)
    with meta_col2:
        st.metric("Site", audit.site_id)
    with meta_col3:
        st.metric("Date", audit.timestamp.strftime('%Y-%m-%d'))
    
    # Responses display
    st.subheader("Audit Responses")
    responses = session.query(Response).filter_by(audit_id=audit.id).all()
    
    # Enhanced dataframe display
    df = pd.DataFrame([{
        "Category": r.category,
        "Keyword": r.keyword,
        "Question": r.question[:60] + "..." if len(r.question) > 60 else r.question,  # Truncate long questions
        "Response": r.response,
    } for r in responses])
    
    # Interactive dataframe with expandable rows
    gb = GridOptionsBuilder.from_dataframe(df)
    
    gb.configure_selection('single', use_checkbox=False)
    grid_options = gb.build()
    
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        height=min(400, 50 + len(responses)*40),  # Dynamic height
        theme="streamlit",
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True
    )
    
    
    # Add export options
    st.download_button(
        "Export to CSV",
        df.to_csv(index=False).encode('utf-8'),
        f"audit_{selected_id}_responses.csv",
        "text/csv"
    )
    
    
session.close()
