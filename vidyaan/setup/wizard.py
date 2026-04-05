import frappe
from frappe.utils.password import update_password

# Import new setup functions
from .setup_stages import get_setup_stages, setup_complete as setup_complete_stages
from .operations.institute_setup import (
	create_institute,
	create_institute_admin_user,
	setup_institute_defaults,
	_generate_unique_abbr,
)


@frappe.whitelist()
def complete_setup(institute_name, admin_email=None, admin_password=None):
	"""Complete Vidyaan setup with institute information.
	
	Args:
		institute_name: Name of the institute
		admin_email: Admin email (optional)
		admin_password: Admin password (optional)
	
	Returns:
		True on success
	"""
	_ensure_country_and_currency()
	
	# Use new setup system if admin details provided
	if admin_email and admin_password:
		args = frappe._dict({
			"institute_name": institute_name,
			"admin_email": admin_email,
			"admin_name": admin_email.split("@")[0],
			"admin_password": admin_password,
			"country": "India",
			"currency": "INR",
		})
		setup_complete_stages(args)
	else:
		# Legacy setup - just create company
		create_company(institute_name)

		# Mark vidyaan setup as complete
		frappe.defaults.set_global_default("vidyaan_setup_complete", 1)

		# Set default company and country in Global Defaults
		frappe.defaults.set_global_default("default_company", institute_name)
		if frappe.db.exists("Global Defaults", "Global Defaults"):
			frappe.db.set_value("Global Defaults", None, "default_company", institute_name)
			frappe.db.set_value("Global Defaults", None, "country", "India")

		# Mark Frappe + ERPNext setup wizard as complete so their wizards don't show
		_mark_setup_wizard_complete()

		frappe.db.commit()

	return True


def _ensure_country_and_currency():
	"""Ensure the default Country and Currency records exist before company creation."""
	if not frappe.db.exists("Country", "India"):
		frappe.get_doc({"doctype": "Country", "country_name": "India", "code": "in"}).insert(ignore_permissions=True)

	if not frappe.db.exists("Currency", "INR"):
		frappe.get_doc({
			"doctype": "Currency",
			"currency_name": "INR",
			"symbol": "₹",
			"fraction": "Paise",
			"fraction_units": 100,
			"number_format": "#,##,###.##",
			"smallest_currency_fraction_value": 0.01,
			"enabled": 1,
		}).insert(ignore_permissions=True)


def _mark_setup_wizard_complete():
	"""Mark all installed apps as setup-complete in Frappe's Installed Application table."""
	if not frappe.db.table_exists("Installed Application"):
		return

	# Set system settings setup_complete flag
	ss = frappe.get_single("System Settings")
	ss.setup_complete = 1
	ss.save(ignore_permissions=True)

	# Mark each installed app as setup complete
	for app in frappe.get_all("Installed Application", pluck="app_name"):
		frappe.db.set_value("Installed Application", {"app_name": app}, "is_setup_complete", 1)


def _generate_unique_abbr(name):
	"""Generate a unique abbreviation for a company name (deprecated - use institute_setup version)."""
	abbr = "".join([c[0] for c in name.split() if c.isalnum()]).upper()
	if not abbr:
		abbr = name[:2].upper()

	# Ensure abbreviation is unique
	base_abbr = abbr
	counter = 1
	while frappe.db.exists("Company", {"abbr": abbr}):
		abbr = f"{base_abbr}{counter}"
		counter += 1

	return abbr


def create_company(name):
	"""Create a company (institute) - for backward compatibility."""
	if frappe.db.exists("Company", name):
		return frappe.get_doc("Company", name)

	abbr = _generate_unique_abbr(name)

	company = frappe.get_doc({
		"doctype": "Company",
		"company_name": name,
		"abbr": abbr,
		"default_currency": "INR",
		"country": "India",
		"create_chart_of_accounts_based_on": "Standard Template",
		"chart_of_accounts": "Standard",
	})
	company.insert(ignore_permissions=True)
	return company


def create_admin_user(email, first_name, password):
	"""Create an admin user - for backward compatibility."""
	if not frappe.db.exists("User", email):
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"send_welcome_email": 0,
			"enabled": 1,
			"user_type": "System User",
		})
		user.insert(ignore_permissions=True)
	else:
		user = frappe.get_doc("User", email)

	update_password(email, password)

	roles = ["System Manager", "Institute Admin"]
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)
		user.add_roles(role)

	user.save(ignore_permissions=True)
	return user
