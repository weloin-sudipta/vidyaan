import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user, _get_instructor_for_user, _get_user_company


@frappe.whitelist()
def get_study_materials(course=None, topic=None):
    """Get study materials (Articles) for the student's enrolled courses."""
    company = _get_user_company()

    filters = {}
    if company:
        filters["company"] = company

    # Article doesn't have a 'topic' field — relationship is through
    # Topic > Topic Content (child table) which links to Article
    # So we find articles via Topic Content child records

    if topic:
        # Get articles linked to this specific topic
        article_names = frappe.get_all(
            "Topic Content",
            filters={"parent": topic, "content_type": "Article"},
            pluck="content"
        )
        if not article_names:
            return []
        filters["name"] = ["in", article_names]
    elif course:
        # Get all topics for this course, then all articles in those topics
        topics = frappe.get_all(
            "Course Topic", filters={"parent": course}, pluck="topic"
        )
        if not topics:
            return []
        article_names = frappe.get_all(
            "Topic Content",
            filters={"parent": ["in", topics], "content_type": "Article"},
            pluck="content"
        )
        if not article_names:
            return []
        filters["name"] = ["in", article_names]

    articles = frappe.get_all(
        "Article",
        filters=filters,
        fields=["name", "title", "author", "content", "publish_date",
                "creation", "modified"],
        order_by="creation desc",
        limit=50
    )

    # Enrich with course/topic info
    for article in articles:
        # Find which topic this article belongs to via Topic Content
        topic_links = frappe.get_all(
            "Topic Content",
            filters={"content": article.name, "content_type": "Article"},
            pluck="parent",
            limit=1
        )
        topic_name = topic_links[0] if topic_links else ""
        article["topic"] = topic_name
        article["topic_name"] = frappe.db.get_value("Topic", topic_name, "topic_name") if topic_name else ""

        # Find course via Course Topic
        if topic_name:
            course_links = frappe.get_all(
                "Course Topic", filters={"topic": topic_name},
                pluck="parent", limit=1
            )
            article["course"] = course_links[0] if course_links else ""
            article["course_name"] = frappe.db.get_value("Course", article["course"], "course_name") if article["course"] else ""
        else:
            article["course"] = ""
            article["course_name"] = ""

        article["upload_date"] = str(article.creation)[:10] if article.creation else ""

        # Get file attachments
        attachments = frappe.get_all(
            "File",
            filters={"attached_to_doctype": "Article", "attached_to_name": article.name},
            fields=["file_url", "file_name", "file_size"],
            limit=5
        )
        article["attachments"] = attachments
        if attachments:
            article["file"] = attachments[0].get("file_url", "")
            article["file_type"] = _get_file_type(attachments[0].get("file_name", ""))
            article["file_size"] = _format_file_size(attachments[0].get("file_size", 0))
        else:
            article["file"] = None
            article["file_type"] = None
            article["file_size"] = None

        # Category from content or default
        article["category"] = "Lecture Notes"

    return articles


def _get_file_type(filename):
    """Get file extension type."""
    if not filename:
        return "Unknown"
    ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else "Unknown"
    return ext


def _format_file_size(size):
    """Format bytes to human readable."""
    if not size:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


@frappe.whitelist()
def get_materials_by_teacher():
    """Get study materials created by the logged-in instructor."""
    instructor = _get_instructor_for_user()
    if not instructor:
        return {"success": False, "materials": []}

    user = frappe.session.user
    user_name = frappe.db.get_value("User", user, "full_name") or user

    articles = frappe.get_all(
        "Article",
        filters={"author": user_name},
        fields=["name", "title", "author", "content",
                "creation", "modified"],
        order_by="creation desc"
    )

    for article in articles:
        topic_links = frappe.get_all(
            "Topic Content",
            filters={"content": article.name, "content_type": "Article"},
            pluck="parent", limit=1
        )
        topic_name = topic_links[0] if topic_links else ""
        article["topic"] = topic_name

        if topic_name:
            course_links = frappe.get_all(
                "Course Topic", filters={"topic": topic_name},
                pluck="parent", limit=1
            )
            article["course"] = course_links[0] if course_links else ""
        else:
            article["course"] = ""
        article["upload_date"] = str(article.creation)[:10] if article.creation else ""

    return {"success": True, "materials": articles}


@frappe.whitelist()
def create_study_material(title=None, course=None, topic=None, category=None,
                          upload_date=None, description=None):
    """Create a new Article (study material) and link it to a Topic."""
    if not title or not course:
        frappe.throw(_("Title and Course are required"))

    instructor = _get_instructor_for_user()
    company = _get_user_company()
    user_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user

    article = frappe.get_doc({
        "doctype": "Article",
        "title": title,
        "author": user_name,
        "content": description or "",
        "company": company or ""
    })
    article.insert()

    # Link article to topic if provided
    if topic and frappe.db.exists("Topic", topic):
        topic_doc = frappe.get_doc("Topic", topic)
        topic_doc.append("topic_content", {
            "content_type": "Article",
            "content": article.name,
        })
        topic_doc.save(ignore_permissions=True)

    # Handle file attachment
    if frappe.request and frappe.request.files.get("file"):
        file = frappe.request.files["file"]
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file.filename,
            "attached_to_doctype": "Article",
            "attached_to_name": article.name,
            "content": file.read(),
            "is_private": 1
        })
        file_doc.save(ignore_permissions=True)

    return {"success": True, "name": article.name}


@frappe.whitelist()
def update_study_material(name=None, title=None, course=None, topic=None,
                          category=None, upload_date=None, description=None):
    """Update an existing Article."""
    if not name:
        frappe.throw(_("Article name is required"))

    article = frappe.get_doc("Article", name)
    if title:
        article.title = title
    if description is not None:
        article.content = description
    article.save()

    # Handle file replacement
    if frappe.request and frappe.request.files.get("file"):
        file = frappe.request.files["file"]
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file.filename,
            "attached_to_doctype": "Article",
            "attached_to_name": article.name,
            "content": file.read(),
            "is_private": 1
        })
        file_doc.save(ignore_permissions=True)

    return {"success": True, "name": article.name}


@frappe.whitelist()
def delete_study_material(name=None):
    """Delete an Article."""
    if not name:
        frappe.throw(_("Article name is required"))

    if not frappe.db.exists("Article", name):
        frappe.throw(_("Article not found"))

    frappe.delete_doc("Article", name, ignore_permissions=True)
    return {"success": True}
