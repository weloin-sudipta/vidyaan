# useTeacherDashboard

## Purpose
Teacher dashboard composable providing comprehensive dashboard data, statistics, and quick actions for teachers.

## Location
`frontend/composables/teacher/useTeacherDashboard.ts`

## State Management

### Reactive State
```javascript
const dashboardData = ref(null)  // Main dashboard data
const pendingTasks = ref([])    // Pending tasks
const classStats = ref([])      // Class statistics
const recentActivities = ref([]) // Recent activities
const loading = ref(false)      // Loading state
```

### Dashboard Data Structure
```javascript
interface TeacherDashboard {
  teacher_info: {
    name: string
    full_name: string
    subjects: string[]
    classes: string[]
  }
  today_schedule: {
    period: string
    subject: string
    class: string
    section: string
    room?: string
  }[]
  pending_assignments: {
    name: string
    title: string
    due_date: string
    pending_submissions: number
    total_students: number
  }[]
  upcoming_exams: {
    name: string
    exam_name: string
    exam_date: string
    subject: string
    class: string
    section: string
  }[]
  attendance_summary: {
    class: string
    section: string
    present_today: number
    total_students: number
    attendance_percentage: number
  }[]
  notices_to_approve: {
    name: string
    title: string
    submitted_by: string
    submitted_on: string
  }[]
}
```

### Task Data Structure
```javascript
interface PendingTask {
  id: string
  type: 'assignment' | 'exam' | 'attendance' | 'notice'
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  due_date?: string
  action_url: string
  metadata: Record<string, any>
}
```

## API Methods

### fetchDashboard()
Retrieves complete teacher dashboard data.

**Returns:** Promise<TeacherDashboard>

### getPendingTasks()
Retrieves pending tasks requiring attention.

**Returns:** Promise<PendingTask[]>

### getClassStatistics(classId, section)
Gets detailed statistics for specific class.

**Parameters:**
```javascript
string, string?  // Class, Section (optional)
```

**Returns:** Promise<ClassStats>

### getRecentActivities(limit)
Retrieves recent teacher activities.

**Parameters:**
```javascript
number?  // Limit (default: 10)
```

**Returns:** Promise<Activity[]>

### quickActions()
Provides quick action methods for common tasks.

**Returns:** Object with action methods

## Usage Examples

### Main Dashboard
```javascript
const { dashboardData, loading } = useTeacherDashboard()

// Load dashboard on mount
onMounted(async () => {
  await fetchDashboard()
})

// Template
<div v-if="dashboardData">
  <!-- Today's Schedule -->
  <div class="schedule">
    <h3>Today's Classes</h3>
    <div v-for="period in dashboardData.today_schedule" :key="period.period">
      <span>{{ period.period }}: {{ period.subject }}</span>
      <span>{{ period.class }}-{{ period.section }}</span>
    </div>
  </div>

  <!-- Pending Tasks -->
  <div class="tasks">
    <h3>Pending Tasks</h3>
    <div v-for="task in dashboardData.pending_assignments" :key="task.name">
      <span>{{ task.title }}</span>
      <span>{{ task.pending_submissions }}/{{ task.total_students }} submissions</span>
    </div>
  </div>
</div>
```

### Pending Tasks Management
```javascript
const { pendingTasks } = useTeacherDashboard()

// Load and display pending tasks
onMounted(async () => {
  const tasks = await getPendingTasks()
  pendingTasks.value = tasks
})

// Template
<div v-for="task in pendingTasks" :key="task.id">
  <div :class="`priority-${task.priority}`">
    <h4>{{ task.title }}</h4>
    <p>{{ task.description }}</p>
    <button @click="handleTaskAction(task)">
      {{ getActionLabel(task.type) }}
    </button>
  </div>
</div>
```

### Class Statistics
```javascript
const { getClassStatistics } = useTeacherDashboard()

const loadClassStats = async (classId, section) => {
  const stats = await getClassStatistics(classId, section)
  classStats.value = stats
}

// Display attendance summary
<div v-for="cls in dashboardData.attendance_summary" :key="cls.class">
  <h4>Class {{ cls.class }}-{{ cls.section }}</h4>
  <p>Present Today: {{ cls.present_today }}/{{ cls.total_students }}</p>
  <p>Attendance: {{ cls.attendance_percentage }}%</p>
</div>
```

### Quick Actions
```javascript
const { quickActions } = useTeacherDashboard()

const actions = quickActions()

// Mark attendance quickly
await actions.markAttendance({
  class: '10',
  section: 'A',
  subject: 'Mathematics',
  attendance: studentAttendanceData
})

// Create quick notice
await actions.createNotice({
  title: 'Class Test Tomorrow',
  content: 'Prepare for mathematics test',
  target_audience: 'Class 10-A'
})
```

## Features

### Comprehensive Overview
- Today's class schedule
- Pending assignments count
- Upcoming examinations
- Attendance summaries
- Notices requiring approval

### Task Management
- Prioritized pending tasks
- Actionable task items
- Due date tracking
- Task completion tracking

### Real-time Updates
- Live attendance counts
- Recent activity feed
- Instant notifications
- Dashboard refresh capability

### Quick Actions
- Rapid attendance marking
- Quick notice creation
- Assignment shortcuts
- Exam scheduling helpers

## Dependencies
- useFrappeFetch for API calls
- useAuth for teacher context
- useAssignments, useAttendance, useExaminations composables

## Business Rules
- Dashboard data filtered by teacher's assigned classes
- Tasks prioritized by urgency and deadlines
- Attendance shows only assigned classes
- Notices show only pending approvals

## Performance Optimizations
- Dashboard data cached for session
- Lazy loading of detailed statistics
- Background refresh for real-time data
- Minimal API calls for quick actions