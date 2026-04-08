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
        # Validate period timings BEFORE we touch Course Schedule, so we never
        # silently create rows with fallback 09:00/45-min times.
        period_timings = self._require_period_timings()
        self.create_course_schedules(period_timings)

    def _require_period_timings(self):
        """Return {period_number: (start_time, end_time)} from Vidyaan Settings,
        or throw if any configured period is missing a valid timing pair."""
        settings = frappe.get_single("Vidyaan Settings")
        period_timings = {
            row.period_number: (row.start_time, row.end_time)
            for row in (settings.period_timings or [])
            if row.start_time and row.end_time
        }
        needed = list(range(1, (self.periods_per_day or 5) + 1))
        missing = [p for p in needed if p not in period_timings]
        if missing:
            frappe.throw(_(
                "Vidyaan Settings → Period Timings is missing entries for period(s): {0}. "
                "Please configure start and end times for every period before submitting "
                "the routine, otherwise Course Schedules would be created with wrong times."
            ).format(", ".join(str(p) for p in missing)))
        return period_timings

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
                fields=["name", "room"]
            )
            if not student_groups:
                results.append({"status": "error", "msg": f"❌ '{pname}' has no active Student Groups (sections)."})
                all_ok = False
                continue

            # Strict room enforcement — Course Schedule.room is mandatory
            # upstream, and the design is "one room per section, never changes".
            roomless = [sg.name for sg in student_groups if not sg.room]
            if roomless:
                preview = ", ".join(roomless[:5]) + ("…" if len(roomless) > 5 else "")
                results.append({
                    "status": "error",
                    "msg": (
                        f"❌ '{pname}' has {len(roomless)} section(s) without a Classroom assigned: "
                        f"{preview}. Open each Student Group and set the 'Classroom' field."
                    ),
                })
                all_ok = False
                continue

            # Per-course instructor coverage — the solver fails later if even
            # ONE course has no eligible teacher, so we must check every course.
            covered_courses = set(frappe.get_all(
                "Instructor Course Mapping",
                filters={
                    "program": pname,
                    "course": ["in", course_names],
                    "parenttype": "Instructor",
                },
                pluck="course",
                distinct=True,
            ))
            uncovered = [c for c in course_names if c not in covered_courses]
            if uncovered:
                preview = ", ".join(uncovered[:5]) + ("…" if len(uncovered) > 5 else "")
                results.append({
                    "status": "error",
                    "msg": (
                        f"❌ '{pname}' has {len(uncovered)} course(s) with no instructor mapped: "
                        f"{preview}. Add Instructor Course Mapping rows for these."
                    ),
                })
                all_ok = False
                continue

            # Distinct instructor count for the OK summary
            instructors = frappe.get_all(
                "Instructor Course Mapping",
                filters={"program": pname, "course": ["in", course_names], "parenttype": "Instructor"},
                fields=["parent"],
                distinct=True
            )

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
        min_load = self.min_teacher_weekly_load or 8
        max_daily = self.max_teacher_periods_per_day or 4
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

        # min_weekly_load infeasibility — silent killer of the solver.
        # If every active teacher MUST take ≥ min_load periods, the floor of
        # forced work cannot exceed the total available slots.
        if total_instructors > 0 and min_load * total_instructors > total_slots:
            suggested_min = max(0, total_slots // total_instructors)
            results.append({
                "status": "error",
                "msg": (
                    f"❌ min_teacher_weekly_load={min_load} × {total_instructors} teachers = "
                    f"{min_load * total_instructors} forced periods, but only {total_slots} slots exist. "
                    f"Lower min_teacher_weekly_load to {suggested_min} or fewer."
                ),
            })
            all_ok = False

        # Daily capacity floor — every day must fit (sections × periods) slots.
        daily_need = len(all_sections) * periods
        daily_capacity = total_instructors * max_daily
        if daily_capacity < daily_need:
            results.append({
                "status": "error",
                "msg": (
                    f"❌ Daily capacity {total_instructors} teachers × {max_daily} periods = "
                    f"{daily_capacity}, but each day needs {daily_need} slots "
                    f"({len(all_sections)} sections × {periods} periods). "
                    f"Increase max_teacher_periods_per_day or add teachers."
                ),
            })
            all_ok = False

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
        section_room_map = {}
        for pname in program_names:
            sgs = frappe.get_all(
                "Student Group",
                filters={"program": pname, "company": company, "disabled": 0},
                fields=["name", "room"],
            )
            for sg in sgs:
                sections.append(sg.name)
                section_program_map[sg.name] = pname
                section_room_map[sg.name] = sg.room

        # Strict: every selected section must have a room (Course Schedule.room
        # is mandatory upstream). Fail loudly here, before solver work.
        roomless = [s for s in sections if not section_room_map.get(s)]
        if roomless:
            preview = ", ".join(roomless[:5]) + ("…" if len(roomless) > 5 else "")
            frappe.throw(_(
                "Cannot generate routine — {0} section(s) have no Classroom assigned: {1}. "
                "Open each Student Group and set the 'Classroom' field."
            ).format(len(roomless), preview))

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

        # 3.5. Pre-flight feasibility — fail fast with a precise reason
        # instead of letting CP-SAT spend the full timeout and return INFEASIBLE.
        diagnostics = self._diagnose_feasibility(
            sections=sections,
            days=days,
            periods=periods,
            active_teachers=active_teachers,
            section_program_map=section_program_map,
            program_courses=program_courses,
        )
        if diagnostics:
            self.status = "Failed"
            self.save()
            frappe.throw(_(
                "Routine is infeasible with current configuration:\n\n• {0}"
            ).format("\n• ".join(diagnostics)))

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
            # Re-run the cheap diagnostic so the user gets concrete hints
            # even when CP-SAT itself can't explain the failure.
            hints = self._diagnose_feasibility(
                sections=sections,
                days=days,
                periods=periods,
                active_teachers=active_teachers,
                section_program_map=section_program_map,
                program_courses=program_courses,
            ) or [
                "Try lowering min_teacher_weekly_load, raising max_teacher_periods_per_day, "
                "or adding more Instructor Course Mapping rows.",
            ]
            frappe.throw(_(
                "Solver could not produce a valid routine within {0}s. Possible causes:\n\n• {1}"
            ).format(self.solver_timeout or 30, "\n• ".join(hints)))

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
                        "course": course,
                        # Inherit the section's dedicated classroom. The
                        # solver does not move sections between rooms.
                        "room": section_room_map.get(sg),
                    })

        self.status = "Generated"
        self.save()
        frappe.msgprint(
            _("Routine generated successfully for {0} sections!").format(len(sections)),
            indicator="green"
        )

    def _diagnose_feasibility(self, sections, days, periods, active_teachers,
                              section_program_map, program_courses):
        """Cheap arithmetic checks that catch the common silent killers of
        the CP-SAT solver. Returns a list of human-readable problems; empty
        list means the configuration is at least theoretically solvable.

        Edge cases respected:
        - Multi-tenant: all inputs are already company-scoped by the caller.
        - Backward compat: pure read-only, no DB writes, no signature change.
        - Idempotent: safe to call from both pre-flight and post-failure paths.
        """
        issues = []
        n_slots = len(sections) * len(days) * len(periods)
        n_teachers = len(active_teachers)
        if n_teachers == 0 or n_slots == 0:
            return ["No teachers or no slots to schedule."]

        max_weekly = self.max_teacher_weekly_load or 18
        min_weekly = self.min_teacher_weekly_load or 8
        max_daily = self.max_teacher_periods_per_day or 4
        max_subj = self.max_subject_per_day or 2

        # 1. Total weekly capacity ceiling
        total_capacity = n_teachers * max_weekly
        if total_capacity < n_slots:
            issues.append(
                f"Total teacher capacity ({n_teachers} × {max_weekly} = {total_capacity}) "
                f"is below required slots ({n_slots}). Add teachers or raise "
                f"max_teacher_weekly_load."
            )

        # 2. min_weekly_load floor — forces every teacher to take ≥ min_weekly
        floor = n_teachers * min_weekly
        if floor > n_slots:
            suggested = max(0, n_slots // n_teachers)
            issues.append(
                f"min_teacher_weekly_load={min_weekly} × {n_teachers} teachers = {floor} "
                f"forced periods, but only {n_slots} slots exist. Lower "
                f"min_teacher_weekly_load to {suggested} or fewer."
            )

        # 3. Daily capacity per day
        daily_capacity = n_teachers * max_daily
        daily_need = len(sections) * len(periods)
        if daily_capacity < daily_need:
            issues.append(
                f"Daily capacity ({n_teachers} × {max_daily} = {daily_capacity}) "
                f"is below daily slots ({daily_need}). Raise max_teacher_periods_per_day."
            )

        # 4. Per-section: enough course variety given max_subject_per_day
        for sg in sections:
            prog = section_program_map[sg]
            n_courses = len(program_courses.get(prog, []))
            week_periods = len(periods) * len(days)
            reachable = n_courses * max_subj * len(days)
            if n_courses == 0:
                issues.append(
                    f"Section '{sg}' (program '{prog}') has no courses assigned."
                )
            elif reachable < week_periods:
                issues.append(
                    f"Section '{sg}' needs {week_periods} weekly slots but the program "
                    f"has only {n_courses} course(s); with max_subject_per_day={max_subj}, "
                    f"the maximum reachable is {reachable}. Add courses to '{prog}' or "
                    f"raise max_subject_per_day."
                )

        return issues

    def create_course_schedules(self, period_timings):
        """On submit, create native Course Schedule entries.

        period_timings is the validated dict returned by _require_period_timings()
        — every configured period is guaranteed present, so we never fall back
        to silent default times.
        """
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

        # Cache section→room lookups so we don't hit the DB N times
        section_rooms = {}

        def _room_for(section_name):
            if section_name not in section_rooms:
                section_rooms[section_name] = frappe.db.get_value(
                    "Student Group", section_name, "room"
                )
            return section_rooms[section_name]

        # Pre-flight: every slot must resolve to a real Room. Course
        # Schedule.room is mandatory upstream — better to fail before any
        # insert than to leak half a routine into the database.
        missing_room_sections = set()
        for slot in self.routine_slots:
            if not (slot.room or _room_for(slot.student_group)):
                missing_room_sections.add(slot.student_group)
        if missing_room_sections:
            preview = ", ".join(sorted(missing_room_sections)[:5])
            more = (
                f"…and {len(missing_room_sections) - 5} more"
                if len(missing_room_sections) > 5 else ""
            )
            frappe.throw(_(
                "Cannot create Course Schedules — these section(s) have no "
                "Classroom set on their Student Group: {0}{1}. "
                "Set the Classroom field on each Student Group and re-submit."
            ).format(preview, more))

        count = 0
        failures = []
        for slot in self.routine_slots:
            from_time, to_time = period_timings[slot.period]
            # slot.room (stamped at generation) wins; fall back to the live
            # Student Group room for routines generated before this feature.
            resolved_room = slot.room or _room_for(slot.student_group)
            try:
                cs = frappe.get_doc({
                    "doctype": "Course Schedule",
                    "student_group": slot.student_group,
                    "instructor": slot.instructor,
                    "course": slot.course,
                    "room": resolved_room,
                    "from_time": from_time,
                    "to_time": to_time,
                    "schedule_date": next_weekday(slot.day)
                })
                cs.insert(ignore_permissions=True)
                count += 1
            except Exception as e:
                failures.append(
                    f"{slot.student_group} {slot.day} P{slot.period}: {e}"
                )
                frappe.log_error(
                    title="Routine: Course Schedule insert failed",
                    message=f"Slot {slot.name}: {e}",
                )

        if failures:
            preview = "\n• ".join(failures[:5])
            more = f"\n…and {len(failures) - 5} more" if len(failures) > 5 else ""
            frappe.throw(_(
                "Created {0} Course Schedule entries but {1} failed:\n\n• {2}{3}\n\n"
                "Fix the underlying issues and re-submit."
            ).format(count, len(failures), preview, more))

        frappe.msgprint(
            _("{0} Course Schedule entries created.").format(count),
            indicator="green"
        )
