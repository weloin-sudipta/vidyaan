"""
Vidyaan Setup Wizard Endpoint

Provides whitelisted methods for the Frappe setup wizard UI to call during setup.
This integrates Vidyaan's setup process with Frappe's UI framework.
"""

import json
import frappe
from frappe import _
from frappe.utils import validate_email_address

from .setup_stages import get_setup_stages, setup_complete
from .operations.institute_setup import (
	create_institute,
	create_institute_admin_user,
	setup_institute_defaults,
)


@frappe.whitelist()
def get_setup_data():
	"""Get available setup data for UI rendering.
	
	Returns:
		Dictionary containing:
		- setup_complete: Boolean indicating if setup is already done
		- countries: List of available countries
		- currencies: List of available currencies
	"""
	# Check if setup is already complete
	is_complete = frappe.db.get_value("Global Defaults", None, "setup_complete")

	return {
		"setup_complete": is_complete or frappe.defaults.get_global_default("vidyaan_setup_complete"),
		"countries": get_countries(),
		"currencies": get_currencies(),
	}


@frappe.whitelist()
def run_setup(setup_data):
	"""Run the complete Vidyaan setup with provided data.

	Args:
		setup_data: JSON string containing setup parameters:
			{
				"institute_name": "Institute Name",
				"institute_abbr": "IN",  # optional
				"admin_email": "admin@example.com",
				"admin_name": "Admin Name",
				"admin_password": "password",
				"country": "India",
				"currency": "INR"
			}

	Returns:
		Dictionary with setup result and user info
	"""
	try:
		# Parse setup data
		if isinstance(setup_data, str):
			data = json.loads(setup_data)
		else:
			data = setup_data

		# Validate required fields
		validate_setup_data(data)

		# Convert to frappe._dict for easier access
		args = frappe._dict(data)

		# Run complete setup
		setup_complete(args)

		# Prepare response
		return {
			"success": True,
			"message": _("Setup completed successfully"),
			"admin_email": data.get("admin_email"),
			"institute_name": data.get("institute_name"),
		}

	except Exception as e:
		frappe.log_error(title="Vidyaan Setup Error")
		return {
			"success": False,
			"message": str(e),
		}


@frappe.whitelist()
def validate_institute_name(institute_name):
	"""Validate that institute name is unique.
	
	Args:
		institute_name: Name to validate
	
	Returns:
		Dictionary with validation result
	"""
	if not institute_name:
		return {"valid": False, "message": _("Institute name is required")}

	if frappe.db.exists("Company", institute_name):
		return {"valid": False, "message": _("Institute with this name already exists")}

	return {"valid": True}


@frappe.whitelist()
def validate_admin_email(admin_email):
	"""Validate admin email format and uniqueness.
	
	Args:
		admin_email: Email to validate
	
	Returns:
		Dictionary with validation result
	"""
	if not admin_email:
		return {"valid": False, "message": _("Email is required")}

	# Validate email format
	try:
		validate_email_address(admin_email)
	except frappe.ValidationError:
		return {"valid": False, "message": _("Invalid email format")}

	return {"valid": True}


def validate_setup_data(data):
	"""Validate all setup data.
	
	Args:
		data: Dictionary containing setup parameters
	
	Raises:
		frappe.ValidationError: If any validation fails
	"""
	# Validate institute name
	institute_name = data.get("institute_name", "").strip()
	if not institute_name:
		frappe.throw(_("Institute name is required"))

	if frappe.db.exists("Company", institute_name):
		frappe.throw(_("Institute with this name already exists"))

	# Validate abbreviation if provided
	abbr = data.get("institute_abbr", "").strip()
	if abbr and frappe.db.exists("Company", {"abbr": abbr}):
		frappe.throw(_("Abbreviation is already in use"))

	# Validate admin email
	admin_email = data.get("admin_email", "").strip()
	if not admin_email:
		frappe.throw(_("Admin email is required"))

	try:
		validate_email_address(admin_email)
	except frappe.ValidationError:
		frappe.throw(_("Invalid admin email format"))

	# Validate password
	password = data.get("admin_password", "")
	if not password:
		frappe.throw(_("Admin password is required"))

	if len(password) < 8:
		frappe.throw(_("Password must be at least 8 characters long"))

	# Reject reserved usernames
	if admin_email.lower() in ("administrator", "guest"):
		frappe.throw(_("'{0}' cannot be used as an admin email").format(admin_email))

	# Validate country and currency if provided
	country = data.get("country", "India")
	if country and not frappe.db.exists("Country", country):
		frappe.throw(_("Selected country {0} does not exist").format(country))

	currency = data.get("currency", "INR")
	if currency and not frappe.db.exists("Currency", currency):
		frappe.throw(_("Selected currency {0} does not exist").format(currency))


def get_countries():
	"""Get list of available countries.
	
	Returns:
		List of country names
	"""
	return frappe.get_list("Country", pluck="country_name") or ["India"]


def get_currencies():
	"""Get list of available currencies.
	
	Returns:
		List of currency codes
	"""
	return frappe.get_list("Currency", filters={"enabled": 1}, pluck="name") or ["INR"]
