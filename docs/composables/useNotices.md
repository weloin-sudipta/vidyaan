# useNotices

## Purpose
Notice/announcement management composable handling creation, approval, distribution, and tracking of school notices.

## Location
`frontend/composable/useNotices.js`

## State Management

### Reactive State
```javascript
const notices = ref([])         // List of notices
const pendingNotices = ref([]) // Notices pending approval
const myNotices = ref([])      // User's created notices
const noticeDetails = ref(null) // Selected notice details
const loading = ref(false)     // Loading state
const publishing = ref(false)  // Publishing state
```

### Notice Data Structure
```javascript
interface Notice {
  name: string           // Notice ID
  title: string          // Notice title
  content: string        // Notice content
  notice_type: 'General' | 'Academic' | 'Event' | 'Emergency'
  priority: 'Low' | 'Medium' | 'High' | 'Critical'
  target_audience: 'All' | 'Students' | 'Teachers' | 'Parents' | 'Class'
  target_class?: string  // Specific class if targeted
  target_section?: string // Specific section if targeted
  attachment?: string    // File attachment URL
  published_by: string   // Creator user ID
  published_on: string   // Publication timestamp
  expiry_date?: string   // Notice expiry date
  status: 'Draft' | 'Pending Approval' | 'Published' | 'Expired' | 'Rejected'
  approved_by?: string   // Approver user ID
  approved_on?: string   // Approval timestamp
  rejection_reason?: string // Rejection reason
  read_by: string[]      // Users who have read
  tags: string[]         // Notice tags
}
```

## API Methods

### fetchNotices(filters)
Retrieves notices list with filters.

**Parameters:**
```javascript
{
  status?: string       // Filter by status
  notice_type?: string  // Filter by type
  priority?: string     // Filter by priority
  target_audience?: string // Filter by audience
  published_by?: string // Filter by creator
  date_from?: string    // Start date
  date_to?: string      // End date
}
```

**Returns:** Promise<Notice[]>

### getNotice(id)
Retrieves single notice details.

**Parameters:**
```javascript
string  // Notice ID
```

**Returns:** Promise<Notice>

### createNotice(data)
Creates new notice (draft or pending approval).

**Parameters:**
```javascript
Omit<Notice, 'name' | 'published_by' | 'published_on' | 'read_by'>
```

**Returns:** Promise<Notice>

### updateNotice(id, data)
Updates existing notice.

**Parameters:**
```javascript
string, Partial<Notice>
```

**Returns:** Promise<Notice>

### publishNotice(id)
Publishes a notice (Admin/Teacher only).

**Parameters:**
```javascript
string  // Notice ID
```

**Returns:** Promise<Notice>

### approveNotice(id, data)
Approves pending notice (Admin only).

**Parameters:**
```javascript
string, {
  approved: boolean
  rejection_reason?: string
}
```

**Returns:** Promise<Notice>

### markAsRead(noticeId)
Marks notice as read by current user.

**Parameters:**
```javascript
string  // Notice ID
```

**Returns:** Promise<void>

### getPendingApprovals()
Retrieves notices pending approval (Admin only).

**Returns:** Promise<Notice[]>

### getMyNotices()
Retrieves notices created by current user.

**Returns:** Promise<Notice[]>

### deleteNotice(id)
Deletes a notice (Creator or Admin only).

**Parameters:**
```javascript
string  // Notice ID
```

**Returns:** Promise<void>

### getNoticeStats()
Gets notice statistics and metrics.

**Returns:** Promise<NoticeStats>

## Usage Examples

### Notice List Display
```javascript
const { notices, loading } = useNotices()

// Fetch notices on mount
onMounted(async () => {
  await fetchNotices({
    status: 'Published',
    target_audience: userRole.value === 'student' ? 'Students' : 'All'
  })
})

// Template
<div v-for="notice in notices" :key="notice.name">
  <div :class="`priority-${notice.priority.toLowerCase()}`">
    <h3>{{ notice.title }}</h3>
    <p>{{ notice.content.substring(0, 100) }}...</p>
    <span>{{ notice.published_on }}</span>
    <button @click="markAsRead(notice.name)" v-if="!notice.read_by.includes(user.name)">
      Mark as Read
    </button>
  </div>
</div>
```

### Creating a Notice
```javascript
const { createNotice, publishing } = useNotices()

const handleCreateNotice = async (form) => {
  try {
    publishing.value = true
    const notice = await createNotice({
      title: form.title,
      content: form.content,
      notice_type: form.type,
      priority: form.priority,
      target_audience: form.audience,
      target_class: form.class,
      target_section: form.section,
      attachment: form.file?.url,
      expiry_date: form.expiryDate,
      tags: form.tags
    })
    showToast('Notice created!')
    // Redirect or refresh list
  } catch (err) {
    showError('Creation failed')
  } finally {
    publishing.value = false
  }
}
```

### Admin Approval Interface
```javascript
const { pendingNotices, approveNotice } = useNotices()

// Load pending notices
onMounted(async () => {
  const pending = await getPendingApprovals()
  pendingNotices.value = pending
})

// Handle approval
const handleApproval = async (noticeId, approved, reason) => {
  try {
    await approveNotice(noticeId, {
      approved,
      rejection_reason: reason
    })
    showToast(approved ? 'Notice approved!' : 'Notice rejected!')
    // Refresh pending list
    const updated = await getPendingApprovals()
    pendingNotices.value = updated
  } catch (err) {
    showError('Approval failed')
  }
}
```

### Notice Details View
```javascript
const { noticeDetails } = useNotices()

const loadNoticeDetails = async (noticeId) => {
  const details = await getNotice(noticeId)
  noticeDetails.value = details
  // Auto-mark as read
  if (!details.read_by.includes(user.value.name)) {
    await markAsRead(noticeId)
  }
}

// Template
<div v-if="noticeDetails">
  <h1>{{ noticeDetails.title }}</h1>
  <div class="notice-meta">
    <span>Type: {{ noticeDetails.notice_type }}</span>
    <span>Priority: {{ noticeDetails.priority }}</span>
    <span>Published: {{ noticeDetails.published_on }}</span>
  </div>
  <div class="notice-content" v-html="noticeDetails.content"></div>
  <div v-if="noticeDetails.attachment">
    <a :href="noticeDetails.attachment" target="_blank">View Attachment</a>
  </div>
</div>
```

## Features

### Multi-level Approval Workflow
- Draft → Pending Approval → Published
- Role-based approval permissions
- Rejection with reasons
- Approval tracking

### Audience Targeting
- All users, Students, Teachers, Parents
- Class/section specific notices
- Role-based filtering

### Read Tracking
- User read status tracking
- Read receipts
- Unread notice indicators

### Priority System
- Low, Medium, High, Critical priorities
- Visual priority indicators
- Priority-based sorting

### Content Management
- Rich text content support
- File attachments
- Expiry date management
- Tag-based organization

## Dependencies
- useFrappeFetch for API calls
- useAuth for role-based permissions
- Rich text editor integration

## Business Rules
- Teachers can create notices, admins approve
- Critical notices bypass approval
- Notices expire automatically
- Read tracking for engagement metrics
- Attachment size limits

## Error Cases
- Permission denied for creation/approval
- Invalid target audience combinations
- Missing required fields
- File upload failures
- Approval workflow violations