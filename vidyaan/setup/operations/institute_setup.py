"""
Institute and Admin User Setup for Vidyaan.

Creates:
1. Institute (Company) with education-specific configuration
2. Institute Admin user with ONLY Vidyaan module access
3. Default settings for the institute
"""

import frappe
from frappe import _
from frappe.utils.password import update_password


# Modules the Institute Admin is allowed to see.
# Everything else is blocked via the User's block_modules table.
ALLOWED_MODULES = {"Vidyaan", "Library", "Education"}


def create_institute(args):
	"""Create a new institute (Company).

	Args:
		args: dict with institute_name, institute_abbr (optional),
		      country (default India), currency (default INR)
	"""
	institute_name = (args.get("institute_name") or "").strip()
	if not institute_name:
		frappe.throw(_("Institute name is required"))

	if frappe.db.exists("Company", institute_name):
		return frappe.get_doc("Company", institute_name)

	abbr = (args.get("institute_abbr") or "").strip() or _generate_unique_abbr(institute_name)
	country = args.get("country") or "India"
	currency = args.get("currency") or "INR"

	company = frappe.get_doc({
		"doctype": "Company",
		"company_name": institute_name,
		"abbr": abbr,
		"default_currency": currency,
		"country": country,
		"create_chart_of_accounts_based_on": "Standard Template",
		"chart_of_accounts": "Standard",
	})
	company.insert(ignore_permissions=True)
	frappe.db.commit()
	return company


def create_institute_admin_user(args):
	"""Create institute admin user with Vidyaan-only access.

	The user receives ONLY the 'Institute Admin' role — NOT System Manager.
	All modules except Vidyaan, Library, and Education are blocked.

	Args:
		args: dict with admin_email, admin_name, admin_password

	Returns:
		User document
	"""
	email = (args.get("admin_email") or "").strip()
	full_name = (args.get("admin_name") or "Administrator").strip()
	password = args.get("admin_password") or ""

	if not email:
		frappe.throw(_("Admin email is required"))

	# Reject reserved usernames
	if email.lower() in ("administrator", "guest"):
		frappe.throw(_("'{0}' cannot be used as an admin email").format(email))

	# Validate password strength
	if len(password) < 8:
		frappe.throw(_("Password must be at least 8 characters long"))

	# Parse name
	parts = full_name.split(" ", 1)
	first_name = parts[0]
	last_name = parts[1] if len(parts) > 1 else ""

	# Ensure Institute Admin role exists
	_ensure_role_exists("Institute Admin")

	if frappe.db.exists("User", email):
		user = frappe.get_doc("User", email)
		user.first_name = first_name
		user.last_name = last_name
		user.full_name = full_name
		user.enabled = 1
		user.user_type = "System User"
	else:
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"last_name": last_name,
			"full_name": full_name,
			"enabled": 1,
			"user_type": "System User",
			"send_welcome_email": 0,
		})
		user.insert(ignore_permissions=True)

	# Clear existing roles and assign ONLY Institute Admin
	user.set("roles", [])
	user.add_roles("Institute Admin")

	# Block all modules except the allowed ones
	_set_module_restrictions(user)

	user.save(ignore_permissions=True)
	frappe.db.commit()

	# Set password
	if password:
		update_password(email, password)
		frappe.db.commit()

	return user


def setup_institute_defaults(args):
	"""Configure global defaults for the institute."""
	institute_name = (args.get("institute_name") or "").strip()
	country = args.get("country") or "India"
	currency = args.get("currency") or "INR"

	if not institute_name:
		return

	if frappe.db.exists("Global Defaults", "Global Defaults"):
		global_defaults = frappe.get_doc("Global Defaults", "Global Defaults")
	else:
		global_defaults = frappe.new_doc("Global Defaults")
		global_defaults.name = "Global Defaults"

	global_defaults.default_company = institute_name
	global_defaults.default_currency = currency
	global_defaults.country = country
	global_defaults.save(ignore_permissions=True)

	# Enable currency
	if frappe.db.exists("Currency", currency):
		frappe.db.set_value("Currency", currency, "enabled", 1)

	frappe.db.commit()


def _set_module_restrictions(user):
	"""Block all modules except ALLOWED_MODULES on the user document.

	This ensures the Institute Admin sidebar only shows Vidyaan,
	Library, and Education modules.
	"""
	all_modules = frappe.get_all("Module Def", pluck="name")
	user.set("block_modules", [])
	for module in all_modules:
		if module not in ALLOWED_MODULES:
			user.append("block_modules", {"module": module})


def _generate_unique_abbr(name):
	"""Generate a unique Company abbreviation from the institute name."""
	abbr = "".join(c[0] for c in name.split() if c and c[0].isalpha()).upper()
	if not abbr:
		abbr = name[:2].upper()

	base_abbr = abbr
	counter = 1
	while frappe.db.exists("Company", {"abbr": abbr}):
		abbr = f"{base_abbr}{counter}"
		counter += 1

	return abbr


def _ensure_role_exists(role_name):
	"""Create a role if it doesn't already exist."""
	if not frappe.db.exists("Role", role_name):
		frappe.get_doc({
			"doctype": "Role",
			"role_name": role_name,
			"desk_access": 1,
		}).insert(ignore_permissions=True)
