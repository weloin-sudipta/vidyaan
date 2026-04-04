import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user, _get_user_company


@frappe.whitelist()
def get_all_events():
    """Get school events. Uses native Frappe Event doctype."""
    company = _get_user_company()

    # Try Frappe's native Event doctype
    events = frappe.get_all(
        "Event",
        filters={
            "status": ["!=", "Cancelled"],
            "event_type": ["!=", "Private"]
        },
        fields=[
            "name", "subject as event_name", "starts_on as date",
            "starts_on", "ends_on", "description",
            "event_category", "event_type", "color"
        ],
        order_by="starts_on desc",
        limit=100
    )

    formatted = []
    tags_set = set()

    for e in events:
        tag = e.get("event_category") or "General"
        tags_set.add(tag)

        start_time = ""
        end_time = ""
        date = ""

        if e.starts_on:
            from datetime import datetime
            dt = e.starts_on if isinstance(e.starts_on, datetime) else datetime.strptime(str(e.starts_on), "%Y-%m-%d %H:%M:%S")
            date = dt.strftime("%Y-%m-%d")
            start_time = dt.strftime("%H:%M")

        if e.ends_on:
            dt_end = e.ends_on if isinstance(e.ends_on, datetime) else datetime.strptime(str(e.ends_on), "%Y-%m-%d %H:%M:%S")
            end_time = dt_end.strftime("%H:%M")

        formatted.append({
            "name": e.name,
            "event_name": e.event_name or "Untitled Event",
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "description": e.description or "",
            "tags": [tag],
            "room": "",
            "programs": [],
            "student_groups": []
        })

    return {
        "success": True,
        "events": formatted,
        "tags": list(tags_set)
    }
