import frappe


def create_default_user():
    """Create or update the default Vidyaan admin user with all required roles."""
    email = "vidyaan@weloin.com"
    required_roles = ["Desk User", "System Manager", "System Administrator", "Institute Admin"]

    if not frappe.db.exists("User", email):
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": "Vidyaan",
            "last_name": "Administrator",
            "enabled": 1,
            "user_type": "System User",
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)
        user.new_password = "Vidyan@2026"
        user.save(ignore_permissions=True)

    # Always ensure correct roles (even if user already existed)
    user = frappe.get_doc("User", email)
    existing_roles = {r.role for r in user.roles}
    for role in required_roles:
        if role not in existing_roles and frappe.db.exists("Role", role):
            user.add_roles(role)
