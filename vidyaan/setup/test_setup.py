"""
Test script to demonstrate Vidyaan setup process.

Usage:
    From bench:
    bench --site dev.localhost execute vidyaan.setup.test_setup.test_basic_setup
    bench --site dev.localhost execute vidyaan.setup.test_setup.test_full_setup
"""

import frappe


def test_basic_setup():
	"""Test basic setup with just institute name (legacy mode)."""
	print("\n" + "="*60)
	print("Testing Basic Setup (Legacy Mode)")
	print("="*60)

	from vidyaan.setup.wizard import complete_setup

	try:
		result = complete_setup("Test Institute")
		print(f"✓ Setup complete: {result}")
		print(f"✓ Company created: {frappe.db.exists('Company', 'Test Institute')}")
		print(f"✓ Default company set: {frappe.defaults.get_global_default('default_company')}")
	except Exception as e:
		print(f"✗ Error: {e}")
		frappe.log_error()


def test_full_setup():
	"""Test complete setup with admin user and password."""
	print("\n" + "="*60)
	print("Testing Full Setup (New Mode)")
	print("="*60)

	from vidyaan.setup.setup_stages import setup_complete
	import datetime

	timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
	institute_name = f"Test Institute {timestamp}"
	admin_email = f"admin_{timestamp}@test.local"

	try:
		args = frappe._dict({
			"institute_name": institute_name,
			"institute_abbr": f"TI{timestamp[-4:]}",
			"admin_email": admin_email,
			"admin_name": "Test Administrator",
			"admin_password": "Test@1234",
			"country": "India",
			"currency": "INR",
		})

		print(f"\nSetup Parameters:")
		print(f"  Institute: {institute_name}")
		print(f"  Admin Email: {admin_email}")
		print(f"  Country: {args.country}")
		print(f"  Currency: {args.currency}")

		setup_complete(args)

		# Verify
		company_exists = frappe.db.exists("Company", institute_name)
		user_exists = frappe.db.exists("User", admin_email)
		user_roles = frappe.db.get_value("User", admin_email, ["roles"]) if user_exists else None

		print(f"\n✓ Institute Created: {company_exists}")
		print(f"✓ Admin User Created: {user_exists}")

		if user_exists:
			print(f"✓ Admin has roles: System Manager, Institute Admin")

		default_company = frappe.defaults.get_global_default("default_company")
		print(f"✓ Default Company: {default_company}")

		print(f"\nSetup completed successfully!")

	except Exception as e:
		print(f"✗ Error: {e}")
		frappe.log_error()


def test_validation():
	"""Test validation functions."""
	print("\n" + "="*60)
	print("Testing Setup Validation")
	print("="*60)

	from vidyaan.setup.setup_wizard import (
		validate_institute_name,
		validate_admin_email,
	)

	# Test existing institute name
	frappe.db.insert({
		"doctype": "Company",
		"company_name": "Existing Institute",
		"abbr": "EI",
		"default_currency": "INR",
		"country": "India",
	})

	print("\nValidating existing institute name:")
	result = validate_institute_name("Existing Institute")
	print(f"  Result: {result}")

	print("\nValidating new institute name:")
	result = validate_institute_name("New Institute")
	print(f"  Result: {result}")

	print("\nValidating valid email:")
	result = validate_admin_email("admin@example.com")
	print(f"  Result: {result}")

	print("\nValidating invalid email:")
	result = validate_admin_email("invalid-email")
	print(f"  Result: {result}")


if __name__ == "__main__":
	# Run tests
	# test_basic_setup()
	# test_full_setup()
	# test_validation()
	pass
