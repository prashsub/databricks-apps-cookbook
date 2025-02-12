import streamlit as st
import pandas as pd
import json
import datetime
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

@st.cache_resource
def get_connection(http_path: str):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name: str, conn) -> pd.DataFrame:
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

def escape_quotes(value):
    if isinstance(value, str):
        return value.replace("'", "''")
    return value

def build_details_literal(entry_list):
    parts = []
    for entry in entry_list:
        sfdc = escape_quotes(str(entry.get("SFDC Use Case Link", "")))
        try:
            days = int(entry.get("# of days in stage", 0))
        except Exception:
            days = 0
        try:
            monthly = int(entry.get("Monthly DBU", 0))
        except Exception:
            monthly = 0
        notes = escape_quotes(str(entry.get("Notes", "")))
        risks = escape_quotes(str(entry.get("Risks, Blockers, Asks", "")))
        part = f"struct('{sfdc}' as sfdc_use_case_link, {days} as days_in_stage, {monthly} as monthly_dbu, '{notes}' as notes, '{risks}' as risks)"
        parts.append(part)
    if parts:
        return "array(" + ", ".join(parts) + ")"
    else:
        return "array()"

def merge_entry(table_name: str, row: dict, conn):
    details_literal = build_details_literal(row['entry'])
    merge_query = f"""
MERGE INTO {table_name} AS target
USING (
  SELECT
    '{escape_quotes(row['account_name'])}' AS account_name,
    '{escape_quotes(row['consumption_expectations'])}' AS consumption_expectations,
    '{escape_quotes(row['uc_serverless_updates'])}' AS uc_serverless_updates,
    {details_literal} AS details,
    '{escape_quotes(row['created_by'])}' AS created_by,
    CAST('{row['created_on']}' AS TIMESTAMP) AS created_on,
    CAST('{row['last_changed']}' AS TIMESTAMP) AS last_changed,
    '{escape_quotes(row['changed_by'])}' AS changed_by
) AS source
ON target.account_name = source.account_name
  AND target.created_by = source.created_by
  AND target.created_on = source.created_on
WHEN MATCHED THEN UPDATE SET
    consumption_expectations = source.consumption_expectations,
    uc_serverless_updates = source.uc_serverless_updates,
    details = source.details,
    last_changed = source.last_changed,
    changed_by = source.changed_by
WHEN NOT MATCHED THEN INSERT (account_name, consumption_expectations, uc_serverless_updates, details, created_by, created_on, last_changed, changed_by)
VALUES (source.account_name, source.consumption_expectations, source.uc_serverless_updates, source.details, source.created_by, source.created_on, source.last_changed, source.changed_by)
"""
    st.info("Executing merge query on Databricks SQL...")
    with conn.cursor() as cursor:
        cursor.execute(merge_query)
    st.success("Operation successful")

def get_user_email():
    try:
        headers = st.context.headers
        email = headers.get("X-Forwarded-Email", "unknown")
    except Exception:
        email = "unknown"
    return email

def format_details(details):
    try:
        if isinstance(details, str):
            details = json.loads(details)
    except Exception:
        pass
    if isinstance(details, list):
        formatted_list = []
        for item in details:
            formatted_str = (
                f"Link: {item.get('sfdc_use_case_link', '')}, "
                f"Days: {item.get('days_in_stage', '')}, "
                f"Monthly DBU: {item.get('monthly_dbu', '')}, "
                f"Notes: {item.get('notes', '')}, "
                f"Risks: {item.get('risks', '')}"
            )
            formatted_list.append(formatted_str)
        return "\n".join(formatted_list)
    return str(details)

def transform_details_for_editor(details):
    transformed = []
    if isinstance(details, str):
        try:
            details = json.loads(details)
        except Exception:
            details = []
    for rec in details or []:
        transformed.append({
            "SFDC Use Case Link": rec.get("sfdc_use_case_link", ""),
            "# of days in stage": rec.get("days_in_stage", 0),
            "Monthly DBU": rec.get("monthly_dbu", 0),
            "Notes": rec.get("notes", ""),
            "Risks, Blockers, Asks": rec.get("risks", "")
        })
    return transformed
