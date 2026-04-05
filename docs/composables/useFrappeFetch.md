# useFrappeFetch

## Purpose
Core API wrapper composable providing standardized Frappe REST API communication with loading states, error handling, and reactive data management.

## Location
`frontend/composable/useFrappeFetch.ts`

## API Contract

### createResource<T>(options)
Creates a reactive resource for API calls.

**Parameters:**
```typescript
interface ResourceOptions<T> {
  url: string           // API method endpoint (without /api/method/)
  params?: Record<string, any>  // Default parameters
  auto?: boolean        // Auto-fetch on creation
  onSuccess?: (data: T) => void
  onError?: (error: any) => void
}
```

**Returns:**
```typescript
interface Resource<T> {
  data: Ref<T | null>     // Response data
  loading: Ref<boolean>   // Loading state
  error: Ref<any>         // Error object
  params: Record<string, any>  // Current parameters
  fetch: (params?) => Promise<T>    // GET-like fetch
  submit: (params?) => Promise<T>   // POST-like submit
  reload: () => Promise<T>          // Refetch with current params
  reset: () => void                 // Clear data and error
}
```

## Usage Examples

### Basic Resource Creation
```typescript
const students = createResource<Student[]>({
  url: 'vidyaan.api_folder.students.get_students',
  auto: true
})
```

### Manual Fetch with Parameters
```typescript
const assignments = createResource({
  url: 'vidyaan.api_folder.assignments.get_assignments'
})

// Later...
await assignments.fetch({ student_id: 'STU001' })
```

### Form Submission
```typescript
const submitAssignment = createResource({
  url: 'vidyaan.api_folder.assignments.submit_assignment',
  onSuccess: () => showToast('Assignment submitted!')
})

await submitAssignment.submit({
  assignment_id: 'ASS001',
  file_url: uploadedFile.url
})
```

## Features

### Loading States
- Automatic loading indicators
- 800ms delay for smooth skeleton visibility
- Reactive `loading` ref for UI binding

### Error Handling
- Standardized error objects
- `onError` callback support
- Error state persistence until next successful call

### Parameter Management
- Default parameters on creation
- Runtime parameter merging
- Parameter persistence across reloads

### Reactive Data
- Vue 3 ref-based reactivity
- SSR-safe implementation
- TypeScript support with generics

## Dependencies
- Nuxt 3 `$fetch`
- Vue 3 `ref`
- Cookie-based authentication (`credentials: 'include'`)

## Error Cases
- Network failures
- Authentication errors (401)
- Permission errors (403)
- Server errors (500)
- Invalid API responses

## Notes
- All API calls include session cookies
- 800ms artificial delay for better UX
- TypeScript generics for type safety
- Automatic error logging to console