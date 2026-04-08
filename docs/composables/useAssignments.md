# useAssignments

Student-side composable for fetching and submitting assignments.

> Last verified: 2026-04-07 — matches current source. See also the
> instructor counterpart `useTeacherAssignments` and the fix log
> `docs/fixes/2026-04-07-student-assignments.md`.

## Location
`frontend/composables/academics/useAssignments.ts` (TypeScript, fully typed, no `any`).

## Public API

```ts
interface UseAssignmentsReturn {
  assignments: Ref<StudentAssignment[]>
  loading:     Ref<boolean>
  error:       Ref<string | null>

  fetchAssignments: () => Promise<StudentAssignment[] | undefined>
  submitAssignment: (
    assignmentName: string,
    submissionFile: string,
    submissionText?: string | null,
  ) => Promise<SubmitAssignmentReturn>
  uploadFile: (file: File) => Promise<UploadFileReturn>
}
```

## Data shapes

```ts
interface StudentAssignmentSubmission {
  name?: string
  status?: 'Pending' | 'Submitted' | 'Late' | 'Graded'
  submission_file?: string
  submission_text?: string
  submitted_on?: string
  score?: number
  feedback?: string
}

interface StudentAssignment {
  name: string
  title: string
  course_name?: string
  topic?: string
  due_date?: string         // ISO date
  max_score?: number
  description?: string
  assignment_file?: string
  status?: 'Published'      // server-side filter — students never see Draft/Closed
  my_submission?: StudentAssignmentSubmission | null
  is_overdue?: boolean
}

type SubmitAssignmentReturn = SubmitAssignmentResult | { error: string } | undefined
type UploadFileReturn       = { file_url: string; file_name?: string } | { error: string }
```

## Backend endpoints

| Composable method | Frappe whitelist method |
|---|---|
| `fetchAssignments()` | `vidyaan.api_folder.assignments.get_student_assignments` |
| `submitAssignment()` | `vidyaan.api_folder.assignments.submit_student_assignment` |
| `uploadFile()`       | `upload_file` (Frappe core, multipart) |

`get_student_assignments` returns the **union** of:
1. Assignments with an existing `Assignment Submission` row for the student.
2. Assignments whose `target_groups` reference a `Student Group` the student
   is currently a member of.

Both subsets are filtered by `Assignment.status == "Published"`. The
`my_submission` field is `{status: "Pending", ...}` when no row exists yet
(the row will be auto-created on first submit).

`submit_student_assignment` will:
- **Throw** if neither `submission_file` nor `submission_text` is supplied.
- **Throw** if the assignment is not currently `Published`.
- **Auto-heal** by appending a fresh submission row when the student is in a
  target group but has no row yet.
- Mark `status = "Late"` when `due_date < today()`, otherwise `"Submitted"`.

## Usage

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useAssignments } from '~/composables/academics/useAssignments'

const { assignments, loading, error, fetchAssignments,
        submitAssignment, uploadFile } = useAssignments()

onMounted(fetchAssignments)

async function handleSubmit(assignmentName: string, file: File) {
  const uploaded = await uploadFile(file)
  if ('error' in uploaded) return alert(uploaded.error)
  if (!uploaded.file_url)  return alert('No file URL returned.')

  const res = await submitAssignment(assignmentName, uploaded.file_url)
  if (!res || 'error' in res) return alert((res as any)?.error ?? 'Failed')
  await fetchAssignments()
}
</script>
```

## Status derivation in the page layer

`pages/academics/assignments.vue` derives a display status with this rule:

```ts
function resolvedStatus(task) {
  if (task.my_submission?.status) return task.my_submission.status
  if (task.is_overdue) return 'Overdue'
  return task.status || 'Active'
}
```

Tabs are: `Active`, `Submitted`, `Overdue`, `Graded`.

## Edge cases handled

- Student joined the target group AFTER publication → still visible.
- Submission with no file selected → inline error before any network call.
- Upload returns malformed shape (no `file_url`) → inline error, no submit.
- Backend called with empty payload → 417 with explicit error message.
- Late submissions → tagged `Late`, still scored.

## Dependencies
- `useFrappeFetch` — `call<T>()` and `callMultipart<T>()`.

## Related docs
- `docs/fixes/2026-04-07-student-assignments.md` — visibility & submit fix log
- `docs/composables/useFrappeFetch.md` — RPC primitive layer
- `docs/workflows/assignment-workflow.md` — high-level workflow
