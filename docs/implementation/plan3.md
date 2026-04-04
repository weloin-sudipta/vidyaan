# Examination & Assignment Management Plan

As requested, this architecture accomplishes both Exams and Assignments **without creating a single new Doctype or modifying existing ones**. We will achieve 100% of the workflow by cleverly utilizing native Frappe Education module Doctypes (`Assessment Plan`, `Assessment Result`, and `Assessment Group`).

---

## Part 1: How We Avoid New Doctypes

Both an Exam and an Assignment are inherently the same thing: an evaluation of a student's grasp on a specific Course, resulting in a score. 

We distinguish between them using the native **`Assessment Group`** tree structure.

**Setup (One-Time by Admin):**
- Create `Assessment Group`: "Exams" (Parent)
  - "Mid-Term Exams"
  - "Final Exams"
- Create `Assessment Group`: "Assignments" (Parent)
  - "Homework"
  - "Major Project"

---

## Part 2: Step-by-Step EXAM Workflow

This workflow covers an Institute Admin choosing a class, allocating courses, dates, and rooms, with all enrolled students automatically included.

**Step 1: Admin Schedules the Exam**
1. Institute Admin opens **Assessment Plan** and clicks New.
2. Selects **Student Group** (This is the specific Section of the Program, e.g., "Class 11 Sci - Sec A").
3. Selects **Assessment Group** = "Final Exams".
4. Selects the **Course** (e.g., "Physics").
5. Fills in the native fields: **Schedule Date**, **From Time**, **To Time**, and **Room**.
6. Admin assigns an **Examiner** and a **Supervisor** (Instructors).
7. Saves and Submits.

**Step 2: Auto-Assignment of Students**
Because the `Assessment Plan` is linked to a `Student Group`, **every single student enrolled in that group is automatically assigned**. The admin does not manually add students.

**Step 3: Conducting & Grading (Secured)**
1. The Instructor (Examiner) opens the native **Assessment Result Tool**.
2. They select the generated Assessment Plan. 
3. The system *automatically fetches a list of every enrolled student in that section*.
4. The Instructor types in the scores and clicks Submit. 
> [!IMPORTANT]
> **Security Hook**: We will write a small validation script in `vidyaan/hooks.py`. When a teacher tries to save grades, the system verifies that the logged-in teacher matches the `Examiner` or `Supervisor` defined by the Institute Admin on the Assessment Plan. If they don't match, the system blocks the save. This ensures teacher A cannot grade teacher B's exam.

### Future Scope: Admit Cards & Exam Settings
As requested, we will immediately build a **Custom Print Format** for Admit Cards. 
- It will be available directly on the **Student Profile** via the native "Print" button.
- The print format will use a Jinja script to auto-fetch all upcoming `Assessment Plans` (Exams) for that student, displaying the Course, Date, Time, and Room in a nice ID card layout.

---

## Part 3: Step-by-Step ASSIGNMENT Workflow

You requested that assignments be mapped to courses, and the Institute Admin can specify which instructor gives/creates them.

**Step 1: Admin Creates the Assignment Shell**
1. Institute Admin opens **Assessment Plan** and clicks New.
2. Selects the **Student Group**.
3. Selects **Assessment Group** = "Homework" (This tells the system it's an assignment, not an exam).
4. Selects the **Course** (e.g., "English").
5. Instructs the system by setting the **Examiner** field to the specific Instructor responsible for the assignment.
6. Sets the **Schedule Date** (This acts as the **Deadline** for the assignment).

**Step 2: Instructor Gives the Assignment**
1. The specified Instructor logs in. Because they are tagged as the `Examiner`, they easily filter Assessment Plans assigned to them.
2. They communicate the actual homework task to the students in class (or via the future frontend LMS).

**Step 3: Submission & Grading**
Just like an Exam, once students hand in the homework, the Instructor opens the **Assessment Result Tool**, selects the Homework Assessment Plan, and mass-enters the grades for all automatically-fetched students.

---

## Part 4: How Weightage & Final Grading Works Natively

You asked: *"assignment have points like 20 poinsts for a course assignment and 80 points in exam then how can i grade with sum ?"*

Frappe handles this **natively** via the **Course Assessment Criteria** child table.

1. When the Admin sets up a **Course** (e.g., "Physics"), they define the Assessment Criteria.
2. They add two rows:
   - Criteria = "Assignments", Weightage = **20%**
   - Criteria = "Final Exam", Weightage = **80%**
3. When the term ends, the Admin uses the **Student Report Generation Tool**. 
4. The system natively calculates all the assignment scores, mathematically reduces them to 20% of the final grade, calculates the exam scores to 80%, and produces the final weighted Report Card.

---

## Summary of Native Field Mapping

| User Requirement | Native Frappe Field |
|---|---|
| Differentiate Exam vs Assignment | `Assessment Group` |
| Assign to a Program/Class | `Student Group` (Represents Program + Section) |
| Select Course | `Course` field in Assessment Plan |
| Exame Date & Time | `Schedule Date`, `From Time`, `To Time` |
| Room Allocation | `Room` field in Assessment Plan |
| Which Instructor gives Assignment | `Examiner` field in Assessment Plan |
| Auto-assign enrolled students | Natively handled by `Assessment Result Tool` |
| Grading Weights (80/20) | `Course Assessment Criteria` (Native) |
| Strict Grading Permissions | Custom Hook in `vidyaan/hooks.py` |
| Admit Card | Custom Print Format on `Student` Doctype |

## User Review Required

> [!NOTE]
> I have designed the **Security Validation** for grading and the **Admit Card Print Format** on the student profile. 
> 
> Shall I execute the code changes to implement the security hook and admit card format now?
