# Vidyaan Architecture & Implementation Blueprint

The goal of this document is to map out the core School ERP features using **existing Frappe / ERPNext / Education Doctypes**, minimizing the need for custom Doctypes. Everything will be structured natively to be SaaS-ready.

## User Review Required

> [!IMPORTANT]
> Please review the Doctype mapping strategies below. This is exactly how Frappe's Education module is designed to be used. Once you approve this map, we will proceed with the technical implementation (permissions, UI setup, and optimizations).

---

## 🏗️ 1. Institute & Staff Management

* **Institute (School)** → `Company` Doctype.
* **Institute Admin** → Given to the main User. They will have full CRUD access over all Doctypes listed below.
* **Teachers / Instructors** → 
  1. Create a `User` (Assign them the "Instructor" Role).
  2. Create an `Employee` (Linked to the User and Company).
  3. Create an `Instructor` (Native Education Doctype, linked to the Employee).
* **Other Staff (Clerk, Accountant, etc.)** → 
  1. Create a `User` (Assign standard Roles like "Accounts Manager").
  2. Create an `Employee` (Linked to the User and Company).

---

## 📚 2. Academic Management (Classes & Streams)

To handle Schools properly, we will use the `Program` and `Course` Doctypes.

### **Programs (Classes / Streams)**
A `Program` in ERPNext represents a grouping of courses that a student enrolls in. 
- For lower classes without streams: Create a Program named **"Class 5"**, **"Class 9"**.
- For higher classes with streams: Create separate Programs like **"Class 11 - Science"** and **"Class 11 - Arts"**.

### **Courses (Subjects)**
A `Course` is a specific subject. 
- **Example Subjects**: "English", "Mathematics", "Physics", "History".
- **Linking**: The "English" Course can be added to the curriculum table of both "Class 11 - Science" and "Class 11 - Arts". "Physics" will only be added to "Class 11 - Science".

---

## 📖 3. Lessons, Chapters & Study Materials

Frappe Education natively supports an LMS (Learning Management System) hierarchy. We will use this to manage chapters and materials!

* **Chapters / Modules** → `Topic` Doctype. 
  * *Example: A Topic named "Thermodynamics" can be linked to the "Physics" Course.*
* **Lessons** → `Article`, `Video`, or `Quiz` Doctypes.
  * *Example: An Article named "Introduction to Thermodynamics" is placed inside the Topic.*
* **Study Materials (PDFs, Notes)** → Use the standard Frappe **Attachments (Files)** mechanism directly on the `Article` or `Topic` to upload notes, OR use the `Course Content` table.

---

## 🧑‍🎓 4. Student Management & Access

* **Students** → `Student` Doctype.
* **Admissions / Enrollment** → `Program Enrollment` Doctype. 
  * *Flow: A Student gets enrolled into "Class 11 - Science".*
* **Accessing Materials** → Once a student is enrolled in a Program, the native LMS portal allows them to log in, see their active Courses, open Topics, read Articles, and download attachments automatically!

---

## 🔒 5. Permissions Layout (For this Phase)

As requested, for now, all access will be restricted to the top-level admins:
* **System Administrator / Institute Admin**: Read, Write, Create, Delete on `Student`, `Instructor`, `Employee`, `Program`, `Course`, `Topic`, `Article`, etc.
* **Instructor Role**: For now, they will have minimal or no permissions until we explicitly enable it in the future (e.g., giving them access to `Student Attendance` later).

## Open Questions

1. Do you want me to write Python setup scripts to automatically generate these exact Permissions in `roles.py`, so that your `Institute Admin` immediately has access to all these Education module Doctypes?
2. Do you want me to rebuild a `workspace.py` that puts all these exact Doctypes (Student, Instructor, Program, Course, Topic, Article) logically on the Dashboard?
3. Are you happy with using `Topic` for Chapters and `Article` for Lessons, as it relies 100% on standard features?