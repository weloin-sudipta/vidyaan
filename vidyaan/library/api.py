import frappe
from frappe.utils import getdate, today, date_diff, add_days


def get_member_for_user(user, library=None):
	"""Resolve Library Member by user email or user field."""
	filters1 = {"user": user}
	filters2 = {"email": user}
	if library:
		filters1["library"] = library
		filters2["library"] = library

	member = frappe.db.get_value("Library Member", filters1, "name")
	if not member:
		member = frappe.db.get_value("Library Member", filters2, "name")
	return member


@frappe.whitelist()
def get_catalog():
	"""Get all books with inventory counts computed from Book Copy aggregation."""
	books = frappe.db.sql(
		"""
		SELECT
			b.name,
			b.title,
			b.author,
			b.category,
			b.book_type as copy_type,
			b.isbn,
			b.library,
			b.cover_image,
			b.shelf,
			COUNT(bc.name) as total_copies,
			SUM(CASE WHEN bc.status = 'Available' THEN 1 ELSE 0 END) as available_copies
		FROM `tabBook` b
		LEFT JOIN `tabBook Copy` bc ON bc.book = b.name
		GROUP BY b.name
		ORDER BY b.title ASC
		""",
		as_dict=True,
	)
	return books


@frappe.whitelist()
def get_my_issues():
	"""Return all Book Issue records for the logged-in user."""
	user = frappe.session.user
	member_name = get_member_for_user(user)

	if not member_name:
		return []

	issues = frappe.get_list(
		"Book Issue",
		filters={"member": member_name, "status": ["in", ["Issued", "Overdue"]]},
		fields=[
			"name", "book", "book_copy",
			"issue_date", "due_date", "return_date",
			"status", "fine_amount", "library",
			"renew_requested", "renewal_count",
		],
		order_by="issue_date desc",
	)

	current_date = getdate(today())
	for issue in issues:
		book_title, book_isbn = frappe.db.get_value("Book", issue["book"], ["title", "isbn"])
		issue["book_title"] = book_title
		issue["book_isbn"] = book_isbn

		due_date = getdate(issue["due_date"])
		days_diff = date_diff(due_date, current_date)

		issue["is_overdue"] = issue["status"] == "Issued" and days_diff < 0
		issue["days_left"] = max(0, days_diff) if issue["status"] == "Issued" else 0
		issue["days_overdue"] = max(0, abs(days_diff)) if issue["is_overdue"] else 0

	return issues


@frappe.whitelist()
def get_my_requests():
	"""Return all active Book Requests for the logged-in user."""
	user = frappe.session.user
	member_name = get_member_for_user(user)

	if not member_name:
		return []

	requests = frappe.get_list(
		"Book Request",
		filters={"member": member_name},
		fields=["*"],
		order_by="creation desc",
	)

	for req in requests:
		book_title = frappe.db.get_value("Book", req["book"], "title")
		req["book_title"] = book_title

	return requests


@frappe.whitelist()
def request_book(book, library):
	"""Create a new book request with queue priority."""
	user = frappe.session.user

	if not library:
		frappe.throw("This book has not been assigned to a Library! Please update the Book record in the Frappe backend first.")

	member_name = get_member_for_user(user, library=library)

	if not member_name:
		frappe.throw("You must be a registered member of this library to request a book.")

	existing_req = frappe.db.exists("Book Request", {
		"member": member_name,
		"book": book,
		"status": ["in", ["Pending", "Approved"]],
	})

	if existing_req:
		frappe.throw("You already have an active request for this book.")

	existing_issue = frappe.db.exists("Book Issue", {
		"member": member_name,
		"book": book,
		"status": "Issued",
	})

	if existing_issue:
		frappe.throw("You already have a physical copy of this book currently issued to you. Please return it before requesting another copy.")

	pending_count = frappe.db.count("Book Request", filters={
		"book": book,
		"library": library,
		"status": "Pending",
	})

	priority_num = pending_count + 1

	req_doc = frappe.get_doc({
		"doctype": "Book Request",
		"library": library,
		"member": member_name,
		"book": book,
		"date": today(),
		"status": "Pending",
		"priority": priority_num,
	})

	req_doc.insert(ignore_permissions=True)

	return {
		"success": True,
		"request_id": req_doc.name,
		"queue_position": priority_num,
	}


@frappe.whitelist()
def cancel_request(request_name):
	"""Cancel a Pending request and reorganize queue priority."""
	req_doc = frappe.get_doc("Book Request", request_name)
	user = frappe.session.user
	member_name = get_member_for_user(user)

	if req_doc.member != member_name:
		frappe.throw("You can only cancel your own requests.")

	if req_doc.status != "Pending":
		frappe.throw(f"You can only cancel Pending requests. This request is currently {req_doc.status}.")

	book = req_doc.book
	library = req_doc.library
	canceled_priority = req_doc.priority

	req_doc.status = "Cancelled"
	req_doc.priority = 0
	req_doc.save(ignore_permissions=True)

	frappe.db.sql(
		"""
		UPDATE `tabBook Request`
		SET priority = priority - 1
		WHERE book = %s
		  AND library = %s
		  AND status = 'Pending'
		  AND priority > %s
		""",
		(book, library, canceled_priority),
	)

	return {"success": True, "message": "Request cancelled successfully."}


@frappe.whitelist()
def renew_book(issue_name):
	"""Request renewal for an Issued book (blocked if reservations exist)."""
	issue_doc = frappe.get_doc("Book Issue", issue_name)
	user = frappe.session.user
	member_name = get_member_for_user(user)

	if issue_doc.member != member_name:
		frappe.throw("You can only renew your own issued books.")

	if issue_doc.status != "Issued":
		frappe.throw("You can only renew books currently marked as Issued.")

	# Check max renewals
	library_doc = frappe.get_doc("Library", issue_doc.library)
	max_renewals = library_doc.max_renewals or 2
	if (issue_doc.renewal_count or 0) >= max_renewals:
		frappe.throw(f"Maximum renewal limit ({max_renewals}) reached for this book.")

	waiting_requests = frappe.db.count("Book Request", {
		"book": issue_doc.book,
		"library": issue_doc.library,
		"status": "Pending",
	})

	if waiting_requests > 0:
		frappe.throw(f"This book cannot be renewed because {waiting_requests} other member(s) are currently waiting for it.")

	issue_doc.db_set("renew_requested", 1)

	return {
		"success": True,
		"message": "Renewal requested successfully",
	}


@frappe.whitelist()
def approve_renewal(issue_name):
	"""Approve a pending renewal request to extend the due date."""
	roles = frappe.get_roles()
	if "Librarian" not in roles and "System Manager" not in roles:
		frappe.throw("Not permitted to approve renewals.")

	issue_doc = frappe.get_doc("Book Issue", issue_name)

	if not issue_doc.renew_requested:
		frappe.throw("No renewal request found for this issue.")

	library_doc = frappe.get_doc("Library", issue_doc.library)
	duration = library_doc.issue_duration_days or 14

	new_due_date = add_days(issue_doc.due_date, duration)
	issue_doc.due_date = new_due_date
	issue_doc.renew_requested = 0
	issue_doc.renewal_count = (issue_doc.renewal_count or 0) + 1
	issue_doc.save(ignore_permissions=True)

	return {
		"success": True,
		"new_due_date": new_due_date,
	}


@frappe.whitelist()
def get_member_details():
	"""Get current user's library member profile."""
	return frappe.get_all(
		"Library Member",
		filters={"user": frappe.session.user},
		fields=["*"],
	)


@frappe.whitelist()
def get_book_recommendations():
	"""
	Netflix-style book recommendation engine.
	Returns up to 5 sections with max 8 books each (40 total).
	Cached per-user with 6-hour TTL.
	"""
	user = frappe.session.user
	cache_key = f"book_recommendations:{user}"

	cached = frappe.cache().get_value(cache_key)
	if cached:
		return cached

	member_name = get_member_for_user(user)
	sections = []

	if member_name:
		# Section 1: Based on Your Reading History
		history_section = _get_history_based_recommendations(member_name)
		if history_section:
			sections.append(history_section)

		# Section 2: Because You Read [X]
		tag_section = _get_tag_based_recommendations(member_name)
		if tag_section:
			sections.append(tag_section)

	# Section 3: Popular in Your Library
	popular_section = _get_popular_books(member_name)
	if popular_section:
		sections.append(popular_section)

	if member_name:
		# Section 4: Students Also Borrowed
		collab_section = _get_collaborative_recommendations(member_name)
		if collab_section:
			sections.append(collab_section)

		# Section 5: For Your Program (school mode only)
		program_section = _get_program_recommendations(member_name)
		if program_section:
			sections.append(program_section)

	result = {"sections": sections}

	frappe.cache().set_value(cache_key, result, expires_in_sec=21600)  # 6 hours

	return result


def _get_user_read_books(member_name):
	"""Get set of book IDs the member has borrowed."""
	return set(
		frappe.db.sql_list(
			"SELECT DISTINCT book FROM `tabBook Issue` WHERE member = %s",
			member_name,
		)
	)


def _get_history_based_recommendations(member_name):
	"""Top categories by borrow frequency -> unread books in those categories."""
	top_categories = frappe.db.sql(
		"""
		SELECT b.category, COUNT(*) as cnt
		FROM `tabBook Issue` bi
		JOIN `tabBook` b ON b.name = bi.book
		WHERE bi.member = %s AND b.category IS NOT NULL AND b.category != ''
		GROUP BY b.category
		ORDER BY cnt DESC
		LIMIT 3
		""",
		member_name,
		as_dict=True,
	)

	if not top_categories:
		return None

	read_books = _get_user_read_books(member_name)
	categories = [c["category"] for c in top_categories]

	books = frappe.db.sql(
		"""
		SELECT b.name, b.title, b.author, b.category, b.cover_image, b.book_type
		FROM `tabBook` b
		WHERE b.category IN ({placeholders})
		ORDER BY b.upload_date DESC
		LIMIT 20
		""".format(placeholders=", ".join(["%s"] * len(categories))),
		categories,
		as_dict=True,
	)

	filtered = [b for b in books if b["name"] not in read_books][:8]

	if not filtered:
		return None

	return {
		"title": "Based on Your Reading History",
		"subtitle": "Books in categories you love",
		"badge": "Personalized",
		"icon": "fa-solid fa-book-open",
		"books": _format_books(filtered),
	}


def _get_tag_based_recommendations(member_name):
	"""Tags from last 5 borrowed books -> books sharing 2+ tags."""
	recent_books = frappe.db.sql_list(
		"""
		SELECT DISTINCT bi.book
		FROM `tabBook Issue` bi
		WHERE bi.member = %s
		ORDER BY bi.issue_date DESC
		LIMIT 5
		""",
		member_name,
	)

	if not recent_books:
		return None

	# Get tags from those books
	tags = frappe.db.sql_list(
		"""
		SELECT DISTINCT bt.tag_name
		FROM `tabBook Tag` bt
		WHERE bt.parent IN ({placeholders}) AND bt.parenttype = 'Book'
		""".format(placeholders=", ".join(["%s"] * len(recent_books))),
		recent_books,
	)

	if len(tags) < 1:
		return None

	read_books = _get_user_read_books(member_name)

	# Find books with 2+ matching tags
	books = frappe.db.sql(
		"""
		SELECT b.name, b.title, b.author, b.category, b.cover_image, b.book_type,
		       COUNT(bt.tag_name) as tag_match
		FROM `tabBook` b
		JOIN `tabBook Tag` bt ON bt.parent = b.name AND bt.parenttype = 'Book'
		WHERE bt.tag_name IN ({placeholders})
		GROUP BY b.name
		HAVING tag_match >= LEAST(2, {tag_count})
		ORDER BY tag_match DESC
		LIMIT 8
		""".format(
			placeholders=", ".join(["%s"] * len(tags)),
			tag_count=len(tags),
		),
		tags,
		as_dict=True,
	)

	filtered = [b for b in books if b["name"] not in read_books][:8]

	if not filtered:
		return None

	last_title = frappe.db.get_value("Book", recent_books[0], "title") or "your recent reads"

	return {
		"title": f"Because You Read \"{last_title}\"",
		"subtitle": "Books with similar themes and topics",
		"badge": "Similar",
		"icon": "fa-solid fa-lightbulb",
		"books": _format_books(filtered),
	}


def _get_popular_books(member_name=None):
	"""Most-issued books the user hasn't read."""
	read_books = _get_user_read_books(member_name) if member_name else set()

	books = frappe.db.sql(
		"""
		SELECT b.name, b.title, b.author, b.category, b.cover_image, b.book_type,
		       COUNT(bi.name) as issue_count
		FROM `tabBook` b
		JOIN `tabBook Issue` bi ON bi.book = b.name
		GROUP BY b.name
		ORDER BY issue_count DESC
		LIMIT 16
		""",
		as_dict=True,
	)

	filtered = [b for b in books if b["name"] not in read_books][:8]

	if not filtered:
		return None

	return {
		"title": "Popular in Your Library",
		"subtitle": "Most borrowed books by all members",
		"badge": "Trending",
		"icon": "fa-solid fa-fire",
		"books": _format_books(filtered),
	}


def _get_collaborative_recommendations(member_name):
	"""Find members with overlapping taste -> their other borrows."""
	my_books = _get_user_read_books(member_name)
	if len(my_books) < 2:
		return None

	book_list = list(my_books)

	# Find members who read at least 2 of the same books
	similar_members = frappe.db.sql_list(
		"""
		SELECT bi.member
		FROM `tabBook Issue` bi
		WHERE bi.book IN ({placeholders}) AND bi.member != %s
		GROUP BY bi.member
		HAVING COUNT(DISTINCT bi.book) >= 2
		LIMIT 10
		""".format(placeholders=", ".join(["%s"] * len(book_list))),
		book_list + [member_name],
	)

	if not similar_members:
		return None

	# Get books those similar members read that we haven't
	books = frappe.db.sql(
		"""
		SELECT b.name, b.title, b.author, b.category, b.cover_image, b.book_type,
		       COUNT(DISTINCT bi.member) as member_count
		FROM `tabBook Issue` bi
		JOIN `tabBook` b ON b.name = bi.book
		WHERE bi.member IN ({placeholders})
		GROUP BY b.name
		ORDER BY member_count DESC
		LIMIT 16
		""".format(placeholders=", ".join(["%s"] * len(similar_members))),
		similar_members,
		as_dict=True,
	)

	filtered = [b for b in books if b["name"] not in my_books][:8]

	if not filtered:
		return None

	return {
		"title": "Students Also Borrowed",
		"subtitle": "Readers with similar taste enjoyed these",
		"badge": "Collaborative",
		"icon": "fa-solid fa-users",
		"books": _format_books(filtered),
	}


def _get_program_recommendations(member_name):
	"""Books borrowed by students in the same program (school mode only)."""
	# Get user -> student -> active program enrollment
	user = frappe.db.get_value("Library Member", member_name, "user")
	if not user:
		return None

	student = frappe.db.get_value("Student", {"user": user}, "name")
	if not student:
		return None

	program = frappe.db.get_value(
		"Program Enrollment",
		{"student": student, "docstatus": 1},
		"program",
		order_by="creation desc",
	)
	if not program:
		return None

	# Find other students in the same program
	classmates = frappe.db.sql_list(
		"""
		SELECT s.user
		FROM `tabProgram Enrollment` pe
		JOIN `tabStudent` s ON s.name = pe.student
		WHERE pe.program = %s AND pe.docstatus = 1 AND s.user != %s AND s.user IS NOT NULL
		""",
		(program, user),
	)

	if not classmates:
		return None

	# Get their library member IDs
	classmate_members = frappe.db.sql_list(
		"""
		SELECT name FROM `tabLibrary Member`
		WHERE user IN ({placeholders})
		""".format(placeholders=", ".join(["%s"] * len(classmates))),
		classmates,
	)

	if not classmate_members:
		return None

	my_books = _get_user_read_books(member_name)

	books = frappe.db.sql(
		"""
		SELECT b.name, b.title, b.author, b.category, b.cover_image, b.book_type,
		       COUNT(DISTINCT bi.member) as popularity
		FROM `tabBook Issue` bi
		JOIN `tabBook` b ON b.name = bi.book
		WHERE bi.member IN ({placeholders})
		GROUP BY b.name
		ORDER BY popularity DESC
		LIMIT 16
		""".format(placeholders=", ".join(["%s"] * len(classmate_members))),
		classmate_members,
		as_dict=True,
	)

	filtered = [b for b in books if b["name"] not in my_books][:8]

	if not filtered:
		return None

	program_name = frappe.db.get_value("Program", program, "program_name") or program

	return {
		"title": f"For Your Program",
		"subtitle": f"Popular among {program_name} students",
		"badge": "Program",
		"icon": "fa-solid fa-graduation-cap",
		"books": _format_books(filtered),
	}


def _format_books(books):
	"""Format book records for API response."""
	formatted = []
	for b in books:
		formatted.append({
			"id": b["name"],
			"title": b["title"],
			"author": b.get("author") or "",
			"category": b.get("category") or "",
			"cover_image": b.get("cover_image") or "",
			"book_type": b.get("book_type") or b.get("copy_type") or "Physical",
		})
	return formatted


# ─── Admin / Librarian APIs ──────────────────────────────────────────────────


def _check_librarian():
	"""Verify current user is a Librarian or System Manager."""
	roles = frappe.get_roles()
	if "Librarian" not in roles and "System Manager" not in roles:
		frappe.throw("Only Librarians or System Managers can access this.")


@frappe.whitelist()
def get_library_stats():
	"""Dashboard stats for the librarian admin panel."""
	_check_librarian()

	total_books = frappe.db.count("Book") or 0
	total_copies = frappe.db.count("Book Copy") or 0
	available_copies = frappe.db.count("Book Copy", {"status": "Available"}) or 0
	issued_copies = frappe.db.count("Book Copy", {"status": "Issued"}) or 0
	total_members = frappe.db.count("Library Member", {"status": "Active"}) or 0
	pending_requests = frappe.db.count("Book Request", {"status": "Pending"}) or 0
	active_issues = frappe.db.count("Book Issue", {"status": "Issued"}) or 0

	overdue_issues = frappe.db.sql(
		"""
		SELECT COUNT(*) FROM `tabBook Issue`
		WHERE status = 'Issued' AND due_date < CURDATE()
		""",
	)[0][0] or 0

	pending_renewals = frappe.db.count("Book Issue", {"status": "Issued", "renew_requested": 1}) or 0

	total_fines = frappe.db.sql(
		"SELECT COALESCE(SUM(fine_amount), 0) FROM `tabBook Issue` WHERE fine_amount > 0"
	)[0][0] or 0

	# Books with low stock (available <= 1 but total > 0)
	low_stock = frappe.db.sql(
		"""
		SELECT COUNT(DISTINCT bc_all.book) FROM `tabBook Copy` bc_all
		WHERE bc_all.book IN (
			SELECT book FROM `tabBook Copy` GROUP BY book
			HAVING SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) <= 1
			   AND COUNT(*) > 1
		)
		"""
	)[0][0] or 0

	return {
		"total_books": total_books,
		"total_copies": total_copies,
		"available_copies": available_copies,
		"issued_copies": issued_copies,
		"total_members": total_members,
		"pending_requests": pending_requests,
		"active_issues": active_issues,
		"overdue_issues": overdue_issues,
		"pending_renewals": pending_renewals,
		"total_fines": total_fines,
		"low_stock": low_stock,
	}


@frappe.whitelist()
def get_inventory():
	"""Get all books with copy counts for admin inventory view."""
	_check_librarian()

	books = frappe.db.sql(
		"""
		SELECT
			b.name, b.title, b.author, b.isbn, b.category, b.book_type,
			b.shelf, b.library, b.cover_image, b.publisher, b.language,
			COUNT(bc.name) as total_copies,
			SUM(CASE WHEN bc.status = 'Available' THEN 1 ELSE 0 END) as available_copies,
			SUM(CASE WHEN bc.status = 'Issued' THEN 1 ELSE 0 END) as issued_copies
		FROM `tabBook` b
		LEFT JOIN `tabBook Copy` bc ON bc.book = b.name
		GROUP BY b.name
		ORDER BY b.title ASC
		""",
		as_dict=True,
	)
	return books


@frappe.whitelist()
def get_all_issues(status=None):
	"""Get all book issues for admin (optionally filtered by status)."""
	_check_librarian()

	filters = {}
	if status:
		if status == "Overdue":
			# Special handling: Issued but past due date
			issues = frappe.db.sql(
				"""
				SELECT bi.name, bi.library, bi.member, bi.book, bi.book_copy,
				       bi.issue_date, bi.due_date, bi.return_date, bi.status,
				       bi.fine_amount, bi.renew_requested, bi.renewal_count,
				       b.title as book_title, b.author as book_author, b.isbn as book_isbn,
				       lm.member_name, lm.member_type, lm.email as member_email
				FROM `tabBook Issue` bi
				JOIN `tabBook` b ON b.name = bi.book
				JOIN `tabLibrary Member` lm ON lm.name = bi.member
				WHERE bi.status = 'Issued' AND bi.due_date < CURDATE()
				ORDER BY bi.due_date ASC
				""",
				as_dict=True,
			)
			_enrich_issues(issues)
			return issues
		else:
			filters["status"] = status

	query = """
		SELECT bi.name, bi.library, bi.member, bi.book, bi.book_copy,
		       bi.issue_date, bi.due_date, bi.return_date, bi.status,
		       bi.fine_amount, bi.renew_requested, bi.renewal_count,
		       b.title as book_title, b.author as book_author, b.isbn as book_isbn,
		       lm.member_name, lm.member_type, lm.email as member_email
		FROM `tabBook Issue` bi
		JOIN `tabBook` b ON b.name = bi.book
		JOIN `tabLibrary Member` lm ON lm.name = bi.member
		{where}
		ORDER BY bi.issue_date DESC
		LIMIT 200
	"""
	if status:
		issues = frappe.db.sql(query.format(where="WHERE bi.status = %s"), (status,), as_dict=True)
	else:
		issues = frappe.db.sql(query.format(where=""), as_dict=True)

	_enrich_issues(issues)
	return issues


def _enrich_issues(issues):
	"""Add computed fields to issue records."""
	current_date = getdate(today())
	for issue in issues:
		due = getdate(issue["due_date"])
		days_diff = date_diff(due, current_date)
		issue["is_overdue"] = issue["status"] == "Issued" and days_diff < 0
		issue["days_left"] = max(0, days_diff) if not issue["is_overdue"] else 0
		issue["days_overdue"] = abs(days_diff) if issue["is_overdue"] else 0


@frappe.whitelist()
def get_all_requests(status=None):
	"""Get all book requests for admin."""
	_check_librarian()

	query = """
		SELECT br.name, br.library, br.member, br.book, br.request_date,
		       br.status, br.priority, br.assigned_copy, br.remarks,
		       b.title as book_title, b.author as book_author,
		       lm.member_name, lm.member_type
		FROM `tabBook Request` br
		JOIN `tabBook` b ON b.name = br.book
		JOIN `tabLibrary Member` lm ON lm.name = br.member
		{where}
		ORDER BY br.creation DESC
		LIMIT 200
	"""
	if status:
		requests = frappe.db.sql(query.format(where="WHERE br.status = %s"), (status,), as_dict=True)
	else:
		requests = frappe.db.sql(query.format(where=""), as_dict=True)
	return requests


@frappe.whitelist()
def get_all_members():
	"""Get all library members for admin."""
	_check_librarian()

	members = frappe.get_all(
		"Library Member",
		fields=[
			"name", "member_name", "member_type", "library", "email",
			"phone", "status", "max_books_allowed", "current_issued_books",
			"join_date", "user",
		],
		order_by="member_name asc",
		limit=500,
	)
	return members


@frappe.whitelist()
def return_book(issue_name):
	"""Process a book return (librarian action)."""
	_check_librarian()

	issue_doc = frappe.get_doc("Book Issue", issue_name)
	if issue_doc.status != "Issued":
		frappe.throw(f"This book issue is already {issue_doc.status}.")

	issue_doc.status = "Returned"
	issue_doc.return_date = today()
	issue_doc.save(ignore_permissions=True)

	return {
		"success": True,
		"fine_amount": issue_doc.fine_amount or 0,
		"message": "Book returned successfully.",
	}


@frappe.whitelist()
def approve_request(request_name):
	"""Approve a pending book request (librarian action)."""
	_check_librarian()

	req_doc = frappe.get_doc("Book Request", request_name)
	if req_doc.status != "Pending":
		frappe.throw(f"Request is {req_doc.status}, not Pending.")

	req_doc.status = "Approved"
	req_doc.approved_by = frappe.session.user
	req_doc.approval_date = frappe.utils.now()
	req_doc.save(ignore_permissions=True)

	return {"success": True, "message": "Request approved successfully."}


@frappe.whitelist()
def reject_request(request_name, remarks=None):
	"""Reject a pending book request."""
	_check_librarian()

	req_doc = frappe.get_doc("Book Request", request_name)
	if req_doc.status != "Pending":
		frappe.throw(f"Request is {req_doc.status}, not Pending.")

	req_doc.status = "Rejected"
	if remarks:
		req_doc.remarks = remarks
	req_doc.save(ignore_permissions=True)

	return {"success": True, "message": "Request rejected."}


@frappe.whitelist()
def issue_from_request(request_name):
	"""Create a Book Issue from an approved request (librarian action)."""
	_check_librarian()

	req_doc = frappe.get_doc("Book Request", request_name)
	return req_doc.create_book_issue()
