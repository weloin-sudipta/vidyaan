# 🎓 Examinations & Assignments: User Guide & Demo

Welcome to the **Vidyaan Advanced Assessment System**. This guide provides a step-by-step walkthrough of how to manage Exams, Assignments, and Grading using native Frappe Education Doctypes with Vidyaan's specialized security and print enhancements.

---

## 🏗️ 1. Setup Phase (Performed by Admin)

### A. Assessment Groups
Vidyaan automatically creates two primary groups under "All Assessment Groups":
- **Exams**: Used for Term-End, Mid-Term, and Final evaluations.
- **Assignments**: Used for Homework, Unit Tests, and Projects.

### B. Course Weightage (Calculated Grading)
To implement a "Sum of Weights" grading system (e.g., 20% Assignment + 80% Final Exam):
1. Open a **Course** (e.g., *Mathematics*).
2. In the **Assessment Criteria** table, add:
   - **Assignments**: 20%
   - **Final Exam**: 80%
3. Save the Course.

---

## 📝 2. Assignment Workflow (Demo)

### Step 1: Schedule the Assignment
1. Go to **Assessment Plan** → New.
2. **Student Group**: Select your class/section.
3. **Assessment Group**: Select *Homework* (under *Assignments*).
4. **Course**: Select *Mathematics*.
5. **Examiner**: Select the specific **Instructor** who will grade this.
6. **Schedule Date**: This is the submission deadline.
7. **Maximum Mark**: e.g., 20.
8. **Submit**.

### Step 2: Instructor Grading
1. The assigned Instructor logs in.
2. Open **Assessment Result Tool**.
3. Select the Assessment Plan created above. 
4. The system **automatically loads all students** in that section.
5. Enter marks (out of 20).
6. **Submit**.

> [!IMPORTANT]
> **Security Check**: Only the Instructor assigned as the *Examiner* or *Supervisor* on the Plan can edit/submit these marks. Other teachers will be blocked.

---

## 🏆 3. Examination Workflow (Demo)

### Step 1: Schedule the Exam
1. Go to **Assessment Plan** → New.
2. **Assessment Group**: Select *Mid-Term* (under *Exams*).
3. **Course**: Select *Science*.
4. **Schedule Date**, **From Time**, **To Time**: Set the exam timing.
5. **Room**: Select the allocated Room.
6. **Maximum Assessment Score**: e.g., 80.
7. **Submit**.

### Step 2: Printing Admit Cards
1. Open a **Student** profile.
2. Click the **Print** button in the top right.
3. Select the **Admit Card** print format.
4. The system will auto-generate a beautiful, professional ID card listing **ONLY** the scheduled exams for that student, including date, time, and room number.

---

## 📊 4. Final Grading & Report Cards

1. Open **Student Report Generation Tool**.
2. Select the Student, Academic Year, and **All Assessment Groups**.
3. The system pulls all "Assignments" (20%) and "Exams" (80%) results.
4. It calculates the final weighted score automatically and produces a PDF Report Card.

---

## ✅ Summary of Implemented Enhancements

| Feature | Implementation | Benefit |
|---|---|---|
| **Weightage** | Native `Course` Criteria | Handles logic like 80/20 sum grading automatically. |
| **Permissions** | `vidyaan/events.py` | Strict! Only the assigned teacher can put grades. |
| **Admit Cards** | Jinja Print Template | Professional, automated, and error-free seat tickets. |
| **Auto-Discovery** | Assessment Plan links | No manual student adding; all enrolled students are fetched. |

---
*Created by Vidyaan ERP – Empowering Digital Education.*
