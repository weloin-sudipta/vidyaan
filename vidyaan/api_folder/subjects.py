import frappe
from frappe import _
from vidyaan.api_folder.profile import _get_student_for_user, _get_user_company


@frappe.whitelist()
def get_program():
    """Get the student's enrolled program with courses and topics."""
    student = _get_student_for_user()
    if not student:
        return None

    # Get active enrollment
    enrollment = frappe.get_all(
        "Program Enrollment",
        filters={"student": student.name, "docstatus": 1},
        fields=["program", "academic_year"],
        order_by="creation desc",
        limit=1
    )
    if not enrollment:
        return None

    program_name = enrollment[0].program
    program = frappe.get_doc("Program", program_name)

    # Build courses with topics
    courses = []
    for pc in program.courses:
        course = frappe.get_doc("Course", pc.course)
        topics = []

        for ct in (course.topics or []):
            topic_doc = frappe.get_doc("Topic", ct.topic)

            # Get articles linked to this topic via Topic Content child table
            article_names = frappe.get_all(
                "Topic Content",
                filters={"parent": topic_doc.name, "content_type": "Article"},
                pluck="content"
            )
            articles = []
            if article_names:
                articles = frappe.get_all(
                    "Article",
                    filters={"name": ["in", article_names]},
                    fields=["name", "title", "author", "content"],
                    limit=20
                )

            topics.append({
                "name": topic_doc.name,
                "topic_name": topic_doc.topic_name,
                "articles": articles
            })

        courses.append({
            "name": course.name,
            "course_name": course.course_name,
            "course_id": course.name,
            "topics": topics
        })

    return {
        "program": program_name,
        "program_name": program.program_name,
        "academic_year": enrollment[0].academic_year or "",
        "courses": courses
    }
