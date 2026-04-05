# useAssignments

## Purpose
Assignment management composable handling CRUD operations for student assignments, submissions, and grading workflows.

## Location
`frontend/composable/useAssignments.js`

## State Management

### Reactive State
```javascript
const assignments = ref([])      // List of assignments
const currentAssignment = ref(null)  // Selected assignment
const submissions = ref([])     // Assignment submissions
const loading = ref(false)      // Loading state
const submitting = ref(false)   // Submission state
```

### Assignment Data Structure
```javascript
interface Assignment {
  name: string           // Assignment ID
  title: string          // Assignment title
  description: string    // Detailed description
  subject: string        // Subject name
  class: string          // Class/Grade
  section: string        // Class section
  teacher: string        // Assigned teacher
  due_date: string       // Due date (YYYY-MM-DD)
  total_marks: number    // Maximum marks
  attachment: string     // File attachment URL
  status: 'Draft' | 'Published' | 'Closed'
  created_on: string     // Creation timestamp
  modified_on: string    // Last modified
}
```

### Submission Data Structure
```javascript
interface Submission {
  name: string           // Submission ID
  assignment: string     // Assignment ID
  student: string        // Student ID
  submitted_on: string   // Submission timestamp
  file_url: string       // Submitted file URL
  remarks: string        // Student remarks
  marks_obtained: number // Awarded marks
  teacher_remarks: string // Teacher feedback
  status: 'Submitted' | 'Graded' | 'Late'
}
```

## API Methods

### fetchAssignments(filters)
Retrieves assignments list with optional filters.

**Parameters:**
```javascript
{
  student_id?: string    // For student view
  teacher_id?: string    // For teacher view
  subject?: string       // Filter by subject
  status?: string        // Filter by status
  class?: string         // Filter by class
}
```

**Returns:** Promise<Assignment[]>

### getAssignment(id)
Retrieves single assignment details.

**Parameters:**
```javascript
string  // Assignment ID
```

**Returns:** Promise<Assignment>

### createAssignment(data)
Creates new assignment (Teacher only).

**Parameters:**
```javascript
Omit<Assignment, 'name' | 'created_on' | 'modified_on'>
```

**Returns:** Promise<Assignment>

### updateAssignment(id, data)
Updates existing assignment.

**Parameters:**
```javascript
string, Partial<Assignment>
```

**Returns:** Promise<Assignment>

### submitAssignment(assignmentId, data)
Submits assignment for student.

**Parameters:**
```javascript
string, {
  file_url: string
  remarks?: string
}
```

**Returns:** Promise<Submission>

### gradeSubmission(submissionId, data)
Grades student submission (Teacher only).

**Parameters:**
```javascript
string, {
  marks_obtained: number
  teacher_remarks?: string
}
```

**Returns:** Promise<Submission>

### getSubmissions(assignmentId)
Retrieves all submissions for assignment.

**Parameters:**
```javascript
string  // Assignment ID
```

**Returns:** Promise<Submission[]>

## Usage Examples

### Student Assignment List
```javascript
const { assignments, loading } = useAssignments()

// Fetch student's assignments
onMounted(async () => {
  await fetchAssignments({ student_id: user.value.name })
})

// Template
<div v-for="assignment in assignments" :key="assignment.name">
  <h3>{{ assignment.title }}</h3>
  <p>Due: {{ assignment.due_date }}</p>
  <p>Marks: {{ assignment.total_marks }}</p>
</div>
```

### Teacher Assignment Creation
```javascript
const { createAssignment } = useAssignments()

const handleCreate = async (form) => {
  try {
    await createAssignment({
      title: form.title,
      description: form.description,
      subject: form.subject,
      class: form.class,
      due_date: form.dueDate,
      total_marks: form.marks
    })
    showToast('Assignment created!')
  } catch (err) {
    showError('Creation failed')
  }
}
```

### Assignment Submission
```javascript
const { submitAssignment, submitting } = useAssignments()

const handleSubmit = async (file) => {
  try {
    await submitAssignment(currentAssignment.value.name, {
      file_url: file.url,
      remarks: 'Completed on time'
    })
    showToast('Assignment submitted!')
  } catch (err) {
    showError('Submission failed')
  }
}
```

### Grading Interface
```javascript
const { gradeSubmission } = useAssignments()

const handleGrade = async (submissionId, marks, feedback) => {
  try {
    await gradeSubmission(submissionId, {
      marks_obtained: marks,
      teacher_remarks: feedback
    })
    showToast('Graded successfully!')
  } catch (err) {
    showError('Grading failed')
  }
}
```

## Features

### Role-Based Access
- Student: View assigned, submit work
- Teacher: Create, update, grade assignments
- Admin: Full access to all assignments

### File Management
- Assignment attachment uploads
- Submission file uploads
- File URL generation and storage

### Status Management
- Assignment lifecycle (Draft → Published → Closed)
- Submission status tracking
- Late submission handling

### Grading Workflow
- Marks assignment
- Teacher feedback
- Grade history tracking

## Dependencies
- useFrappeFetch for API communication
- useAuth for role-based permissions
- File upload utilities

## Business Rules
- Due date validation
- Late submission penalties
- Maximum marks constraints
- File size/type restrictions
- Teacher-student relationship validation

## Error Cases
- Permission denied
- File upload failures
- Validation errors
- Network timeouts
- Concurrent modification conflicts