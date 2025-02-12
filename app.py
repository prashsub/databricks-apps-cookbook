import streamlit as st
from utils import get_connection
# Import page functions from the views folder.
from views.home import home_page
from views.view_submissions import view_submissions
from views.submit_new_entry import submit_new_entry
from views.modify_entry import modify_entry

st.set_page_config(layout="wide")
st.logo("assets/logo.svg")

# If the connection and table name are not set, initialize them.
if "conn" not in st.session_state:
    st.session_state.conn = None
if "table_name_input" not in st.session_state:
    st.session_state.table_name_input = "prashanth_subrahmanyam_catalog.usecase_tracking.submissions"

def initialize_connection():
    http_path_input = st.sidebar.text_input("Databricks SQL Warehouse HTTP Path", placeholder="/sql/1.0/warehouses/xxxxxx", key="http_path")
    table_name_input = st.sidebar.text_input("Unity Catalog Table Name", value="prashanth_subrahmanyam_catalog.usecase_tracking.submissions", placeholder="catalog.schema.table", key="table_name")
    # Attempt to initialize the connection if both inputs are provided
    if http_path_input and table_name_input and st.session_state.conn is None:
        st.session_state.conn = get_connection(http_path_input)
        st.session_state.table_name_input = table_name_input

initialize_connection()

# Define groups and pages.
groups = [
    {
        "title": "Home",
        "views": [
            {"page": home_page, "label": "Home", "icon": "🏠"}
        ]
    },
    {
        "title": "Main Functions",
        "views": [
            {"page": view_submissions, "label": "View Submissions", "icon": "👁️"},
            {"page": submit_new_entry, "label": "Submit New Entry", "icon": "📝"},
            {"page": modify_entry, "label": "Modify Submission", "icon": "✏️"}
        ]
    }
]

pages = {
    group.get("title", ""): [
        st.Page(
            view.get("page"),
            title=view.get("label"),
            icon=view.get("icon")
        )
        for view in group["views"]
    ]
    for group in groups
}

# Create and run the navigation.
pg = st.navigation(pages)
pg.run()
