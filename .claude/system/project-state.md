# Project State
# Auto-updated by neuro after each task

project_name: Vidyaan
project_type: school erp          # e.g. school erp, ecommerce, hrms
tech_stack:
  backend: frappe + python
  frontend: nuxt 4

## Completed Features
# List of implemented modules/features
# Format: - feature_name: [doctype/page names]

- Multi-Tenant SaaS Isolation: Company (institute), custom fields on Student, Instructor, Program, Course, Topic, Article, Program Enrollment, Course Schedule, Student Group, Student Attendance
- Setup Wizard: vidyaan_setup.js, setup/wizard.py
- AI-Powered Routine/Timetable Generation: Routine Generation, Routine Slot, Instructor Course Mapping, Period Timing, Vidyaan Settings
- Instructor-Course Mapping: Instructor Course Mapping doctype
- Period Timing Configuration: Period Timing doctype
- Examinations & Assignments: Assessment Plan, Assessment Result, Assessment Group, Course Assessment Criteria, Student Report Generation Tool
- Admit Cards: Student doctype print format
- Publication System: Publication doctype with approval workflow
- Dashboard & Workspace: Vidyaan Dashboard workspace
- Student/Teacher Frontend Portal: Nuxt 4 app with role-based pages
- Library Management: Book, Book Category, Book Copy, Book Issue, Book Request, Book Tag, Library, Library Member doctypes

## In Progress
# Currently being built

- Frontend migration from MaxEdu to Vidyaan branding
- Admin dashboard frontend
- Routine generation UI
- Attendance UI
- Fee management integration

## Backlog
# Planned but not started

- Inter-school material sharing
- Room assignment in solver
- Student Application/Leave system
- SMS/Email notifications
- Student/Parent portal login
- Report cards / Transcripts

## Ignored Suggestions
# Features suggested but user said "never"
# neuro will not suggest these again

## DocTypes
# All doctypes created in this project
# Format: - DocType: [fieldnames]

# Custom Vidyaan DocTypes
- Instructor Course Mapping: course, program, is_preferred
- Period Timing: period_number, start_time, end_time
- Publication: publication_type, title, content, target_type, target_student_group, featured_image, status, approver_role
- Routine Generation: company, program, day_filter, constraint_max_subject_per_day, constraint_max_teacher_periods_per_day, constraint_max_teacher_weekly_load, constraint_min_teacher_weekly_load, status
- Routine Generation Program: program, course_count, student_group_count
- Routine Slot: routine_generation, program, course, instructor, student_group, day_of_week, period_number, room
- Student Noc: student, noc_type, purpose, effective_date, destination, status
- Student Request: student, subject, description, category, priority, status
- Vidyaan Settings: period_timings (child table)

# Library DocTypes
- Book: title, author, isbn, category, tags, copies_available, total_copies
- Book Category: category_name, description
- Book Copy: book, copy_number, status, condition
- Book Issue: book_copy, library_member, issue_date, due_date, return_date, status
- Book Request: book, library_member, request_date, status
- Book Tag: tag_name
- Library: library_name, address, contact
- Library Member: library, user, member_id, membership_date, status

# Native Education/ERPNext DocTypes (extended)
- Company: (institute setup)
- Student: (with company field)
- Instructor: (with company field, course_mappings child table)
- Program: (with company field)
- Course: (with company field)
- Topic: (with company field)
- Article: (with company field)
- Program Enrollment: (with company field)
- Course Schedule: (with company field)
- Student Group: (with company field)
- Student Attendance: (with company field)
- Assessment Plan: (with company field)
- Assessment Result: (with company field)
- Assessment Group: (exams/assignments categories)
- Grading Scale: (with company field)
- Fee Structure: (with company field)
- Fees: (with company field)
- Publication: (custom, with company field)

## API Endpoints
# All whitelisted APIs
# Format: - /api/method/[app].[module].[method]: [what it does]

# Core APIs
- /api/method/vidyaan.api.get_student_dashboard_data: Get student dashboard stats
- /api/method/vidyaan.api.get_student_schedule: Get student timetable

# Applications
- /api/method/vidyaan.api_folder.applications.get_available_application_types: List application types
- /api/method/vidyaan.api_folder.applications.get_my_applications: Get user's applications
- /api/method/vidyaan.api_folder.applications.get_application_detail: Get application details
- /api/method/vidyaan.api_folder.applications.submit_noc: Submit NOC application
- /api/method/vidyaan.api_folder.applications.submit_request: Submit general request
- /api/method/vidyaan.api_folder.applications.submit_leave: Submit leave application

# Assignments
- /api/method/vidyaan.api_folder.assignments.get_assignments: Get student assignments
- /api/method/vidyaan.api_folder.assignments.submit_assignment: Submit assignment
- /api/method/vidyaan.api_folder.assignments.get_instructor_courses: Get instructor courses
- /api/method/vidyaan.api_folder.assignments.get_instructor_student_groups: Get student groups for course
- /api/method/vidyaan.api_folder.assignments.get_instructor_assignment_templates: Get assignment templates
- /api/method/vidyaan.api_folder.assignments.create_assignment_template: Create assignment template
- /api/method/vidyaan.api_folder.assignments.publish_assignment_template: Publish assignment
- /api/method/vidyaan.api_folder.assignments.get_template_submissions: Get submissions
- /api/method/vidyaan.api_folder.assignments.grade_assignment: Grade assignment

# Attendance
- /api/method/vidyaan.api_folder.attendance.get_attendance: Get attendance records
- /api/method/vidyaan.api_folder.attendance.get_attendance_summary: Get attendance summary

# Events
- /api/method/vidyaan.api_folder.event.get_all_events: Get all events

# Exams
- /api/method/vidyaan.api_folder.exam.get_exams: Get exam schedules
- /api/method/vidyaan.api_folder.exam.get_results: Get exam results
- /api/method/vidyaan.api_folder.exam.get_admit_data: Get admit card data

# Faculty
- /api/method/vidyaan.api_folder.faculty.get_all_faculty_data: Get faculty list

# Fees
- /api/method/vidyaan.api_folder.fees.get_my_fee: Get student fees

# Notices
- /api/method/vidyaan.api_folder.notices.get_approved_notices: Get approved notices
- /api/method/vidyaan.api_folder.notices.get_notice: Get notice by slug

# Profile
- /api/method/vidyaan.api_folder.profile.get_user_info: Get user info
- /api/method/vidyaan.api_folder.profile.get_profile: Get profile data
- /api/method/vidyaan.api_folder.profile.update_profile: Update profile

# Schedule
- /api/method/vidyaan.api_folder.schedule.get_student_schedule: Get student schedule

# Student
- /api/method/vidyaan.api_folder.student.get_student_by_institute: Get students by institute
- /api/method/vidyaan.api_folder.student.get_student_dashboard_data: Get student dashboard

# Study Materials
- /api/method/vidyaan.api_folder.study_materials.get_study_materials: Get study materials
- /api/method/vidyaan.api_folder.study_materials.get_materials_by_teacher: Get teacher materials
- /api/method/vidyaan.api_folder.study_materials.create_study_material: Create material
- /api/method/vidyaan.api_folder.study_materials.update_study_material: Update material
- /api/method/vidyaan.api_folder.study_materials.delete_study_material: Delete material

# Subjects
- /api/method/vidyaan.api_folder.subjects.get_program: Get programs

# Teacher Classes
- /api/method/vidyaan.api_folder.teachers_classes.get_my_classes: Get teacher classes
- /api/method/vidyaan.api_folder.teachers_classes.mark_attendance_bulk: Mark attendance

# Teacher Data
- /api/method/vidyaan.api_folder.teacher_data.get_my_profile: Get teacher profile
- /api/method/vidyaan.api_folder.teacher_data.get_teacher_pending_tasks: Get pending tasks

# Teacher Grading
- /api/method/vidyaan.api_folder.teacher_grading.get_my_exams: Get teacher exams
- /api/method/vidyaan.api_folder.teacher_grading.get_my_courses: Get teacher courses
- /api/method/vidyaan.api_folder.teacher_grading.get_exam_students: Get exam students
- /api/method/vidyaan.api_folder.teacher_grading.submit_exam_results: Submit exam results

# Library
- /api/method/vidyaan.library.api.get_catalog: Get book catalog
- /api/method/vidyaan.library.api.get_my_issues: Get issued books
- /api/method/vidyaan.library.api.get_my_requests: Get book requests
- /api/method/vidyaan.library.api.request_book: Request book
- /api/method/vidyaan.library.api.cancel_request: Cancel request
- /api/method/vidyaan.library.api.renew_book: Renew book
- /api/method/vidyaan.library.api.approve_renewal: Approve renewal
- /api/method/vidyaan.library.api.get_member_details: Get member details
- /api/method/vidyaan.library.api.get_book_recommendations: Get recommendations
- /api/method/vidyaan.library.api.get_library_stats: Get library stats
- /api/method/vidyaan.library.api.get_inventory: Get inventory
- /api/method/vidyaan.library.api.get_all_issues: Get all issues
- /api/method/vidyaan.library.api.get_all_requests: Get all requests
- /api/method/vidyaan.library.api.get_all_members: Get all members
- /api/method/vidyaan.library.api.return_book: Return book
- /api/method/vidyaan.library.api.approve_request: Approve request
- /api/method/vidyaan.library.api.reject_request: Reject request
- /api/method/vidyaan.library.api.issue_from_request: Issue from request

# Setup
- /api/method/vidyaan.setup.wizard.complete_setup: Complete institute setup

# Routine Generation
- /api/method/vidyaan.vidyaan.doctype.routine_generation.routine_generation.check_readiness: Check routine generation readiness
- /api/method/vidyaan.vidyaan.doctype.routine_generation.routine_generation.generate_routine: Generate routine

# Book Request
- /api/method/vidyaan.library.doctype.book_request.book_request.create_book_issue: Create book issue

## Known Limitations
# Workarounds in use — from no-solution protocol

- Orphan custom fields from previous installs (fixed in custom_fields.py cleanup)
- Publication approver role mismatch (fixed to Institute Admin)
- Examiner validation chain fragility (added fallback lookups)
- Frontend still uses MaxEdu branding (migration in progress)