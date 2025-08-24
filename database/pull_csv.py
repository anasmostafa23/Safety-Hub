import pandas as pd
from sqlalchemy import create_engine
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "safetyhub.db")
engine = create_engine(f"sqlite:///{db_path}")

# Join audits + responses into a single table
query = """
SELECT a.id as audit_id, a.site_id, r.keyword, r.response
FROM audits a
JOIN responses r ON a.id = r.audit_id
"""
df = pd.read_sql(query, engine)

df.to_csv("audits_export.csv", index=False)
print("Exported", len(df), "rows")
