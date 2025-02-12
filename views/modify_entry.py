import streamlit as st
import pandas as pd
import datetime
from utils import read_table, transform_details_for_editor, merge_entry, get_user_email

def modify_entry():
    st.header("Modify Existing Entry")
    conn = st.session_state.get("conn")
    table_name = st.session_state.get("table_name_input")
    if not conn or not table_name:
        st.error("Connection or table name not provided.")
        return
    
    try:
        df = read_table(table_name, conn)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    if df.empty:
        st.info("No entries found to modify.")
        return
    
    with st.expander("Filter Submissions"):
        unique_accounts = df["account_name"].unique().tolist()
        unique_created_by = df["created_by"].unique().tolist()
        unique_last_modified = df["changed_by"].unique().tolist()
        filter_accounts = st.multiselect("Filter by Account Name", options=unique_accounts, default=unique_accounts)
        filter_created_by = st.multiselect("Filter by Created By", options=unique_created_by, default=unique_created_by)
        filter_last_modified = st.multiselect("Filter by Last Modified By", options=unique_last_modified, default=unique_last_modified)
    
    filtered_df = df[
        (df["account_name"].isin(filter_accounts)) &
        (df["created_by"].isin(filter_created_by)) &
        (df["changed_by"].isin(filter_last_modified))
    ]
    
    if filtered_df.empty:
        st.info("No entries match the applied filters. Adjust your filter criteria.")
        return

    filtered_df["display"] = (
        filtered_df["account_name"].astype(str) + " - " +
        filtered_df["created_by"].astype(str) + " - " +
        filtered_df["created_on"].astype(str)
    )
    selection = st.selectbox("Select an entry to modify", filtered_df["display"].tolist())
    key_parts = selection.split(" - ")
    if len(key_parts) < 3:
        st.error("Selected entry key is invalid.")
        return
    account_key, created_by_key, created_on_key = key_parts[0], key_parts[1], key_parts[2]
    try:
        row_data = df[
            (df["account_name"] == account_key) &
            (df["created_by"] == created_by_key) &
            (df["created_on"] == created_on_key)
        ].iloc[0]
    except Exception as e:
        st.error("Could not locate the selected entry for modification.")
        return

    st.info(f"Modifying entry created by {row_data['created_by']} on {row_data['created_on']}")
    st.text_input("Account Name", value=row_data["account_name"], disabled=True)
    st.text_input("Created By", value=row_data["created_by"], disabled=True)
    st.text_input("Created On", value=row_data["created_on"], disabled=True)
    
    modified_consumption = st.text_area("Consumption Expectations", value=row_data["consumption_expectations"])
    modified_uc_serverless = st.text_area("UC & Serverless Updates", value=row_data["uc_serverless_updates"])
    
    try:
        entry_initial = transform_details_for_editor(row_data["details"])
    except Exception:
        entry_initial = []
        
    default_df = pd.DataFrame(entry_initial, columns=[
        "SFDC Use Case Link",
        "# of days in stage",
        "Monthly DBU",
        "Notes",
        "Risks, Blockers, Asks"
    ]) if entry_initial else pd.DataFrame(columns=[
        "SFDC Use Case Link",
        "# of days in stage",
        "Monthly DBU",
        "Notes",
        "Risks, Blockers, Asks"
    ])
    
    modified_entry_df = st.data_editor(default_df, num_rows="dynamic", key="modify_entry_data", hide_index=True)
    
    if st.button("Save Changes"):
        last_changed = datetime.datetime.now().isoformat()
        user_email = get_user_email()
        entry_list = modified_entry_df.to_dict(orient="records")
        row = {
            "account_name": row_data["account_name"],
            "consumption_expectations": modified_consumption,
            "uc_serverless_updates": modified_uc_serverless,
            "entry": entry_list,
            "created_by": row_data["created_by"],
            "created_on": row_data["created_on"],
            "changed_by": user_email,
            "last_changed": last_changed
        }
        try:
            merge_entry(table_name, row, conn)
            st.success("Entry modified successfully!")
        except Exception as e:
            st.error(f"Error updating entry: {e}")
