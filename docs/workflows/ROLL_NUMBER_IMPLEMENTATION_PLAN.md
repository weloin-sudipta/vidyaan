# Roll Number Assignment System - Implementation Plan

**Document Version:** 1.0  
**Date:** April 18, 2026  
**Author:** Vidyaan Education App Team  
**Status:** Draft - Ready for Development

---

## Table of Contents
1. [Overview](#overview)
2. [Current State Analysis](#current-state-analysis)
3. [Data Model Design](#data-model-design)
4. [Assignment Strategies](#assignment-strategies)
5. [Implementation Plan](#implementation-plan)
6. [Edge Cases & Error Handling](#edge-cases--error-handling)
7. [Testing Strategy](#testing-strategy)
8. [Security Considerations](#security-considerations)
9. [Timeline & Milestones](#timeline--milestones)
10. [Success Criteria](#success-criteria)

---

## Overview

This document outlines a comprehensive implementation plan for a **flexible roll number assignment system** in the Vidyaan education app. The system will support multiple assignment strategies that different schools can use based on their processes:

- **Previous Year Grade-wise:** Assign roll numbers based on previous year's marks (merit-based)
- **Alphabetical by Name:** Assign based on student name (first letter, then full name)
- **Programme Enrollment Order:** Assign based on enrollment date (chronological)
- **Manual:** Admin manually assigns roll numbers per student

### Key Features
✅ Multiple assignment strategies  
✅ Preview before executing  
✅ Manual override capability  
✅ Audit trail for compliance  
✅ Automatic assignment for newly enrolled students  
✅ Multi-school/institute support  
✅ Comprehensive edge case handling  

---

## Current State Analysis

### Existing Roll Number System
- **Where:** Roll numbers currently stored in **Student Group** → `group_roll_number` field
- **Limitation:** Assigned per group sequentially (1, 2, 3...) with no strategy support
- **Scope:** Only applicable to Student Group members
- **Structure:** Stored in `Student Group Student` child table

### Relevant DocTypes & Relationships
```
Academic Year
  ├─ Student Group (one per program/batch/year)
  │  └─ Students (with group_roll_number)
  ├─ Programme Enrollment (student → program → year)
  │  └─ Course Enrollment (auto-created)
  └─ Assessment Result (student grades)
```

### Data Available for Assignment
- ✅ **Previous Year Marks:** Stored in Assessment Result DocType
- ✅ **Student Names:** Available in Student DocType
- ✅ **Enrollment Dates:** Stored in Programme Enrollment
- ✅ **Student Status:** Active/Inactive tracked in Student Group Student
- ✅ **Multi-tenancy:** All data already isolated by `company` field

### Gaps to Fill
- ❌ No global `roll_number` field on Student
- ❌ No strategy configuration system
- ❌ No audit trail for roll number assignments
- ❌ No preview/approval mechanism
- ❌ No automatic assignment for new enrollments

---

## Data Model Design

### 1. New DocType: "Roll Number Assignment"

**Purpose:** Main tool for assigning roll numbers with full audit trail and flexibility

**Location:** `vidyaan/vidyaan/doctype/roll_number_assignment/`

**Fields:**
```json
{
  "doctype": "Roll Number Assignment",
  "fields": [
    {
      "fieldname": "academic_year",
      "fieldtype": "Link",
      "options": "Academic Year",
      "reqd": 1,
      "label": "Academic Year"
    },
    {
      "fieldname": "program",
      "fieldtype": "Link",
      "options": "Program",
      "reqd": 1,
      "label": "Program"
    },
    {
      "fieldname": "assignment_strategy",
      "fieldtype": "Select",
      "options": "Previous Year Grade-wise\nAlphabetical by Name\nProgramme Enrollment Order\nManual",
      "reqd": 1,
      "label": "Assignment Strategy",
      "default": "Previous Year Grade-wise"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "options": "Draft\nCompleted\nPartially Completed\nCancelled",
      "read_only": 1,
      "label": "Status",
      "default": "Draft"
    },
    {
      "fieldname": "total_students",
      "fieldtype": "Int",
      "read_only": 1,
      "label": "Total Students",
      "default": 0
    },
    {
      "fieldname": "assigned_count",
      "fieldtype": "Int",
      "read_only": 1,
      "label": "Assigned Count",
      "default": 0
    },
    {
      "fieldname": "pending_count",
      "fieldtype": "Int",
      "read_only": 1,
      "label": "Pending Count",
      "default": 0
    },
    {
      "fieldname": "created_by_user",
      "fieldtype": "Link",
      "options": "User",
      "read_only": 1,
      "label": "Created By"
    },
    {
      "fieldname": "execution_date",
      "fieldtype": "DateTime",
      "read_only": 1,
      "label": "Executed On"
    },
    {
      "fieldname": "notes",
      "fieldtype": "Text Editor",
      "label": "Notes & Comments"
    },
    {
      "fieldname": "assignments",
      "fieldtype": "Table",
      "options": "Roll Number Assignment Detail",
      "label": "Roll Number Assignments"
    }
  ]
}
```

**Child Table: "Roll Number Assignment Detail"**
```json
{
  "doctype": "Roll Number Assignment Detail",
  "fields": [
    {
      "fieldname": "student",
      "fieldtype": "Link",
      "options": "Student",
      "reqd": 1
    },
    {
      "fieldname": "student_name",
      "fieldtype": "Data",
      "read_only": 1
    },
    {
      "fieldname": "assigned_roll_number",
      "fieldtype": "Int",
      "label": "Assigned Roll Number"
    },
    {
      "fieldname": "assignment_method",
      "fieldtype": "Select",
      "options": "Auto\nManual",
      "default": "Auto"
    },
    {
      "fieldname": "sort_value",
      "fieldtype": "Data",
      "label": "Sort Basis",
      "help": "Marks for grade-wise, name for alphabetical, enrollment date for order"
    },
    {
      "fieldname": "status",
      "fieldtype": "Select",
      "options": "Assigned\nPending",
      "default": "Assigned"
    },
    {
      "fieldname": "assigned_on",
      "fieldtype": "DateTime",
      "read_only": 1
    }
  ]
}
```

---

### 2. New DocType: "Roll Number Settings"

**Purpose:** School-wide configuration for roll number assignment behavior

**Location:** `vidyaan/vidyaan/doctype/roll_number_settings/`

**Fields:**
```json
{
  "doctype": "Roll Number Settings",
  "fields": [
    {
      "fieldname": "company",
      "fieldtype": "Link",
      "options": "Company",
      "reqd": 1,
      "unique": 1,
      "label": "Institute/School"
    },
    {
      "fieldname": "default_strategy",
      "fieldtype": "Select",
      "options": "Previous Year Grade-wise\nAlphabetical by Name\nProgramme Enrollment Order\nManual",
      "default": "Previous Year Grade-wise",
      "label": "Default Assignment Strategy"
    },
    {
      "fieldname": "auto_assign_new_students",
      "fieldtype": "Check",
      "default": 1,
      "label": "Auto-assign Roll Numbers for Newly Enrolled Students"
    },
    {
      "fieldname": "roll_number_format",
      "fieldtype": "Select",
      "options": "Sequential\nPrefixed\nProgram-Year",
      "default": "Sequential",
      "label": "Roll Number Format",
      "help": "Sequential: 1,2,3 | Prefixed: A001,A002 | Program-Year: PRO-2026-001"
    },
    {
      "fieldname": "roll_number_prefix",
      "fieldtype": "Data",
      "label": "Prefix (if applicable)",
      "help": "e.g., 'A' for A001, '10-' for 10-001"
    },
    {
      "fieldname": "roll_number_starting_value",
      "fieldtype": "Int",
      "default": 1,
      "label": "Starting Roll Number"
    },
    {
      "fieldname": "handle_new_midyear_students",
      "fieldtype": "Select",
      "options": "Auto Assign Last + 1\nLeave Blank\nAssign in Next Batch",
      "default": "Auto Assign Last + 1",
      "label": "New Mid-Year Students Strategy"
    },
    {
      "fieldname": "require_approval_before_execute",
      "fieldtype": "Check",
      "default": 1,
      "label": "Require Preview Approval Before Executing"
    }
  ]
}
```

---

### 3. Modification to Student DocType

**Add Field: `roll_number`**
```json
{
  "fieldname": "roll_number",
  "fieldtype": "Link",
  "options": "Roll Number Assignment",
  "label": "Roll Number Assignment",
  "read_only": 1,
  "help": "Automatically populated when roll number is assigned",
  "description": "Reference to the Roll Number Assignment that assigned this student's number"
}
```

**Add Field: `student_roll_number`** (Display only - for quick view)
```json
{
  "fieldname": "student_roll_number",
  "fieldtype": "Int",
  "label": "Roll Number",
  "read_only": 1,
  "help": "Current assigned roll number",
  "depends_on": "eval: doc.roll_number"
}
```

---

## Assignment Strategies

### Strategy 1: Previous Year Grade-wise

**Logic Flow:**
```
1. Fetch all Programme Enrollments for (academic_year, program)
2. For each enrolled student:
   a. Query Assessment Result for previous_year (same program if applicable)
   b. Get total_score (marks)
   c. If no previous year data → mark as "Pending", roll_number = null
3. Sort students by:
   - Primary: total_score DESC (highest marks first)
   - Secondary: first_name ASC (alphabetical as tiebreaker)
4. Assign sequential roll numbers (1, 2, 3...)
5. For pending students → assign after all merit-sorted students
```

**Best For:** Merit-based schools, competitive programs

**Python Implementation:**
```python
def assign_by_previous_grade(academic_year, program):
    """Assign roll numbers based on previous year grade"""
    
    # Get all enrolled students
    enrollments = frappe.get_all(
        'Programme Enrollment',
        filters={
            'academic_year': academic_year,
            'program': program,
            'docstatus': 1
        },
        fields=['student', 'student_name']
    )
    
    students_with_marks = []
    pending_students = []
    
    previous_year = get_previous_academic_year(academic_year)
    
    for enrollment in enrollments:
        # Try to get previous year marks
        marks = get_previous_year_marks(enrollment.student, program, previous_year)
        
        if marks is not None:
            students_with_marks.append({
                'student': enrollment.student,
                'name': enrollment.student_name,
                'marks': marks,
                'sort_value': str(marks)
            })
        else:
            pending_students.append({
                'student': enrollment.student,
                'name': enrollment.student_name,
                'marks': None,
                'sort_value': 'No Previous Year Data'
            })
    
    # Sort by marks DESC, then name ASC
    students_with_marks.sort(
        key=lambda x: (-x['marks'], x['name'])
    )
    
    # Combine: graded students first, then pending
    final_order = students_with_marks + pending_students
    
    # Assign roll numbers
    assignments = []
    for idx, student in enumerate(final_order):
        roll_number = idx + 1 if student['marks'] is not None else None
        assignments.append({
            'student': student['student'],
            'assigned_roll_number': roll_number,
            'sort_value': student['sort_value'],
            'status': 'Assigned' if roll_number else 'Pending'
        })
    
    return assignments
```

**Edge Cases:**
- ✅ Student new to school (no previous year data) → Blank roll number, marked "Pending"
- ✅ Multiple students with same marks → Alphabetical tiebreaker
- ✅ Previous year marks not finalized → Delay assignment or mark "Pending"
- ✅ Student has multiple Assessment Results → Take latest/highest

---

### Strategy 2: Alphabetical by Name

**Logic Flow:**
```
1. Fetch all Programme Enrollments for (academic_year, program)
2. For each student, extract:
   - first_letter = first_name[0].upper()
   - full_name = first_name + last_name
3. Sort by:
   - Primary: first_letter ASC
   - Secondary: full_name ASC
4. Assign sequential roll numbers (1, 2, 3...)
```

**Best For:** All types of schools, fair allocation

**Python Implementation:**
```python
def assign_by_name(academic_year, program):
    """Assign roll numbers alphabetically by name"""
    
    enrollments = frappe.get_all(
        'Programme Enrollment',
        filters={
            'academic_year': academic_year,
            'program': program,
            'docstatus': 1
        },
        fields=['student'],
        as_dict=True
    )
    
    # Fetch full student info
    students = []
    for enrollment in enrollments:
        student_doc = frappe.get_doc('Student', enrollment.student)
        first_letter = (student_doc.first_name[0] if student_doc.first_name else 'Z').upper()
        full_name = f"{student_doc.first_name or ''} {student_doc.last_name or ''}"
        
        students.append({
            'student': student_doc.name,
            'first_letter': first_letter,
            'full_name': full_name.strip(),
            'sort_value': f"{first_letter} - {full_name}"
        })
    
    # Sort alphabetically
    students.sort(key=lambda x: (x['first_letter'], x['full_name']))
    
    # Assign
    assignments = []
    for idx, student in enumerate(students):
        assignments.append({
            'student': student['student'],
            'assigned_roll_number': idx + 1,
            'sort_value': student['sort_value'],
            'status': 'Assigned'
        })
    
    return assignments
```

**Edge Cases:**
- ✅ Student with no first_name → Use email or ID as fallback
- ✅ Special characters in name → Sanitize before sorting
- ✅ Duplicate full names → Maintain chronological order as secondary sort

---

### Strategy 3: Programme Enrollment Order

**Logic Flow:**
```
1. Fetch all Programme Enrollments for (academic_year, program)
2. Order by: creation date ASC (oldest first)
3. Assign sequential roll numbers (1, 2, 3...)
```

**Best For:** Fair first-come-first-served allocation

**Python Implementation:**
```python
def assign_by_enrollment_order(academic_year, program):
    """Assign roll numbers by enrollment order (chronological)"""
    
    enrollments = frappe.get_all(
        'Programme Enrollment',
        filters={
            'academic_year': academic_year,
            'program': program,
            'docstatus': 1
        },
        fields=['student', 'student_name', 'creation'],
        order_by='creation ASC'
    )
    
    assignments = []
    for idx, enrollment in enumerate(enrollments):
        assignments.append({
            'student': enrollment.student,
            'assigned_roll_number': idx + 1,
            'sort_value': enrollment.creation.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'Assigned'
        })
    
    return assignments
```

**Edge Cases:**
- ✅ Students enrolled on same date → Maintain database order
- ✅ New enrollment added after assignment → Auto-assign with next available number

---

### Strategy 4: Manual Assignment

**Logic Flow:**
```
1. Display all enrolled students in a table
2. Admin manually enters roll numbers for each
3. Validate: No duplicates, no gaps
4. Commit only after validation
```

**Python Implementation:**
```python
def validate_manual_assignment(assignment_doc):
    """Validate manually assigned roll numbers"""
    
    roll_numbers = []
    for detail in assignment_doc.assignments:
        if detail.assigned_roll_number:
            if detail.assigned_roll_number in roll_numbers:
                frappe.throw(f"Duplicate roll number: {detail.assigned_roll_number}")
            roll_numbers.append(detail.assigned_roll_number)
    
    # Check for reasonable range
    if roll_numbers:
        max_roll = max(roll_numbers)
        if max_roll > len(assignment_doc.assignments) * 1.5:
            frappe.msgprint("Warning: Roll number seems too high for student count")
    
    return True
```

**Edge Cases:**
- ✅ Admin leaves some students blank → Mark as "Pending"
- ✅ Admin enters duplicate numbers → Validation error
- ✅ Roll number > student count → Allowed (for flexibility)

---

## Implementation Plan

### Phase 1: Data Model & Backend Setup (Days 1-3)

**Deliverables:**
- ✅ Roll Number Assignment DocType created
- ✅ Roll Number Settings DocType created
- ✅ Student DocType extended with roll_number field
- ✅ Database migrations applied
- ✅ Default settings configured for school

**Tasks:**
1. Create DocType JSON files in `vidyaan/vidyaan/doctype/`
2. Create migration script for Student field
3. Initialize default Roll Number Settings for company
4. Run `bench migrate` to apply changes

**Files to Create:**
```
vidyaan/vidyaan/doctype/roll_number_assignment/
├── roll_number_assignment.json
├── roll_number_assignment.py
└── roll_number_assignment.js

vidyaan/vidyaan/doctype/roll_number_assignment_detail/
└── roll_number_assignment_detail.json

vidyaan/vidyaan/doctype/roll_number_settings/
├── roll_number_settings.json
└── roll_number_settings.py

vidyaan/patches/
└── v1_0_0_add_roll_number_to_student.py
```

---

### Phase 2: Core Assignment Logic (Days 4-8)

**Deliverables:**
- ✅ All 4 assignment strategy functions implemented
- ✅ Unit tests passing
- ✅ Helper functions for formatting & validation

**File:** `vidyaan/vidyaan/api_folder/roll_number.py`

**Functions to Implement:**
```python
# Utility functions
get_academic_year_by_name(name)
get_previous_academic_year(academic_year)
get_programme_enrollment_students(academic_year, program)
get_previous_year_marks(student, program, previous_year)
format_roll_number(number, settings)

# Strategy functions
assign_by_previous_grade(academic_year, program, settings)
assign_by_name(academic_year, program, settings)
assign_by_enrollment_order(academic_year, program, settings)
prepare_manual_assignment(academic_year, program, settings)

# Main orchestrator
validate_assignment_prerequisites(academic_year, program, strategy)
execute_assignment(assignment_doc)
rollback_assignment(assignment_doc)
update_student_roll_numbers(assignment_doc)
sync_to_student_group(assignment_doc)

# API endpoints
@frappe.whitelist()
def preview_assignment(academic_year, program, strategy):
    """Preview roll number assignment before executing"""

@frappe.whitelist()
def execute_roll_number_assignment(assignment_name):
    """Execute the assignment and update Student records"""

@frappe.whitelist()
def get_unassigned_students(academic_year, program):
    """Get students with no roll number assigned"""
```

**Testing:**
```python
# test_roll_number_assignment.py
def test_assign_by_previous_grade():
    # Test merit-based assignment
    # Verify marks sorting
    # Verify tiebreaker (alphabetical)
    # Verify pending handling

def test_assign_by_name():
    # Test alphabetical sorting
    # Test special characters handling
    # Test duplicate names

def test_assign_by_enrollment_order():
    # Test chronological ordering
    # Test creation date sorting

def test_format_roll_number():
    # Test Sequential: 1, 2, 3
    # Test Prefixed: A001, A002
    # Test Program-Year: PRO-2026-001

def test_validate_no_duplicates():
    # Test duplicate detection
    # Test error handling

def test_handle_missing_previous_year():
    # Test new student handling
    # Test pending status
```

---

### Phase 3: Frontend UI & Preview (Days 9-14)

**Deliverables:**
- ✅ Roll Number Assignment form UI
- ✅ Preview table with manual editing
- ✅ Execute and rollback buttons
- ✅ CSV export functionality
- ✅ Error handling & user feedback

**File:** `vidyaan/vidyaan/doctype/roll_number_assignment/roll_number_assignment.js`

**Features to Implement:**

```javascript
// 1. Strategy Selection UI
frappe.ui.form.on('Roll Number Assignment', {
  onload: function(frm) {
    // Load available strategies
    // Show relevant help text
  },
  
  assignment_strategy: function(frm) {
    // Update form based on strategy
    // Show preview recommendations
  }
})

// 2. Preview Button
cur_frm.add_custom_button('Preview Assignment', function() {
  frappe.call({
    method: 'vidyaan.api_folder.roll_number.preview_assignment',
    args: {
      academic_year: frm.doc.academic_year,
      program: frm.doc.program,
      strategy: frm.doc.assignment_strategy
    },
    callback: function(r) {
      if (r.message) {
        show_preview_modal(r.message)
      }
    }
  })
})

// 3. Execute Button
cur_frm.add_custom_button('Execute Assignment', function() {
  frappe.confirm(
    'Are you sure? This will assign roll numbers to all students.',
    function() {
      frappe.call({
        method: 'vidyaan.api_folder.roll_number.execute_roll_number_assignment',
        args: { assignment_name: frm.doc.name },
        callback: function(r) {
          if (r.message.success) {
            frappe.msgprint('Roll numbers assigned successfully!')
            frm.reload_doc()
          }
        }
      })
    }
  )
})

// 4. Preview Modal with Editing
function show_preview_modal(preview_data) {
  let html = `<table class="table table-bordered">
    <thead>
      <tr>
        <th>Student Name</th>
        <th>Current Roll#</th>
        <th>Proposed Roll#</th>
        <th>Sort Value</th>
        <th>Status</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>`
  
  preview_data.forEach(item => {
    html += `<tr>
      <td>${item.student_name}</td>
      <td>${item.current_roll_number || '-'}</td>
      <td><input type="number" class="form-control" 
           value="${item.assigned_roll_number || ''}" 
           data-student="${item.student}"></td>
      <td>${item.sort_value}</td>
      <td><span class="badge">${item.status}</span></td>
      <td><button class="btn btn-sm btn-danger">Clear</button></td>
    </tr>`
  })
  
  html += `</tbody></table>
    <button class="btn btn-primary">Confirm & Execute</button>
    <button class="btn btn-default">Cancel</button>`
  
  frappe.msgprint({
    message: html,
    title: 'Preview Roll Number Assignment'
  })
}

// 5. Export to CSV
cur_frm.add_custom_button('Export CSV', function() {
  let csv = 'Student Name,Assigned Roll Number,Sort Value,Status\n'
  frm.doc.assignments.forEach(item => {
    csv += `"${item.student_name}",${item.assigned_roll_number},${item.sort_value},${item.status}\n`
  })
  
  let blob = new Blob([csv], { type: 'text/csv' })
  let url = window.URL.createObjectURL(blob)
  let a = document.createElement('a')
  a.href = url
  a.download = `roll_numbers_${frm.doc.academic_year}_${frm.doc.program}.csv`
  a.click()
})
```

**Preview Table Features:**
- Student Name | Current Roll# | Proposed Roll# | Sort Value | Status | Action
- Allow manual editing of proposed roll numbers
- Show warning if duplicate detected
- Show warning if data missing
- Color-code pending students

---

### Phase 4: Edge Cases & Error Handling (Days 15-18)

**Deliverables:**
- ✅ All edge cases handled
- ✅ Detailed error messages
- ✅ Rollback mechanism
- ✅ Audit trail & logging

**Edge Case Handling:**

| Edge Case | Solution | Code Location |
|-----------|----------|----------------|
| **Student in current year but NOT previous year** | `assign_by_previous_grade()` sets roll_number = null, status = "Pending" | In strategy function |
| **Multiple students with identical marks** | Use alphabetical name as tiebreaker in sort lambda | Strategy function |
| **New student enrolled after assignment** | Check `auto_assign_new_students` setting; auto-assign last+1 | Webhook in Programme Enrollment |
| **Admin cancels assignment halfway** | Rollback function sets all assigned roll_numbers to null, marked as Draft | `rollback_assignment()` |
| **Duplicate roll number detected** | Pre-execution validation throws error with conflicting numbers | `execute_assignment()` |
| **Student enrollment status changes** | Revalidate before executing; show warning if status changed | `validate_assignment_prerequisites()` |
| **Multi-school scenario** | All queries filtered by `company` field (native Frappe isolation) | Query filters |
| **Marks not yet finalized** | Check Assessment Result status; show warning; recommend "Manual" strategy | `validate_assignment_prerequisites()` |
| **Student with no name** | Use email or Student ID as fallback for sorting | Strategy functions |
| **Concurrent assignment attempts** | Add unique constraint: (academic_year, program, status != "Cancelled") | DocType validation |

**Implementation:**

```python
# vidyaan/api_folder/roll_number.py

def validate_assignment_prerequisites(academic_year, program, strategy):
    """Pre-flight checks before assignment"""
    
    # Check: Academic year exists
    if not frappe.db.exists('Academic Year', academic_year):
        raise ValueError(f"Academic Year {academic_year} not found")
    
    # Check: Program exists
    if not frappe.db.exists('Program', program):
        raise ValueError(f"Program {program} not found")
    
    # Check: No concurrent assignment in progress
    existing = frappe.get_all(
        'Roll Number Assignment',
        filters={
            'academic_year': academic_year,
            'program': program,
            'status': ['in', ['Draft', 'Completed']]
        }
    )
    if existing:
        raise ValueError(
            f"Assignment already exists for {academic_year}/{program}. "
            f"Please cancel the previous one first."
        )
    
    # Check: Sufficient enrolled students
    enrollments = get_programme_enrollment_students(academic_year, program)
    if not enrollments:
        raise ValueError(f"No enrolled students found for {academic_year}/{program}")
    
    # Strategy-specific checks
    if strategy == "Previous Year Grade-wise":
        prev_year = get_previous_academic_year(academic_year)
        if not prev_year:
            frappe.msgprint(
                "Warning: No previous academic year found. "
                "All students will be marked as Pending.",
                indicator='orange'
            )
    
    return True


def execute_assignment(assignment_doc):
    """Main execution orchestrator"""
    
    try:
        # Validate
        validate_assignment_prerequisites(
            assignment_doc.academic_year,
            assignment_doc.program,
            assignment_doc.assignment_strategy
        )
        
        # Get assignments based on strategy
        assignments = []
        if assignment_doc.assignment_strategy == "Previous Year Grade-wise":
            assignments = assign_by_previous_grade(
                assignment_doc.academic_year,
                assignment_doc.program
            )
        elif assignment_doc.assignment_strategy == "Alphabetical by Name":
            assignments = assign_by_name(
                assignment_doc.academic_year,
                assignment_doc.program
            )
        elif assignment_doc.assignment_strategy == "Programme Enrollment Order":
            assignments = assign_by_enrollment_order(
                assignment_doc.academic_year,
                assignment_doc.program
            )
        
        # Validate no duplicates
        roll_numbers = [a['assigned_roll_number'] for a in assignments if a['assigned_roll_number']]
        if len(roll_numbers) != len(set(roll_numbers)):
            duplicates = [x for x in roll_numbers if roll_numbers.count(x) > 1]
            raise ValueError(f"Duplicate roll numbers detected: {duplicates}")
        
        # Update assignment_doc
        assignment_doc.assignments = []
        for assignment in assignments:
            assignment_doc.append('assignments', assignment)
        
        assignment_doc.total_students = len(assignments)
        assignment_doc.assigned_count = len([a for a in assignments if a['status'] == 'Assigned'])
        assignment_doc.pending_count = len([a for a in assignments if a['status'] == 'Pending'])
        assignment_doc.status = 'Completed' if assignment_doc.pending_count == 0 else 'Partially Completed'
        assignment_doc.execution_date = frappe.utils.now()
        assignment_doc.save(ignore_permissions=True)
        
        # Update Student records
        update_student_roll_numbers(assignment_doc)
        
        # Sync to Student Group (for backward compatibility)
        sync_to_student_group(assignment_doc)
        
        # Log audit trail
        log_assignment_audit(
            assignment_doc.name,
            assignment_doc.academic_year,
            assignment_doc.program,
            assignment_doc.assignment_strategy,
            'Success',
            frappe.session.user
        )
        
        return {'success': True, 'message': 'Roll numbers assigned successfully'}
        
    except Exception as e:
        frappe.log_error(
            title="Roll Number Assignment Error",
            message=str(e),
            reference_doctype="Roll Number Assignment",
            reference_name=assignment_doc.name
        )
        raise


def rollback_assignment(assignment_doc):
    """Rollback executed assignment"""
    
    if assignment_doc.status == 'Draft':
        return {'message': 'Assignment not executed yet'}
    
    try:
        # Clear Student roll_number field
        for detail in assignment_doc.assignments:
            student = frappe.get_doc('Student', detail.student)
            student.roll_number = None
            student.student_roll_number = None
            student.save(ignore_permissions=True)
        
        # Clear assignment status
        assignment_doc.status = 'Draft'
        assignment_doc.assignments = []
        assignment_doc.execution_date = None
        assignment_doc.save(ignore_permissions=True)
        
        # Log audit
        log_assignment_audit(
            assignment_doc.name,
            assignment_doc.academic_year,
            assignment_doc.program,
            'Rollback',
            'Success',
            frappe.session.user
        )
        
        frappe.msgprint('Assignment rolled back successfully')
        return {'success': True}
        
    except Exception as e:
        frappe.log_error(title="Rollback Error", message=str(e))
        raise
```

---

### Phase 5: Automation & Post-Assignment (Days 19-21)

**Deliverables:**
- ✅ Auto-assignment hook for new enrollments
- ✅ Notification system
- ✅ Sync to Student Group
- ✅ Cache invalidation

**File:** `vidyaan/hooks.py`

```python
doc_events = {
    "Programme Enrollment": {
        "on_submit": "vidyaan.api_folder.roll_number.auto_assign_on_new_enrollment"
    }
}

hooks = [
    # ... other hooks ...
    doc_events
]
```

**Implementation:**

```python
# vidyaan/api_folder/roll_number.py

def auto_assign_on_new_enrollment(doc, method):
    """Auto-assign roll number when student enrolls mid-year"""
    
    # Get Roll Number Settings
    try:
        settings = frappe.get_doc("Roll Number Settings", doc.company)
    except:
        # Settings not configured
        return
    
    if not settings.auto_assign_new_students:
        return
    
    # Check if assignment exists for this year/program
    active_assignment = frappe.get_all(
        'Roll Number Assignment',
        filters={
            'academic_year': doc.academic_year,
            'program': doc.program,
            'status': ['!=', 'Draft']
        },
        limit=1
    )
    
    if not active_assignment:
        # No active assignment, skip
        return
    
    assignment_doc = frappe.get_doc('Roll Number Assignment', active_assignment[0].name)
    
    # Check if student already has roll number
    if frappe.db.exists('Student', {'name': doc.student, 'roll_number': ['!=', '']}):
        return
    
    # Get last assigned roll number
    last_detail = frappe.db.get_all(
        'Roll Number Assignment Detail',
        filters={'parent': assignment_doc.name},
        fields=['assigned_roll_number'],
        order_by='assigned_roll_number desc',
        limit=1
    )
    
    if last_detail:
        new_roll_number = last_detail[0].assigned_roll_number + 1
    else:
        new_roll_number = settings.roll_number_starting_value
    
    # Add to assignment
    assignment_doc.append('assignments', {
        'student': doc.student,
        'assigned_roll_number': new_roll_number,
        'assignment_method': 'Auto',
        'sort_value': f'New enrollment - {frappe.utils.now()}',
        'status': 'Assigned'
    })
    
    assignment_doc.assigned_count += 1
    assignment_doc.total_students += 1
    assignment_doc.save(ignore_permissions=True)
    
    # Update Student
    student = frappe.get_doc('Student', doc.student)
    student.roll_number = assignment_doc.name
    student.student_roll_number = new_roll_number
    student.save(ignore_permissions=True)
    
    # Notify
    frappe.publish_realtime(
        'roll_number_assigned',
        {
            'student': doc.student,
            'roll_number': new_roll_number,
            'academic_year': doc.academic_year
        },
        user=frappe.session.user
    )


def update_student_roll_numbers(assignment_doc):
    """Update Student DocType with assigned roll numbers"""
    
    for detail in assignment_doc.assignments:
        student = frappe.get_doc('Student', detail.student)
        student.roll_number = assignment_doc.name
        student.student_roll_number = detail.assigned_roll_number
        student.save(ignore_permissions=True)


def sync_to_student_group(assignment_doc):
    """Sync roll numbers to Student Group for backward compatibility"""
    
    # Find Student Group for this program/year
    student_groups = frappe.get_all(
        'Student Group',
        filters={
            'academic_year': assignment_doc.academic_year,
            'program': assignment_doc.program
        }
    )
    
    for sg in student_groups:
        sg_doc = frappe.get_doc('Student Group', sg.name)
        
        # Update group_roll_number for each student
        for student_row in sg_doc.students:
            detail = next(
                (d for d in assignment_doc.assignments if d.student == student_row.student),
                None
            )
            if detail:
                student_row.group_roll_number = detail.assigned_roll_number
        
        sg_doc.save(ignore_permissions=True)


def log_assignment_audit(assignment_id, academic_year, program, strategy, status, user):
    """Audit trail logging"""
    
    frappe.db.set_value(
        'Roll Number Assignment',
        assignment_id,
        {
            'created_by_user': user,
            'execution_date': frappe.utils.now() if status == 'Success' else None
        }
    )
    
    # Log to system log
    frappe.logger().info(
        f"Roll Number Assignment: {assignment_id} | "
        f"Year: {academic_year} | Program: {program} | "
        f"Strategy: {strategy} | Status: {status} | User: {user}"
    )


def get_previous_academic_year(academic_year):
    """Get previous academic year"""
    
    current_year = frappe.get_doc('Academic Year', academic_year)
    
    prev_years = frappe.get_all(
        'Academic Year',
        filters={'year_end_date': ['<', current_year.year_start_date]},
        order_by='year_end_date desc',
        limit=1
    )
    
    if prev_years:
        return prev_years[0].name
    return None
```

---

## Edge Cases & Error Handling

### Comprehensive Edge Case Table

| # | Edge Case | Severity | Solution | Detection | Rollback |
|---|-----------|----------|----------|-----------|----------|
| 1 | Student in current year but NO previous year data | Medium | Mark as "Pending", roll_number = null | In strategy function | Auto |
| 2 | Multiple students with identical marks | Low | Alphabetical tiebreaker by name | Sort lambda | N/A |
| 3 | New student enrolled AFTER assignment complete | Medium | Auto-assign last+1 if auto_assign_enabled | Hook on Programme Enrollment | Manual |
| 4 | Admin cancels mid-execution | High | Rollback: set all roll_numbers to null | Try-except in execute | Rollback function |
| 5 | Duplicate roll number assigned | Critical | Validation before execute, throw error | Pre-execution validation | Prevent |
| 6 | Student marked inactive after assignment | Medium | Revalidate; warn admin | `validate_assignment_prerequisites()` | Manual decision |
| 7 | Two schools (multi-tenant) assignments collide | Critical | Isolated by `company` field | Query filters | Native isolation |
| 8 | Assessment marks not finalized | Medium | Show warning; recommend "Manual" strategy | `validate_assignment_prerequisites()` | Admin choice |
| 9 | Student with no first/last name | Low | Use email or ID as fallback | Fallback in strategy functions | N/A |
| 10 | Concurrent assignment attempts | High | Unique constraint: (year, program, status) | DB constraint | Prevent |
| 11 | Roll number format conflicts | Low | Validate format before execute | `validate_roll_number_format()` | Prevent |
| 12 | Student enrollment deleted during execution | High | Try-catch; partial rollback | Exception handling | Partial rollback |
| 13 | Network failure during bulk update | High | Transaction isolation; DB rollback | DB transaction | DB rollback |
| 14 | Permission denied on Student update | High | Verify System Manager access | `ignore_permissions=True` | Check access |
| 15 | Roll number exceeds database field limit | Low | Validate max value (Int = 2,147,483,647) | Field validation | Prevent |

### Error Messages & User Feedback

```python
# Validation Error Messages
ERROR_NO_STUDENTS = "No enrolled students found for {0}/{1}"
ERROR_PREVIOUS_YEAR_NOT_FOUND = "Previous academic year not found. Consider using 'Alphabetical by Name' strategy"
ERROR_MARKS_NOT_FINALIZED = "Assessment marks for {0} are not yet finalized. Please finalize before proceeding"
ERROR_DUPLICATE_ROLL_NUMBERS = "Duplicate roll numbers detected: {0}. Please review and try again"
ERROR_CONCURRENT_ASSIGNMENT = "An assignment is already in progress for {0}/{1}. Please wait or cancel it first"

# Warning Messages
WARNING_NO_PREVIOUS_YEAR = "{0} students have no previous year data and will be marked as Pending"
WARNING_NEW_MID_YEAR = "New students enrolled after this assignment will be auto-assigned roll numbers"
WARNING_READONLY_FIELDS = "Note: Roll numbers are read-only once assigned. Use 'Rollback' to reassign"

# Success Messages
SUCCESS_ASSIGNMENT_COMPLETED = "Roll numbers assigned successfully to {0} students ({1} assigned, {2} pending)"
SUCCESS_ASSIGNMENT_ROLLED_BACK = "Assignment rolled back. All roll numbers cleared"
```

---

## Testing Strategy

### Unit Tests

**File:** `vidyaan/tests/test_roll_number_assignment.py`

```python
import frappe
from frappe.test_utils import FrappeTestCase
from vidyaan.api_folder.roll_number import *

class TestRollNumberAssignment(FrappeTestCase):
    
    def setUp(self):
        """Set up test data"""
        self.academic_year = frappe.get_doc({
            'doctype': 'Academic Year',
            'academic_year_name': '2026',
            'year_start_date': '2026-01-01',
            'year_end_date': '2026-12-31'
        }).insert()
        
        self.program = frappe.get_doc({
            'doctype': 'Program',
            'program_name': 'Bachelor of Science',
            'program_abbreviation': 'B.Sc'
        }).insert()
        
        # Create test students
        self.students = []
        names = [('Alice', 'Kumar', 95), ('Bob', 'Singh', 93), ('Charlie', 'Patel', 88)]
        for first, last, marks in names:
            student = frappe.get_doc({
                'doctype': 'Student',
                'first_name': first,
                'last_name': last
            }).insert()
            self.students.append(student)
    
    # Test 1: Previous Year Grade-wise
    def test_assign_by_previous_grade(self):
        assignments = assign_by_previous_grade(
            self.academic_year.name,
            self.program.name
        )
        
        # Verify sorted by marks DESC
        self.assertEqual(assignments[0]['student'], self.students[0].name)  # 95 marks
        self.assertEqual(assignments[1]['student'], self.students[1].name)  # 93 marks
        self.assertEqual(assignments[2]['student'], self.students[2].name)  # 88 marks
        
        # Verify roll numbers assigned
        self.assertEqual(assignments[0]['assigned_roll_number'], 1)
        self.assertEqual(assignments[1]['assigned_roll_number'], 2)
        self.assertEqual(assignments[2]['assigned_roll_number'], 3)
    
    # Test 2: Alphabetical by Name
    def test_assign_by_name(self):
        assignments = assign_by_name(
            self.academic_year.name,
            self.program.name
        )
        
        # Verify sorted alphabetically
        self.assertEqual(assignments[0]['student'], 'Alice')
        self.assertEqual(assignments[1]['student'], 'Bob')
        self.assertEqual(assignments[2]['student'], 'Charlie')
    
    # Test 3: Enrollment Order
    def test_assign_by_enrollment_order(self):
        assignments = assign_by_enrollment_order(
            self.academic_year.name,
            self.program.name
        )
        
        # Should be in creation date order
        for i, assignment in enumerate(assignments):
            self.assertEqual(assignment['assigned_roll_number'], i + 1)
    
    # Test 4: No Duplicate Detection
    def test_validate_no_duplicates(self):
        assignments = [
            {'student': 'S1', 'assigned_roll_number': 1},
            {'student': 'S2', 'assigned_roll_number': 2},
            {'student': 'S3', 'assigned_roll_number': 2}  # Duplicate
        ]
        
        with self.assertRaises(ValueError):
            validate_no_duplicates(assignments)
    
    # Test 5: Missing Previous Year Data
    def test_handle_missing_previous_year_data(self):
        # Create student with no previous year marks
        student = frappe.get_doc({
            'doctype': 'Student',
            'first_name': 'NewStudent'
        }).insert()
        
        assignments = assign_by_previous_grade(
            self.academic_year.name,
            self.program.name
        )
        
        # Verify new student marked as Pending
        new_student_detail = next(
            (a for a in assignments if a['student'] == student.name),
            None
        )
        self.assertEqual(new_student_detail['status'], 'Pending')
        self.assertIsNone(new_student_detail['assigned_roll_number'])

# Run tests
# bench run-tests vidyaan.tests.test_roll_number_assignment
```

### Integration Tests

```python
def test_full_assignment_workflow(self):
    """Test complete assignment workflow"""
    
    # 1. Create assignment
    assignment = frappe.get_doc({
        'doctype': 'Roll Number Assignment',
        'academic_year': self.academic_year.name,
        'program': self.program.name,
        'assignment_strategy': 'Previous Year Grade-wise'
    }).insert()
    
    # 2. Execute
    result = execute_assignment(assignment)
    self.assertTrue(result['success'])
    
    # 3. Verify Student records updated
    for detail in assignment.assignments:
        student = frappe.get_doc('Student', detail.student)
        self.assertEqual(student.student_roll_number, detail.assigned_roll_number)
    
    # 4. Rollback
    rollback_assignment(assignment)
    
    # 5. Verify rolled back
    assignment.reload()
    self.assertEqual(assignment.status, 'Draft')
    self.assertEqual(len(assignment.assignments), 0)
```

### Manual Testing Checklist

```
Phase 1: Basic Assignment
- [ ] Create Roll Number Assignment for 2026 B.Sc programme
- [ ] Select "Previous Year Grade-wise" strategy
- [ ] Click "Preview Assignment"
- [ ] Verify preview shows students sorted by marks
- [ ] Click "Execute Assignment"
- [ ] Verify Student records updated with roll numbers
- [ ] Verify Student Group table updated
- [ ] Export CSV and verify data

Phase 2: Edge Cases
- [ ] Create assignment with 1 new student (no previous year data)
- [ ] Verify new student marked "Pending" with blank roll number
- [ ] Create assignment with duplicate marks
- [ ] Verify alphabetical tiebreaker applied
- [ ] Add new student mid-year, verify auto-assign if enabled
- [ ] Rollback assignment and verify Student records cleared

Phase 3: Different Strategies
- [ ] Test "Alphabetical by Name" strategy
- [ ] Test "Programme Enrollment Order" strategy
- [ ] Test "Manual" strategy with admin-entered roll numbers
- [ ] Verify format options (Sequential, Prefixed, Program-Year)

Phase 4: Multi-tenant
- [ ] Login as different school/company
- [ ] Create separate assignment for same year/program
- [ ] Verify no cross-school data pollution
- [ ] Verify different roll number sequences per school

Phase 5: Error Handling
- [ ] Try assignment without enrolled students (should error)
- [ ] Try concurrent assignments (should error)
- [ ] Try manual assignment with duplicates (should error)
- [ ] Try assignment with invalid academic year (should error)
- [ ] Interrupt mid-execution and verify rollback
```

---

## Security Considerations

### Access Control

**Permissions:**
- **Create/Edit:** System Manager only
- **View:** System Manager, Institute Administrator
- **Submit:** N/A (non-submitted DocType)
- **Execute:** System Manager only (via API)
- **View Audit Trail:** System Manager, Institute Administrator

**Implementation:**
```python
# On Roll Number Assignment DocType
{
  "permissions": [
    {
      "role": "System Manager",
      "permissions": ["Create", "Read", "Write", "Delete", "Submit"]
    },
    {
      "role": "Institute Administrator",
      "permissions": ["Read"]
    }
  ]
}
```

### Data Validation

✅ Validate student belongs to program & academic year  
✅ Validate no duplicate assignments in same school for same year/program  
✅ Validate roll number format before saving  
✅ Prevent assignment if user lacks permission  
✅ Audit trail for all changes (who, when, what)  
✅ Rate limiting on API endpoints (prevent bulk abuse)  

### Audit Trail

```python
# Log all assignments
def log_assignment_audit(assignment_id, academic_year, program, strategy, status, user):
    """Create audit log entry"""
    
    log_entry = frappe.get_doc({
        'doctype': 'Assignment Audit Log',
        'assignment': assignment_id,
        'academic_year': academic_year,
        'program': program,
        'strategy': strategy,
        'status': status,
        'user': user,
        'timestamp': frappe.utils.now()
    }).insert(ignore_permissions=True)
    
    return log_entry.name
```

### Multi-tenancy Isolation

- All queries filter by `company` (Frappe native isolation)
- Student records already company-scoped
- Programme Enrollment company-scoped
- No cross-company data leakage possible

---

## Timeline & Milestones

### Week 1: Weeks 1 (Days 1-7)
**Goal:** Data model ready, backend functions implemented

| Day | Task | Status |
|-----|------|--------|
| 1-2 | Create DocTypes & migrations | 🎯 |
| 3-5 | Implement all strategy functions | 🎯 |
| 6-7 | Unit tests & debugging | 🎯 |
| | **Deliverable:** Backend API ready for testing | ✅ |

### Week 2: Days 8-14
**Goal:** Frontend UI complete, preview working

| Day | Task | Status |
|-----|------|--------|
| 8-10 | Build assignment form & buttons | 🎯 |
| 11-12 | Implement preview modal with editing | 🎯 |
| 13-14 | CSV export & error messages | 🎯 |
| | **Deliverable:** UI complete and testable | ✅ |

### Week 3: Days 15-21
**Goal:** Edge cases handled, automation working

| Day | Task | Status |
|-----|------|--------|
| 15-17 | Comprehensive edge case handling | 🎯 |
| 18 | Automation hooks for new enrollments | 🎯 |
| 19-20 | Integration tests & manual testing | 🎯 |
| 21 | Documentation & final review | 🎯 |
| | **Deliverable:** Production-ready feature | ✅ |

### Week 4: Days 22-28
**Goal:** Deployment, monitoring, user training

| Day | Task | Status |
|-----|------|--------|
| 22-24 | Final testing with real data | 🎯 |
| 25 | Deploy to staging | 🎯 |
| 26 | Deploy to production | 🎯 |
| 27-28 | User training & documentation | 🎯 |
| | **Deliverable:** Live in production | ✅ |

---

## Success Criteria

### Functional Requirements
- ✅ Support all 4 assignment strategies (Grade, Alphabetical, Enrollment, Manual)
- ✅ Preview functionality with manual override capability
- ✅ Automatic assignment for newly enrolled mid-year students
- ✅ Export roll numbers to CSV format
- ✅ Rollback mechanism if needed
- ✅ Multi-school isolation maintained

### Performance Requirements
- ✅ Assign 1000+ students in < 10 seconds
- ✅ Preview generation < 3 seconds
- ✅ No UI lag on large datasets

### Data Integrity
- ✅ Zero data loss during assignment
- ✅ Zero duplicate roll numbers per school/year/program
- ✅ Complete audit trail of all changes
- ✅ Consistent state even after errors/rollback

### User Experience
- ✅ Clear error messages for all failure scenarios
- ✅ Helpful warning messages (missing data, duplicates, etc.)
- ✅ Intuitive UI with preview before execution
- ✅ Accessible documentation & admin guide

### Testing & Quality
- ✅ Unit tests: 100% coverage of core functions
- ✅ Integration tests: Full workflow tested
- ✅ Manual tests: All edge cases verified
- ✅ Zero critical bugs in production

### Security & Compliance
- ✅ Only System Manager can execute assignments
- ✅ Complete audit trail for compliance
- ✅ Multi-tenant isolation verified
- ✅ All inputs validated

---

## Future Enhancements

### Short-term (Next 2 months)
1. **Custom Formula Support** - Let schools define custom sorting formula
2. **Batch Assignment** - Assign multiple programs at once
3. **Re-assignment Tool** - Change roll numbers mid-year if needed
4. **CSV Import** - Load roll numbers from external spreadsheet

### Medium-term (Next 6 months)
1. **Integration Reports** - Show roll numbers in student reports
2. **Roll Number Validation** - Prevent gaps or conflicts in numbering
3. **Historical Tracking** - View previous roll number assignments
4. **Bulk Operations** - Queue assignments for multiple years/programs

### Long-term (Next 12 months)
1. **AI-Based Optimization** - Suggest best strategy based on historical data
2. **Mobile App Support** - Manage assignments via mobile
3. **Real-time Sync** - Synchronize with external SIS systems
4. **Advanced Analytics** - Dashboard showing roll number trends

---

## References & Resources

- [Frappe Framework Documentation](https://frappeframework.com/docs/)
- [Vidyaan Education App Code](../vidyaan/)
- [Student DocType Reference](../vidyaan/doctype/student/)
- [Programme Enrollment Reference](../vidyaan/doctype/programme_enrollment/)

---

## Approval & Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Project Lead | ________ | __/__/____ | __________ |
| Developer | ________ | __/__/____ | __________ |
| QA Lead | ________ | __/__/____ | __________ |
| Product Manager | ________ | __/__/____ | __________ |

---

**Document Prepared By:** Vidyaan Development Team  
**Last Updated:** April 18, 2026  
**Version:** 1.0 (Draft)  
**Status:** Ready for Implementation

---

*For questions or clarifications, please contact the Vidyaan Development Team.*
