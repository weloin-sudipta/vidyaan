import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_user_company


@frappe.whitelist()
def get_holidays(year=None):
    """Fetch holidays from the company's default holiday list."""
    company = _get_user_company()
    if not company:
        return []

    default_holiday_list = frappe.get_value("Company", company, "default_holiday_list")
    if not default_holiday_list:
        return []

    # Holiday List has a child table 'holidays' (Doctype 'Holiday')
    filters = [
        ["parent", "=", default_holiday_list],
        ["parenttype", "=", "Holiday List"]
    ]
    
    if year:
        filters.append(["holiday_date", ">=", f"{year}-01-01"])
        filters.append(["holiday_date", "<=", f"{year}-12-31"])

    holidays = frappe.get_all(
        "Holiday",
        filters=filters,
        fields=["holiday_date as date", "description as title"],
        order_by="holiday_date asc"
    )

    # Format for frontend consistency
    formatted_holidays = []
    for h in holidays:
        formatted_holidays.append({
            "date": str(h.date),
            "title": h.title,
            "type": "holiday",
            "icon": "fa fa-calendar"
        })

    return formatted_holidays
