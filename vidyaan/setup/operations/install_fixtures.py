"""
Install default fixtures and data for Vidyaan setup.

This module creates the basic data structures needed for Vidyaan to function,
including countries, currencies, and other ERPNext/Education defaults.
"""

import frappe
from frappe import _
from frappe.desk.page.setup_wizard.setup_wizard import make_records


def install_fixtures(country=None):
	"""Install basic fixtures for Vidyaan.
	
	Args:
		country: Country name (default: India)
	"""
	if country is None:
		country = "India"

	records = [
		# Ensure at least an empty Address Template exists for this Country
		{"doctype": "Address Template", "country": country},
	]

	make_records(records)

	# Ensure country exists
	if not frappe.db.exists("Country", country):
		frappe.get_doc({
			"doctype": "Country",
			"country_name": country,
			"code": "in" if country == "India" else country[:2].lower(),
		}).insert(ignore_permissions=True)

	# Ensure INR currency exists
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

	# Enable the currency
	frappe.db.set_value("Currency", "INR", "enabled", 1)
