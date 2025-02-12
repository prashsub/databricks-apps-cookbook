import streamlit as st

def home_page():
    st.header("Home")
    st.write("Welcome to the Databricks CRUD App!")
    st.write("Use the sidebar navigation to view submissions, create a new entry, or modify an existing one.")
    conn = st.session_state.get("conn")
    table_name = st.session_state.get("table_name_input")
    st.write("Connection:", conn.host)
    st.write("Table Name:", table_name)
