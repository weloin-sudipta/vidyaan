# useAttendance

## Purpose
Attendance management composable handling student attendance marking, tracking, and reporting for teachers and students.

## Location
`frontend/composables/academics/useAttendance.ts`

## State Management

### Reactive State
```javascript
const attendanceRecords = ref([])  // Attendance records
const todayAttendance = ref([])   // Today's attendance
const attendanceStats = ref(null) // Statistics data
const loading = ref(false)        // Loading state
const marking = ref(false)        // Attendance marking state
```

### Attendance Record Structure
```javascript
interface AttendanceRecord {
  name: string           // Record ID
  student: string        // Student ID
  student_name: string   // Student full name
  class: string          // Class/Grade
  section: string        // Section
  subject: string        // Subject
  date: string           // Attendance date (YYYY-MM-DD)
  status: 'Present' | 'Absent' | 'Late' | 'Excused'
  marked_by: string      // Teacher who marked
  marked_on: string      // Timestamp
  remarks: string        // Additional notes
  period: string         // Class period (1-8)
}
```

### Attendance Statistics Structure
```javascript
interface AttendanceStats {
  total_days: number     // Total working days
  present_days: number   // Days present
  absent_days: number    // Days absent
  late_days: number      // Days late
  excused_days: number   // Days excused
  attendance_percentage: number  // Overall percentage
  monthly_stats: {       // Monthly breakdown
    month: string
    present: number
    absent: number
    percentage: number
  }[]
}
```

## API Methods

### fetchAttendance(filters)
Retrieves attendance records with filters.

**Parameters:**
```javascript
{
  student_id?: string    // For specific student
  class?: string         // Filter by class
  section?: string       // Filter by section
  subject?: string       // Filter by subject
  date_from?: string     // Start date
  date_to?: string       // End date
  status?: string        // Filter by status
}
```

**Returns:** Promise<AttendanceRecord[]>

### markAttendanceBulk(data)
Bulk marks attendance for class/section.

**Parameters:**
```javascript
{
  class: string
  section: string
  subject: string
  date: string
  period: string
  attendance: {
    student_id: string
    status: 'Present' | 'Absent' | 'Late' | 'Excused'
    remarks?: string
  }[]
}
```

**Returns:** Promise<AttendanceRecord[]>

### markSingleAttendance(data)
Marks attendance for individual student.

**Parameters:**
```javascript
{
  student: string
  class: string
  section: string
  subject: string
  date: string
  period: string
  status: 'Present' | 'Absent' | 'Late' | 'Excused'
  remarks?: string
}
```

**Returns:** Promise<AttendanceRecord>

### getAttendanceStats(studentId, period)
Retrieves attendance statistics.

**Parameters:**
```javascript
string, {         // Student ID
  from_date?: string
  to_date?: string
}
```

**Returns:** Promise<AttendanceStats>

### getTodayAttendance(class, section)
Gets today's attendance for class.

**Parameters:**
```javascript
string, string    // Class, Section
```

**Returns:** Promise<AttendanceRecord[]>

### updateAttendanceRecord(id, updates)
Updates existing attendance record.

**Parameters:**
```javascript
string, Partial<AttendanceRecord>
```

**Returns:** Promise<AttendanceRecord>

## Usage Examples

### Teacher Attendance Marking
```javascript
const { markAttendanceBulk, marking } = useAttendance()

const handleMarkAttendance = async (attendanceData) => {
  try {
    await markAttendanceBulk({
      class: '10',
      section: 'A',
      subject: 'Mathematics',
      date: new Date().toISOString().split('T')[0],
      period: '1',
      attendance: [
        { student_id: 'STU001', status: 'Present' },
        { student_id: 'STU002', status: 'Absent', remarks: 'Sick' }
      ]
    })
    showToast('Attendance marked!')
  } catch (err) {
    showError('Failed to mark attendance')
  }
}
```

### Student Attendance View
```javascript
const { attendanceRecords, attendanceStats } = useAttendance()

// Fetch student's attendance
onMounted(async () => {
  await fetchAttendance({ student_id: user.value.name })
  const stats = await getAttendanceStats(user.value.name)
  attendanceStats.value = stats
})

// Template
<div class="stats">
  <p>Attendance: {{ attendanceStats?.attendance_percentage }}%</p>
  <p>Present: {{ attendanceStats?.present_days }} days</p>
</div>
```

### Today's Attendance Overview
```javascript
const { getTodayAttendance } = useAttendance()

const loadTodayAttendance = async () => {
  const today = await getTodayAttendance('10', 'A')
  todayAttendance.value = today
}

// Template
<div v-for="record in todayAttendance" :key="record.name">
  <span>{{ record.student_name }}</span>
  <span :class="record.status.toLowerCase()">
    {{ record.status }}
  </span>
</div>
```

### Attendance Report Generation
```javascript
const { fetchAttendance } = useAttendance()

const generateReport = async (studentId, month) => {
  const fromDate = `${new Date().getFullYear()}-${month}-01`
  const toDate = new Date(new Date().getFullYear(), month, 0).toISOString().split('T')[0]

  const records = await fetchAttendance({
    student_id: studentId,
    date_from: fromDate,
    date_to: toDate
  })

  // Generate report from records
  return records
}
```

## Features

### Bulk Operations
- Class-wide attendance marking
- Batch processing for efficiency
- Roll call interface support

### Status Management
- Multiple attendance states
- Remarks for special cases
- Status change tracking

### Reporting & Analytics
- Individual student statistics
- Class/section summaries
- Monthly/yearly reports
- Attendance percentage calculations

### Real-time Updates
- Live attendance status
- Today's attendance dashboard
- Instant marking confirmation

## Dependencies
- useFrappeFetch for API calls
- useAuth for role permissions
- Date utilities for period calculations

## Business Rules
- One attendance record per student per period per day
- Teacher can only mark attendance for assigned classes
- Students can only view their own attendance
- Late attendance threshold (15 minutes)
- Excused absence requires approval

## Error Cases
- Duplicate attendance marking
- Invalid date/period combinations
- Permission violations
- Student not in class/section
- Network failures during bulk operations