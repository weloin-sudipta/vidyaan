"""
Vidyaan Test Data Generator
============================
Creates comprehensive test data for full frontend testing of the Vidyaan School ERP.

Usage:
    bench --site <site-name> execute vidyaan.tests.create_test_data.create_all
    bench --site <site-name> execute vidyaan.tests.create_test_data.delete_all

This script creates:
    - Company (School)
    - Academic Year & Terms
    - Programs (Classes) & Courses (Subjects)
    - Rooms (Classrooms)
    - Instructors (Teachers)
    - Students & Guardians
    - Student Groups (Sections)
    - Program Enrollments
    - Course Schedules (Timetable entries)
    - Student Attendance records
    - Assessment Plans & Results (Exams + Assignments)
    - Fee Structure & Fees
    - Grading Scale
    - Library data (Library, Categories, Books, Copies, Members, Issues, Requests)
    - Publications (Notices, News, Announcements)
    - Student NOCs
    - Student Requests
    - Routine Generation
    - Vidyaan Settings
"""

import frappe
from frappe.utils import today, add_days, add_months, getdate, nowdate, now_datetime
import random
import json

# ─── Constants ────────────────────────────────────────────────────────────────

COMPANY_NAME = "Vidyaan Demo School"
COMPANY_ABBR = "VDS"
ACADEMIC_YEAR = "2026-2027"
TERM_1 = "First Term"
TERM_2 = "Second Term"

PROGRAMS = [
    {"name": "Class 1", "program_abbreviation": "C1"},
    {"name": "Class 2", "program_abbreviation": "C2"},
    {"name": "Class 3", "program_abbreviation": "C3"},
    {"name": "Class 4", "program_abbreviation": "C4"},
    {"name": "Class 5", "program_abbreviation": "C5"},
    {"name": "Class 6", "program_abbreviation": "C6"},
    {"name": "Class 7", "program_abbreviation": "C7"},
    {"name": "Class 8", "program_abbreviation": "C8"},
    {"name": "Class 9", "program_abbreviation": "C9"},
    {"name": "Class 10", "program_abbreviation": "C10"},
]

COURSES = [
    "English", "Mathematics", "Science", "Social Studies", "Hindi",
    "Computer Science", "Physical Education", "Art & Craft",
    "Moral Science", "Environmental Studies",
]

ROOMS = [
    {"room_name": "Room 101", "room_number": "101", "seating_capacity": 40},
    {"room_name": "Room 102", "room_number": "102", "seating_capacity": 40},
    {"room_name": "Room 103", "room_number": "103", "seating_capacity": 40},
    {"room_name": "Room 201", "room_number": "201", "seating_capacity": 35},
    {"room_name": "Room 202", "room_number": "202", "seating_capacity": 35},
    {"room_name": "Room 203", "room_number": "203", "seating_capacity": 35},
    {"room_name": "Computer Lab", "room_number": "LAB1", "seating_capacity": 30},
    {"room_name": "Science Lab", "room_number": "LAB2", "seating_capacity": 30},
    {"room_name": "Art Room", "room_number": "ART1", "seating_capacity": 25},
    {"room_name": "Library Hall", "room_number": "LIB1", "seating_capacity": 50},
]

TEACHERS = [
    {"first": "Rajesh", "last": "Sharma", "gender": "Male", "subjects": ["Mathematics", "Science"]},
    {"first": "Priya", "last": "Verma", "gender": "Female", "subjects": ["English", "Hindi"]},
    {"first": "Amit", "last": "Patel", "gender": "Male", "subjects": ["Science", "Environmental Studies"]},
    {"first": "Sunita", "last": "Gupta", "gender": "Female", "subjects": ["Social Studies", "Moral Science"]},
    {"first": "Vikram", "last": "Singh", "gender": "Male", "subjects": ["Mathematics", "Computer Science"]},
    {"first": "Anjali", "last": "Desai", "gender": "Female", "subjects": ["English", "Art & Craft"]},
    {"first": "Deepak", "last": "Kumar", "gender": "Male", "subjects": ["Physical Education", "Moral Science"]},
    {"first": "Meena", "last": "Joshi", "gender": "Female", "subjects": ["Hindi", "Social Studies"]},
    {"first": "Ramesh", "last": "Nair", "gender": "Male", "subjects": ["Computer Science", "Mathematics"]},
    {"first": "Kavita", "last": "Reddy", "gender": "Female", "subjects": ["Science", "Environmental Studies"]},
    {"first": "Suresh", "last": "Yadav", "gender": "Male", "subjects": ["English", "Moral Science"]},
    {"first": "Neha", "last": "Agarwal", "gender": "Female", "subjects": ["Mathematics", "Science"]},
]

STUDENT_FIRST_NAMES_MALE = [
    "Arjun", "Rohan", "Aditya", "Karan", "Vivek", "Rahul", "Nikhil", "Siddharth",
    "Ankit", "Manish", "Pranav", "Harsh", "Dev", "Ishaan", "Varun",
]
STUDENT_FIRST_NAMES_FEMALE = [
    "Ananya", "Priya", "Riya", "Sneha", "Pooja", "Kavya", "Ishita", "Tanvi",
    "Meera", "Divya", "Nisha", "Shruti", "Aditi", "Sakshi", "Simran",
]
STUDENT_LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Reddy", "Nair",
    "Joshi", "Yadav", "Agarwal", "Desai", "Mehta", "Thakur", "Chauhan",
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

BOOK_DATA = [
    {"title": "The Adventures of Tom Sawyer", "author": "Mark Twain", "category": "Fiction", "isbn": "978-0-14-036673-3"},
    {"title": "A Brief History of Time", "author": "Stephen Hawking", "category": "Science", "isbn": "978-0-553-38016-3"},
    {"title": "Mathematics for Class 10", "author": "R.D. Sharma", "category": "Textbook", "isbn": "978-93-5253-001-1"},
    {"title": "NCERT Science Class 9", "author": "NCERT", "category": "Textbook", "isbn": "978-81-7450-001-1"},
    {"title": "The Story of My Experiments with Truth", "author": "M.K. Gandhi", "category": "Biography", "isbn": "978-0-14-044948-2"},
    {"title": "Wings of Fire", "author": "A.P.J. Abdul Kalam", "category": "Biography", "isbn": "978-81-7371-146-6"},
    {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "category": "Fiction", "isbn": "978-0-7475-3269-9"},
    {"title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "category": "History", "isbn": "978-0-06-231609-7"},
    {"title": "The Jungle Book", "author": "Rudyard Kipling", "category": "Fiction", "isbn": "978-0-14-118280-2"},
    {"title": "Panchatantra Stories", "author": "Vishnu Sharma", "category": "Mythology", "isbn": "978-81-291-1417-4"},
    {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "category": "Computer Science", "isbn": "978-0-262-03384-8"},
    {"title": "Environmental Studies for Class 5", "author": "NCERT", "category": "Textbook", "isbn": "978-81-7450-002-2"},
]

BOOK_CATEGORIES = ["Fiction", "Science", "Textbook", "Biography", "History", "Mythology", "Computer Science", "Reference"]

# Topics per course (3 topics each)
COURSE_TOPICS = {
    "English": ["Grammar & Composition", "Literature & Poetry", "Writing Skills"],
    "Mathematics": ["Algebra & Equations", "Geometry & Mensuration", "Statistics & Probability"],
    "Science": ["Physics - Motion & Force", "Chemistry - Elements & Compounds", "Biology - Life Processes"],
    "Social Studies": ["History - Ancient Civilizations", "Geography - Maps & Climate", "Civics - Government & Rights"],
    "Hindi": ["Vyakaran (Grammar)", "Gadya (Prose)", "Kavita (Poetry)"],
    "Computer Science": ["Programming Basics", "Computer Networks", "Data & Information"],
    "Physical Education": ["Sports & Athletics", "Health & Nutrition", "Yoga & Fitness"],
    "Art & Craft": ["Drawing & Sketching", "Painting Techniques", "Craft & Design"],
    "Moral Science": ["Values & Ethics", "Famous Leaders & Stories", "Social Responsibility"],
    "Environmental Studies": ["Ecosystems & Biodiversity", "Pollution & Conservation", "Natural Resources"],
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_create(doctype, filters, doc_data):
    """Get existing doc or create new one."""
    name = frappe.db.exists(doctype, filters)
    if name:
        return frappe.get_doc(doctype, name)
    doc = frappe.get_doc({"doctype": doctype, **doc_data})
    doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
    return doc


def _safe_submit(doc):
    """Submit a doc if it's in Draft state."""
    if doc.docstatus == 0:
        doc.submit()


def _ensure_holiday_list():
    """Create a default Holiday List and set it on the company if missing."""
    hl_name = f"School Holidays {ACADEMIC_YEAR}"
    if not frappe.db.exists("Holiday List", hl_name):
        hl = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": hl_name,
            "from_date": "2026-04-01",
            "to_date": "2027-03-31",
            "weekly_off": "Sunday",
        })
        hl.insert(ignore_permissions=True)

    # Set on all companies that don't have a default holiday list
    for company_name in [COMPANY_NAME] + frappe.get_all("Company", pluck="name"):
        current_hl = frappe.db.get_value("Company", company_name, "default_holiday_list")
        if not current_hl:
            frappe.db.set_value("Company", company_name, "default_holiday_list", hl_name)
    frappe.db.commit()


# ─── Creators ─────────────────────────────────────────────────────────────────

def _ensure_transit_warehouse_type():
    """Ensure the required ERPNext Warehouse Type exists before Company creation."""
    if not frappe.db.exists("Warehouse Type", "Transit"):
        frappe.get_doc({
            "doctype": "Warehouse Type",
            "name": "Transit",
            "warehouse_type": "Transit",
        }).insert(ignore_permissions=True, ignore_if_duplicate=True)
        frappe.db.commit()


def _ensure_default_company():
    """Ensure the current user has a valid default Company set."""
    try:
        frappe.defaults.set_user_default("Company", COMPANY_NAME, user="Administrator")
    except Exception:
        pass

    try:
        frappe.defaults.set_global_default("Company", COMPANY_NAME)
    except Exception:
        pass


def _ensure_genders():
    """Ensure basic gender records exist before creating Person records."""
    for gender in ["Male", "Female"]:
        if not frappe.db.exists("Gender", gender):
            frappe.get_doc({
                "doctype": "Gender",
                "gender": gender,
            }).insert(ignore_permissions=True, ignore_if_duplicate=True)
    frappe.db.commit()


def _ensure_uom():
    """Ensure basic UOMs exist."""
    print("Ensuring UOMs...")
    for uom in ["Unit", "Nos", "Each"]:
        if not frappe.db.exists("UOM", uom):
            try:
                frappe.get_doc({
                    "doctype": "UOM",
                    "uom_name": uom,
                    "name": uom
                }).insert(ignore_permissions=True, ignore_if_duplicate=True)
            except Exception:
                pass
    frappe.db.commit()
    print("  UOMs ensured.")


def _ensure_item_group():
    """Ensure 'Fee Component' Item Group exists."""
    print("Ensuring Item Group...")
    if not frappe.db.exists("Item Group", "Fee Component"):
        try:
            # Check for root item group
            root = frappe.db.get_value("Item Group", {"is_group": 1, "lft": 1}, "name")
            if not root:
                # Create a default root if missing
                root = "All Item Groups"
                if not frappe.db.exists("Item Group", root):
                    frappe.get_doc({
                        "doctype": "Item Group",
                        "item_group_name": root,
                        "is_group": 1,
                        "parent_item_group": ""
                    }).insert(ignore_permissions=True)

            frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": "Fee Component",
                "parent_item_group": root,
                "is_group": 0
            }).insert(ignore_permissions=True)
        except Exception as e:
            print(f"  Warning: Could not create Item Group: {e}")
    frappe.db.commit()
    print("  Item Groups ensured.")


def _ensure_income_account():
    """Ensure a default income account exists or set one."""
    # This is often needed by Fee Category -> Item logic
    account = frappe.db.get_value("Account", {"account_type": "Income Account", "company": COMPANY_NAME}, "name")
    if not account:
        # Try to find any income account
        account = frappe.db.get_value("Account", {"root_type": "Income", "company": COMPANY_NAME, "is_group": 0}, "name")

    if account:
        # Optionally set it on the Item Group if needed, but for now we just want to know it exists
        pass
    return account


def create_company():
    """Create the demo school company."""
    print("Creating Company...")
    if frappe.db.exists("Company", COMPANY_NAME):
        company = frappe.get_doc("Company", COMPANY_NAME)
        _ensure_default_company()
        return company

    _ensure_transit_warehouse_type()

    company = frappe.get_doc({
        "doctype": "Company",
        "company_name": COMPANY_NAME,
        "abbr": COMPANY_ABBR,
        "country": "India",
        "default_currency": "INR",
        "domain": "Education",
    })
    company.insert(ignore_permissions=True)
    frappe.db.commit()
    _ensure_default_company()
    return company


def create_academic_year():
    """Create academic year 2026-2027."""
    print("Creating Academic Year...")
    return _get_or_create("Academic Year", {"academic_year_name": ACADEMIC_YEAR}, {
        "academic_year_name": ACADEMIC_YEAR,
        "year_start_date": "2026-04-01",
        "year_end_date": "2027-03-31",
    })


def create_academic_terms():
    """Create two terms for the academic year."""
    print("Creating Academic Terms...")
    t1 = _get_or_create("Academic Term", {"term_name": TERM_1, "academic_year": ACADEMIC_YEAR}, {
        "term_name": TERM_1,
        "academic_year": ACADEMIC_YEAR,
        "term_start_date": "2026-04-01",
        "term_end_date": "2026-09-30",
    })
    t2 = _get_or_create("Academic Term", {"term_name": TERM_2, "academic_year": ACADEMIC_YEAR}, {
        "term_name": TERM_2,
        "academic_year": ACADEMIC_YEAR,
        "term_start_date": "2026-10-01",
        "term_end_date": "2027-03-31",
    })
    return t1, t2


def create_grading_scale():
    """Create a standard grading scale."""
    print("Creating Grading Scale...")
    if frappe.db.exists("Grading Scale", "Standard Grading"):
        return frappe.get_doc("Grading Scale", "Standard Grading")

    doc = frappe.get_doc({
        "doctype": "Grading Scale",
        "grading_scale_name": "Standard Grading",
        "description": "Standard grading scale for Vidyaan Demo School",
        "intervals": [
            {"grade_code": "A+", "threshold": 90, "grade_description": "Outstanding"},
            {"grade_code": "A", "threshold": 80, "grade_description": "Excellent"},
            {"grade_code": "B+", "threshold": 70, "grade_description": "Very Good"},
            {"grade_code": "B", "threshold": 60, "grade_description": "Good"},
            {"grade_code": "C+", "threshold": 50, "grade_description": "Above Average"},
            {"grade_code": "C", "threshold": 40, "grade_description": "Average"},
            {"grade_code": "D", "threshold": 33, "grade_description": "Below Average"},
            {"grade_code": "F", "threshold": 0, "grade_description": "Fail"},
        ]
    })
    doc.insert(ignore_permissions=True)
    return doc


def create_courses():
    """Create courses (subjects)."""
    print("Creating Courses...")
    created = []
    for course_name in COURSES:
        doc = _get_or_create("Course", {"course_name": course_name}, {
            "course_name": course_name,
            "course_abbreviation": course_name[:3].upper(),
            "company": COMPANY_NAME,
        })
        created.append(doc)
    return created


def create_topics_and_articles():
    """Create Topics for each course and sample Articles as study materials."""
    print("Creating Topics & Articles...")
    topic_count = 0
    article_count = 0

    for course_name, topic_names in COURSE_TOPICS.items():
        course_doc = frappe.db.exists("Course", course_name)
        if not course_doc:
            continue

        course = frappe.get_doc("Course", course_name)
        existing_topics = [ct.topic for ct in (course.get("topics") or [])]

        for t_idx, topic_name in enumerate(topic_names):
            # Create Topic if not exists
            topic_full = f"{topic_name}"
            if not frappe.db.exists("Topic", {"topic_name": topic_full}):
                topic_doc = frappe.get_doc({
                    "doctype": "Topic",
                    "topic_name": topic_full,
                    "description": f"Study material for {topic_full} under {course_name}.",
                    "company": COMPANY_NAME,
                })
                topic_doc.insert(ignore_permissions=True)
                topic_count += 1
            else:
                topic_doc = frappe.get_doc("Topic", {"topic_name": topic_full})

            # Link Topic to Course (via Course Topic child table)
            if topic_doc.name not in existing_topics:
                course.append("topics", {"topic": topic_doc.name})
                existing_topics.append(topic_doc.name)

            # Create 1-2 Articles per topic
            for a_idx in range(2):
                article_title = f"{topic_full} - {'Notes' if a_idx == 0 else 'Reference Material'}"
                if not frappe.db.exists("Article", {"title": article_title}):
                    article = frappe.get_doc({
                        "doctype": "Article",
                        "title": article_title,
                        "author": TEACHERS[t_idx % len(TEACHERS)]["first"] + " " + TEACHERS[t_idx % len(TEACHERS)]["last"],
                        "content": f"<h3>{article_title}</h3><p>Comprehensive study material for {topic_full} in {course_name}. "
                                   f"This covers all key concepts, examples, and practice exercises.</p>"
                                   f"<ul><li>Key Concept 1</li><li>Key Concept 2</li><li>Key Concept 3</li></ul>",
                        "company": COMPANY_NAME,
                    })
                    article.insert(ignore_permissions=True)
                    article_count += 1

                    # Link article to topic via topic_content child table
                    try:
                        topic_doc.reload()
                        topic_doc.append("topic_content", {
                            "content_type": "Article",
                            "content": article.name,
                        })
                        topic_doc.save(ignore_permissions=True)
                    except Exception:
                        pass

        # Save course with new topic links
        try:
            course.save(ignore_permissions=True)
        except Exception:
            pass

    frappe.db.commit()
    print(f"  Created {topic_count} topics, {article_count} articles")


def create_programs():
    """Create programs (classes) with linked courses."""
    print("Creating Programs...")
    created = []
    for prog in PROGRAMS:
        if frappe.db.exists("Program", prog["name"]):
            doc = frappe.get_doc("Program", prog["name"])
            # Ensure company is set correctly
            if doc.company != COMPANY_NAME:
                doc.company = COMPANY_NAME
                doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "Program",
                "program_name": prog["name"],
                "program_abbreviation": prog["program_abbreviation"],
                "company": COMPANY_NAME,
            })
            # Link courses to program
            for course_name in COURSES:
                doc.append("courses", {
                    "course": course_name,
                    "required": 1,
                })
            doc.insert(ignore_permissions=True)
        created.append(doc)
    return created


def create_rooms():
    """Create classrooms and labs."""
    print("Creating Rooms...")
    created = []
    for room in ROOMS:
        doc = _get_or_create("Room", {"room_name": room["room_name"]}, {
            "room_name": room["room_name"],
            "room_number": room["room_number"],
            "seating_capacity": room["seating_capacity"],
        })
        created.append(doc)
    return created


def create_instructors():
    """Create teacher records with course mappings."""
    print("Creating Instructors...")

    # REQUIRED: ERPNext Instructor.autoname() throws if this is unset.
    # "Full Name" uses instructor_name directly (no Employee link or naming series needed).
    if not frappe.db.get_single_value("Education Settings", "instructor_created_by"):
        frappe.db.set_single_value("Education Settings", "instructor_created_by", "Full Name")
        frappe.db.commit()

    created = []
    frappe.flags.in_import = True  # Bypass user creation throttle

    for i, teacher in enumerate(TEACHERS):
        full_name = f"{teacher['first']} {teacher['last']}"
        email = f"{teacher['first'].lower()}.{teacher['last'].lower()}@vidyaandemo.com"

        # Create user if not exists
        if not frappe.db.exists("User", email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": teacher["first"],
                "last_name": teacher["last"],
                "enabled": 1,
                "user_type": "Website User",
                "send_welcome_email": 0,
                "new_password": "Teacher@123",
                "roles": [{"role": "Instructor"}],
            })
            user.insert(ignore_permissions=True)

        # ── Create / get Employee linked to this user ──────────────────────
        # Required so _get_instructor_for_user() can resolve User → Employee → Instructor.
        emp_name = frappe.db.get_value("Employee", {"user_id": email}, "name")
        if not emp_name:
            emp_doc = frappe.get_doc({
                "doctype": "Employee",
                "first_name": teacher["first"],
                "last_name": teacher["last"],
                "employee_name": full_name,
                "gender": teacher["gender"],
                "date_of_birth": "1985-01-01",
                "date_of_joining": "2020-06-01",
                "status": "Active",
                "company": COMPANY_NAME,
                "user_id": email,
            })
            emp_doc.insert(ignore_permissions=True)
            emp_name = emp_doc.name
            print(f"  + Employee {emp_name} for {full_name}")

        # ── Create / get Instructor linked to that Employee ────────────────
        existing = (
            frappe.db.exists("Instructor", {"employee": emp_name})
            or frappe.db.exists("Instructor", {"instructor_name": full_name})
        )
        if existing:
            doc = frappe.get_doc("Instructor", existing)
            # Patch in employee link if missing (handles old test data)
            if not doc.employee:
                doc.employee = emp_name
                doc.save(ignore_permissions=True)
                print(f"  ~ Linked Instructor {doc.name} → Employee {emp_name}")
        else:
            doc = frappe.get_doc({
                "doctype": "Instructor",
                "instructor_name": full_name,
                "gender": teacher["gender"],
                "company": COMPANY_NAME,
                "employee": emp_name,
            })
            doc.insert(ignore_permissions=True)

        # Add course mappings (custom child table)
        if hasattr(doc, "course_mappings") and not doc.course_mappings:
            for subject in teacher["subjects"]:
                # Map to a few programs
                for prog in PROGRAMS[:5]:
                    doc.append("course_mappings", {
                        "course": subject,
                        "program": prog["name"],
                        "is_preferred": random.choice([0, 1]),
                    })
            try:
                doc.save(ignore_permissions=True)
            except Exception as e:
                print(f"  ! Failed to save course_mappings for {full_name}: {e}")

        created.append(doc)

    frappe.flags.in_import = False
    return created


def create_students():
    """Create 60 student records with user accounts for login."""
    print("Creating Students (60 students)...")
    created = []
    student_id = 1

    # Skip auto user creation in Student.validate — we create users ourselves
    original_skip = frappe.db.get_single_value("Education Settings", "user_creation_skip")
    frappe.db.set_single_value("Education Settings", "user_creation_skip", 1)
    # Bypass user creation throttle
    frappe.flags.in_import = True

    for prog_idx, prog in enumerate(PROGRAMS[:6]):  # 6 classes, 10 students each
        for s in range(10):
            if s < 5:
                first_name = STUDENT_FIRST_NAMES_MALE[s + prog_idx]
                gender = "Male"
            else:
                first_name = STUDENT_FIRST_NAMES_FEMALE[s - 5 + prog_idx]
                gender = "Female"
            last_name = STUDENT_LAST_NAMES[(s + prog_idx) % len(STUDENT_LAST_NAMES)]
            email = f"student{student_id:03d}@vidyaandemo.com"

            # Create user account for student login
            if not frappe.db.exists("User", email):
                try:
                    user = frappe.get_doc({
                        "doctype": "User",
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "gender": gender,
                        "enabled": 1,
                        "user_type": "Website User",
                        "send_welcome_email": 0,
                        "new_password": "Student@123",
                        "roles": [{"role": "Student"}],
                    })
                    user.flags.ignore_timestamps = True
                    user.insert(ignore_permissions=True)
                except frappe.TimestampMismatchError:
                    frappe.db.commit()
                    # Retry once
                    if not frappe.db.exists("User", email):
                        user = frappe.get_doc({
                            "doctype": "User",
                            "email": email,
                            "first_name": first_name,
                            "last_name": last_name,
                            "gender": gender,
                            "enabled": 1,
                            "user_type": "Website User",
                            "send_welcome_email": 0,
                            "new_password": "Student@123",
                            "roles": [{"role": "Student"}],
                        })
                        user.insert(ignore_permissions=True)

            existing = frappe.db.get_value("Student", {"student_email_id": email}, "name")
            if existing:
                doc = frappe.get_doc("Student", existing)
            else:
                full_name = f"{first_name} {last_name}"
                # If a Customer with the same name already exists, link it
                existing_customer = frappe.db.exists("Customer", full_name)

                doc = frappe.get_doc({
                    "doctype": "Student",
                    "first_name": first_name,
                    "last_name": last_name,
                    "student_email_id": email,
                    "user": email,
                    "gender": gender,
                    "date_of_birth": f"{2026 - 6 - prog_idx}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                    "joining_date": "2026-04-01",
                    "company": COMPANY_NAME,
                    "enabled": 1,
                    "blood_group": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
                })
                if existing_customer:
                    doc.customer = existing_customer
                doc.insert(ignore_permissions=True)

            created.append({"doc": doc, "program": prog["name"]})
            student_id += 1

    # Restore original setting
    frappe.db.set_single_value("Education Settings", "user_creation_skip", original_skip or 0)
    frappe.flags.in_import = False
    frappe.db.commit()
    print("  All student users created with password: Student@123")
    return created


def create_guardians(students):
    """Create guardian records and link to students."""
    print("Creating Guardians...")
    created = []
    guardian_names = [
        ("Rakesh", "Sharma"), ("Sunil", "Verma"), ("Manoj", "Patel"),
        ("Vijay", "Gupta"), ("Anil", "Singh"), ("Sanjay", "Kumar"),
        ("Ramesh", "Reddy"), ("Suresh", "Nair"), ("Dinesh", "Joshi"),
        ("Mahesh", "Yadav"), ("Ajay", "Agarwal"), ("Naresh", "Desai"),
    ]

    for i, (first, last) in enumerate(guardian_names):
        email = f"guardian{i+1:03d}@vidyaandemo.com"
        existing = frappe.db.get_value("Guardian", {"guardian_name": f"{first} {last}"}, "name")
        if existing:
            doc = frappe.get_doc("Guardian", existing)
        else:
            doc = frappe.get_doc({
                "doctype": "Guardian",
                "guardian_name": f"{first} {last}",
                "email_address": email,
                "mobile_number": f"98765{i:05d}",
                "relation": random.choice(["Father", "Mother", "Guardian"]),
            })
            doc.insert(ignore_permissions=True)
        created.append(doc)

    # Link guardians to students and set student mobile/address
    relations = ["Father", "Mother", "Father", "Father", "Mother", "Father",
                 "Mother", "Father", "Father", "Mother", "Father", "Mother"]
    for idx, student_data in enumerate(students):
        student_doc = frappe.get_doc("Student", student_data["doc"].name)
        guardian = created[idx % len(created)]

        # Link guardian if not already linked
        already_linked = any(g.guardian == guardian.name for g in (student_doc.get("guardians") or []))
        if not already_linked:
            try:
                student_doc.append("guardians", {
                    "guardian": guardian.name,
                    "guardian_name": guardian.guardian_name,
                    "relation": relations[idx % len(relations)],
                })
            except Exception:
                pass

        # Set student contact details
        if not student_doc.student_mobile_number:
            student_doc.student_mobile_number = f"91700{idx:06d}"
        if not student_doc.address_line_1:
            student_doc.address_line_1 = f"{100 + idx}, Demo Street, Block {chr(65 + idx % 6)}"
        if not student_doc.city:
            student_doc.city = random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Kolkata"])
        if not student_doc.state:
            student_doc.state = random.choice(["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "West Bengal"])

        try:
            student_doc.save(ignore_permissions=True)
        except Exception:
            pass

    frappe.db.commit()
    return created


def create_student_groups(students):
    """Create student groups (sections) and add students."""
    print("Creating Student Groups...")
    created = []

    for prog in PROGRAMS[:6]:
        for section in ["A"]:
            group_name = f"{prog['name']} - Section {section} - {ACADEMIC_YEAR}"
            existing = frappe.db.exists("Student Group", {"student_group_name": group_name})
            if existing:
                doc = frappe.get_doc("Student Group", existing)
            else:
                doc = frappe.get_doc({
                    "doctype": "Student Group",
                    "student_group_name": group_name,
                    "group_based_on": "Batch",
                    "program": prog["name"],
                    "academic_year": ACADEMIC_YEAR,
                    "academic_term": f"{TERM_1} ({ACADEMIC_YEAR})" if frappe.db.exists("Academic Term", f"{TERM_1} ({ACADEMIC_YEAR})") else None,
                    "max_strength": 40,
                    "company": COMPANY_NAME,
                })
                # Add students from this program
                prog_students = [s for s in students if s["program"] == prog["name"]]
                for student_data in prog_students:
                    doc.append("students", {
                        "student": student_data["doc"].name,
                        "student_name": f"{student_data['doc'].first_name} {student_data['doc'].last_name}",
                        "active": 1,
                    })
                doc.insert(ignore_permissions=True)
            created.append(doc)

    frappe.db.commit()
    return created


def create_program_enrollments(students):
    """Create program enrollments for each student."""
    print("Creating Program Enrollments...")
    for student_data in students:
        student = student_data["doc"]
        program = student_data["program"]

        existing = frappe.db.exists("Program Enrollment", {
            "student": student.name,
            "program": program,
            "academic_year": ACADEMIC_YEAR,
        })
        if not existing:
            try:
                doc = frappe.get_doc({
                    "doctype": "Program Enrollment",
                    "student": student.name,
                    "student_name": f"{student.first_name} {student.last_name}",
                    "program": program,
                    "academic_year": ACADEMIC_YEAR,
                    "academic_term": f"{TERM_1} ({ACADEMIC_YEAR})" if frappe.db.exists("Academic Term", f"{TERM_1} ({ACADEMIC_YEAR})") else None,
                    "enrollment_date": "2026-04-01",
                    "company": COMPANY_NAME,
                })
                doc.insert(ignore_permissions=True)
                _safe_submit(doc)
            except Exception as e:
                print(f"  Skipping enrollment for {student.name}: {e}")

    frappe.db.commit()


def create_course_schedules(instructors=None, student_groups=None, rooms=None):
    """Create timetable entries (Course Schedule) for one week per group.

    If called without arguments, load existing instructors, student groups,
    and rooms from the current company.
    """
    print("Creating Course Schedules...")
    count = 0

    if instructors is None:
        instructors = frappe.get_all(
            "Instructor",
            filters={"company": COMPANY_NAME, "status": "Active"},
            fields=["name"]
        )
    if student_groups is None:
        student_groups = frappe.get_all(
            "Student Group",
            filters={"company": COMPANY_NAME, "disabled": 0},
            fields=["name", "program"]
        )
    if rooms is None:
        rooms = frappe.get_all(
            "Room",
            fields=["name"]
        )

    if not instructors:
        frappe.throw(_("No active instructors found for course schedule creation."))
    if not student_groups:
        frappe.throw(_("No student groups found for course schedule creation."))
    if not rooms:
        frappe.throw(_("No rooms found for course schedule creation."))

    for grp_idx, group in enumerate(student_groups):
        # Each group gets its own week to avoid instructor/room conflicts
        base_date = getdate(add_days("2026-04-28", grp_idx * 7))  # Stagger by week
        room_base = grp_idx % len(rooms)

        for day_idx, day in enumerate(DAYS):
            for period in range(1, 6):  # 5 periods per day
                course_idx = (day_idx * 5 + period - 1) % len(COURSES)
                course = COURSES[course_idx]
                # Assign different instructors per group to avoid conflicts
                instructor = instructors[(course_idx + grp_idx * 2) % len(instructors)]
                room = rooms[(room_base + period - 1) % len(rooms)]

                # Calculate times
                hour = 9 + (period - 1)
                start_time = f"{hour:02d}:00"
                end_time = f"{hour:02d}:45"

                schedule_date = add_days(base_date, day_idx)

                existing = frappe.db.exists("Course Schedule", {
                    "student_group": group.name,
                    "course": course,
                    "schedule_date": str(schedule_date),
                })
                if not existing:
                    try:
                        doc = frappe.get_doc({
                            "doctype": "Course Schedule",
                            "student_group": group.name,
                            "course": course,
                            "instructor": instructor.name,
                            "room": room.name,
                            "schedule_date": str(schedule_date),
                            "from_time": start_time,
                            "to_time": end_time,
                            "company": COMPANY_NAME,
                        })
                        doc.insert(ignore_permissions=True)
                        count += 1
                    except Exception as e:
                        pass

    frappe.db.commit()
    print(f"  Created {count} course schedules")


def create_attendance(students, student_groups):
    """Create attendance records for the past 15 working days."""
    print("Creating Student Attendance...")

    # Ensure Holiday List exists for company
    _ensure_holiday_list()

    count = 0
    base_date = getdate(today())

    for group in student_groups:
        prog_students = [s for s in students if s["program"] == group.program]

        for day_offset in range(1, 16):  # 15 days of attendance
            att_date = add_days(base_date, -day_offset)
            # Skip weekends
            if getdate(att_date).weekday() >= 5:
                continue

            for student_data in prog_students:
                student = student_data["doc"]
                existing = frappe.db.exists("Student Attendance", {
                    "student": student.name,
                    "date": str(att_date),
                })
                if not existing:
                    status = random.choices(
                        ["Present", "Absent"],
                        weights=[85, 15],
                    )[0]
                    try:
                        doc = frappe.get_doc({
                            "doctype": "Student Attendance",
                            "student": student.name,
                            "student_group": group.name,
                            "date": str(att_date),
                            "status": status,
                            "company": COMPANY_NAME,
                        })
                        doc.insert(ignore_permissions=True)
                        _safe_submit(doc)
                        count += 1
                    except Exception as e:
                        if count == 0:
                            print(f"  Attendance error (first): {e}")
                        pass

    frappe.db.commit()
    print(f"  Created {count} attendance records")


def create_assessment_plans_and_results(student_groups, instructors):
    """Create exams and assignments with results."""
    print("Creating Assessment Plans & Results...")

    # Ensure assessment groups exist
    for group_name in ["Exams", "Assignments"]:
        if not frappe.db.exists("Assessment Group", group_name):
            try:
                root = frappe.db.get_value("Assessment Group", {"is_group": 1, "lft": 1}, "name")
                if root:
                    frappe.get_doc({
                        "doctype": "Assessment Group",
                        "assessment_group_name": group_name,
                        "parent_assessment_group": root,
                        "is_group": 1,
                    }).insert(ignore_permissions=True)
            except Exception:
                pass

    grading_scale = "Standard Grading" if frappe.db.exists("Grading Scale", "Standard Grading") else None

    exam_count = 0
    for grp_idx, group in enumerate(student_groups):
        for exam_idx, exam_type in enumerate(["Mid-Term Exam", "Unit Test 1", "Unit Test 2"]):
            course = COURSES[exam_idx % len(COURSES)]
            instructor = instructors[exam_idx % len(instructors)]
            # Stagger dates per group to avoid supervisor conflicts
            schedule_date = add_days(today(), 7 + exam_idx * 14 + grp_idx)

            plan_name = f"{exam_type} - {course} - {group.name}"
            existing = frappe.db.exists("Assessment Plan", {"assessment_name": plan_name})
            if existing:
                continue

            # Use different supervisors per group to avoid conflicts
            supervisor = instructors[(grp_idx + 1) % len(instructors)]

            try:
                plan = frappe.get_doc({
                    "doctype": "Assessment Plan",
                    "assessment_name": plan_name,
                    "student_group": group.name,
                    "course": course,
                    "assessment_group": "Exams",
                    "grading_scale": grading_scale,
                    "schedule_date": str(schedule_date),
                    "from_time": "10:00",
                    "to_time": "12:00",
                    "room": frappe.get_all("Room", pluck="name", limit=1)[0] if frappe.get_all("Room", pluck="name", limit=1) else None,
                    "maximum_assessment_score": 100,
                    "examiner": instructor.name,
                    "supervisor": supervisor.name,
                    "academic_year": ACADEMIC_YEAR,
                    "assessment_criteria": [
                        {"assessment_criteria": _ensure_assessment_criteria("Theory"), "maximum_score": 70},
                        {"assessment_criteria": _ensure_assessment_criteria("Practical"), "maximum_score": 30},
                    ]
                })
                plan.insert(ignore_permissions=True)
                _safe_submit(plan)
                exam_count += 1

                # Create results for past exams
                if exam_idx == 0:
                    _create_results_for_plan(plan, group)

            except Exception as e:
                print(f"  Skipping plan {plan_name}: {e}")

    # Create assignments for ALL groups
    assign_count = 0
    for group in student_groups:
        for a_idx in range(3):
            course = COURSES[(a_idx + 3) % len(COURSES)]
            plan_name = f"Assignment {a_idx+1} - {course} - {group.name}"

            existing = frappe.db.exists("Assessment Plan", {"assessment_name": plan_name})
            if existing:
                continue

            try:
                plan = frappe.get_doc({
                    "doctype": "Assessment Plan",
                    "assessment_name": plan_name,
                    "student_group": group.name,
                    "course": course,
                    "assessment_group": "Assignments",
                    "grading_scale": grading_scale,
                    "schedule_date": str(add_days(today(), -3 + a_idx * 5)),  # -3, +2, +7 days
                    "maximum_assessment_score": 50,
                    "examiner": instructors[a_idx % len(instructors)].name,
                    "academic_year": ACADEMIC_YEAR,
                    "assessment_criteria": [
                        {"assessment_criteria": _ensure_assessment_criteria("Theory"), "maximum_score": 50},
                    ]
                })
                plan.insert(ignore_permissions=True)
                _safe_submit(plan)
                assign_count += 1
            except Exception as e:
                print(f"  Skipping assignment {plan_name}: {e}")

    frappe.db.commit()
    print(f"  Created {exam_count} exams, {assign_count} assignments")


def _ensure_assessment_criteria(name):
    """Ensure an assessment criteria exists."""
    if not frappe.db.exists("Assessment Criteria", name):
        frappe.get_doc({
            "doctype": "Assessment Criteria",
            "assessment_criteria": name,
        }).insert(ignore_permissions=True)
    return name


def _create_results_for_plan(plan, group):
    """Create assessment results for all students in a group."""
    students_in_group = frappe.get_all(
        "Student Group Student",
        filters={"parent": group.name, "active": 1},
        fields=["student", "student_name"],
    )
    for sg_student in students_in_group:
        try:
            result = frappe.get_doc({
                "doctype": "Assessment Result",
                "student": sg_student.student,
                "student_name": sg_student.student_name,
                "assessment_plan": plan.name,
                "total_score": 0,
                "details": [],
            })
            total = 0
            for criteria in plan.assessment_criteria:
                score = round(random.uniform(criteria.maximum_score * 0.4, criteria.maximum_score), 1)
                total += score
                result.append("details", {
                    "assessment_criteria": criteria.assessment_criteria,
                    "maximum_score": criteria.maximum_score,
                    "score": score,
                })
            result.total_score = total
            result.insert(ignore_permissions=True)
            _safe_submit(result)
        except Exception:
            pass


def create_fee_structure_and_fees(students):
    """Create fee structures and fee records."""
    print("Creating Fee Structure & Fees...")

    # Fee categories
    for cat_name in ["Tuition Fee", "Library Fee", "Lab Fee", "Transport Fee", "Activity Fee"]:
        # Pre-create Item to avoid MandatoryError: stock_uom in Education app's Fee Category logic
        if not frappe.db.exists("Item", cat_name):
            try:
                # Ensure UOM exists again just in case
                stock_uom = "Unit"
                if not frappe.db.exists("UOM", stock_uom):
                    frappe.get_doc({"doctype": "UOM", "uom_name": stock_uom, "name": stock_uom}).insert(ignore_permissions=True)

                item = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": cat_name,
                    "item_name": cat_name,
                    "item_group": "Fee Component",
                    "is_sales_item": 1,
                    "is_service_item": 1,
                    "is_stock_item": 0,
                    "stock_uom": stock_uom
                })
                item.insert(ignore_permissions=True)
                frappe.db.commit()  # Commit each item to be sure
            except Exception as e:
                print(f"  Warning: Could not pre-create Item {cat_name}: {e}")

        if not frappe.db.exists("Fee Category", cat_name):
            try:
                frappe.get_doc({
                    "doctype": "Fee Category",
                    "category_name": cat_name,
                }).insert(ignore_permissions=True, ignore_if_duplicate=True)
                frappe.db.commit()
            except Exception as e:
                print(f"  Error creating Fee Category {cat_name}: {e}")

    # Fee structure
    for prog in PROGRAMS[:6]:
        fs_name = f"Fee Structure - {prog['name']} - {ACADEMIC_YEAR}"
        if frappe.db.exists("Fee Structure", {"name": ["like", f"%{prog['name']}%{ACADEMIC_YEAR}%"]}):
            continue

        try:
            fs = frappe.get_doc({
                "doctype": "Fee Structure",
                "program": prog["name"],
                "academic_year": ACADEMIC_YEAR,
                "company": COMPANY_NAME,
                "components": [
                    {"fees_category": "Tuition Fee", "amount": 5000},
                    {"fees_category": "Library Fee", "amount": 500},
                    {"fees_category": "Lab Fee", "amount": 800},
                    {"fees_category": "Activity Fee", "amount": 300},
                ]
            })
            fs.insert(ignore_permissions=True)
            _safe_submit(fs)
        except Exception as e:
            print(f"  Skipping fee structure for {prog['name']}: {e}")

    # Create a few fee records for students
    fee_count = 0
    for student_data in students[:20]:
        student = student_data["doc"]
        program = student_data["program"]

        if frappe.db.exists("Fees", {"student": student.name, "academic_year": ACADEMIC_YEAR}):
            continue

        # Look up the program enrollment and fee structure
        enrollment = frappe.db.get_value("Program Enrollment", {
            "student": student.name,
            "program": program,
            "academic_year": ACADEMIC_YEAR,
            "docstatus": 1,
        }, "name")

        fee_structure = frappe.db.get_value("Fee Structure", {
            "program": program,
            "academic_year": ACADEMIC_YEAR,
            "docstatus": 1,
        }, "name")

        try:
            fee = frappe.get_doc({
                "doctype": "Fees",
                "student": student.name,
                "program": program,
                "program_enrollment": enrollment,
                "fee_structure": fee_structure,
                "academic_year": ACADEMIC_YEAR,
                "due_date": str(add_days(today(), 30)),
                "company": COMPANY_NAME,
                "components": [
                    {"fees_category": "Tuition Fee", "amount": 5000},
                    {"fees_category": "Library Fee", "amount": 500},
                ]
            })
            fee.insert(ignore_permissions=True)
            _safe_submit(fee)
            fee_count += 1
        except Exception as e:
            if fee_count == 0 and not hasattr(create_fee_structure_and_fees, '_err_shown'):
                print(f"  Fees error: {e}")
                print("  (Fees creation may require ERPNext accounts setup - skipping)")
                create_fee_structure_and_fees._err_shown = True

    frappe.db.commit()
    print(f"  Created {fee_count} fee records")


def create_publications():
    """Create notices, news, and announcements."""
    print("Creating Publications...")

    # Create a placeholder image for News publications
    placeholder_image = "/assets/vidyaan/images/placeholder.png"

    publications = [
        {
            "title": "Annual Sports Day Announcement",
            "type": "Notice",
            "content": "<p>We are pleased to announce that the Annual Sports Day will be held on <b>May 15, 2026</b>. All students are expected to participate. Parents are cordially invited to attend.</p><p>Events include: 100m race, long jump, relay race, tug of war, and more!</p>",
            "target_type": "Global",
            "approval_type": "By Role",
            "approver_role": "System Manager",
            "publish_date": str(add_days(today(), 7)),
        },
        {
            "title": "Parent-Teacher Meeting Schedule",
            "type": "Notice",
            "content": "<p>The Parent-Teacher Meeting for all classes will be held on <b>April 20, 2026</b> from 10 AM to 1 PM. Parents are requested to meet the class teachers to discuss student progress.</p>",
            "target_type": "Global",
            "approval_type": "By Role",
            "approver_role": "System Manager",
            "publish_date": str(add_days(today(), 3)),
        },
        {
            "title": "Science Exhibition Winners",
            "type": "News",
            "content": "<p>Congratulations to all participants of the Inter-School Science Exhibition! Our school secured <b>1st place</b> in the senior category and <b>2nd place</b> in the junior category.</p><p>Special mention to Arjun Sharma (Class 6) for his innovative solar energy project.</p>",
            "featured_image": placeholder_image,
            "approval_type": "By Role",
            "approver_role": "System Manager",
            "publish_date": str(add_days(today(), -3)),
        },
        {
            "title": "New Library Books Available",
            "type": "Announcement",
            "content": "<p>The school library has been updated with 200+ new books across all categories. Students can visit the library during break hours to explore the new collection.</p><p>New additions include latest NCERT reference books, popular fiction, and science encyclopedias.</p>",
            "approval_type": "By Role",
            "approver_role": "System Manager",
            "publish_date": str(today()),
        },
        {
            "title": "Holiday Notice - Republic Day",
            "type": "Notice",
            "content": "<p>The school will remain closed on <b>January 26, 2027</b> on account of Republic Day. Classes will resume on January 27, 2027.</p>",
            "target_type": "Global",
            "approval_type": "By Role",
            "approver_role": "System Manager",
            "publish_date": str(add_days(today(), 14)),
        },
        {
            "title": "Annual Day Celebration",
            "type": "News",
            "content": "<p>The Annual Day celebration was a grand success! Students showcased their talent through dance, drama, and music performances. Chief Guest Shri Ramesh Patel appreciated the efforts of students and teachers.</p>",
            "featured_image": placeholder_image,
            "approval_type": "By Role",
            "approver_role": "System Manager",
            "publish_date": str(add_days(today(), -10)),
        },
    ]

    for pub_data in publications:
        if frappe.db.exists("Publication", {"title": pub_data["title"]}):
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "Publication",
                **pub_data,
            })
            doc.insert(ignore_permissions=True)
        except Exception as e:
            print(f"  Skipping publication '{pub_data['title']}': {e}")

    frappe.db.commit()


def create_student_nocs(students):
    """Create Student NOC records."""
    print("Creating Student NOCs...")

    noc_types = [
        ("Leaving Certificate", "Moving to another city due to parent's job transfer"),
        ("Bonafide Certificate", "Required for passport application"),
        ("Transfer Certificate", "Transferring to another school"),
        ("Character Certificate", "Required for scholarship application"),
        ("No Dues Certificate", "End of academic year clearance"),
    ]

    count = 0
    # Create NOCs spread across students from different classes
    for i, (noc_type, purpose) in enumerate(noc_types):
        # Pick students from different classes: index 5, 15, 25, 35, 45 (one per class)
        student_idx = i * 10 + 5
        if student_idx >= len(students):
            student_idx = i
        if student_idx >= len(students):
            break
        student = students[student_idx]["doc"]

        existing = frappe.db.exists("Student NOC", {
            "student": student.name,
            "noc_type": noc_type,
        })
        if existing:
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Student NOC",
                "student": student.name,
                "student_name": f"{student.first_name} {student.last_name}",
                "program": students[student_idx]["program"],
                "academic_year": ACADEMIC_YEAR,
                "noc_type": noc_type,
                "purpose": purpose,
                "effective_date": str(add_days(today(), 15 + i * 5)),
                "library_clearance": random.choice(["Cleared", "Pending Dues", "Not Applicable"]),
                "accounts_clearance": random.choice(["Cleared", "Pending Dues", "Not Applicable"]),
                "lab_clearance": random.choice(["Cleared", "Not Applicable"]),
                "hostel_clearance": "Not Applicable",
            })
            doc.insert(ignore_permissions=True)
            count += 1
        except Exception as e:
            print(f"  Skipping NOC: {e}")

    frappe.db.commit()
    print(f"  Created {count} NOCs")


def create_student_requests(students):
    """Create Student Request records."""
    print("Creating Student Requests...")

    requests = [
        {"category": "Academic", "priority": "High", "subject": "Request for extra classes in Mathematics", "description": "<p>I am finding it difficult to keep up with the Mathematics syllabus. I kindly request extra classes or tutoring sessions.</p>"},
        {"category": "Facility", "priority": "Medium", "subject": "Broken fan in Room 102", "description": "<p>The ceiling fan in Room 102 is not working properly. It makes a lot of noise and barely provides any air. Please get it repaired.</p>"},
        {"category": "Permission", "priority": "Low", "subject": "Permission to use computer lab after school", "description": "<p>I would like permission to use the computer lab after school hours (3 PM - 5 PM) for my science project research.</p>"},
        {"category": "Complaint", "priority": "Urgent", "subject": "Water cooler not working near playground", "description": "<p>The water cooler near the playground has been out of order for 3 days. Students have no access to drinking water during sports period.</p>"},
        {"category": "General", "priority": "Medium", "subject": "Request for school ID card replacement", "description": "<p>I lost my school ID card during the sports day event. I need a replacement card issued at the earliest.</p>"},
        {"category": "Administrative", "priority": "High", "subject": "Fee receipt duplicate required", "description": "<p>I need a duplicate fee receipt for Term 1 as the original was damaged. This is required for my scholarship application.</p>"},
        {"category": "Academic", "priority": "Medium", "subject": "Request to change elective subject", "description": "<p>I would like to change my elective from Art & Craft to Computer Science for the next term. I have discussed this with my parents.</p>"},
        {"category": "Facility", "priority": "High", "subject": "Library timing extension request", "description": "<p>As exams are approaching, I request the library hours be extended till 6 PM on weekdays for the next month.</p>"},
    ]

    count = 0
    for i, req_data in enumerate(requests):
        # Spread requests across different classes
        student_idx = i * 7 + 3  # picks students 3,10,17,24,31,38,45,52
        if student_idx >= len(students):
            student_idx = i
        if student_idx >= len(students):
            break
        student = students[student_idx]["doc"]

        existing = frappe.db.exists("Student Request", {
            "student": student.name,
            "subject": req_data["subject"],
        })
        if existing:
            continue

        try:
            doc = frappe.get_doc({
                "doctype": "Student Request",
                "student": student.name,
                "student_name": f"{student.first_name} {student.last_name}",
                "academic_year": ACADEMIC_YEAR,
                **req_data,
            })
            doc.insert(ignore_permissions=True)
            count += 1
        except Exception as e:
            print(f"  Skipping request: {e}")

    frappe.db.commit()
    print(f"  Created {count} requests")


def create_library_data():
    """Create full library test data."""
    print("Creating Library Data...")

    # Library
    library = _get_or_create("Library", {"library_code": "VDSLIB01"}, {
        "library_name": "Vidyaan Central Library",
        "library_code": "VDSLIB01",
        "library_type": "School",
        "owner_type": "Organization",
        "organization": COMPANY_NAME,
        "contact_email": "library@vidyaandemo.com",
        "contact_phone": "9876500000",
        "address": "Vidyaan Demo School Campus",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "max_books_per_member": 3,
        "issue_duration_days": 14,
        "fine_per_day": 5,
        "max_renewals": 2,
        "allow_reservation": 1,
        "auto_assign_on_return": 1,
        "allow_digital_access": 1,
    })

    # Book Categories
    for cat in BOOK_CATEGORIES:
        _get_or_create("Book Category", {"category_name": cat}, {
            "category_name": cat,
            "description": f"Books in the {cat} category",
        })

    # Books & Book Copies
    books = []
    for book_data in BOOK_DATA:
        book = _get_or_create("Book", {"title": book_data["title"]}, {
            "title": book_data["title"],
            "author": book_data["author"],
            "isbn": book_data["isbn"],
            "category": book_data["category"],
            "book_type": "Physical",
            "publisher": "Demo Publisher",
            "publication_year": random.randint(2015, 2024),
            "language": "English",
            "library": library.name,
            "description": f"A great book by {book_data['author']}",
        })
        books.append(book)

        # Create 2-3 copies per book
        for copy_idx in range(random.randint(2, 3)):
            barcode = f"BC-{book_data['isbn'][-4:]}-{copy_idx+1:02d}"
            _get_or_create("Book Copy", {"barcode": barcode}, {
                "book": book.name,
                "barcode": barcode,
                "shelf": f"Shelf-{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 5)}",
                "status": "Available",
                "condition": random.choice(["New", "Good", "Good", "Old"]),
            })

    # Library Members (mix of students and teachers)
    members = []
    # Student members
    all_students = frappe.get_all("Student", filters={"company": COMPANY_NAME}, fields=["name", "first_name", "last_name", "student_email_id"], limit=15)
    for student in all_students[:10]:
        member_name = f"{student.first_name} {student.last_name}"
        member = _get_or_create("Library Member", {"member_name": member_name, "library": library.name}, {
            "member_name": member_name,
            "member_type": "Student",
            "library": library.name,
            "email": student.student_email_id,
            "phone": f"98765{random.randint(10000, 99999)}",
            "status": "Active",
            "max_books_allowed": 3,
        })
        members.append(member)

    # Teacher members
    all_instructors = frappe.get_all("Instructor", filters={"company": COMPANY_NAME}, fields=["name", "instructor_name"], limit=5)
    for inst in all_instructors:
        member = _get_or_create("Library Member", {"member_name": inst.instructor_name, "library": library.name}, {
            "member_name": inst.instructor_name,
            "member_type": "Teacher",
            "library": library.name,
            "status": "Active",
            "max_books_allowed": 5,
        })
        members.append(member)

    # Book Issues
    available_copies = frappe.get_all("Book Copy", filters={"status": "Available"}, fields=["name", "book"], limit=8)
    issue_count = 0
    for i, copy in enumerate(available_copies[:6]):
        if i >= len(members):
            break
        member = members[i]
        book = copy.book

        existing = frappe.db.exists("Book Issue", {"book_copy": copy.name, "status": "Issued"})
        if existing:
            continue

        try:
            issue = frappe.get_doc({
                "doctype": "Book Issue",
                "library": library.name,
                "member": member.name,
                "book": book,
                "book_copy": copy.name,
                "issue_date": str(add_days(today(), -random.randint(1, 10))),
                "due_date": str(add_days(today(), random.randint(3, 14))),
                "status": "Issued",
            })
            issue.insert(ignore_permissions=True)

            # Update copy status
            frappe.db.set_value("Book Copy", copy.name, "status", "Issued")
            issue_count += 1
        except Exception as e:
            print(f"  Skipping book issue: {e}")

    # Book Requests
    req_count = 0
    for i in range(4):
        if i >= len(members) or i >= len(books):
            break
        member = members[i + 6] if i + 6 < len(members) else members[i]
        book = books[i + 6] if i + 6 < len(books) else books[i]

        existing = frappe.db.exists("Book Request", {"member": member.name, "book": book.name, "status": "Pending"})
        if existing:
            continue

        try:
            req = frappe.get_doc({
                "doctype": "Book Request",
                "library": library.name,
                "member": member.name,
                "book": book.name,
                "request_date": str(today()),
                "status": "Pending",
                "remarks": f"Would like to borrow {book.title}",
            })
            req.insert(ignore_permissions=True)
            req_count += 1
        except Exception as e:
            pass

    frappe.db.commit()
    print(f"  Created library with {len(books)} books, {len(members)} members, {issue_count} issues, {req_count} requests")


def create_routine_generation(instructors, student_groups):
    """Create a Routine Generation record."""
    print("Creating Routine Generation...")

    existing = frappe.db.exists("Routine Generation", {"academic_year": ACADEMIC_YEAR, "company": COMPANY_NAME})
    if existing:
        print("  Already exists, skipping.")
        return

    try:
        programs_list = []
        for group in student_groups[:3]:
            if group.program:
                programs_list.append({"program": group.program})

        if not programs_list:
            print("  No programs to add, skipping.")
            return

        doc = frappe.get_doc({
            "doctype": "Routine Generation",
            "naming_series": "VDY-RTN-.YYYY.-",
            "company": COMPANY_NAME,
            "academic_year": ACADEMIC_YEAR,
            "programs": programs_list,
            "monday": 1,
            "tuesday": 1,
            "wednesday": 1,
            "thursday": 1,
            "friday": 1,
            "saturday": 0,
            "sunday": 0,
            "periods_per_day": 5,
            "max_subject_per_day": 2,
            "max_teacher_periods_per_day": 4,
            "min_teacher_weekly_load": 8,
            "max_teacher_weekly_load": 18,
            "solver_timeout": 30,
        })
        doc.insert(ignore_permissions=True)
        print("  Created Routine Generation (Draft)")
    except Exception as e:
        print(f"  Skipping routine generation: {e}")

    frappe.db.commit()


def setup_vidyaan_settings():
    """Configure Vidyaan Settings singleton."""
    print("Configuring Vidyaan Settings...")
    try:
        settings = frappe.get_single("Vidyaan Settings")
        settings.company = COMPANY_NAME
        settings.default_academic_year = ACADEMIC_YEAR
        if frappe.db.exists("Academic Term", {"term_name": TERM_1, "academic_year": ACADEMIC_YEAR}):
            terms = frappe.get_all("Academic Term", filters={"academic_year": ACADEMIC_YEAR}, pluck="name", limit=1)
            if terms:
                settings.default_academic_term = terms[0]
        settings.default_periods_per_day = 5
        settings.default_days = "Monday,Tuesday,Wednesday,Thursday,Friday"
        settings.max_subject_per_day = 2
        settings.max_teacher_periods_per_day = 4
        settings.min_teacher_weekly_load = 8
        settings.max_teacher_weekly_load = 18
        settings.solver_timeout = 30

        if not settings.period_timings:
            default_timings = [
                {"period_number": 1, "start_time": "09:00:00", "end_time": "09:45:00"},
                {"period_number": 2, "start_time": "09:45:00", "end_time": "10:30:00"},
                {"period_number": 3, "start_time": "10:30:00", "end_time": "11:15:00"},
                {"period_number": 4, "start_time": "11:30:00", "end_time": "12:15:00"},
                {"period_number": 5, "start_time": "12:15:00", "end_time": "13:00:00"},
            ]
            for timing in default_timings:
                settings.append("period_timings", timing)

        settings.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        print(f"  Error configuring settings: {e}")


def create_user_permissions(students, instructors):
    """Create User Permissions so _get_user_company() works for all test users."""
    print("Creating User Permissions...")
    count = 0

    # Student user permissions
    for student_data in students:
        student = student_data["doc"]
        email = student.student_email_id
        if not email:
            continue
        existing = frappe.db.exists("User Permission", {
            "user": email, "allow": "Company", "for_value": COMPANY_NAME,
        })
        if not existing:
            try:
                frappe.get_doc({
                    "doctype": "User Permission",
                    "user": email,
                    "allow": "Company",
                    "for_value": COMPANY_NAME,
                    "apply_to_all_doctypes": 1,
                }).insert(ignore_permissions=True)
                count += 1
            except Exception:
                pass

    # Teacher user permissions
    for idx, instructor in enumerate(instructors):
        if idx < len(TEACHERS):
            teacher = TEACHERS[idx]
            email = f"{teacher['first'].lower()}.{teacher['last'].lower()}@vidyaandemo.com"
        else:
            continue
        existing = frappe.db.exists("User Permission", {
            "user": email, "allow": "Company", "for_value": COMPANY_NAME,
        })
        if not existing:
            try:
                frappe.get_doc({
                    "doctype": "User Permission",
                    "user": email,
                    "allow": "Company",
                    "for_value": COMPANY_NAME,
                    "apply_to_all_doctypes": 1,
                }).insert(ignore_permissions=True)
                count += 1
            except Exception:
                pass

    frappe.db.commit()
    print(f"  Created {count} user permissions")


def create_current_week_schedules(instructors, student_groups, rooms):
    """Create course schedules for the CURRENT week so today's classes show on dashboard."""
    print("Creating Current Week Schedules...")
    count = 0
    base_date = getdate(today())
    # Find Monday of current week
    monday = add_days(base_date, -base_date.weekday())

    for grp_idx, group in enumerate(student_groups):
        room_base = grp_idx % len(rooms)

        for day_idx in range(5):  # Mon-Fri
            schedule_date = add_days(monday, day_idx)

            for period in range(1, 6):
                course_idx = (day_idx * 5 + period - 1) % len(COURSES)
                course = COURSES[course_idx]
                instructor = instructors[(course_idx + grp_idx * 2) % len(instructors)]
                room = rooms[(room_base + period - 1) % len(rooms)]

                hour = 9 + (period - 1)
                start_time = f"{hour:02d}:00"
                end_time = f"{hour:02d}:45"

                existing = frappe.db.exists("Course Schedule", {
                    "student_group": group.name,
                    "course": course,
                    "schedule_date": str(schedule_date),
                })
                if not existing:
                    try:
                        doc = frappe.get_doc({
                            "doctype": "Course Schedule",
                            "student_group": group.name,
                            "course": course,
                            "instructor": instructor.name,
                            "room": room.name,
                            "schedule_date": str(schedule_date),
                            "from_time": start_time,
                            "to_time": end_time,
                            "company": COMPANY_NAME,
                        })
                        doc.insert(ignore_permissions=True)
                        count += 1
                    except Exception:
                        pass

    frappe.db.commit()
    print(f"  Created {count} current-week schedules")


def approve_publications():
    """Submit and approve all publications so they show in the notices API."""
    print("Approving Publications...")
    count = 0
    pubs = frappe.get_all("Publication", filters={"docstatus": 0}, pluck="name")
    for pub_name in pubs:
        try:
            # Direct DB update to submit and approve - avoids on_submit hook
            # which tries to use frappe.assign_to (not always available)
            frappe.db.set_value("Publication", pub_name, {
                "docstatus": 1,
                "status": "Approved",
            }, update_modified=True)
            count += 1
        except Exception as e:
            print(f"  Could not approve {pub_name}: {e}")

    frappe.db.commit()
    print(f"  Approved {count} publications")


def link_library_members_to_users():
    """Set the user field on Library Members so library API can resolve them."""
    print("Linking Library Members to Users...")
    count = 0

    # Link student members
    all_students = frappe.get_all("Student", filters={"company": COMPANY_NAME},
                                  fields=["name", "first_name", "last_name", "student_email_id"])
    for student in all_students:
        full_name = f"{student.first_name} {student.last_name}"
        member = frappe.db.get_value("Library Member", {"member_name": full_name}, "name")
        if member and student.student_email_id:
            current_user = frappe.db.get_value("Library Member", member, "user")
            if not current_user:
                frappe.db.set_value("Library Member", member, "user", student.student_email_id)
                count += 1

    # Link teacher members - look up email from our TEACHERS constant
    for teacher in TEACHERS:
        email = f"{teacher['first'].lower()}.{teacher['last'].lower()}@vidyaandemo.com"
        full_name = f"{teacher['first']} {teacher['last']}"
        member = frappe.db.get_value("Library Member", {"member_name": full_name}, "name")
        if member:
            current_user = frappe.db.get_value("Library Member", member, "user")
            if not current_user:
                frappe.db.set_value("Library Member", member, "user", email)
                count += 1

    frappe.db.commit()
    print(f"  Linked {count} library members to users")


# ─── Main Entry Points ───────────────────────────────────────────────────────

def create_all(fresh=True):
    """
    Create all test data for Vidyaan frontend testing.

    Usage:
        bench --site <site-name> execute vidyaan.tests.create_test_data.create_all
        bench --site <site-name> execute vidyaan.tests.create_test_data.create_all --kwargs '{"fresh": true}'
    """
    print("=" * 60)
    print("  VIDYAAN TEST DATA GENERATOR")
    print("=" * 60)
    print()

    if fresh:
        print("Cleaning up any existing test data first...")
        print()
        try:
            delete_all()
        except Exception as e:
            print(f"  Cleanup warning (continuing): {e}")
        print()

    frappe.flags.ignore_permissions = True

    # Core setup
    create_company()
    create_academic_year()
    create_academic_terms()
    grading_scale = create_grading_scale()
    courses = create_courses()
    create_topics_and_articles()
    programs = create_programs()
    rooms = create_rooms()
    _ensure_genders()
    _ensure_uom()
    _ensure_item_group()
    instructors = create_instructors()

    # People
    students = create_students()
    guardians = create_guardians(students)
    student_groups = create_student_groups(students)
    create_program_enrollments(students)

    # Academics
    create_course_schedules(instructors, student_groups, rooms)
    create_current_week_schedules(instructors, student_groups, rooms)
    create_attendance(students, student_groups)
    create_assessment_plans_and_results(student_groups, instructors)
    create_fee_structure_and_fees(students)

    # Vidyaan custom doctypes
    create_publications()
    approve_publications()
    create_student_nocs(students)
    create_student_requests(students)
    create_routine_generation(instructors, student_groups)

    # Library
    create_library_data()
    link_library_members_to_users()

    # Permissions & Settings
    create_user_permissions(students, instructors)
    setup_vidyaan_settings()

    frappe.flags.ignore_permissions = False
    frappe.db.commit()

    print()
    print("=" * 60)
    print("  TEST DATA CREATION COMPLETE!")
    print("=" * 60)
    print()
    _print_summary()
    _print_login_credentials()


def _print_summary():
    """Print a summary of created test data."""
    counts = {
        "Company": frappe.db.count("Company", {"name": COMPANY_NAME}),
        "Academic Year": frappe.db.count("Academic Year", {"academic_year_name": ACADEMIC_YEAR}),
        "Programs": frappe.db.count("Program"),
        "Courses": frappe.db.count("Course"),
        "Rooms": frappe.db.count("Room"),
        "Instructors": frappe.db.count("Instructor", {"company": COMPANY_NAME}),
        "Students": frappe.db.count("Student", {"company": COMPANY_NAME}),
        "Guardians": frappe.db.count("Guardian"),
        "Student Groups": frappe.db.count("Student Group", {"academic_year": ACADEMIC_YEAR}),
        "Program Enrollments": frappe.db.count("Program Enrollment", {"academic_year": ACADEMIC_YEAR}),
        "Course Schedules": frappe.db.count("Course Schedule"),
        "Student Attendance": frappe.db.count("Student Attendance", {"docstatus": 1}),
        "Assessment Plans": frappe.db.count("Assessment Plan", {"docstatus": 1}),
        "Assessment Results": frappe.db.count("Assessment Result", {"docstatus": 1}),
        "Fee Structures": frappe.db.count("Fee Structure", {"docstatus": 1}),
        "Fees": frappe.db.count("Fees", {"docstatus": 1}),
        "Publications": frappe.db.count("Publication"),
        "Student NOCs": frappe.db.count("Student NOC"),
        "Student Requests": frappe.db.count("Student Request"),
        "Routine Generations": frappe.db.count("Routine Generation"),
        "Libraries": frappe.db.count("Library"),
        "Books": frappe.db.count("Book"),
        "Book Copies": frappe.db.count("Book Copy"),
        "Library Members": frappe.db.count("Library Member"),
        "Book Issues": frappe.db.count("Book Issue"),
        "Book Requests": frappe.db.count("Book Request"),
        "User Permissions": frappe.db.count("User Permission", {"user": ["like", "%@vidyaandemo.com"]}),
        "Publications (Approved)": frappe.db.count("Publication", {"status": "Approved", "docstatus": 1}),
    }

    print("  DATA SUMMARY:")
    print("  " + "-" * 40)
    for label, count in counts.items():
        print(f"  {label:<25} {count:>5}")
    print("  " + "-" * 40)


def _print_login_credentials():
    """Print login credentials for test users."""
    print()
    print("  LOGIN CREDENTIALS:")
    print("  " + "-" * 55)
    print(f"  {'Role':<12} {'Email':<40} {'Password'}")
    print("  " + "-" * 55)
    print(f"  {'Student':<12} {'student001@vidyaandemo.com':<40} Student@123")
    print(f"  {'Student':<12} {'student002@vidyaandemo.com':<40} Student@123")
    print(f"  {'Student':<12} {'... (student001 to student060)':<40} Student@123")
    print(f"  {'Teacher':<12} {'rajesh.sharma@vidyaandemo.com':<40} Teacher@123")
    print(f"  {'Teacher':<12} {'priya.verma@vidyaandemo.com':<40} Teacher@123")
    print(f"  {'Teacher':<12} {'... (12 teachers total)':<40} Teacher@123")
    print("  " + "-" * 55)


def delete_all():
    """
    Delete all test data created by this script.

    Usage: bench --site <site-name> execute vidyaan.tests.create_test_data.delete_all

    WARNING: This will delete ALL data for the demo company!
    """
    print("=" * 60)
    print("  DELETING VIDYAAN TEST DATA")
    print("=" * 60)
    print()

    frappe.flags.ignore_permissions = True

    # Delete in reverse dependency order
    _delete_all_docs("Book Issue")
    _delete_all_docs("Book Request")
    _delete_all_docs("Book Copy")
    _delete_all_docs("Book")
    _delete_all_docs("Library Member")
    _delete_all_docs("Library", {"library_code": "VDSLIB01"})
    _delete_all_docs("Book Category")

    _delete_all_docs("Routine Generation", {"company": COMPANY_NAME})

    # Also delete the broken publication with literal naming
    if frappe.db.exists("Publication", "PUB-2026-04-#####"):
        try:
            frappe.delete_doc("Publication", "PUB-2026-04-#####", force=True, ignore_permissions=True)
        except Exception:
            pass
    _delete_all_docs("Student Request", {"academic_year": ACADEMIC_YEAR})
    _delete_all_docs("Student NOC", {"academic_year": ACADEMIC_YEAR})
    _delete_all_docs("Publication", cancel_first=True)

    _delete_all_docs("Assessment Result", cancel_first=True)
    _delete_all_docs("Assessment Plan", {"academic_year": ACADEMIC_YEAR}, cancel_first=True)

    _delete_all_docs("Student Attendance", {"company": COMPANY_NAME}, cancel_first=True)
    _delete_all_docs("Course Schedule", {"company": COMPANY_NAME})
    _delete_all_docs("Fees", {"company": COMPANY_NAME}, cancel_first=True)
    _delete_all_docs("Fee Structure", {"company": COMPANY_NAME}, cancel_first=True)

    _delete_all_docs("Program Enrollment", {"academic_year": ACADEMIC_YEAR}, cancel_first=True)
    _delete_all_docs("Student Group", {"academic_year": ACADEMIC_YEAR})
    _delete_all_docs("Guardian")
    _delete_all_docs("Student", {"company": COMPANY_NAME})

    # Clean up auto-created Customers for students
    student_customers = frappe.get_all("Customer", filters={"customer_group": "Student"}, pluck="name")
    for cust in student_customers:
        try:
            frappe.delete_doc("Customer", cust, force=True, ignore_permissions=True)
        except Exception:
            pass
    if student_customers:
        print(f"  Deleted {len(student_customers)} student Customer records")

    _delete_all_docs("Instructor", {"company": COMPANY_NAME})

    _delete_all_docs("Room")

    # Delete topics and articles
    _delete_all_docs("Article", {"company": COMPANY_NAME})
    _delete_all_docs("Topic", {"company": COMPANY_NAME})
    _delete_all_docs("Academic Term", {"academic_year": ACADEMIC_YEAR})
    _delete_all_docs("Academic Year", {"academic_year_name": ACADEMIC_YEAR})
    _delete_all_docs("Holiday List", {"holiday_list_name": f"School Holidays {ACADEMIC_YEAR}"})

    # Delete User Permissions for test users
    test_perms = frappe.get_all("User Permission", filters={
        "user": ["like", "%@vidyaandemo.com"],
    }, pluck="name")
    for perm in test_perms:
        try:
            frappe.delete_doc("User Permission", perm, force=True, ignore_permissions=True)
        except Exception:
            pass
    if test_perms:
        print(f"  Deleted {len(test_perms)} User Permission records")

    # Delete test users (teachers + students)
    for teacher in TEACHERS:
        email = f"{teacher['first'].lower()}.{teacher['last'].lower()}@vidyaandemo.com"
        if frappe.db.exists("User", email):
            frappe.delete_doc("User", email, force=True, ignore_permissions=True)

    # Delete student users
    student_users = frappe.get_all("User", filters={"email": ["like", "%@vidyaandemo.com"]}, pluck="name")
    for email in student_users:
        try:
            frappe.delete_doc("User", email, force=True, ignore_permissions=True)
        except Exception:
            pass
    if student_users:
        print(f"  Deleted {len(student_users)} test users")

    frappe.flags.ignore_permissions = False
    frappe.db.commit()

    print()
    print("=" * 60)
    print("  TEST DATA DELETION COMPLETE!")
    print("=" * 60)


def _delete_all_docs(doctype, filters=None, cancel_first=False):
    """Delete all documents of a given type."""
    try:
        docs = frappe.get_all(doctype, filters=filters or {}, pluck="name")
        for name in docs:
            try:
                if cancel_first:
                    doc = frappe.get_doc(doctype, name)
                    if doc.docstatus == 1:
                        doc.cancel()
                frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
            except Exception:
                pass
        if docs:
            print(f"  Deleted {len(docs)} {doctype} records")
        frappe.db.commit()
    except Exception as e:
        print(f"  Error deleting {doctype}: {e}")
