groups = [
    {
        "views": [
            {
                "label": "Introduction",
                "help": "",
                "page": "views/app_intro.py",
                "icon": ":material/skillet_cooktop:",
            },
        ],
    },
    {
        "title": "Use Case Details",
        "views": [
            {
                "label": "View Account and Use Case updates",
                "help": "Query a Unity Catalog Delta table.",
                "page": "views/view_submissions.py",
                "icon": ":material/home:",
            },
            {
                "label": "Submit a new update",
                "help": "Submit a new update for an account and it's use cases",
                "page": "views/submit_new_entry.py",
                "icon": ":material/add_box:",
            },
            {
                "label": "Modify an existing submission",
                "help": "Interactively edit a Delta table in the UI.",
                "page": "views/modify_entry.py",
                "icon": ":material/edit_document:",
            },
        ],
    },
]
