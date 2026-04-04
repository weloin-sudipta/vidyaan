import frappe

def create_vidyaan_onboarding():
    create_onboarding_steps()
    create_module_onboarding()

def create_onboarding_steps():
    steps = [
        {
            "name": "Create a Class Program",
            "title": "Set up your first Class",
            "description": "Programs are essentially Classes or Streams (e.g., 'Class 11 Science'). Let's create your first one to organize your subjects.",
            "reference_document": "Program",
            "action": "Create Entry",
            "is_complete": 0,
            "is_skippable": 0
        },
        {
            "name": "Add a Subject Course",
            "title": "Create a Subject",
            "description": "Courses are subjects like 'Mathematics' or 'Physics'. Create one so you can eventually attach it to your Program.",
            "reference_document": "Course",
            "action": "Create Entry",
            "is_complete": 0,
            "is_skippable": 0
        },
        {
            "name": "Onboard Instructors",
            "title": "Add a Teacher",
            "description": "Teachers will need profiles to manage classes and students. Let's add an Instructor record.",
            "reference_document": "Instructor",
            "action": "Create Entry",
            "is_complete": 0,
            "is_skippable": 0
        }
    ]
    
    for step in steps:
        if not frappe.db.exists("Onboarding Step", step["name"]):
            try:
                frappe.get_doc(dict(doctype="Onboarding Step", **step)).insert(ignore_permissions=True)
            except Exception:
                pass

def create_module_onboarding():
    onboarding_name = "Vidyaan Institute Setup"
    
    if not frappe.db.exists("Module Onboarding", onboarding_name):
        try:
            doc = frappe.get_doc({
                "doctype": "Module Onboarding",
                "title": onboarding_name,
                "subtitle": "Follow these steps to configure your School ERP",
                "success_message": "Congratulations! Your Institute is ready to manage students and classes.",
                "module": "Vidyaan",
                "steps": [
                    {"step": "Create a Class Program"},
                    {"step": "Add a Subject Course"},
                    {"step": "Onboard Instructors"}
                ]
            })
            doc.insert(ignore_permissions=True)
        except Exception:
            pass
