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
			filters={"student": student, "docstatus": ["<", 2]},
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
			filters={"student": student, "docstatus": ["<", 2]},
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
			filters={"student": student, "docstatus": ["<", 2]},
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

	# Attach workflow steps to each application
	wf_cache = {}
	for app in applications:
		dt = app["doctype"]
		if dt not in wf_cache:
			wf_cache[dt] = _get_workflow_steps(dt)
		app["workflow_steps"] = wf_cache[dt]

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
def submit_noc(noc_type, purpose, effective_date=None, destination=None):
	student = _get_student_for_user()
	if not student:
		frappe.throw("You are not registered as a student.")

	doc = frappe.get_doc({
		"doctype": "Student NOC",
		"student": student,
		"noc_type": noc_type,
		"purpose": purpose,
		"effective_date": effective_date or None,
		"destination": destination or None,
	})
	doc.insert(ignore_permissions=True)
	try:
		doc.submit()
	except Exception:
		pass  # Submit may fail if workflow requires approval
	return {"success": True, "name": doc.name}


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
		doc.submit()
	except Exception:
		pass  # Submit may fail if workflow requires approval
	return {"success": True, "name": doc.name}


@frappe.whitelist()
def submit_leave(from_date, to_date, reason=None, student_group=None):
	student = _get_student_for_user()
	if not student:
		frappe.throw("You are not registered as a student.")

	# Auto-resolve student group if not provided
	if not student_group:
		groups = frappe.get_all(
			"Student Group Student",
			filters={"student": student, "active": 1},
			pluck="parent",
			limit=1
		)
		student_group = groups[0] if groups else None

	doc = frappe.get_doc({
		"doctype": "Student Leave Application",
		"student": student,
		"from_date": from_date,
		"to_date": to_date,
		"reason": reason or "",
		"attendance_based_on": "Student Group" if student_group else "",
		"student_group": student_group,
	})
	doc.insert(ignore_permissions=True)
	try:
		doc.submit()
	except Exception:
		pass  # Submit may fail if workflow or validation prevents it
	return {"success": True, "name": doc.name}
