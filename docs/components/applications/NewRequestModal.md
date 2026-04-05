# NewRequestModal

## Purpose
Modal dialog component for creating new student requests (leave, fee waiver, transfer, etc.) with form validation and file uploads.

## Location
`frontend/components/applications/NewRequestModal.vue`

## Props

### Required Props
```typescript
interface Props {
  modelValue: boolean    // Modal visibility (v-model)
  requestTypes: RequestType[] // Available request types
  student?: Student      // Student information
}
```

### Request Type Structure
```typescript
interface RequestType {
  value: string          // Type identifier
  label: string          // Display label
  fields: FormField[]    // Required form fields
  requiresApproval: boolean // Needs approval workflow
  maxFiles?: number      // Maximum file attachments
}
```

### Form Field Structure
```typescript
interface FormField {
  name: string           // Field name
  label: string          // Field label
  type: 'text' | 'textarea' | 'date' | 'select' | 'file'
  required?: boolean     // Field is required
  options?: string[]     // Select options
  validation?: string    // Validation regex
  placeholder?: string   // Input placeholder
}
```

## Events

### Emitted Events
```typescript
interface Emits {
  'update:modelValue': [value: boolean]  // Modal visibility update
  'submit': [requestData: RequestData]   // Request submitted
  'cancel': []                           // Request cancelled
}
```

## Request Data Structure
```typescript
interface RequestData {
  type: string           // Request type
  title: string          // Request title
  description: string    // Detailed description
  priority: 'low' | 'medium' | 'high' // Request priority
  fields: Record<string, any> // Dynamic form fields
  attachments: File[]    // File attachments
  metadata: {
    student_id: string
    student_name: string
    class: string
    section: string
  }
}
```

## Slots

### Named Slots
- `header` - Custom modal header
- `footer` - Custom modal footer
- `form-fields` - Custom form field rendering

## Usage Examples

### Basic Request Modal
```vue
<template>
  <NewRequestModal
    v-model="showModal"
    :request-types="requestTypes"
    :student="currentStudent"
    @submit="handleSubmit"
    @cancel="showModal = false"
  />
</template>

<script setup>
const requestTypes = [
  {
    value: 'leave',
    label: 'Leave Application',
    fields: [
      { name: 'from_date', label: 'From Date', type: 'date', required: true },
      { name: 'to_date', label: 'To Date', type: 'date', required: true },
      { name: 'reason', label: 'Reason', type: 'textarea', required: true }
    ],
    requiresApproval: true,
    maxFiles: 2
  }
]
</script>
```

### With Custom Form Fields
```vue
<template>
  <NewRequestModal
    v-model="showModal"
    :request-types="requestTypes"
    :student="student"
  >
    <template #form-fields="{ currentType, formData }">
      <div class="custom-fields">
        <div v-if="currentType.value === 'leave'">
          <label>Medical Certificate</label>
          <input type="file" accept=".pdf,.jpg,.png" />
        </div>
      </div>
    </template>
  </NewRequestModal>
</template>
```

## Features

### Dynamic Form Generation
- Form fields based on request type
- Real-time validation
- Conditional field display
- Custom field types support

### File Upload Management
- Multiple file attachments
- File type validation
- Size limit enforcement
- Upload progress indicators

### Request Workflow
- Draft saving capability
- Approval workflow integration
- Status tracking
- Notification system

### User Experience
- Step-by-step wizard for complex requests
- Auto-save functionality
- Form data persistence
- Mobile-responsive design

## Form Validation

### Built-in Validators
- Required field validation
- Date range validation
- File type/size validation
- Custom regex patterns
- Cross-field validation

### Validation Rules
```javascript
const validationRules = {
  date: (value) => isValidDate(value),
  email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
  phone: (value) => /^\+?[\d\s\-\(\)]+$/.test(value),
  file: (file) => file.size <= MAX_SIZE && ALLOWED_TYPES.includes(file.type)
}
```

## Styling

### CSS Classes
```css
.new-request-modal {
  /* Modal container */
}

.request-form {
  /* Form container */
}

.form-field {
  /* Individual form field */
}

.form-field--error {
  /* Error state styling */
}

.file-upload {
  /* File upload area */
}

.form-navigation {
  /* Form step navigation */
}
```

### Theme Variables
```css
:root {
  --modal-max-width: 600px;
  --form-field-spacing: 16px;
  --error-color: #ef4444;
  --success-color: #10b981;
}
```

## Dependencies
- Vue 3 Composition API
- Form validation library (VeeValidate)
- File upload utilities
- Modal dialog component
- Tailwind CSS for styling

## Business Logic
- Request types loaded from configuration
- Student data auto-populated
- Approval workflow triggered on submit
- File attachments stored in Frappe

## Error Handling
- Form validation errors
- File upload failures
- Network errors
- Permission denied scenarios
- Duplicate request prevention