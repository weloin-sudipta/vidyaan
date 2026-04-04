import frappe
from frappe import _


@frappe.whitelist()
def get_approved_notices():
    """Get all approved publications (notices, news, announcements)."""
    publications = frappe.get_all(
        "Publication",
        filters={"status": "Approved", "docstatus": 1},
        fields=[
            "name", "title", "type", "content", "publish_date",
            "target_type", "target_student_group", "featured_image",
            "creation", "modified"
        ],
        order_by="publish_date desc, creation desc"
    )

    notices = []
    news = []
    pin_notices = []
    tags = ["All"]

    for pub in publications:
        # Strip HTML tags for description preview
        import re
        plain_text = re.sub(r'<[^>]+>', '', pub.content or '')
        description = plain_text[:200].strip()

        item = {
            "name": pub.name,
            "id": pub.name,
            "title": pub.title,
            "type": pub.type,
            "content": pub.content or "",
            "description": description,
            "date": str(pub.publish_date) if pub.publish_date else str(pub.creation)[:10],
            "category": pub.type,
            "target_type": pub.target_type or "",
            "target_student_group": pub.target_student_group or "",
            "featured_image": pub.featured_image or "",
            "slug": pub.name,
            "icon": "fa-bullhorn" if pub.type == "Notice" else ("fa-newspaper-o" if pub.type == "News" else "fa-bell"),
        }

        if pub.type == "News":
            news.append(item)
        elif pub.type == "Notice":
            notices.append(item)
        else:
            notices.append(item)

        if pub.type not in tags:
            tags.append(pub.type)

    return {
        "pinNotices": pin_notices,
        "notices": notices,
        "news": news,
        "tags": tags,
        "topics": []
    }


@frappe.whitelist()
def get_notice(slug=None):
    """Get a single publication by name."""
    if not slug:
        frappe.throw(_("Slug is required"))

    if not frappe.db.exists("Publication", slug):
        frappe.throw(_("Notice not found"), frappe.DoesNotExistError)

    pub = frappe.get_doc("Publication", slug)

    return {
        "name": pub.name,
        "title": pub.title,
        "type": pub.type,
        "content": pub.content or "",
        "date": str(pub.publish_date) if pub.publish_date else str(pub.creation)[:10],
        "category": pub.type,
        "target_type": pub.target_type or "",
        "target_student_group": pub.target_student_group or "",
        "featured_image": pub.featured_image or "",
        "status": pub.status or "",
        "slug": pub.name
    }
