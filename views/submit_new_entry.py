import streamlit as st
import pandas as pd
import datetime
from utils import merge_entry, get_user_email

def submit_new_entry():
    st.header("Submit New Entry")
    conn = st.session_state.get("conn")
    table_name = st.session_state.get("table_name_input")
    if not conn or not table_name:
        st.error("Connection or table name not provided.")
        return
    with st.form("new_entry_form"):
        account_name = st.text_input("Account Name")
        consumption_exp = st.text_area("Consumption Expectations")
        uc_serverless = st.text_area("UC & Serverless Updates")
        
        st.markdown("### Details")
        default_df = pd.DataFrame(columns=[
            "SFDC Use Case Link",
            "# of days in stage",
            "Monthly DBU",
            "Notes",
            "Risks, Blockers, Asks"
        ])
        column_config = {
            "SFDC Use Case Link": st.column_config.TextColumn("SFDC Use Case Link"),
            "# of days in stage": st.column_config.NumberColumn("# of days in stage", format="%d", step=1),
            "Monthly DBU": st.column_config.NumberColumn("Monthly DBU", format="%d", step=1),
            "Notes": st.column_config.TextColumn("Notes"),
            "Risks, Blockers, Asks": st.column_config.TextColumn("Risks, Blockers, Asks")
        }
        
        entry_df = st.data_editor(
            default_df,
            num_rows="dynamic",
            key="new_entry_data",
            hide_index=True,
            column_config=column_config
        )
        submitted = st.form_submit_button("Submit Entry")
        
        if submitted:
            current_time = datetime.datetime.now().isoformat()
            user_email = get_user_email()
            entry_list = entry_df.to_dict(orient="records")
            row = {
                "account_name": account_name,
                "consumption_expectations": consumption_exp,
                "uc_serverless_updates": uc_serverless,
                "entry": entry_list,
                "created_by": user_email,
                "created_on": current_time,
                "changed_by": user_email,
                "last_changed": current_time
            }
            try:
                merge_entry(table_name, row, conn)
                st.success("New entry submitted successfully!")
            except Exception as e:
                st.error(f"Error submitting entry: {e}")
