import frappe
from frappe import _


@frappe.whitelist()
def get_student_dashboard_data():
    """Proxy to student.get_student_dashboard_data for backward compat."""
    from vidyaan.api_folder.student import get_student_dashboard_data as _get
    return _get()


@frappe.whitelist()
def get_student_schedule():
    """Proxy to schedule.get_student_schedule for backward compat."""
    from vidyaan.api_folder.schedule import get_student_schedule as _get
    return _get()


@frappe.whitelist()
def get_holidays(year=None):
    """Proxy to holiday.get_holidays."""
    from vidyaan.api_folder.holiday import get_holidays as _get
    return _get(year=year)
