"""
Vidyaan Setup Wizard — Backend Stages

Hooked via `setup_wizard_stages` in hooks.py. Frappe calls get_setup_stages(args)
and merges the returned stages with those from other apps.

Stages:
1. Create Institute (Company)
2. Create Institute Admin user (restricted to Vidyaan module)
3. Configure defaults
"""

import frappe
from frappe import _

from .operations.institute_setup import (
	create_institute,
	create_institute_admin_user,
	setup_institute_defaults,
)


def get_setup_stages(args=None):
	"""Return Vidyaan setup stages for the Frappe setup wizard.

	Called by Frappe's setup_wizard_stages hook. Receives the merged
	form values from all slides (Frappe welcome + Vidyaan institute).
	"""
	if frappe.db.sql("select name from tabCompany"):
		# A company already exists — nothing to do on our end.
		return []

	return [
		{
			"status": _("Setting up Institute"),
			"fail_msg": _("Failed to create institute"),
			"tasks": [
				{
					"fn": stage_setup_institute,
					"args": args,
					"fail_msg": _("Failed to create institute"),
				}
			],
		},
		{
			"status": _("Creating Institute Admin"),
			"fail_msg": _("Failed to create admin user"),
			"tasks": [
				{
					"fn": stage_create_admin,
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
	]


def stage_setup_institute(args):
	"""Create the institute (Company)."""
	create_institute(args)


def stage_create_admin(args):
	"""Create the institute admin user with Vidyaan-only access."""
	create_institute_admin_user(args)


def stage_setup_defaults(args):
	"""Set global defaults for the institute."""
	setup_institute_defaults(args)


def on_setup_complete(args):
	"""Post-setup hook (setup_wizard_complete).

	Runs after all stages from all apps have finished. Marks Vidyaan
	setup as complete and logs in as the new admin.
	"""
	frappe.defaults.set_global_default("vidyaan_setup_complete", 1)

	institute_name = args.get("institute_name")
	if institute_name and frappe.db.exists("Company", institute_name):
		frappe.defaults.set_global_default("default_company", institute_name)

	# Log in as the newly created admin
	admin_email = args.get("admin_email")
	if admin_email and hasattr(frappe.local, "login_manager"):
		frappe.local.login_manager.login_as(admin_email)


def setup_complete(args=None):
	"""Run complete setup programmatically (for testing / bench commands)."""
	if args is None:
		args = frappe._dict()

	stages = get_setup_stages(args)
	for stage in stages:
		for task in stage.get("tasks", []):
			fn = task.get("fn")
			if fn:
				fn(task.get("args"))

	on_setup_complete(args)
