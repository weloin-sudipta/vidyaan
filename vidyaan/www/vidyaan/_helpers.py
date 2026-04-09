"""Shared helpers for Vidyaan website pages."""

import frappe
from frappe import _

ALLOWED_ROLES = {"Administrator", "System Manager", "Institute Admin"}


def guard(context):
	"""Reject unauthenticated users and users without an admin role.

	Sets the standard Frappe context flags so the page redirects/raises
	the right way. Should be the first call in every page's get_context.
	"""
	user = frappe.session.user

	if user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + frappe.local.request.path
		raise frappe.Redirect

	roles = set(frappe.get_roles(user))
	if user != "Administrator" and not (roles & ALLOWED_ROLES):
		frappe.throw(_("You are not permitted to access the Vidyaan admin panel."), frappe.PermissionError)

	context.no_cache = 1
	context.show_sidebar = False

	# Pre-compute user display fields — Jinja sandbox doesn't expose
	# frappe.utils.get_fullname, so we set them on context instead.
	full_name = frappe.db.get_value("User", user, "full_name") or user
	context.vd_user = user
	context.vd_user_fullname = full_name
	context.vd_user_initial = (full_name or user or "?")[0].upper()


def safe_count(doctype, filters=None):
	"""frappe.db.count that returns 0 if the doctype is not installed."""
	try:
		return frappe.db.count(doctype, filters or {})
	except Exception:
		return 0


def safe_get_list(doctype, **kwargs):
	try:
		return frappe.get_all(doctype, **kwargs)
	except Exception:
		return []
