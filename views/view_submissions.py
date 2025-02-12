import streamlit as st
import pandas as pd
from utils import read_table, format_details


def view_submissions():
    st.header("View All Submissions")
    conn = st.session_state.get("conn")
    table_name = st.session_state.get("table_name_input")
    if not conn or not table_name:
        st.error("Connection or table name not provided.")
        return
    try:
        df = read_table(table_name, conn)
        if "details" in df.columns:
            df["details"] = df["details"].apply(format_details)
        
        # Rename columns for display
        column_mapping = {
            "account_name": "Account Name",
            "consumption_expectations": "Consumption Expectations",
            "uc_serverless_updates": "UC & Serverless Updates",
            "details": "Details",
            "created_by": "Created By",
            "created_on": "Created On",
            "changed_by": "Last Modified By",
            "last_changed": "Last Modified On"
        }
        df = df.rename(columns=column_mapping)
        
        st.sidebar.header("Filters")
        account_name_filter = st.sidebar.multiselect("Filter by Account Name", options=df["Account Name"].unique())
        created_by_filter = st.sidebar.multiselect("Filter by Created By", options=df["Created By"].unique())
        last_modified_filter = st.sidebar.multiselect("Filter by Last Modified By", options=df["Last Modified By"].unique())
        
        filtered_df = df[
            ((len(account_name_filter) == 0) | (df["Account Name"].isin(account_name_filter))) &
            ((len(created_by_filter) == 0) | (df["Created By"].isin(created_by_filter))) &
            ((len(last_modified_filter) == 0) | (df["Last Modified By"].isin(last_modified_filter)))
        ]
        
        st.dataframe(filtered_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading data: {e}")
