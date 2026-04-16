import frappe
from frappe import _
from frappe.utils import now_datetime, today, getdate
from vidyaan.api_folder.profile import (
	_get_student_for_user,
	_get_instructor_for_user,
	_get_user_company,
)


# ═══════════════════════════════════════════════════════════════════════════
# NEW ASSIGNMENT SYSTEM  (Assignment DocType)
# ═══════════════════════════════════════════════════════════════════════════


# ─── Internal helpers ────────────────────────────────────────────────────


def _require_instructor():
	"""Return the Instructor record for the current user, or throw."""
	instructor = _get_instructor_for_user()
	if not instructor:
		frappe.throw(_("No Instructor record found for the current user."), frappe.PermissionError)
	return instructor


def _require_student():
	"""Return the Student record for the current user, or throw."""
	student = _get_student_for_user()
	if not student:
		frappe.throw(_("No Student record found for the current user."), frappe.PermissionError)
	return student


def _check_instructor_owns(assignment_doc, instructor):
	"""Throw PermissionError if instructor does not own the assignment."""
	if assignment_doc.instructor != instructor.name:
		frappe.throw(
			_("You do not have permission to modify Assignment '{0}'.").format(assignment_doc.name),
			frappe.PermissionError,
		)


def _validate_comment_access(doc, student_id=None):
	"""Validate that the current user has permission to comment on this assignment.

	- Teachers: Must own the assignment.
	- Students: Must be enrolled in the assignment and only access their own thread.
	            Cannot comment if assignment is Closed.
	"""
	instructor = _get_instructor_for_user()
	student = _get_student_for_user()

	if instructor:
		_check_instructor_owns(doc, instructor)
		return instructor

	if student:
		# Check enrollment in the doc.submissions child table
		enrolled = False
		for s in doc.submissions or []:
			if s.student == student.name:
				enrolled = True
				break

		if not enrolled:
			frappe.throw(_("You are not enrolled in this assignment."), frappe.PermissionError)

		if student_id and student_id != student.name:
			frappe.throw(_("You can only access your own conversation."), frappe.PermissionError)

		if doc.status == "Closed":
			frappe.throw(_("Assignment is closed. No more messages allowed."), frappe.ValidationError)

		return student

	frappe.throw(_("You do not have permission to access these messages."), frappe.PermissionError)


def _validate_comment_access(doc, student_id=None):
	"""Validate that the current user has permission to comment on this assignment.

	- Teachers: Must own the assignment.
	- Students: Must be enrolled in the assignment and only access their own thread.
	            Cannot comment if assignment is Closed.
	"""
	instructor = _get_instructor_for_user()
	student = _get_student_for_user()

	if instructor:
		_check_instructor_owns(doc, instructor)
		return instructor

	if student:
		# Check enrollment in the doc.submissions child table
		enrolled = False
		for s in doc.submissions or []:
			if s.student == student.name:
				enrolled = True
				break

		if not enrolled:
			frappe.throw(_("You are not enrolled in this assignment."), frappe.PermissionError)

		if student_id and student_id != student.name:
			frappe.throw(_("You can only access your own conversation."), frappe.PermissionError)

		if doc.status == "Closed":
			frappe.throw(_("Assignment is closed. No more messages allowed."), frappe.ValidationError)

		return student

	frappe.throw(_("You do not have permission to access these messages."), frappe.PermissionError)


def _resolve_target_groups(assign_to, student_groups_list, course, instructor):
	"""Return a validated list of Student Group names for the assignment.

	assign_to: "All Enrolled" | "Specific Groups"
	student_groups_list: list of names (used only for Specific Groups)
	"""
	if assign_to == "All Enrolled":
		groups = get_instructor_student_groups(course=course)
		names = [g["name"] if isinstance(g, dict) else g.name for g in groups]
		if not names:
			frappe.throw(
				_(
					"No student groups found for course '{0}'. "
					"Open the Course in Frappe Desk and confirm you are mapped to it as an "
					"instructor (Instructor → Courses), AND that the course is part of a "
					"Program with an active Student Group. Alternatively switch to "
					"'Specific Groups' and pick groups manually."
				).format(course)
			)
		return names
	else:
		# Specific Groups
		if not student_groups_list:
			frappe.throw(_("At least one Student Group is required when 'Assign To' is 'Specific Groups'."))
		validated = []
		for sg in student_groups_list:
			if not frappe.db.exists("Student Group", sg):
				frappe.throw(_("Student Group '{0}' not found.").format(sg))
			validated.append(sg)
		return validated


# ─── Instructor: create / manage ────────────────────────────────────────


@frappe.whitelist()
def create_assignment(data=None):
	"""Create a new Assignment document (status remains Draft).

	data keys: title, course, program, academic_year, topic, due_date, max_score, assign_to,
	           student_groups (list), description, assignment_file
	Returns: {success, name}
	"""
	import json

	if not data:
		frappe.throw(_("No data provided."))
	if isinstance(data, str):
		data = json.loads(data)

	instructor = _require_instructor()

	title = (data.get("title") or "").strip()
	course = (data.get("course") or "").strip()
	due_date = data.get("due_date") or ""
	max_score = float(data.get("max_score") or 100)
	assign_to = (data.get("assign_to") or "All Enrolled").strip()
	student_groups_list = data.get("student_groups") or []
	description = data.get("description") or ""
	assignment_file = data.get("assignment_file") or ""
	topic = data.get("topic") or None
	academic_year = data.get("academic_year") or None
	program = data.get("program") or None

	if not title:
		frappe.throw(_("Title is required."))
	if not course:
		frappe.throw(_("Course is required."))
	if not frappe.db.exists("Course", course):
		frappe.throw(_("Course '{0}' not found.").format(course))
	if not due_date:
		frappe.throw(_("Due Date is required."))

	target_group_names = _resolve_target_groups(assign_to, student_groups_list, course, instructor)

	target_rows = [{"student_group": sg} for sg in target_group_names]

	doc = frappe.get_doc(
		{
			"doctype": "Assignment",
			"title": title,
			"course": course,
			"program": program,
			"academic_year": academic_year,
			"topic": topic,
			"instructor": instructor.name,
			"due_date": due_date,
			"max_score": max_score,
			"assign_to": assign_to,
			"description": description,
			"assignment_file": assignment_file,
			"status": "Draft",
			"target_groups": target_rows,
		}
	)
	doc.insert(ignore_permissions=False)

	return {"success": True, "name": doc.name}


@frappe.whitelist()
def publish_assignment(name=None):
	"""Publish a Draft assignment and populate the submissions child table.

	For each target group, fetches all active Student Group Student rows and
	appends one Assignment Submission row per unique student.
	Returns: {success, name, submission_count}
	"""
	if not name:
		frappe.throw(_("Assignment name is required."))

	instructor = _require_instructor()
	doc = frappe.get_doc("Assignment", name)
	_check_instructor_owns(doc, instructor)

	# Idempotent: already published
	if doc.status == "Published":
		submission_count = len(doc.submissions or [])
		return {"success": True, "name": doc.name, "submission_count": submission_count}

	if doc.status == "Closed":
		frappe.throw(_("Cannot publish a Closed assignment."))

	# Collect unique students across all target groups
	seen_students = set()
	new_rows = []

	for tg_row in doc.target_groups or []:
		sg = tg_row.student_group
		if not sg:
			continue
		members = frappe.get_all(
			"Student Group Student", filters={"parent": sg, "active": 1}, fields=["student"]
		)
		for m in members:
			if m.student and m.student not in seen_students:
				seen_students.add(m.student)
				new_rows.append(
					{
						"student": m.student,
						"student_group": sg,
						"status": "Pending",
					}
				)

	# Append rows only for students not already present
	existing_students = {r.student for r in (doc.submissions or [])}
	for row in new_rows:
		if row["student"] not in existing_students:
			doc.append("submissions", row)

	doc.status = "Published"
	if not doc.published_on:
		doc.published_on = now_datetime()

	doc.save(ignore_permissions=True)

	return {
		"success": True,
		"name": doc.name,
		"submission_count": len([r for r in doc.submissions if r.student]),
	}


@frappe.whitelist()
def update_assignment(name=None, data=None):
	"""Update a Draft assignment's editable fields.

	Only allowed when status == "Draft". Owner instructor only.
	Returns: {success, name}
	"""
	import json

	if not name:
		frappe.throw(_("Assignment name is required."))
	if not data:
		frappe.throw(_("No data provided."))
	if isinstance(data, str):
		data = json.loads(data)

	instructor = _require_instructor()
	doc = frappe.get_doc("Assignment", name)
	_check_instructor_owns(doc, instructor)

	if doc.status != "Draft":
		frappe.throw(_("Only Draft assignments can be updated. Current status: {0}.").format(doc.status))

	editable = ["title", "topic", "due_date", "max_score", "description", "assignment_file", "academic_year", "program"]
	for field in editable:
		if field in data and data[field] is not None:
			doc.set(field, data[field])

	# Re-sync target_groups when provided
	if "student_groups" in data and data["student_groups"] is not None:
		incoming = data["student_groups"]
		for sg in incoming:
			if not frappe.db.exists("Student Group", sg):
				frappe.throw(_("Student Group '{0}' not found.").format(sg))
		doc.target_groups = []
		for sg in incoming:
			doc.append("target_groups", {"student_group": sg})

	doc.save(ignore_permissions=False)
	return {"success": True, "name": doc.name}


@frappe.whitelist()
def delete_assignment(name=None):
	"""Delete a Draft assignment. Blocked if any submission has a score.

	Owner instructor only.
	Returns: {success}
	"""
	if not name:
		frappe.throw(_("Assignment name is required."))

	instructor = _require_instructor()
	doc = frappe.get_doc("Assignment", name)
	_check_instructor_owns(doc, instructor)

	# Check if any submissions have been graded
	graded_submissions = frappe.get_all(
		"Assignment Submission", filters={"assignment": name, "score": ["is", "not null"]}, limit=1
	)
	if graded_submissions:
		frappe.throw(
			_(
				"Cannot delete Assignment '{0}': one or more submissions have "
				"already been graded. Close the assignment instead."
			).format(doc.title)
		)

	frappe.delete_doc("Assignment", name, ignore_permissions=False)
	return {"success": True}


@frappe.whitelist()
def close_assignment(name=None):
	"""Set a Published assignment's status to Closed. Owner only.

	Returns: {success}
	"""
	if not name:
		frappe.throw(_("Assignment name is required."))

	instructor = _require_instructor()
	doc = frappe.get_doc("Assignment", name)
	_check_instructor_owns(doc, instructor)

	doc.status = "Closed"
	doc.save(ignore_permissions=True)
	return {"success": True}


@frappe.whitelist()
def get_instructor_assignments(course=None, status=None, academic_year=None, program=None):
	"""Get all assignments belonging to the current instructor.

	Optional filters: course, status
	Returns a list of assignment objects enriched with submission counts.
	"""
	instructor = _require_instructor()

	filters = {"instructor": instructor.name}
	if course:
		filters["course"] = course
	if status:
		filters["status"] = status
	if academic_year:
		filters["academic_year"] = academic_year
	if program:
		filters["program"] = program

	assignments = frappe.get_all(
		"Assignment",
		filters=filters,
		fields=[
			"name",
			"title",
			"course",
			"program",
			"academic_year",
			"topic",
			"instructor",
			"due_date",
			"max_score",
			"assign_to",
			"status",
			"published_on",
			"description",
			"assignment_file",
			"creation",
		],
		order_by="creation desc",
	)

	if not assignments:
		return []

	# Resolve course_name in bulk
	course_names_map = {}
	course_ids = list({a.course for a in assignments if a.course})
	if course_ids:
		for row in frappe.get_all(
			"Course", filters={"name": ["in", course_ids]}, fields=["name", "course_name"]
		):
			course_names_map[row.name] = row.course_name

	# Fetch target_groups in bulk
	assignment_names = [a.name for a in assignments]

	tg_rows = frappe.get_all(
		"Assignment Target Group",
		filters={"parent": ["in", assignment_names], "parenttype": "Assignment"},
		fields=["parent", "student_group", "student_group_name"],
	)
	tg_map = {}
	for r in tg_rows:
		tg_map.setdefault(r.parent, []).append(
			{
				"student_group": r.student_group,
				"student_group_name": r.student_group_name,
			}
		)

	# Fetch Assignment Student (not submission documents) for accurate counts
	student_rows = frappe.get_all(
		"Assignment Student",
		filters={"parent": ["in", assignment_names], "parenttype": "Assignment"},
		fields=["parent", "status"],
	)
	student_map = {}
	for r in student_rows:
		student_map.setdefault(r.parent, []).append(r)

	for a in assignments:
		a["course_name"] = course_names_map.get(a.course, a.course)
		a["target_groups"] = tg_map.get(a.name, [])
		students = student_map.get(a.name, [])
		a["student_count"] = len(students)
		a["submission_count"] = sum(1 for s in students if s.status != "Pending")
		a["graded_count"] = sum(1 for s in students if s.status == "Graded")
		a["pending_count"] = sum(1 for s in students if s.status == "Pending")

	return assignments


@frappe.whitelist()
def get_assignment_submissions(name=None):
	"""Get all submissions for an assignment, grouped by student.

	Owner instructor only.
	Returns submissions grouped by student with student details.
	"""
	if not name:
		frappe.throw(_("Assignment name is required."))

	instructor = _require_instructor()
	doc = frappe.get_doc("Assignment", name)
	_check_instructor_owns(doc, instructor)

	# Get all submissions for this assignment
	submissions = frappe.get_all(
		"Assignment Submission",
		filters={"assignment": name},
		fields=[
			"name",
			"student",
			"student_name",
			"student_group",
			"submitted_on",
			"submission_file",
			"submission_text",
			"score",
			"remarks",
			"graded_by",
			"graded_on",
			"status",
		],
		order_by="student, submitted_on desc",
	)

	# Group by student
	student_submissions = {}
	for sub in submissions:
		student_id = sub.student
		if student_id not in student_submissions:
			student_submissions[student_id] = {
				"student": sub.student,
				"student_name": sub.student_name,
				"student_group": sub.student_group,
				"submissions": [],
			}
		student_submissions[student_id]["submissions"].append(
			{
				"id": sub.name,
				"submitted_on": str(sub.submitted_on or ""),
				"submission_file": sub.submission_file or "",
				"submission_text": sub.submission_text or "",
				"score": sub.score,
				"remarks": sub.remarks or "",
				"graded_by": sub.graded_by,
				"graded_on": str(sub.graded_on or ""),
				"status": sub.status,
			}
		)

	return {"assignment": name, "student_submissions": list(student_submissions.values())}


@frappe.whitelist()
def get_assignment_detail(name=None):
	"""Get full assignment details including submissions and comments.

	- Instructor: Sees all students and all submissions.
	- Student: Sees only their own submissions.
	"""
	if not name:
		frappe.throw(_("Assignment name is required."))

	doc = frappe.get_doc("Assignment", name)
	instructor = _get_instructor_for_user()
	student = _get_student_for_user()

	if not instructor and not student:
		frappe.throw(_("You do not have permission to view this assignment."), frappe.PermissionError)

	result = doc.as_dict()
	result["course_name"] = frappe.db.get_value("Course", doc.course, "course_name") or doc.course

	# Filter submissions based on role and context
	sub_filters = {"assignment": name}
	student_id_context = frappe.form_dict.get("student_id")

	if instructor:
		# If instructor is looking at a specific student, filter for that student's history
		if student_id_context:
			sub_filters["student"] = student_id_context
	elif student:
		# Students only ever see their own submissions
		sub_filters["student"] = student.name

	submissions = frappe.get_all(
		"Assignment Submission",
		filters=sub_filters,
		fields=[
			"name",
			"student",
			"student_name",
			"student_group",
			"submitted_on",
			"submission_file",
			"submission_text",
			"score",
			"remarks",
			"graded_by",
			"graded_on",
			"status",
		],
		order_by="student, submitted_on desc, name desc",
	)

	result["all_submissions"] = [
		{
			"id": s.name,
			"student": s.student,
			"student_name": s.student_name,
			"student_group": s.student_group,
			"submitted_on": str(s.submitted_on or ""),
			"submission_file": s.submission_file or "",
			"submission_text": s.submission_text or "",
			"score": s.score,
			"remarks": s.remarks or "",
			"graded_by": s.graded_by,
			"graded_on": str(s.graded_on or ""),
			"status": s.status,
		}
		for s in submissions
	]

	# If student, also return a specific student_status row
	if student:
		for row in doc.submissions or []:
			if row.student == student.name:
				result["my_student_status"] = row.as_dict()
				break

	# Get Assignment Comments (Messaging)
	# We use a unique reference name to keep student-teacher chats private per student
	# Step 4: Validate access
	_validate_comment_access(doc, student_id_context)

	msg_filters = {
		"reference_doctype": "Assignment",
		"reference_name": name,
		"comment_type": "Comment"
	}

	# Identify the private thread via 'subject'
	if student:
		msg_filters["subject"] = student.name
	elif instructor and student_id_context:
		msg_filters["subject"] = student_id_context
	else:
		# General thread (no subject)
		msg_filters["subject"] = ["in", [None, "", "_general_"]]

	comments = frappe.get_all(
		"Comment",
		filters=msg_filters,
		fields=["name", "content", "comment_by", "creation", "comment_email"],
		order_by="creation asc",
		ignore_permissions=True,
	)

	# Resolve names and format message list for frontend
	user_names = {}
	result["messages"] = []
	for c in comments:
		email = c.comment_email or c.comment_by
		if email not in user_names:
			user_names[email] = frappe.db.get_value("User", email, "full_name") or email

		result["messages"].append(
			{
				"id": c.name,
				"content": c.content or "",
				"author": user_names[email],
				"author_email": email,
				"creation": str(c.creation),
				"is_me": email == frappe.session.user,
			}
		)

	return result


@frappe.whitelist()
def add_assignment_comment(name, content, student_id=None):
	"""Add a message (Comment) to an assignment, possibly student-specific."""
	if not name or not content:
		frappe.throw(_("Assignment name and content are required."))

	doc = frappe.get_doc("Assignment", name)
	_validate_comment_access(doc, student_id)

	# We use the internal helper for consistency
	comment = _add_private_comment(name, content, student_id)

	return {
		"success": True,
		"comment": {
			"id": comment.name,
			"content": comment.content,
			"author": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
			"author_email": frappe.session.user,
			"creation": str(comment.creation),
			"is_me": True,
		},
	}


@frappe.whitelist()
def request_resubmission(assignment, student_id, message=None):
	"""Teacher requests a resubmission for a student."""
	if not assignment or not student_id:
		frappe.throw(_("Assignment and Student ID are required."))

	instructor = _require_instructor()
	doc = frappe.get_doc("Assignment", assignment)
	_check_instructor_owns(doc, instructor)

	# Find the student's overall status row
	student_row = None
	for row in doc.submissions or []:
		if row.student == student_id:
			student_row = row
			break

	if not student_row:
		frappe.throw(_("Student {0} is not enrolled in this assignment.").format(student_id))

	if message:
		full_message = _("<b>Teacher Request: Resubmit Assignment</b><br>{0}").format(message)
	else:
		full_message = _("<b>Teacher Request: Resubmit Assignment</b>")

	# Use the private thread for the resubmission request
	_add_private_comment(assignment, full_message, student_id)

	# Note: We don't update student_row.status = "Pending" automatically
	# as the student status logic handles it based on submission presence.
	return {"success": True}


def _add_private_comment(name, content, student_id=None):
	"""Internal helper to add a comment to a student-specific assignment thread."""
	# We use the real assignment name to avoid LinkValidationError.
	# The private thread is identified by the 'subject' field.
	target_student = student_id
	if not target_student:
		student = _get_student_for_user()
		if student:
			target_student = student.name

	# We manually create the comment to use our custom fields
	comment = frappe.get_doc(
		{
			"doctype": "Comment",
			"comment_type": "Comment",
			"reference_doctype": "Assignment",
			"reference_name": name,
			"subject": target_student or "_general_",
			"content": content,
			"comment_by": frappe.session.user,
			"comment_email": frappe.session.user,
		}
	)
	comment.insert(ignore_permissions=True)
	return comment


# ─── Instructor: grading ────────────────────────────────────────────────


@frappe.whitelist()
def grade_submission(submission_id=None, score=None, remarks="", assignment=None, student=None):
	"""Grade a specific Assignment Submission document.

	Owner instructor only. score must be between 0 and max_score.
	Updates the submission and the student's overall grade in the assignment.
	Returns: {success}
	"""
	if not submission_id and assignment and student:
		# Fallback: find the latest submission for this student on this assignment
		submission_id = frappe.db.get_value(
			"Assignment Submission",
			{"assignment": assignment, "student": student},
			"name",
			order_by="submitted_on desc",
		)

	if not submission_id:
		frappe.throw(_("Submission ID is required."))
	if score is None:
		frappe.throw(_("Score is required."))

	instructor = _require_instructor()
	submission_doc = frappe.get_doc("Assignment Submission", submission_id)

	# Check instructor owns the assignment
	assignment_doc = frappe.get_doc("Assignment", submission_doc.assignment)
	_check_instructor_owns(assignment_doc, instructor)

	score = float(score)
	if score < 0:
		frappe.throw(_("Score cannot be negative."))
	if score > assignment_doc.max_score:
		frappe.throw(
			_("Score {0} exceeds max score {1} for this assignment.").format(score, assignment_doc.max_score)
		)

	# Grade the specific submission
	submission_doc.score = score
	submission_doc.remarks = remarks
	submission_doc.graded_by = frappe.session.user
	submission_doc.graded_on = now_datetime()
	submission_doc.status = "Graded"
	submission_doc.save(ignore_permissions=True)

	# Update student's overall grade in assignment
	student_row = None
	for row in assignment_doc.submissions or []:
		if row.student == submission_doc.student:
			student_row = row
			break

	if student_row:
		student_row.score = score
		student_row.remarks = remarks
		student_row.graded_by = frappe.session.user
		student_row.graded_on = now_datetime()
		student_row.status = "Graded"
		assignment_doc.save(ignore_permissions=True)

	return {"success": True}


# ─── Student: submit / view ─────────────────────────────────────────────


def _student_in_target_groups(doc, student_name):
	"""Return the student_group name if the student belongs to any of the
	assignment's target groups, else None."""
	target_sgs = [tg.student_group for tg in (doc.target_groups or []) if tg.student_group]
	if not target_sgs:
		return None
	row = frappe.db.get_value(
		"Student Group Student",
		{"parent": ["in", target_sgs], "student": student_name},
		["parent"],
	)
	return row  # parent name (= student group), or None


@frappe.whitelist()
def submit_student_assignment(assignment=None, submission_file=None, submission_text=None):
	"""Record a student's submission on a Published assignment.

	Behavior:
	- Late submissions allowed, marked with status "Late".
	- Either submission_file or submission_text MUST be provided.
	- Creates a new Assignment Submission document for each submission.
	- Ensures student has an entry in the assignment's submissions table for overall tracking.

	Returns: {success}
	"""
	if not assignment:
		frappe.throw(_("Assignment name is required."))

	# Hard guard: require at least one payload
	submission_file = (submission_file or "").strip() if isinstance(submission_file, str) else submission_file
	submission_text = (submission_text or "").strip() if isinstance(submission_text, str) else submission_text
	if not submission_file and not submission_text:
		frappe.throw(_("Submission must include a file or text. Nothing was uploaded."))

	student = _require_student()
	doc = frappe.get_doc("Assignment", assignment)

	if doc.status != "Published":
		frappe.throw(
			_("Assignment '{0}' is not currently accepting submissions (status: {1}).").format(
				assignment, doc.status
			)
		)

	# Ensure student has an entry in the assignment's submissions table
	student_row = None
	for row in doc.submissions or []:
		if row.student == student.name:
			student_row = row
			break

	# Auto-heal: student joined a target group AFTER the assignment was published
	if not student_row:
		membership_sg = _student_in_target_groups(doc, student.name)
		if not membership_sg:
			frappe.throw(_("You are not enrolled in this assignment."))
		student_row = doc.append(
			"submissions",
			{
				"student": student.name,
				"student_group": membership_sg,
				"status": "Pending",
			},
		)
		doc.save(ignore_permissions=True)

	# Determine if late
	is_late = doc.due_date and getdate(doc.due_date) < getdate(today())
	new_status = "Late" if is_late else "Submitted"

	# Update student's overall tracking status
	if student_row.status != "Graded":
		student_row.status = new_status
		doc.save(ignore_permissions=True)

	# Create new Assignment Submission document
	submission_doc = frappe.get_doc(
		{
			"doctype": "Assignment Submission",
			"assignment": assignment,
			"student": student.name,
			"student_group": student_row.student_group,
			"submitted_on": now_datetime(),
			"status": new_status,
			"submission_file": submission_file,
			"submission_text": submission_text,
		}
	)
	submission_doc.insert(ignore_permissions=True)

	return {"success": True}


@frappe.whitelist()
def get_student_assignments():
	"""Get all Published assignments that the current student should see.

	A student "should see" an assignment when EITHER:
	  a) they already have an Assignment Submission row on it, OR
	  b) they are a member of one of the assignment's target student groups
	     (handles students who joined the group AFTER publication, and
	     instructors who never re-published), OR
	  c) they have an Assignment Student row for the assignment
	     (handles students who were assigned when the assignment was published).

	Returns a list with the student's submissions embedded
	(all submissions for the student on each assignment).
	"""
	student = _require_student()

	# ── 1. Direct submission rows ────────────────────────────────────────
	sub_rows = frappe.get_all(
		"Assignment Submission",
		filters={
			"student": student.name,
		},
		fields=[
			"name",
			"assignment",
			"submitted_on",
			"submission_file",
			"submission_text",
			"score",
			"remarks",
			"graded_on",
			"status",
		],
		order_by="submitted_on desc",
	)
	sub_by_assignment = {}
	for r in sub_rows:
		if r.assignment not in sub_by_assignment:
			sub_by_assignment[r.assignment] = []
		sub_by_assignment[r.assignment].append(r)
	direct_names = set(sub_by_assignment.keys())

	# ── 2. Group-membership fallback ─────────────────────────────────────
	student_groups = frappe.get_all(
		"Student Group Student",
		filters={"student": student.name},
		pluck="parent",
	)
	membership_names: set[str] = set()
	if student_groups:
		tg_assignment_names = frappe.get_all(
			"Assignment Target Group",
			filters={
				"student_group": ["in", student_groups],
				"parenttype": "Assignment",
			},
			pluck="parent",
		)
		membership_names = set(tg_assignment_names)

	# ── 3. Assignment Student rows fallback ──────────────────────────────
	assigned_names = set()
	assigned_assignments = frappe.get_all(
		"Assignment Student",
		filters={
			"student": student.name,
			"parenttype": "Assignment",
		},
		pluck="parent",
	)
	assigned_names = set(assigned_assignments)

	candidate_names = list(direct_names | membership_names | assigned_names)
	if not candidate_names:
		return []

	assignments = frappe.get_all(
		"Assignment",
		filters={
			"name": ["in", candidate_names],
			"status": "Published",
		},
		fields=[
			"name",
			"title",
			"course",
			"topic",
			"due_date",
			"max_score",
			"description",
			"assignment_file",
			"status",
		],
	)

	assignments = frappe.get_all(
		"Assignment",
		filters={
			"name": ["in", candidate_names],
			"status": "Published",
		},
		fields=[
			"name",
			"title",
			"course",
			"topic",
			"due_date",
			"max_score",
			"description",
			"assignment_file",
			"status",
		],
	)

	# Bulk resolve course names
	course_ids = list({a.course for a in assignments if a.course})
	course_names_map = {}
	if course_ids:
		for row in frappe.get_all(
			"Course", filters={"name": ["in", course_ids]}, fields=["name", "course_name"]
		):
			course_names_map[row.name] = row.course_name

	result = []
	for a in assignments:
		submissions = sub_by_assignment.get(a.name, [])
		has_submissions = len(submissions) > 0
		latest_submission = submissions[0] if submissions else None

		# Check if overdue (no submissions or latest is not submitted/graded/late)
		sub_status = latest_submission.status if latest_submission else None
		is_overdue = (
			a.due_date
			and getdate(a.due_date) < getdate(today())
			and sub_status not in ("Submitted", "Graded", "Late")
		)

		# Format submissions for output
		formatted_submissions = [
			{
				"id": s.name,
				"submitted_on": str(s.submitted_on or ""),
				"submission_file": s.submission_file or "",
				"submission_text": s.submission_text or "",
				"score": s.score,
				"remarks": s.remarks or "",
				"graded_on": str(s.graded_on or ""),
				"status": s.status,
			}
			for s in submissions
		]

		result.append(
			{
				"name": a.name,
				"title": a.title,
				"course": a.course,
				"course_name": course_names_map.get(a.course, a.course),
				"topic": a.topic,
				"due_date": str(a.due_date) if a.due_date else "",
				"max_score": a.max_score,
				"description": a.description or "",
				"assignment_file": a.assignment_file or "",
				"status": a.status,
				# For backward compatibility: provide latest submission as singular
				"my_submission": {
					"id": latest_submission.name,
					"submitted_on": str(latest_submission.submitted_on or ""),
					"submission_file": latest_submission.submission_file or "",
					"submission_text": latest_submission.submission_text or "",
					"score": latest_submission.score,
					"remarks": latest_submission.remarks or "",
					"graded_on": str(latest_submission.graded_on or ""),
					"status": latest_submission.status,
				}
				if latest_submission
				else None,
				# All submissions for the student
				"my_submissions": formatted_submissions,
				"has_submissions": has_submissions,
				"is_overdue": is_overdue,
			}
		)
	print(f"get_student_assignments: student={student.name}, count={len(result)}")
	return result


# ─── Shared helpers (kept for both old and new systems) ─────────────────


@frappe.whitelist()
def get_instructor_courses():
	"""Get courses the logged-in instructor teaches."""
	instructor = _get_instructor_for_user()
	if not instructor:
		return []

	mappings = frappe.get_all(
		"Instructor Course Mapping",
		filters={"parent": instructor.name, "parenttype": "Instructor"},
		fields=["course", "course_name", "program"],
	)

	seen = set()
	courses = []
	for m in mappings:
		if m.course not in seen:
			seen.add(m.course)
			course_name = m.course_name or frappe.db.get_value("Course", m.course, "course_name") or m.course
			courses.append({"name": m.course, "course_name": course_name, "program": m.program})

	return courses


@frappe.whitelist()
def get_instructor_programs():
	"""Get programs the logged-in instructor teaches."""
	instructor = _get_instructor_for_user()
	if not instructor:
		return []

	mappings = frappe.get_all(
		"Instructor Course Mapping",
		filters={"parent": instructor.name, "parenttype": "Instructor"},
		fields=["program"],
		distinct=1
	)
	
	program_names = [m.program for m in mappings if m.program]
	if not program_names:
		return []

	return frappe.get_all(
		"Program",
		filters={"name": ["in", program_names]},
		fields=["name", "program_name"],
		ignore_permissions=True
	)


@frappe.whitelist()
def get_instructor_academic_years():
	"""Get all active academic years."""
	return frappe.get_all("Academic Year", fields=["name", "academic_year_name"], order_by="year_start_date desc", ignore_permissions=True)


@frappe.whitelist()
def get_instructor_student_groups(course=None):
	"""Get student groups the logged-in instructor teaches.

	Honors TWO data models simultaneously (whichever is populated):
	  1. Explicit  — Student Group Instructor child rows (the Education
	                 module's native model).
	  2. Implicit  — Instructor Course Mapping rows on the Instructor doc.
	                 A group is included if its program is one the
	                 instructor teaches the given course in.

	The union of both is returned, deduplicated, optionally filtered by
	course (the course must also be present in each group's program).
	"""
	instructor = _get_instructor_for_user()
	if not instructor:
		return []

	company = _get_user_company()

	# ── 1. Explicit links (Student Group Instructor) ──────────────────────
	explicit_names = set(
		frappe.get_all(
			"Student Group Instructor",
			filters={"instructor": instructor.name},
			pluck="parent",
		)
	)

	# ── 2. Implicit links (Instructor Course Mapping → program → groups) ──
	icm_filters = {"parent": instructor.name, "parenttype": "Instructor"}
	if course:
		icm_filters["course"] = course
	programs_taught = list(
		{
			row
			for row in frappe.get_all(
				"Instructor Course Mapping",
				filters=icm_filters,
				pluck="program",
			)
			if row
		}
	)

	implicit_names = set()
	if programs_taught:
		sg_filters = {"program": ["in", programs_taught], "disabled": 0}
		if company:
			sg_filters["company"] = company
		implicit_names = set(
			frappe.get_all(
				"Student Group",
				filters=sg_filters,
				pluck="name",
			)
		)

	union_names = list(explicit_names | implicit_names)
	if not union_names:
		return []

	sg_filters = {"name": ["in", union_names], "disabled": 0}
	if company:
		sg_filters["company"] = company

	groups = frappe.get_all(
		"Student Group",
		filters=sg_filters,
		fields=["name", "student_group_name", "program"],
		order_by="student_group_name asc",
	)

	# When a specific course is requested, ensure each group's program
	# actually contains that course (defensive — implicit list is already
	# filtered, but explicit list may include groups whose program does not).
	if course:
		groups = [
			g for g in groups if frappe.db.exists("Program Course", {"parent": g.program, "course": course})
		]

	return groups


# ─── Backward-compatibility thin wrapper ────────────────────────────────


@frappe.whitelist()
def submit_assignment(assignment_name=None, submission_file=None):
	"""Thin wrapper kept for frontend backward-compatibility.

	DEPRECATED: migrate callers to submit_student_assignment().
	Delegates to the new submit_student_assignment() function.
	"""
	return submit_student_assignment(
		assignment=assignment_name,
		submission_file=submission_file,
	)


# ═══════════════════════════════════════════════════════════════════════════
# LEGACY FUNCTIONS  (Assessment Plan based — kept for safe migration)
# Renamed with _legacy suffix. Do NOT call these from new code.
# ═══════════════════════════════════════════════════════════════════════════


@frappe.whitelist()
def get_assignments_legacy():
	"""LEGACY: Get assignment-type Assessment Plans for the student.

	Replaced by get_student_assignments().
	"""
	student = _get_student_for_user()
	if not student:
		return []

	groups = frappe.get_all(
		"Student Group Student", filters={"student": student.name, "active": 1}, pluck="parent"
	)
	if not groups:
		return []

	plans = frappe.get_all(
		"Assessment Plan",
		filters={
			"student_group": ["in", groups],
			"docstatus": 1,
			"assessment_group": ["like", "%Assignment%"],
		},
		fields=[
			"name",
			"assessment_name",
			"course",
			"student_group",
			"schedule_date",
			"maximum_assessment_score",
			"examiner",
			"assessment_group",
		],
		order_by="schedule_date desc",
	)

	for p in plans:
		result = frappe.db.get_value(
			"Assessment Result",
			{"student": student.name, "assessment_plan": p.name, "docstatus": 1},
			["total_score", "grade"],
			as_dict=True,
		)
		p["submitted"] = bool(result)
		p["score"] = result.total_score if result else None
		p["grade"] = result.grade if result else None
		p["deadline"] = str(p.schedule_date) if p.schedule_date else ""

		course_name = frappe.db.get_value("Course", p.course, "course_name") or p.course
		p["title"] = p.assessment_name or course_name
		p["course_name"] = course_name
		p["due_date"] = str(p.schedule_date) if p.schedule_date else ""
		p["description"] = p.assessment_name or ""
		p["assignment_file"] = None

		if result and p["grade"]:
			p["status"] = "Evaluated"
		elif result:
			p["status"] = "Submitted"
		elif p.schedule_date and str(p.schedule_date) < frappe.utils.today():
			p["status"] = "Overdue"
		else:
			p["status"] = "Active"

	return plans


@frappe.whitelist()
def get_instructor_assignment_templates_legacy(course=None):
	"""LEGACY: Get assignment-type Assessment Plans created by this instructor.

	Replaced by get_instructor_assignments().
	"""
	instructor = _get_instructor_for_user()
	if not instructor:
		return []

	filters = {
		"examiner": instructor.name,
		"docstatus": ["in", [0, 1]],
		"assessment_group": ["like", "%Assignment%"],
	}
	if course:
		filters["course"] = course

	return frappe.get_all(
		"Assessment Plan",
		filters=filters,
		fields=[
			"name",
			"assessment_name",
			"course",
			"student_group",
			"schedule_date",
			"maximum_assessment_score",
			"docstatus",
			"assessment_group",
		],
		order_by="schedule_date desc",
	)


@frappe.whitelist()
def create_assignment_template_legacy(data=None):
	"""LEGACY: Create Assessment Plan based assignments.

	Replaced by create_assignment().
	"""
	if not data:
		frappe.throw(_("No data provided"))

	import json

	if isinstance(data, str):
		data = json.loads(data)

	instructor = _get_instructor_for_user()
	if not instructor:
		frappe.throw(_("No instructor record found for the logged-in user"))

	title = (data.get("title") or "").strip()
	course = (data.get("course") or "").strip()
	if not title:
		frappe.throw(_("Title is required"))
	if not course:
		frappe.throw(_("Course is required"))
	if not frappe.db.exists("Course", course):
		match = frappe.db.get_value("Course", {"course_name": course}, "name")
		if not match:
			frappe.throw(_("Course '{0}' not found").format(course))
		course = match

	schedule_date = data.get("due_date") or data.get("deadline") or frappe.utils.today()

	course_doc = frappe.get_doc("Course", course)
	grading_scale = course_doc.default_grading_scale
	if not grading_scale:
		grading_scale = frappe.db.get_value("Grading Scale", {}, "name")
	if not grading_scale:
		frappe.throw(
			_(
				"No Grading Scale found. Set a default grading scale on the Course "
				"or create at least one Grading Scale."
			)
		)

	assessment_group = (
		data.get("assessment_group")
		or frappe.db.get_value(
			"Assessment Group", {"assessment_group_name": "Assignments", "is_group": 0}, "name"
		)
		or frappe.db.get_value("Assessment Group", {"is_group": 0}, "name")
	)
	if not assessment_group:
		frappe.throw(
			_(
				"No leaf Assessment Group found. Please create an Assessment Group "
				"(e.g. 'Assignments') under your root assessment group first."
			)
		)

	max_score = float(data.get("max_score") or 100)
	criteria_rows = []
	if course_doc.assessment_criteria:
		for cc in course_doc.assessment_criteria:
			weightage = float(cc.weightage or 0)
			row_score = round((weightage / 100.0) * max_score, 2) if weightage else max_score
			criteria_rows.append(
				{
					"assessment_criteria": cc.assessment_criteria,
					"maximum_score": row_score,
				}
			)
	if not criteria_rows:
		fallback = frappe.db.get_value("Assessment Criteria", {}, "name")
		if not fallback:
			frappe.throw(
				_(
					"Course '{0}' has no assessment criteria and no Assessment "
					"Criteria records exist. Add at least one before creating "
					"assignments."
				).format(course)
			)
		criteria_rows.append(
			{
				"assessment_criteria": fallback,
				"maximum_score": max_score,
			}
		)

	assign_to = (data.get("assign_to") or "").strip()
	explicit_group = (data.get("student_group") or "").strip()

	target_groups = []
	if assign_to == "All Enrolled":
		groups = get_instructor_student_groups(course=course)
		target_groups = [g["name"] if isinstance(g, dict) else g.name for g in groups]
		if not target_groups:
			frappe.throw(
				_(
					"No student groups found for course '{0}' that you are assigned to. "
					"Either create/join a student group or pick 'Specific Group'."
				).format(course)
			)
	else:
		if not explicit_group:
			frappe.throw(_("Student Group is required when not assigning to all enrolled"))
		if not frappe.db.exists("Student Group", explicit_group):
			frappe.throw(_("Student Group '{0}' not found").format(explicit_group))
		target_groups = [explicit_group]

	description = data.get("description") or ""
	assignment_file = data.get("assignment_file") or ""
	created = []

	for sg in target_groups:
		try:
			plan = frappe.get_doc(
				{
					"doctype": "Assessment Plan",
					"assessment_name": title,
					"course": course,
					"student_group": sg,
					"assessment_group": assessment_group,
					"grading_scale": grading_scale,
					"schedule_date": schedule_date,
					"from_time": "00:00:00",
					"to_time": "23:59:00",
					"maximum_assessment_score": max_score,
					"examiner": instructor.name,
					"assessment_criteria": criteria_rows,
				}
			)
			plan.insert()

			if description:
				plan.add_comment("Comment", text=description)

			if assignment_file:
				try:
					frappe.get_doc(
						{
							"doctype": "File",
							"file_url": assignment_file,
							"attached_to_doctype": "Assessment Plan",
							"attached_to_name": plan.name,
						}
					).insert(ignore_permissions=True)
				except Exception:
					frappe.log_error(
						title="create_assignment_template_legacy: file attach failed",
						message=frappe.get_traceback(),
					)

			created.append(plan.name)
		except frappe.DuplicateEntryError:
			frappe.log_error(
				title="create_assignment_template_legacy: duplicate skipped",
				message=f"Duplicate Assessment Plan for group {sg}",
			)
			continue

	if not created:
		frappe.throw(_("No assignments were created. Please check the inputs and try again."))

	return {
		"success": True,
		"created": created,
		"count": len(created),
		"name": created[0],
	}


@frappe.whitelist()
def publish_assignment_template_legacy(template_name=None):
	"""LEGACY: Submit (publish) an assignment Assessment Plan.

	Replaced by publish_assignment().
	"""
	if not template_name:
		frappe.throw(_("Template name is required"))

	plan = frappe.get_doc("Assessment Plan", template_name)
	plan.submit()

	return {"success": True, "name": plan.name}


@frappe.whitelist()
def get_template_submissions_legacy(template_name=None):
	"""LEGACY: Get student submissions (Assessment Results) for an assignment.

	Replaced by get_assignment_detail().
	"""
	if not template_name:
		return []

	return frappe.get_all(
		"Assessment Result",
		filters={"assessment_plan": template_name},
		fields=["name", "student", "student_name", "total_score", "grade", "docstatus", "comment"],
		order_by="student_name asc",
	)


@frappe.whitelist()
def grade_assignment_legacy(assignment_name=None, score=None, remarks=""):
	"""LEGACY: Grade a student's assignment (Assessment Result).

	Replaced by grade_submission().
	"""
	if not assignment_name:
		frappe.throw(_("Assignment name is required"))

	result = frappe.get_doc("Assessment Result", assignment_name)
	if result.docstatus == 1:
		frappe.throw(_("Result already submitted"))

	if result.details:
		for detail in result.details:
			detail.score = float(score) if score else 0

	result.total_score = float(score) if score else 0
	result.comment = remarks
	result.save()

	return {"success": True, "name": result.name}

	return {"success": True, "name": result.name}
