"""Configure Website Settings for the Vidyaan admin shell.

Sets the favicon to the Education app logo, the brand HTML to a small
logo + "Vidyaan" wordmark, the home page to `vidyaan` (which redirects
to /vidyaan/dashboard), and adds the admin nav items as top bar items
so they also appear when desk pages reuse the standard navbar.
"""

import frappe


VIDYAAN_FAVICON = "/assets/education/edu-logo.svg"
VIDYAAN_BRAND_HTML = (
	'<img src="/assets/education/edu-logo.svg" '
	'style="width:24px;height:24px;vertical-align:middle;margin-right:6px;border-radius:6px;"/>'
	'<span style="font-weight:700;letter-spacing:.2px;">Vidyaan</span>'
)


def execute():
	if not frappe.db.exists("DocType", "Website Settings"):
		return

	ws = frappe.get_single("Website Settings")

	ws.favicon = VIDYAAN_FAVICON
	ws.brand_html = VIDYAAN_BRAND_HTML
	ws.home_page = "vidyaan"
	ws.app_logo = VIDYAAN_FAVICON
	ws.app_name = "Vidyaan"

	# Replace top bar items with the Vidyaan admin nav.
	desired = [
		("Dashboard",   "/vidyaan/dashboard"),
		("Students",    "/vidyaan/students"),
		("Programs",    "/vidyaan/programs"),
		("Admissions",  "/vidyaan/admissions"),
		("Attendance",  "/vidyaan/attendance"),
		("Fees",        "/vidyaan/fees"),
		("Settings",    "/vidyaan/settings"),
	]
	ws.set("top_bar_items", [])
	for label, url in desired:
		ws.append("top_bar_items", {"label": label, "url": url})

	ws.flags.ignore_permissions = True
	ws.flags.ignore_mandatory = True
	ws.save()
	frappe.db.commit()
