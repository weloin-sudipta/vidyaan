import frappe
from frappe.model.document import Document
from frappe import _
import math

class RoutineGeneration(Document):

    DAY_MAP = {
        "monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday",
        "thursday": "Thursday", "friday": "Friday", "saturday": "Saturday",
        "sunday": "Sunday"
    }

    def validate(self):
        self.validate_company_ownership()

    def validate_company_ownership(self):
        """Step 0: Ensure all selected programs belong to this institute."""
        for row in self.programs:
            prog_company = frappe.db.get_value("Program", row.program, "company")
            if prog_company and prog_company != self.company:
                frappe.throw(
                    _("Program '{0}' belongs to another Institute. Remove it.").format(row.program)
                )

    def on_submit(self):
        """On submit, auto-create Course Schedule entries from generated slots."""
        if self.status != "Generated" or not self.routine_slots:
            frappe.throw(_("Please generate the routine before submitting."))
        self.create_course_schedules()

    def get_active_days(self):
        """Return list of active day names from checkboxes."""
        return [v for k, v in self.DAY_MAP.items() if self.get(k)]

    # =========================================================
    # READINESS CHECK (called from JS via whitelisted method)
    # =========================================================
    @frappe.whitelist()
    def check_readiness(self):
        """Run full readiness validation and return structured result."""
        company = self.company
        days = self.get_active_days()
        periods = self.periods_per_day or 5
        program_names = [r.program for r in self.programs]
        results = []
        all_ok = True

        if not program_names:
            return {"ok": False, "results": [{"status": "error", "msg": "No programs selected."}]}

        if not days:
            return {"ok": False, "results": [{"status": "error", "msg": "No school days selected."}]}

        # Per-program checks
        for pname in program_names:
            # Ownership check
            prog_company = frappe.db.get_value("Program", pname, "company")
            if prog_company and prog_company != company:
                results.append({"status": "error", "msg": f"❌ '{pname}' does not belong to your Institute."})
                all_ok = False
                continue

            # Course check
            courses = frappe.get_all(
                "Program Course", filters={"parent": pname}, fields=["course"]
            )
            if not courses:
                results.append({"status": "error", "msg": f"❌ '{pname}' has no courses assigned."})
                all_ok = False
                continue

            course_names = [c.course for c in courses]

            # Student Group (section) check
            student_groups = frappe.get_all(
                "Student Group",
                filters={"program": pname, "company": company, "disabled": 0},
                fields=["name"]
            )
            if not student_groups:
                results.append({"status": "error", "msg": f"❌ '{pname}' has no active Student Groups (sections)."})
                all_ok = False
                continue

            # Instructor mapping check
            instructors = frappe.get_all(
                "Instructor Course Mapping",
                filters={"program": pname, "course": ["in", course_names], "parenttype": "Instructor"},
                fields=["parent"],
                distinct=True
            )
            if not instructors:
                results.append({"status": "error", "msg": f"❌ No instructors mapped to '{pname}'."})
                all_ok = False
                continue

            results.append({
                "status": "ok",
                "msg": f"✅ '{pname}': {len(courses)} courses, {len(student_groups)} section(s), {len(instructors)} instructor(s)"
            })

        # Global capacity check
        all_sections = []
        for pname in program_names:
            sgs = frappe.get_all(
                "Student Group",
                filters={"program": pname, "company": company, "disabled": 0},
                pluck="name"
            )
            all_sections.extend(sgs)

        total_slots = len(all_sections) * len(days) * periods
        max_load = self.max_teacher_weekly_load or 18
        min_teachers = math.ceil(total_slots / max_load) if max_load > 0 else 0

        total_instructors = frappe.db.count("Instructor", {"company": company, "status": "Active"})

        if total_instructors < min_teachers:
            results.append({
                "status": "warning",
                "msg": f"⚠️ You have {total_instructors} teachers but need at least {min_teachers} for {total_slots} total slots ({len(all_sections)} sections × {len(days)} days × {periods} periods)."
            })
            all_ok = False
        else:
            results.append({
                "status": "ok",
                "msg": f"✅ Capacity: {total_instructors} teachers available for {total_slots} slots (need ≥{min_teachers})"
            })

        return {"ok": all_ok, "results": results, "sections": len(all_sections)}

    # =========================================================
    # SOLVER ENGINE
    # =========================================================
    @frappe.whitelist()
    def generate_routine(self):
        """Run OR-Tools CP-SAT solver to generate the timetable."""
        try:
            from ortools.sat.python import cp_model
        except ImportError:
            frappe.throw(_("OR-Tools is not installed. Run: pip install ortools"))

        company = self.company
        days = self.get_active_days()
        periods = list(range(1, (self.periods_per_day or 5) + 1))
        program_names = [r.program for r in self.programs]

        # 1. Discover all sections (Student Groups) scoped to company
        sections = []
        section_program_map = {}
        for pname in program_names:
            sgs = frappe.get_all(
                "Student Group",
                filters={"program": pname, "company": company, "disabled": 0},
                pluck="name"
            )
            for sg in sgs:
                sections.append(sg)
                section_program_map[sg] = pname

        if not sections:
            frappe.throw(_("No active Student Groups (sections) found for the selected programs."))

        # 2. Get all courses per program
        program_courses = {}
        all_courses = set()
        for pname in program_names:
            courses = frappe.get_all(
                "Program Course", filters={"parent": pname}, pluck="course"
            )
            program_courses[pname] = courses
            all_courses.update(courses)

        all_courses = list(all_courses)

        # 3. Get all instructors with their mappings (company-scoped)
        instructors = frappe.get_all(
            "Instructor",
            filters={"company": company, "status": "Active"},
            pluck="name"
        )

        if not instructors:
            frappe.throw(_("No active instructors found for your Institute."))

        # Build teacher → subject mapping from Instructor Course Mapping child table
        teacher_subject_map = {}
        teacher_preferences = {}
        for inst in instructors:
            mappings = frappe.get_all(
                "Instructor Course Mapping",
                filters={"parent": inst, "parenttype": "Instructor"},
                fields=["course", "program", "is_preferred"]
            )
            pairs = []
            for m in mappings:
                if m.program in program_names and m.course in all_courses:
                    pairs.append((m.course, m.program))
                    if m.is_preferred:
                        teacher_preferences[(inst, m.program)] = 5
            if pairs:
                teacher_subject_map[inst] = pairs

        active_teachers = list(teacher_subject_map.keys())
        if not active_teachers:
            frappe.throw(_("No instructor-course mappings found for the selected programs."))

        # 4. Build OR-Tools model
        model = cp_model.CpModel()

        # Create teacher-subject pairs index
        teacher_subject_pairs = []
        for t in active_teachers:
            for (course, program) in teacher_subject_map[t]:
                teacher_subject_pairs.append((t, course, program))

        pair_index = {i: p for i, p in enumerate(teacher_subject_pairs)}

        # Schedule variables: schedule[(section, day, period)] = index into teacher_subject_pairs
        schedule = {}
        for sg in sections:
            prog = section_program_map[sg]
            # Only valid pairs for this program
            valid_indices = [i for i, (t, c, p) in pair_index.items()
                          if p == prog and c in program_courses.get(prog, [])]

            if not valid_indices:
                frappe.throw(_(f"No valid teacher-course mappings for section '{sg}'"))

            for d in days:
                for p in periods:
                    schedule[(sg, d, p)] = model.NewIntVar(
                        0, len(teacher_subject_pairs) - 1, f"{sg}_{d}_{p}"
                    )
                    # Restrict to valid pairs only
                    model.AddAllowedAssignments(
                        [schedule[(sg, d, p)]], [[i] for i in valid_indices]
                    )

        # CONSTRAINT 1: Teacher cannot teach two sections at the same time
        for d in days:
            for p in periods:
                for t in active_teachers:
                    t_indices = [i for i, (teacher, c, pr) in pair_index.items() if teacher == t]
                    if not t_indices:
                        continue

                    bool_vars = []
                    for sg in sections:
                        for idx in t_indices:
                            b = model.NewBoolVar(f"conflict_{sg}_{d}_{p}_{t}_{idx}")
                            model.Add(schedule[(sg, d, p)] == idx).OnlyEnforceIf(b)
                            model.Add(schedule[(sg, d, p)] != idx).OnlyEnforceIf(b.Not())
                            bool_vars.append(b)

                    model.Add(sum(bool_vars) <= 1)

        # CONSTRAINT 2: Max same subject per day per section
        max_subj = self.max_subject_per_day or 2
        for sg in sections:
            prog = section_program_map[sg]
            for d in days:
                for course in program_courses.get(prog, []):
                    c_indices = [i for i, (t, c, pr) in pair_index.items()
                               if c == course and pr == prog]
                    if not c_indices:
                        continue

                    count_vars = []
                    for p in periods:
                        for idx in c_indices:
                            b = model.NewBoolVar(f"subj_{sg}_{d}_{p}_{course}")
                            model.Add(schedule[(sg, d, p)] == idx).OnlyEnforceIf(b)
                            model.Add(schedule[(sg, d, p)] != idx).OnlyEnforceIf(b.Not())
                            count_vars.append(b)

                    model.Add(sum(count_vars) <= max_subj)

        # CONSTRAINT 3: Max teacher periods per day
        max_daily = self.max_teacher_periods_per_day or 4
        for t in active_teachers:
            t_indices = [i for i, (teacher, c, pr) in pair_index.items() if teacher == t]
            for d in days:
                daily_vars = []
                for sg in sections:
                    for p in periods:
                        for idx in t_indices:
                            b = model.NewBoolVar(f"daily_{t}_{d}_{sg}_{p}")
                            model.Add(schedule[(sg, d, p)] == idx).OnlyEnforceIf(b)
                            model.Add(schedule[(sg, d, p)] != idx).OnlyEnforceIf(b.Not())
                            daily_vars.append(b)
                model.Add(sum(daily_vars) <= max_daily)

        # CONSTRAINT 4: Teacher weekly load bounds
        min_weekly = self.min_teacher_weekly_load or 8
        max_weekly = self.max_teacher_weekly_load or 18
        for t in active_teachers:
            t_indices = [i for i, (teacher, c, pr) in pair_index.items() if teacher == t]
            weekly_vars = []
            for sg in sections:
                for d in days:
                    for p in periods:
                        for idx in t_indices:
                            b = model.NewBoolVar(f"weekly_{t}_{sg}_{d}_{p}")
                            model.Add(schedule[(sg, d, p)] == idx).OnlyEnforceIf(b)
                            model.Add(schedule[(sg, d, p)] != idx).OnlyEnforceIf(b.Not())
                            weekly_vars.append(b)

            model.Add(sum(weekly_vars) >= min_weekly)
            model.Add(sum(weekly_vars) <= max_weekly)

        # OBJECTIVE: Maximize teacher preferences
        score = []
        for (t, prog), weight in teacher_preferences.items():
            t_indices = [i for i, (teacher, c, pr) in pair_index.items()
                        if teacher == t and pr == prog]
            for sg in sections:
                if section_program_map[sg] == prog:
                    for d in days:
                        for p in periods:
                            for idx in t_indices:
                                b = model.NewBoolVar(f"pref_{t}_{sg}_{d}_{p}")
                                model.Add(schedule[(sg, d, p)] == idx).OnlyEnforceIf(b)
                                model.Add(schedule[(sg, d, p)] != idx).OnlyEnforceIf(b.Not())
                                score.append(b * weight)

        if score:
            model.Maximize(sum(score))

        # 5. Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.solver_timeout or 30
        result = solver.Solve(model)

        if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            self.status = "Failed"
            self.save()
            frappe.throw(_(
                "Could not generate a valid routine with current constraints. "
                "Try adjusting constraints or adding more teachers."
            ))

        # 6. Extract solution and populate routine_slots
        self.routine_slots = []
        for sg in sections:
            prog = section_program_map[sg]
            for d in days:
                for p in periods:
                    idx = solver.Value(schedule[(sg, d, p)])
                    teacher, course, program = pair_index[idx]
                    self.append("routine_slots", {
                        "student_group": sg,
                        "program": prog,
                        "day": d,
                        "period": p,
                        "instructor": teacher,
                        "course": course
                    })

        self.status = "Generated"
        self.save()
        frappe.msgprint(
            _("Routine generated successfully for {0} sections!").format(len(sections)),
            indicator="green"
        )

    def create_course_schedules(self):
        """On submit, create native Course Schedule entries."""
        settings = frappe.get_single("Vidyaan Settings")
        period_timings = {row.period_number: (row.start_time, row.end_time)
                        for row in (settings.period_timings or [])}

        # Map day names to the next occurrence of that weekday
        from datetime import date, timedelta
        today = date.today()
        day_name_to_weekday = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }

        def next_weekday(day_name):
            target = day_name_to_weekday.get(day_name, 0)
            days_ahead = target - today.weekday()
            if days_ahead < 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).isoformat()

        count = 0
        for slot in self.routine_slots:
            from_time = period_timings.get(slot.period, (None, None))[0] if period_timings else None
            to_time = period_timings.get(slot.period, (None, None))[1] if period_timings else None

            if not from_time or not to_time:
                # Fallback: generate 45-min slots starting at 09:00
                base_hour = 9
                start_minutes = (slot.period - 1) * 45
                from_time = f"{base_hour + start_minutes // 60:02d}:{start_minutes % 60:02d}:00"
                end_minutes = start_minutes + 45
                to_time = f"{base_hour + end_minutes // 60:02d}:{end_minutes % 60:02d}:00"

            try:
                cs = frappe.get_doc({
                    "doctype": "Course Schedule",
                    "student_group": slot.student_group,
                    "instructor": slot.instructor,
                    "course": slot.course,
                    "room": slot.room if slot.room else None,
                    "from_time": from_time,
                    "to_time": to_time,
                    "schedule_date": next_weekday(slot.day)
                })
                cs.insert(ignore_permissions=True)
                count += 1
            except Exception as e:
                frappe.log_error(f"Failed to create Course Schedule: {e}")

        frappe.msgprint(
            _("{0} Course Schedule entries created.").format(count),
            indicator="green"
        )
