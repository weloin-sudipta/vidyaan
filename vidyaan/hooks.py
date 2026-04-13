app_name = "vidyaan"
app_title = "Vidyaan"
app_publisher = "Weloin"
app_description = "School erp system"
app_email = "bcasudipta@gmail.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["erpnext", "hrms", "education"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "vidyaan",
# 		"logo": "/assets/vidyaan/logo.png",
# 		"title": "Vidyaan",
# 		"route": "/vidyaan",
# 		"has_permission": "vidyaan.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vidyaan/css/vidyaan.css"
# app_include_js = "/assets/vidyaan/js/vidyaan.js"

# include js, css files in header of web template
web_include_css = "/assets/vidyaan/css/vidyaan_web.css"
web_include_js = "/assets/vidyaan/js/vidyaan_web.js"

# Website context overrides — favicon + brand for the public site.
website_context = {
	"favicon": "/assets/education/edu-logo.svg",
	"splash_image": "/assets/education/edu-logo.svg",
	"brand_html": '<img src="/assets/education/edu-logo.svg" style="width:24px;height:24px;vertical-align:middle;margin-right:6px;"/> Vidyaan',
}

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vidyaan/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "vidyaan/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
role_home_page = {
	"Institute Admin": "vidyaan/dashboard",
	"System Manager": "vidyaan/dashboard",
	"Administrator": "vidyaan/dashboard",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "vidyaan.utils.jinja_methods",
# 	"filters": "vidyaan.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "vidyaan.install.before_install"
after_install = "vidyaan.setup.install.after_install"

# Setup Wizard
# ------------
setup_wizard_requires = "assets/vidyaan/js/vidyaan_setup.js"
setup_wizard_stages = "vidyaan.setup.setup_stages.get_setup_stages"
setup_wizard_complete = "vidyaan.setup.setup_stages.on_setup_complete"

# Uninstallation
# ------------

# before_uninstall = "vidyaan.uninstall.before_uninstall"
# after_uninstall = "vidyaan.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vidyaan.utils.before_app_install"
# after_app_install = "vidyaan.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vidyaan.utils.before_app_uninstall"
# after_app_uninstall = "vidyaan.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vidyaan.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Assessment Result": {
		"validate": "vidyaan.events.validate_assessment_result",
		"before_submit": "vidyaan.events.validate_assessment_result",
	},
	"Assessment Plan": {
		"on_submit": "vidyaan.utils.create_assessment_publication"
	},
	"Program Enrollment": {
		"after_insert": "vidyaan.events.on_program_enrollment_created"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vidyaan.tasks.all"
# 	],
# 	"daily": [
# 		"vidyaan.tasks.daily"
# 	],
# 	"hourly": [
# 		"vidyaan.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vidyaan.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vidyaan.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "vidyaan.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"vidyaan.library_management.api.get_catalog": "vidyaan.library.api.get_catalog",
	"vidyaan.library_management.api.get_my_issues": "vidyaan.library.api.get_my_issues",
	"vidyaan.library_management.api.get_my_requests": "vidyaan.library.api.get_my_requests",
	"vidyaan.library_management.api.request_book": "vidyaan.library.api.request_book",
	"vidyaan.library_management.api.cancel_request": "vidyaan.library.api.cancel_request",
	"vidyaan.library_management.api.renew_book": "vidyaan.library.api.renew_book",
	"vidyaan.library_management.api.approve_renewal": "vidyaan.library.api.approve_renewal",
	"vidyaan.library_management.api.get_member_details": "vidyaan.library.api.get_member_details",
	"vidyaan.api_folder.library.get_book_recommendations": "vidyaan.library.api.get_book_recommendations",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vidyaan.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vidyaan.utils.before_request"]
# after_request = ["vidyaan.utils.after_request"]

# Job Events
# ----------
# before_job = ["vidyaan.utils.before_job"]
# after_job = ["vidyaan.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"vidyaan.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

extend_bootinfo = "vidyaan.utils.extend_bootinfo"
