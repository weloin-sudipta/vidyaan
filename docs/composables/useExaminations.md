# useExaminations

## Purpose
Examination management composable handling exam creation, scheduling, result management, and grading workflows.

## Location
`frontend/composables/academics/useExaminations.ts`

## State Management

### Reactive State
```javascript
const examinations = ref([])     // List of examinations
const currentExam = ref(null)   // Selected examination
const examResults = ref([])     // Exam results
const loading = ref(false)      // Loading state
const grading = ref(false)      // Grading operation state
```

### Examination Data Structure
```javascript
interface Examination {
  name: string           // Exam ID
  exam_name: string      // Exam title
  exam_type: 'Unit Test' | 'Mid Term' | 'Final Exam' | 'Practical'
  subject: string        // Subject name
  class: string          // Class/Grade
  section: string        // Class section
  academic_year: string  // Academic year
  academic_term: string  // Term/Semester
  exam_date: string      // Exam date (YYYY-MM-DD)
  start_time: string     // Start time (HH:MM)
  end_time: string       // End time (HH:MM)
  duration: number       // Duration in minutes
  total_marks: number    // Maximum marks
  passing_marks: number  // Minimum passing marks
  syllabus: string       // Exam syllabus
  instructions: string   // Exam instructions
  status: 'Draft' | 'Scheduled' | 'Ongoing' | 'Completed'
  created_by: string     // Teacher who created
}
```

### Exam Result Data Structure
```javascript
interface ExamResult {
  name: string           // Result ID
  examination: string   // Exam ID
  student: string       // Student ID
  student_name: string  // Student name
  marks_obtained: number // Obtained marks
  grade: string         // Letter grade (A+, A, B+, etc.)
  percentage: number    // Percentage score
  remarks: string       // Teacher remarks
  status: 'Pass' | 'Fail' | 'Absent'
  graded_by: string     // Teacher who graded
  graded_on: string     // Grading timestamp
}
```

## API Methods

### fetchExaminations(filters)
Retrieves examinations list with filters.

**Parameters:**
```javascript
{
  teacher_id?: string    // For teacher view
  student_id?: string    // For student view
  class?: string         // Filter by class
  section?: string       // Filter by section
  subject?: string       // Filter by subject
  exam_type?: string     // Filter by exam type
  status?: string        // Filter by status
  academic_year?: string // Filter by year
}
```

**Returns:** Promise<Examination[]>

### getExamination(id)
Retrieves single examination details.

**Parameters:**
```javascript
string  // Examination ID
```

**Returns:** Promise<Examination>

### createExamination(data)
Creates new examination (Teacher only).

**Parameters:**
```javascript
Omit<Examination, 'name' | 'created_by'>
```

**Returns:** Promise<Examination>

### updateExamination(id, data)
Updates existing examination.

**Parameters:**
```javascript
string, Partial<Examination>
```

**Returns:** Promise<Examination>

### scheduleExamination(id, scheduleData)
Schedules examination with date/time.

**Parameters:**
```javascript
string, {
  exam_date: string
  start_time: string
  end_time: string
  duration: number
}
```

**Returns:** Promise<Examination>

### submitExamResult(examId, studentId, resultData)
Submits exam result for student.

**Parameters:**
```javascript
string, string, {
  marks_obtained: number
  remarks?: string
}
```

**Returns:** Promise<ExamResult>

### bulkSubmitResults(examId, results)
Bulk submits results for entire class.

**Parameters:**
```javascript
string, {
  student_id: string
  marks_obtained: number
  remarks?: string
}[]
```

**Returns:** Promise<ExamResult[]>

### getExamResults(examId)
Retrieves all results for examination.

**Parameters:**
```javascript
string  // Exam ID
```

**Returns:** Promise<ExamResult[]>

### getStudentResults(studentId, filters)
Gets examination results for student.

**Parameters:**
```javascript
string, {
  academic_year?: string
  subject?: string
}
```

**Returns:** Promise<ExamResult[]>

### calculateGrade(marks, totalMarks)
Calculates letter grade from marks.

**Parameters:**
```javascript
number, number  // Obtained marks, total marks
```

**Returns:** string (Grade)

## Usage Examples

### Teacher Exam Creation
```javascript
const { createExamination } = useExaminations()

const handleCreateExam = async (form) => {
  try {
    await createExamination({
      exam_name: form.title,
      exam_type: form.type,
      subject: form.subject,
      class: form.class,
      section: form.section,
      academic_year: '2024-25',
      academic_term: 'Term 1',
      total_marks: form.totalMarks,
      passing_marks: form.passingMarks,
      syllabus: form.syllabus,
      instructions: form.instructions
    })
    showToast('Exam created!')
  } catch (err) {
    showError('Creation failed')
  }
}
```

### Exam Scheduling
```javascript
const { scheduleExamination } = useExaminations()

const handleSchedule = async (examId, schedule) => {
  try {
    await scheduleExamination(examId, {
      exam_date: schedule.date,
      start_time: schedule.startTime,
      end_time: schedule.endTime,
      duration: schedule.duration
    })
    showToast('Exam scheduled!')
  } catch (err) {
    showError('Scheduling failed')
  }
}
```

### Bulk Result Submission
```javascript
const { bulkSubmitResults } = useExaminations()

const handleBulkSubmit = async (examId, results) => {
  try {
    await bulkSubmitResults(examId, results.map(r => ({
      student_id: r.studentId,
      marks_obtained: r.marks,
      remarks: r.remarks
    })))
    showToast('Results submitted!')
  } catch (err) {
    showError('Submission failed')
  }
}
```

### Student Results View
```javascript
const { getStudentResults } = useExaminations()

// Fetch student's exam results
onMounted(async () => {
  const results = await getStudentResults(user.value.name, {
    academic_year: '2024-25'
  })
  examResults.value = results
})

// Template
<div v-for="result in examResults" :key="result.name">
  <h4>{{ result.examination_name }}</h4>
  <p>Marks: {{ result.marks_obtained }}/{{ result.total_marks }}</p>
  <p>Grade: {{ result.grade }}</p>
  <p>Status: {{ result.status }}</p>
</div>
```

## Features

### Exam Lifecycle Management
- Draft → Scheduled → Ongoing → Completed
- Date/time validation
- Duration management
- Status tracking

### Grading System
- Automatic grade calculation
- Configurable grading scales
- Pass/fail determination
- Percentage calculations

### Bulk Operations
- Class-wide result submission
- Batch processing
- Result validation

### Academic Year Support
- Year-wise filtering
- Term/semester tracking
- Academic calendar integration

## Dependencies
- useFrappeFetch for API calls
- useAuth for role permissions
- Date/time utilities

## Business Rules
- Teachers can only manage exams for assigned subjects
- Students can only view their own results
- Exam scheduling prevents conflicts
- Results must be within valid mark ranges
- Passing marks cannot exceed total marks

## Error Cases
- Schedule conflicts
- Invalid mark ranges
- Permission violations
- Duplicate result submissions
- Academic year validation failures