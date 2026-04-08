"""
Test suite for Routine Generation.

Strategy
--------
1. setUpClass cleans any leftover `_RGT_*` fixtures, then creates a fresh,
   minimal-but-realistic dataset in the dependency-correct order:

       Courses → Program (with Program Courses)
              → Instructors (each with Instructor Course Mapping rows)
              → Student Groups (sections)
              → Vidyaan Settings → Period Timings (only if missing)

2. Each test method exercises ONE public surface of the doctype:
       a. check_readiness  → must report ok=True
       b. generate_routine → must populate routine_slots and set status=Generated
       c. on_submit        → must create native Course Schedule rows

3. tearDownClass removes everything we created so the suite is fully
   idempotent and leaves no residue in the site database.

Edge cases respected
--------------------
- Multi-tenant: every fixture is scoped to one Company.
- No real production data is touched — all names are prefixed `_RGT_`.
- Period Timings in Vidyaan Settings are only seeded if missing, never
  overwritten (real config is preserved).
- Tests use the SAME public APIs that the JS form buttons call, so a green
  test means the user-facing flow works end-to-end.
"""

import frappe
import unittest

PREFIX = "_RGT_"
COMPANY = "Vidyaan Demo School"
ACADEMIC_YEAR = "2025-2026"

COURSES = [f"{PREFIX}Math", f"{PREFIX}Science", f"{PREFIX}English"]
PROGRAM = f"{PREFIX}Program A"
INSTRUCTORS = [
    # name, [(course, program, is_preferred)]
    (f"{PREFIX}Teacher 1", [(COURSES[0], PROGRAM, 1), (COURSES[1], PROGRAM, 0)]),
    (f"{PREFIX}Teacher 2", [(COURSES[1], PROGRAM, 0), (COURSES[2], PROGRAM, 1)]),
    (f"{PREFIX}Teacher 3", [(COURSES[0], PROGRAM, 0), (COURSES[2], PROGRAM, 0)]),
]
SECTIONS = [f"{PREFIX}Section A1", f"{PREFIX}Section A2"]

# One dedicated classroom per section — never changes for the section.
# Room is autonamed (HTL-ROOM-YYYY-NNNNN), so we store the room_name LABEL
# here and resolve to the actual document name at runtime.
ROOM_LABELS = {
    f"{PREFIX}Section A1": f"{PREFIX}Room 101",
    f"{PREFIX}Section A2": f"{PREFIX}Room 102",
}
# Populated by _create_rooms() with the autonamed Room.name for each label.
RUNTIME_ROOMS: dict = {}


# ─── Cleanup helpers ─────────────────────────────────────────────────────

def _cleanup():
    """Remove every `_RGT_*` fixture, in dependency order, ignoring missing."""
    # 1. Cancel + delete any Routine Generation doc that references our prefix
    for rg in frappe.get_all(
        "Routine Generation",
        filters={"name": ["like", f"%{PREFIX}%"]},
        fields=["name", "docstatus"],
    ):
        try:
            doc = frappe.get_doc("Routine Generation", rg.name)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc("Routine Generation", rg.name, force=True)
        except Exception:
            pass

    # 2. Course Schedule rows we may have created on submit
    for cs in frappe.get_all(
        "Course Schedule",
        filters={"course": ["in", COURSES]},
        pluck="name",
    ):
        try:
            frappe.delete_doc("Course Schedule", cs, force=True, ignore_permissions=True)
        except Exception:
            pass

    # 3. Student Groups
    for sg in SECTIONS:
        if frappe.db.exists("Student Group", sg):
            try:
                frappe.delete_doc("Student Group", sg, force=True, ignore_permissions=True)
            except Exception:
                pass

    # 3b. Rooms (after Student Groups so the FK is gone). Room is autonamed,
    # so we query by room_name LIKE prefix and delete every match.
    for room in frappe.get_all(
        "Room",
        filters={"room_name": ["like", f"{PREFIX}%"]},
        pluck="name",
    ):
        try:
            frappe.delete_doc("Room", room, force=True, ignore_permissions=True)
        except Exception:
            pass
    RUNTIME_ROOMS.clear()

    # 4. Instructors (deletes child Instructor Course Mapping rows automatically)
    for inst, _ in INSTRUCTORS:
        if frappe.db.exists("Instructor", inst):
            try:
                frappe.delete_doc("Instructor", inst, force=True, ignore_permissions=True)
            except Exception:
                pass

    # 5. Program (deletes Program Course rows automatically)
    if frappe.db.exists("Program", PROGRAM):
        try:
            frappe.delete_doc("Program", PROGRAM, force=True, ignore_permissions=True)
        except Exception:
            pass

    # 6. Courses
    for c in COURSES:
        if frappe.db.exists("Course", c):
            try:
                frappe.delete_doc("Course", c, force=True, ignore_permissions=True)
            except Exception:
                pass

    frappe.db.commit()


# ─── Fixture builders ────────────────────────────────────────────────────

def _ensure_period_timings():
    """Seed Vidyaan Settings → Period Timings only if empty. Never overwrite."""
    settings = frappe.get_single("Vidyaan Settings")
    if settings.period_timings:
        return
    base_times = [
        (1, "09:00:00", "09:45:00"),
        (2, "09:45:00", "10:30:00"),
        (3, "10:45:00", "11:30:00"),
        (4, "11:30:00", "12:15:00"),
        (5, "13:00:00", "13:45:00"),
    ]
    for n, s, e in base_times:
        settings.append("period_timings", {
            "period_number": n,
            "start_time": s,
            "end_time": e,
        })
    settings.save(ignore_permissions=True)


def _create_courses():
    for c in COURSES:
        if frappe.db.exists("Course", c):
            continue
        doc = frappe.get_doc({
            "doctype": "Course",
            "course_name": c,
            "company": COMPANY,
        })
        doc.insert(ignore_permissions=True)


def _create_program():
    if frappe.db.exists("Program", PROGRAM):
        return
    doc = frappe.get_doc({
        "doctype": "Program",
        "program_name": PROGRAM,
        "company": COMPANY,
        "courses": [{"course": c, "required": 1} for c in COURSES],
    })
    doc.insert(ignore_permissions=True)


def _create_instructors():
    for inst_name, mappings in INSTRUCTORS:
        if frappe.db.exists("Instructor", inst_name):
            continue
        doc = frappe.get_doc({
            "doctype": "Instructor",
            "instructor_name": inst_name,
            "company": COMPANY,
            "status": "Active",
            "course_mappings": [
                {
                    "course": course,
                    "program": program,
                    "is_preferred": pref,
                }
                for (course, program, pref) in mappings
            ],
        })
        doc.insert(ignore_permissions=True)


def _create_rooms():
    """Create one Room per section label and remember its autonamed name."""
    for sg_name, label in ROOM_LABELS.items():
        # Already created in this run?
        if RUNTIME_ROOMS.get(sg_name):
            continue
        # Existing Room with this label (e.g., from a half-failed prior run)?
        existing = frappe.db.get_value("Room", {"room_name": label}, "name")
        if existing:
            RUNTIME_ROOMS[sg_name] = existing
            continue
        doc = frappe.get_doc({
            "doctype": "Room",
            "room_name": label,
            "seating_capacity": 30,
        }).insert(ignore_permissions=True)
        RUNTIME_ROOMS[sg_name] = doc.name


def _create_student_groups():
    for sg_name in SECTIONS:
        if frappe.db.exists("Student Group", sg_name):
            continue
        doc = frappe.get_doc({
            "doctype": "Student Group",
            "student_group_name": sg_name,
            "company": COMPANY,
            "academic_year": ACADEMIC_YEAR,
            "group_based_on": "Batch",
            "program": PROGRAM,
            "disabled": 0,
            "room": RUNTIME_ROOMS[sg_name],
        })
        doc.insert(ignore_permissions=True)


def _create_routine_doc():
    """Build (but do not save) a fresh Routine Generation skeleton."""
    return frappe.get_doc({
        "doctype": "Routine Generation",
        "company": COMPANY,
        "academic_year": ACADEMIC_YEAR,
        "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1,
        "saturday": 0, "sunday": 0,
        "periods_per_day": 5,
        "max_subject_per_day": 2,
        "max_teacher_periods_per_day": 4,
        "min_teacher_weekly_load": 1,    # generous floor for tiny test fleet
        "max_teacher_weekly_load": 18,
        "solver_timeout": 30,
        "programs": [{"program": PROGRAM}],
    })


# ─── Test class ──────────────────────────────────────────────────────────

class TestRoutineGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _cleanup()
        _ensure_period_timings()
        _create_courses()
        _create_program()
        _create_instructors()
        _create_rooms()
        _create_student_groups()
        frappe.db.commit()

    @classmethod
    def tearDownClass(cls):
        _cleanup()

    # ── 1. Readiness ────────────────────────────────────────────────────
    def test_01_check_readiness_passes(self):
        rg = _create_routine_doc()
        rg.insert(ignore_permissions=True)
        result = rg.check_readiness()
        self.assertTrue(
            result["ok"],
            msg=f"Readiness should pass for clean fixtures, got: {result}",
        )
        # Sanity: 2 sections × 5 days × 5 periods
        self.assertEqual(result["sections"], 2)

    # ── 2. Generation ───────────────────────────────────────────────────
    def test_02_generate_routine_succeeds(self):
        rg = _create_routine_doc()
        rg.insert(ignore_permissions=True)
        rg.generate_routine()
        rg.reload()
        self.assertEqual(rg.status, "Generated")
        # 2 sections × 5 days × 5 periods = 50 slots
        self.assertEqual(len(rg.routine_slots), 50)
        # Every slot must reference one of OUR teachers and OUR courses
        teachers = {n for n, _ in INSTRUCTORS}
        for slot in rg.routine_slots:
            self.assertIn(slot.instructor, teachers)
            self.assertIn(slot.course, COURSES)
            self.assertEqual(slot.program, PROGRAM)

    # ── 3. Submission → Course Schedule ─────────────────────────────────
    def test_03_submit_creates_course_schedules(self):
        rg = _create_routine_doc()
        rg.insert(ignore_permissions=True)
        rg.generate_routine()
        rg.reload()
        rg.submit()
        # Each routine_slot should produce one Course Schedule row
        rows = frappe.get_all(
            "Course Schedule",
            filters={"course": ["in", COURSES]},
            pluck="name",
        )
        self.assertEqual(len(rows), 50)

    # ── 3b. Negative: missing room blocks generation ────────────────────
    def test_03b_missing_room_blocks_generation(self):
        # Strip room from one section and confirm both readiness and
        # generation refuse to proceed.
        sg = frappe.get_doc("Student Group", SECTIONS[0])
        original_room = sg.room
        sg.room = None
        sg.save(ignore_permissions=True)
        try:
            rg = _create_routine_doc()
            rg.insert(ignore_permissions=True)
            result = rg.check_readiness()
            self.assertFalse(result["ok"])
            self.assertTrue(any("Classroom" in r["msg"] for r in result["results"]))
            with self.assertRaises(frappe.ValidationError):
                rg.generate_routine()
        finally:
            sg = frappe.get_doc("Student Group", SECTIONS[0])
            sg.room = original_room
            sg.save(ignore_permissions=True)
            frappe.db.commit()

    # ── 4. Negative: missing Period Timings is rejected at submit ───────
    def test_04_submit_blocks_when_period_timings_missing(self):
        # Snapshot + clear timings
        settings = frappe.get_single("Vidyaan Settings")
        snapshot = [row.as_dict() for row in (settings.period_timings or [])]
        settings.period_timings = []
        settings.save(ignore_permissions=True)
        try:
            rg = _create_routine_doc()
            rg.insert(ignore_permissions=True)
            rg.generate_routine()
            rg.reload()
            with self.assertRaises(frappe.ValidationError):
                rg.submit()
        finally:
            # Restore
            settings = frappe.get_single("Vidyaan Settings")
            settings.period_timings = []
            for row in snapshot:
                settings.append("period_timings", {
                    "period_number": row.get("period_number"),
                    "start_time": row.get("start_time"),
                    "end_time": row.get("end_time"),
                })
            settings.save(ignore_permissions=True)
            frappe.db.commit()
