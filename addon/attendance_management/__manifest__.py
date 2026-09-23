{
    "name": "Attendance Management",
    "version": "1.0.0",
    "category": "Human Resources",
    "summary": "Attendance data and employee working time management",
    "description": """
        Attendance Management
        =====================

        This module manages:

        - Employee mapping
        - Raw attendance data
        - Processed attendance
        - Attendance errors
        - Employee working time
    """,
    "author": "Nguyen Manh Truong",
    "license": "LGPL-3",
    "depends": [
        "hr",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/employee_mapping_views.xml",
        "views/raw_attendance_views.xml",
        "views/device_views.xml",
        "views/sync_log_views.xml",
    ],
    "installable": True,
    "application": True,
}
