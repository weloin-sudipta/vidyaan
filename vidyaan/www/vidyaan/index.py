import frappe


def get_context(context):
	# /vidyaan → redirect based on session
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/vidyaan/dashboard"
	else:
		frappe.local.flags.redirect_location = "/vidyaan/dashboard"
	raise frappe.Redirect
