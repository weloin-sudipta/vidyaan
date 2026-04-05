"""
Vidyaan Setup Wizard - Main Setup Orchestrator

This module handles the complete Vidyaan setup flow with proper stages:
1. Install Presets - Create default data structures
2. Setup Institute - Create company/institute with customizations
3. Create Institute Admin - Create admin user and set password
4. Setup Defaults - Configure global settings
5. Finalization - Mark setup as complete
"""

import frappe
from frappe import _
from frappe.utils.password import update_password

from .operations.install_fixtures import install_fixtures
from .operations.institute_setup import (
	create_institute,
	create_institute_admin_user,
	setup_institute_defaults,
)


def get_setup_stages(args=None):
	"""Get all setup stages for Vidyaan initialization.
	
	Args:
		args: Dictionary containing setup parameters:
			- institute_name: Name of the institute (company)
			- institute_abbr: Abbreviation for the institute
			- admin_email: Email of the admin user
			- admin_name: Full name of the admin user
			- admin_password: Password for the admin user
			- country: Country (default: India)
			- currency: Currency (default: INR)
	
	Returns:
		List of setup stage dictionaries with tasks
	"""
	if frappe.db.sql("select name from tabCompany"):
		# Setup already done, just finalize
		stages = [
			{
				"status": _("Finalizing Setup"),
				"fail_msg": _("Failed to finalize setup"),
				"tasks": [
					{
						"fn": finalize_setup,
						"args": args,
						"fail_msg": _("Failed to finalize setup"),
					}
				],
			}
		]
	else:
		stages = [
			{
				"status": _("Installing Presets"),
				"fail_msg": _("Failed to install presets"),
				"tasks": [
					{
						"fn": stage_install_fixtures,
						"args": args,
						"fail_msg": _("Failed to install presets"),
					}
				],
			},
			{
				"status": _("Setting up Institute"),
				"fail_msg": _("Failed to setup institute"),
				"tasks": [
					{
						"fn": stage_setup_institute,
						"args": args,
						"fail_msg": _("Failed to setup institute"),
					}
				],
			},
			{
				"status": _("Creating Institute Admin User"),
				"fail_msg": _("Failed to create admin user"),
				"tasks": [
					{
						"fn": stage_create_admin_user,
						"args": args,
						"fail_msg": _("Failed to create admin user"),
					}
				],
			},
			{
				"status": _("Configuring Defaults"),
				"fail_msg": _("Failed to configure defaults"),
				"tasks": [
					{
						"fn": stage_setup_defaults,
						"args": args,
						"fail_msg": _("Failed to configure defaults"),
					}
				],
			},
			{
				"status": _("Finalizing Setup"),
				"fail_msg": _("Failed to finalize setup"),
				"tasks": [
					{
						"fn": finalize_setup,
						"args": args,
						"fail_msg": _("Failed to finalize setup"),
					}
				],
			},
		]

	return stages


def stage_install_fixtures(args):
	"""Stage 1: Install default fixtures and data."""
	install_fixtures(args.get("country", "India"))


def stage_setup_institute(args):
	"""Stage 2: Setup the institute (company) with all customizations."""
	create_institute(args)


def stage_create_admin_user(args):
	"""Stage 3: Create institute admin user and set password."""
	create_institute_admin_user(args)


def stage_setup_defaults(args):
	"""Stage 4: Configure default settings for the institute."""
	setup_institute_defaults(args)


def finalize_setup(args):
	"""Stage 5: Mark setup as complete and prepare for use."""
	# Mark Vidyaan setup as complete
	frappe.defaults.set_global_default("vidyaan_setup_complete", 1)

	# Set default company
	institute_name = args.get("institute_name")
	if institute_name and frappe.db.exists("Company", institute_name):
		frappe.defaults.set_global_default("default_company", institute_name)

	# Mark Frappe + ERPNext setup wizard as complete
	if frappe.db.table_exists("Installed Application"):
		ss = frappe.get_single("System Settings")
		ss.setup_complete = 1
		ss.save(ignore_permissions=True)

		for app in frappe.get_all("Installed Application", pluck="app_name"):
			frappe.db.set_value(
				"Installed Application",
				{"app_name": app},
				"is_setup_complete",
				1,
			)

	frappe.db.commit()


def setup_complete(args=None):
	"""Run complete setup programmatically (for testing/automation).
	
	This function runs all setup stages without the UI wizard.
	"""
	if args is None:
		args = frappe._dict()

	stages = get_setup_stages(args)
	for stage in stages:
		for task in stage.get("tasks", []):
			fn = task.get("fn")
			task_args = task.get("args")
			if fn:
				fn(task_args)
