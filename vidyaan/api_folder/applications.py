import frappe
from frappe.utils import today, now, getdate, get_datetime
from frappe.model.workflow import get_workflow_name

# Supported application doctypes and their display config
APPLICATION_DOCTYPES = {
	"Student Leave Application": {
		"key": "leave",
		"label": "Leave Application",
		"icon": "fa-calendar-times-o",
		"color": "blue",
		"description": "Apply for leave of absence",
	},
	"Student NOC": {
		"key": "noc",
		"label": "NOC Application",
		"icon": "fa-file-text",
		"color": "purple",
		"description": "Request No Objection Certificate",
	},
	"Student Request": {
		"key": "request",
		"label": "General Request",
		"icon": "fa-paper-plane",
		"color": "indigo",
		"description": "Submit a request to administration",
	},
}


def _get_student_for_user():
	return frappe.db.get_value("Student", {"user": frappe.session.user}, "name")


def _get_workflow_steps(doctype):
	"""Get ordered workflow states for a doctype (for timeline rendering)."""
	wf_name = get_workflow_name(doctype)
	if not wf_name:
		return []

	wf = frappe.get_doc("Workflow", wf_name)
	steps = []
	seen = set()
	for state in wf.states:
		if state.state not in seen:
			seen.add(state.state)
			steps.append({
				"state": state.state,
				"doc_status": state.doc_status,
				"allow_edit": state.allow_edit or "",
			})
	return steps


def _get_doc_workflow_state(doc):
	"""Get current workflow state or fall back to status/docstatus."""
	ws = doc.get("workflow_state")
	if ws:
		return ws
	status = doc.get("status")
	if status and status != "Draft":
		return status
	return "Approved" if doc.docstatus == 1 else ("Cancelled" if doc.docstatus == 2 else "Draft")


def _get_allowed_workflow_states(doctype):
    """Return distinct source workflow states where the current user has an allowed transition."""
    workflow_name = get_workflow_name(doctype)
    if not workflow_name:
        return []

    workflow = frappe.get_cached_doc("Workflow", workflow_name)
    if not workflow.is_active:
        return []

    user_roles = set(frappe.get_roles())  # set for O(1) lookup

    return list({
        transition.state
        for transition in workflow.transitions
        if transition.allowed in user_roles
    })


# ─── APIs ─────────────────────────────────────────────────────────────────────


@frappe.whitelist()
def get_available_application_types():
	"""
	Return application types that the student can see.
	A type is available if:
	  - The doctype exists
	  - An active workflow is configured for it OR it's Student Leave Application (always available)
	"""
	available = []
	for doctype, config in APPLICATION_DOCTYPES.items():
		if not frappe.db.exists("DocType", doctype):
			continue

		wf_name = get_workflow_name(doctype)
		# Student Leave Application is always available (Education core doctype)
		# Others require an active workflow set up by admin
		if doctype == "Student Leave Application" or wf_name:
			entry = {**config, "doctype": doctype, "has_workflow": bool(wf_name)}
			if wf_name:
				entry["workflow_steps"] = _get_workflow_steps(doctype)
			available.append(entry)

	return available


@frappe.whitelist()
def get_my_applications():
	"""Get all applications for the logged-in student, with workflow tracking."""
	student = _get_student_for_user()
	if not student:
		return []

	applications = []

	# Student NOC
	if frappe.db.exists("DocType", "Student NOC"):
		for noc in frappe.get_all(
			"Student NOC",
			filters={"student": student, "docstatus": ["<", 3]}, # Include docstatus 2 (Cancelled/Rejected)
			fields=["name", "noc_type", "purpose", "status", "application_date", "workflow_state", "docstatus", "creation"],
			order_by="creation desc",
			ignore_permissions=True,
		):
			applications.append({
				"name": noc.name,
				"type": "NOC",
				"key": "noc",
				"subject": noc.noc_type,
				"description": noc.purpose or "",
				"status": noc.workflow_state or noc.status,
				"date": str(noc.application_date),
				"doctype": "Student NOC",
				"docstatus": noc.docstatus,
				"creation": str(noc.creation),
			})

	# Student Request
	if frappe.db.exists("DocType", "Student Request"):
		for req in frappe.get_all(
			"Student Request",
			filters={"student": student, "docstatus": ["<", 3]}, # Include docstatus 2
			fields=["name", "subject", "category", "status", "priority", "request_date", "workflow_state", "docstatus", "creation"],
			order_by="creation desc",
			ignore_permissions=True,
		):
			applications.append({
				"name": req.name,
				"type": req.category or "Request",
				"key": "request",
				"subject": req.subject,
				"description": "",
				"status": req.workflow_state or req.status,
				"priority": req.priority,
				"date": str(req.request_date),
				"doctype": "Student Request",
				"docstatus": req.docstatus,
				"creation": str(req.creation),
			})

	# Student Leave Application
	if frappe.db.exists("DocType", "Student Leave Application"):
		# Check which fields exist to avoid column errors
		leave_fields = ["name", "from_date", "to_date", "reason", "total_leave_days", "docstatus", "creation"]
		leave_meta = frappe.get_meta("Student Leave Application")
		if leave_meta.has_field("workflow_state"):
			leave_fields.append("workflow_state")
		for leave in frappe.get_all(
			"Student Leave Application",
			filters={"student": student, "docstatus": ["<", 3]}, # Include docstatus 2
			fields=leave_fields,
			order_by="creation desc",
			ignore_permissions=True,
		):
			applications.append({
				"name": leave.name,
				"type": "Leave",
				"key": "leave",
				"subject": f"Leave: {leave.from_date} to {leave.to_date}",
				"description": leave.reason or "",
				"status": leave.workflow_state or ("Approved" if leave.docstatus == 1 else "Pending"),
				"date": str(leave.from_date),
				"days": leave.total_leave_days,
				"doctype": "Student Leave Application",
				"docstatus": leave.docstatus,
				"creation": str(leave.creation),
			})

	applications.sort(key=lambda x: x.get("creation", ""), reverse=True)

	# Attach workflow steps and latest comment for rejected apps to each application
	wf_cache = {}
	for app in applications:
		dt = app["doctype"]
		if dt not in wf_cache:
			wf_cache[dt] = _get_workflow_steps(dt)
		app["workflow_steps"] = wf_cache[dt]

		# Fetch rejection reason if rejected or cancelled
		if app["status"] in ["Rejected", "Cancelled"] or "Reject" in str(app["status"]):
			latest_comment = frappe.get_all(
				"Comment",
				filters={
					"reference_doctype": dt,
					"reference_name": app["name"],
					"comment_type": "Comment"
				},
				fields=["content"],
				order_by="creation desc",
				limit=1
			)
			if latest_comment:
				from frappe.utils import strip_html
				app["rejection_reason"] = strip_html(latest_comment[0].content)

	return applications


@frappe.whitelist()
def get_application_detail(doctype, name):
	"""Get full application detail with workflow timeline."""
	student = _get_student_for_user()
	if not student:
		frappe.throw("You are not registered as a student.")

	if doctype not in APPLICATION_DOCTYPES:
		frappe.throw("Invalid application type.")

	doc = frappe.get_doc(doctype, name)
	if doc.student != student:
		frappe.throw("You can only view your own applications.")

	current_state = _get_doc_workflow_state(doc)
	result = {
		"name": doc.name,
		"doctype": doctype,
		"status": current_state,
		"docstatus": doc.docstatus,
		"date": str(doc.get("application_date") or doc.get("request_date") or doc.get("from_date") or ""),
		"workflow_steps": _get_workflow_steps(doctype),
		"current_state": current_state,
	}

	if doctype == "Student NOC":
		result.update({
			"type": "NOC", "subject": doc.noc_type, "purpose": doc.purpose,
			"noc_type": doc.noc_type, "destination": doc.destination,
			"effective_date": str(doc.effective_date) if doc.effective_date else "",
			"clearances": {
				"library": {"status": doc.library_clearance, "remarks": doc.library_remarks},
				"accounts": {"status": doc.accounts_clearance, "remarks": doc.accounts_remarks},
				"lab": {"status": doc.lab_clearance, "remarks": doc.lab_remarks},
				"hostel": {"status": doc.hostel_clearance, "remarks": doc.hostel_remarks},
			},
			"approved_by": doc.approved_by,
			"admin_remarks": doc.admin_remarks,
		})
	elif doctype == "Student Request":
		result.update({
			"type": doc.category, "subject": doc.subject, "description": doc.description,
			"priority": doc.priority, "response": doc.response,
			"resolution_remarks": doc.resolution_remarks,
		})
	elif doctype == "Student Leave Application":
		result.update({
			"type": "Leave", "subject": f"Leave: {doc.from_date} to {doc.to_date}",
			"from_date": str(doc.from_date), "to_date": str(doc.to_date),
			"reason": doc.reason, "total_leave_days": doc.total_leave_days,
		})

	# Workflow action history
	result["action_log"] = frappe.get_all(
		"Comment",
		filters={"reference_doctype": doctype, "reference_name": name, "comment_type": "Workflow"},
		fields=["content", "comment_by", "creation"],
		order_by="creation asc",
	)

	return result


# ─── Submission APIs ──────────────────────────────────────────────────────────


@frappe.whitelist()
def submit_noc(noc_type, purpose, effective_date=None, destination=None, supporting_document=None):
	student = _get_student_for_user()
	if not student:
		frappe.throw("You are not registered as a student.")

	# Auto-fetch the program from Program Enrollment
	program = frappe.db.get_value("Program Enrollment", {"student": student, "docstatus": 1}, "program", order_by="creation desc")

	doc = frappe.get_doc({
		"doctype": "Student NOC",
		"student": student,
		"noc_type": noc_type,
		"purpose": purpose,
		"effective_date": effective_date or None,
		"destination": destination or None,
		"supporting_document": supporting_document or None,
		"program": program or None,
	})
	doc.insert(ignore_permissions=True)
	try:
		if get_workflow_name("Student NOC"):
			from frappe.model.workflow import apply_workflow
			apply_workflow(doc, "Submit")
		else:
			doc.submit()
	except Exception as e:
		frappe.log_error(title="Submit NOC Error", message=str(e))
		pass  # Submit may fail if workflow requires approval
	return {"success": True, "name": doc.name, "program": program}


@frappe.whitelist()
def get_student_program():
	student = _get_student_for_user()
	if not student:
		return None
	return frappe.db.get_value("Program Enrollment", {"student": student, "docstatus": 1}, "program", order_by="creation desc")


@frappe.whitelist()
def submit_request(subject, description, category="General", priority="Medium"):
	student = _get_student_for_user()
	if not student:
		frappe.throw("You are not registered as a student.")

	doc = frappe.get_doc({
		"doctype": "Student Request",
		"student": student,
		"subject": subject,
		"description": description,
		"category": category,
		"priority": priority,
	})
	doc.insert(ignore_permissions=True)
	try:
		if not get_workflow_name("Student Request"):
			doc.submit()
	except Exception:
		pass  # Submit may fail if workflow requires approval
	return {"success": True, "name": doc.name}


@frappe.whitelist()
def get_leave_options():
	"""Fetch available student groups and course schedules for the student to select when applying for leave."""
	student = _get_student_for_user()
	if not student:
		return {"student_groups": [], "course_schedules": []}
		
	# Fetch active student groups
	groups = frappe.get_all(
		"Student Group Student",
		filters={"student": student, "active": 1},
		pluck="parent"
	)
	
	schedules = []
	if groups:
		schedules = frappe.get_all(
			"Course Schedule",
			filters={"student_group": ["in", groups]},
			fields=["name", "course", "schedule_date"]
		)
		
	return {
		"student_groups": [{"label": g, "value": g} for g in groups],
		"course_schedules": [{"label": f"{s.name} ({s.course} on {s.schedule_date})", "value": s.name} for s in schedules]
	}


@frappe.whitelist()
def get_students_in_group(student_group):
	"""Fetch all active students in a specific student group."""
	student = _get_student_for_user()
	if not student:
		frappe.throw("You are not registered as a student.")
	
	# Security: Verify the student is in this group
	is_in_group = frappe.db.exists(
		"Student Group Student",
		{"parent": student_group, "student": student, "active": 1}
	)
	if not is_in_group:
		frappe.throw("You are not a member of this student group.")
	
	students = frappe.get_all(
		"Student Group Student",
		filters={"parent": student_group, "active": 1},
		fields=["student", "student_name"],
		order_by="student_name"
	)
	
	return [{"label": s.student_name, "value": s.student} for s in students]


@frappe.whitelist()
def get_filtered_course_schedules(student_group, from_date, to_date):
	"""Fetch course schedules for a student group filtered by date range."""
	student = _get_student_for_user()
	if not student:
		frappe.throw("You are not registered as a student.")
	
	# Security: Verify the student is in this group
	is_in_group = frappe.db.exists(
		"Student Group Student",
		{"parent": student_group, "student": student, "active": 1}
	)
	if not is_in_group:
		frappe.throw("You are not a member of this student group.")
	
	from frappe.utils import getdate
	from_d = getdate(from_date)
	to_d = getdate(to_date)
	
	schedules = frappe.get_all(
		"Course Schedule",
		filters={
			"student_group": student_group,
			"schedule_date": ["between", [from_d, to_d]]
		},
		fields=["name", "course", "schedule_date", "from_time", "to_time"],
		order_by="schedule_date"
	)
	
	return [
		{
			"label": f"{s.course} on {s.schedule_date} ({s.from_time} - {s.to_time})",
			"value": s.name
		} for s in schedules
	]

@frappe.whitelist()
def submit_leave(from_date, to_date, reason=None, attendance_based_on="Student Group", student_group=None, course_schedule=None):
	student = _get_student_for_user()
	if not student:
		frappe.throw("You are not registered as a student.")

	# Auto-resolve student group if "Student Group" is selected but no group is provided
	if attendance_based_on == "Student Group" and not student_group:
		groups = frappe.get_all(
			"Student Group Student",
			filters={"student": student, "active": 1},
			pluck="parent",
			limit=1
		)
		student_group = groups[0] if groups else None
		
	# Check for required fields based on attendance setup
	if attendance_based_on == "Course Schedule" and not course_schedule:
		frappe.throw("Course Schedule is required when attendance is based on Course Schedule")

	doc = frappe.get_doc({
		"doctype": "Student Leave Application",
		"student": student,
		"from_date": from_date,
		"to_date": to_date,
		"reason": reason or "",
		"attendance_based_on": attendance_based_on,
		"student_group": student_group if attendance_based_on == "Student Group" else None,
		"course_schedule": course_schedule if attendance_based_on == "Course Schedule" else None,
	})
	doc.insert(ignore_permissions=True)
	
	try:
		if get_workflow_name("Student Leave Application"):
			from frappe.model.workflow import apply_workflow
			apply_workflow(doc, "Submit")
		else:
			doc.submit()
	except Exception as e:
		frappe.log_error(title="Submit Leave Error", message=str(e))
		pass  # Submit may fail if workflow or validation prevents it
	return {"success": True, "name": doc.name}

# ─── Teacher APIs ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_teacher_pending_applications():
	"""Fetch all applications (Leaves and NOCs) pending teacher approval for the current instructor."""
	from vidyaan.api_folder.profile import _get_instructor_for_user
	instructor = _get_instructor_for_user()
	if not instructor:
		frappe.throw("You are not registered as an Instructor.")
		
	# Get instructor's student groups
	assigned_groups = frappe.get_all(
		"Student Group Instructor",
		filters={"instructor": instructor.name},
		pluck="parent",
		ignore_permissions=True
	)
	
	# Also include groups from Course Schedule if applicable
	schedule_groups = frappe.get_all(
		"Course Schedule",
		filters={"instructor": instructor.name},
		pluck="student_group",
		distinct=True,
		ignore_permissions=True
	)
	
	all_groups = list(set(assigned_groups + schedule_groups))
	
	if not all_groups:
		return []
		
	# Get all students in these groups
	students = frappe.get_all(
		"Student Group Student",
		filters={"parent": ["in", all_groups], "active": 1},
		pluck="student",
		ignore_permissions=True
	)
	
	if not students:
		return []

	enhanced_apps = []

	# Leaves
	leave_states = _get_allowed_workflow_states("Student Leave Application")
	leave_filters = {
		"student": ["in", students]
	}
	# Only filter on workflow_state if the field actually exists on the doctype.
	# ERPNext Education's Student Leave Application ships without it; Vidyaan
	# injects it as a custom field. On sites where the custom field hasn't been
	# applied yet (pre-migrate), a filter on workflow_state would raise a
	# "Unknown column" error and break the pending applications query.
	leave_meta = frappe.get_meta("Student Leave Application")
	if leave_meta.has_field("workflow_state"):
		if leave_states:
			leave_filters["workflow_state"] = ["in", leave_states]
		else:
			leave_filters["workflow_state"] = "Pending Review"
	else:
		leave_filters["docstatus"] = 0

	leaves = frappe.get_all(
		"Student Leave Application",
		filters=leave_filters,
		fields=["name", "student", "student_name", "from_date", "to_date", "reason", "total_leave_days", "attendance_based_on", "student_group", "course_schedule", "creation"],
		order_by="creation desc",
		ignore_permissions=True
	)
	for leave in leaves:
		sg_info = ""
		if leave.attendance_based_on == "Student Group" and leave.student_group:
			sg_info = leave.student_group
		elif leave.course_schedule:
			cs = frappe.db.get_value("Course Schedule", leave.course_schedule, ["student_group", "course"])
			if cs:
				sg_info = f"{cs[0]} ({cs[1]})"
		
		enhanced_apps.append({
			"app_type": "Leave",
			"name": leave.name,
			"student": leave.student,
			"student_name": leave.student_name,
			"from_date": str(leave.from_date),
			"to_date": str(leave.to_date),
			"date_range": f"{leave.from_date} to {leave.to_date}",
			"reason": leave.reason,
			"total_leave_days": leave.total_leave_days,
			"group_info": sg_info,
			"creation": str(leave.creation)
		})

	# NOCs
	if frappe.db.exists("DocType", "Student NOC"):
		noc_states = _get_allowed_workflow_states("Student NOC")
		noc_filters = {
			"student": ["in", students]
		}
		noc_meta = frappe.get_meta("Student NOC")
		if noc_meta.has_field("workflow_state"):
			if noc_states:
				noc_filters["workflow_state"] = ["in", noc_states]
			else:
				noc_filters["workflow_state"] = ["in", ["Pending Review"]]
		else:
			noc_filters["docstatus"] = 0

		nocs = frappe.get_all(
			"Student NOC",
			filters=noc_filters,
			fields=["name", "student", "student_name", "noc_type", "purpose", "application_date", "creation", "program", "supporting_document"],
			order_by="creation desc",
			ignore_permissions=True
		)
		
		for noc in nocs:
			enhanced_apps.append({
				"app_type": "NOC",
				"name": noc.name,
				"student": noc.student,
				"student_name": noc.student_name,
				"date_range": str(noc.application_date),
				"reason": noc.purpose,
				"noc_type": noc.noc_type,
				"group_info": noc.program or "N/A",
				"supporting_document": noc.supporting_document,
				"creation": str(noc.creation)
			})
	
	# Sort combined by creation
	enhanced_apps.sort(key=lambda x: x.get("creation", ""), reverse=True)
	
	return enhanced_apps


@frappe.whitelist()
def get_teacher_leave_statistics():
	"""Get application approval statistics for teacher dashboard."""
	from vidyaan.api_folder.profile import _get_instructor_for_user
	instructor = _get_instructor_for_user()
	if not instructor:
		frappe.throw("You are not registered as an Instructor.")
	
	# Get instructor's student groups and students
	assigned_groups = frappe.get_all(
		"Student Group Instructor",
		filters={"instructor": instructor.name},
		pluck="parent",
		ignore_permissions=True
	)
	schedule_groups = frappe.get_all(
		"Course Schedule",
		filters={"instructor": instructor.name},
		pluck="student_group",
		distinct=True,
		ignore_permissions=True
	)
	all_groups = list(set(assigned_groups + schedule_groups))
	
	students = []
	if all_groups:
		students = frappe.get_all(
			"Student Group Student",
			filters={"parent": ["in", all_groups], "active": 1},
			pluck="student",
			ignore_permissions=True
		)

	if not students:
		return {"pending": 0, "approved": 0, "rejected": 0, "total": 0}

	# Leaves
	leave_meta = frappe.get_meta("Student Leave Application")
	if leave_meta.has_field("workflow_state"):
		total_pending = frappe.db.count(
			"Student Leave Application",
			filters={"workflow_state": "Pending Review", "student": ["in", students]}
		)
	else:
		total_pending = frappe.db.count(
			"Student Leave Application",
			filters={"docstatus": 0, "student": ["in", students]}
		)
	total_approved = frappe.db.count(
		"Student Leave Application",
		filters={"workflow_state": "Approved", "docstatus": 1, "student": ["in", students]}
	)
	total_rejected = frappe.db.count(
		"Student Leave Application",
		filters={"workflow_state": "Rejected", "student": ["in", students]}
	)

	# NOCs
	if frappe.db.exists("DocType", "Student NOC"):
		noc_states = _get_allowed_workflow_states("Student NOC")
		noc_meta = frappe.get_meta("Student NOC")
		if noc_meta.has_field("workflow_state"):
			if noc_states:
				total_pending += frappe.db.count(
					"Student NOC",
					filters={"workflow_state": ["in", noc_states], "student": ["in", students]}
				)
			else:
				total_pending += frappe.db.count(
					"Student NOC",
					filters={"workflow_state": ["in", ["Pending Review"]], "student": ["in", students]}
				)
		else:
			total_pending += frappe.db.count(
				"Student NOC",
				filters={"docstatus": 0, "student": ["in", students]}
			)
		total_approved += frappe.db.count(
			"Student NOC",
			filters={"workflow_state": "Approved", "docstatus": 1, "student": ["in", students]}
		)
		total_rejected += frappe.db.count(
			"Student NOC",
			filters={"workflow_state": "Rejected", "student": ["in", students]}
		)

	return {
		"pending": total_pending,
		"approved": total_approved,
		"rejected": total_rejected,
		"total": total_pending + total_approved + total_rejected
	}

# @frappe.whitelist()
# def review_application(name, action, app_type="Leave"):
# 	"""Teacher action to approve or reject a pending leave or noc application."""
# 	from vidyaan.api_folder.profile import _get_instructor_for_user
# 	if not _get_instructor_for_user():
# 		frappe.throw("You must be an instructor to perform this action")
		
# 	if action not in ["Approve", "Reject"]:
# 		frappe.throw("Invalid action. Must be Approve or Reject")
	
# 	doctype = "Student Leave Application" if app_type == "Leave" else "Student NOC"
# 	allowed_states = _get_allowed_workflow_states(doctype)
# 	if allowed_states:
# 		if frappe.get_value(doctype, name, "workflow_state") not in allowed_states:
# 			frappe.throw("Application is not in a state you can review")
# 	else:
# 		if frappe.get_value(doctype, name, "workflow_state") != "Pending Teacher Approval":
# 			frappe.throw("Application is not in a pending state")
		
# 	doc = frappe.get_doc(doctype, name)
# 	# Change workflow state depending on transition configuration
# 	if action == "Approve":
# 		doc.workflow_state = "Pending Admin Approval"
# 	else:
# 		doc.workflow_state = "Rejected"
		
# 	# Simulate workflow transition via code
# 	doc.save(ignore_permissions=True)
	
# 	return {"success": True, "state": doc.workflow_state}

@frappe.whitelist()
def review_application(name, action, app_type="Leave", reason=None):
    from vidyaan.api_folder.profile import _get_instructor_for_user
    if not _get_instructor_for_user():
        frappe.throw("You must be an instructor to perform this action")

    if action not in ["Approve", "Reject"]:
        frappe.throw("Invalid action. Must be Approve or Reject")

    doctype = "Student Leave Application" if app_type == "Leave" else "Student NOC"
    allowed_states = _get_allowed_workflow_states(doctype)

    current_state = frappe.get_value(doctype, name, "workflow_state")
    if allowed_states and current_state not in allowed_states:
        frappe.throw("Application is not in a state you can review")

    doc = frappe.get_doc(doctype, name)

    # Let Frappe resolve the correct next state from the workflow definition
    from frappe.model.workflow import apply_workflow
    apply_workflow(doc, action)  # "Approve" or "Reject"

    # Save rejection reason as a comment if provided
    if action == "Reject" and reason:
        doc.add_comment("Comment", text=reason)

    return {"success": True, "state": doc.workflow_state}
