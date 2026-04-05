"""
Institute and Admin User Setup for Vidyaan.

This module handles creation of:
1. Institute (Company) with education-specific configuration
2. Institute Admin user with proper roles and password
3. Default settings for the institute
"""

import frappe
from frappe.utils.password import update_password


def create_institute(args):
	"""Create a new institute (Company) with Vidyaan configurations.
	
	Args:
		args: Dictionary containing:
			- institute_name: Name of the institute
			- institute_abbr: Optional abbreviation (auto-generated if not provided)
			- country: Country (default: India)
			- currency: Currency (default: INR)
	"""
	institute_name = args.get("institute_name")
	if not institute_name:
		frappe.throw("Institute name is required")

	# Check if company already exists
	if frappe.db.exists("Company", institute_name):
		return frappe.get_doc("Company", institute_name)

	abbr = args.get("institute_abbr") or _generate_unique_abbr(institute_name)
	country = args.get("country", "India")
	currency = args.get("currency", "INR")

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
	"""Create institute admin user with password.
	
	Args:
		args: Dictionary containing:
			- admin_email: Email of admin user
			- admin_name: Full name of admin user
			- admin_password: Password for admin user (will be set after creation)
	
	Returns:
		User document
	"""
	email = args.get("admin_email")
	full_name = args.get("admin_name", "Administrator")
	password = args.get("admin_password")

	if not email:
		frappe.throw("Admin email is required")

	# Parse name
	names = full_name.split(" ", 1) if full_name else ["Administrator"]
	first_name = names[0]
	last_name = names[1] if len(names) > 1 else ""

	# Check if user already exists
	if frappe.db.exists("User", email):
		user = frappe.get_doc("User", email)
		# Update name if provided and different
		if full_name and (user.first_name != first_name or user.last_name != last_name):
			user.first_name = first_name
			user.last_name = last_name
			user.full_name = full_name
	else:
		# Create new user
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

	# Ensure System Manager and Institute Admin roles exist
	_ensure_roles_exist()

	# Add roles to user
	user.add_roles("System Manager", "Institute Admin")
	user.save(ignore_permissions=True)
	frappe.db.commit()

	# Set password if provided
	if password:
		update_password(email, password)
		frappe.db.commit()

	return user


def setup_institute_defaults(args):
	"""Setup default settings for the institute.
	
	Args:
		args: Dictionary containing setup parameters
	"""
	institute_name = args.get("institute_name")
	country = args.get("country", "India")
	currency = args.get("currency", "INR")

	if not institute_name:
		return

	# Get or create Global Defaults
	if frappe.db.exists("Global Defaults", "Global Defaults"):
		global_defaults = frappe.get_doc("Global Defaults", "Global Defaults")
	else:
		global_defaults = frappe.new_doc("Global Defaults")
		global_defaults.name = "Global Defaults"

	# Update global defaults
	global_defaults.default_company = institute_name
	global_defaults.default_currency = currency
	global_defaults.country = country

	global_defaults.save(ignore_permissions=True)
	frappe.db.commit()

	# Enable the currency
	if frappe.db.exists("Currency", currency):
		frappe.db.set_value("Currency", currency, "enabled", 1)

	frappe.db.commit()


def _generate_unique_abbr(name):
	"""Generate a unique abbreviation for a company name.
	
	Args:
		name: Company name
	
	Returns:
		Unique abbreviation string
	"""
	# Try to create abbreviation from first letters
	abbr = "".join([c[0] for c in name.split() if c.isalnum()]).upper()

	# If no letters in name, use first 2 characters
	if not abbr:
		abbr = name[:2].upper()

	# Ensure abbreviation is unique
	base_abbr = abbr
	counter = 1
	while frappe.db.exists("Company", {"abbr": abbr}):
		abbr = f"{base_abbr}{counter}"
		counter += 1

	return abbr


def _ensure_roles_exist():
	"""Ensure Institute Admin and System Manager roles exist."""
	roles_to_create = ["Institute Admin", "System Manager"]

	for role_name in roles_to_create:
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc({
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": 1,
			}).insert(ignore_permissions=True)
