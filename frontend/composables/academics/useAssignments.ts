import { ref, type Ref } from 'vue'
import { call, callMultipart } from '~/composables/api/useFrappeFetch'

// ─── Student-side assignment shapes ───────────────────────────────────────
export interface StudentAssignmentSubmission {
  name?: string
  status?: string
  submission_file?: string
  submission_text?: string
  submitted_on?: string
  score?: number
  feedback?: string
  [key: string]: unknown
}

export interface StudentAssignment {
  name: string
  title: string
  course_name?: string
  topic?: string
  due_date?: string
  max_score?: number
  description?: string
  assignment_file?: string
  status?: string
  my_submission?: StudentAssignmentSubmission | null
  is_overdue?: boolean
  [key: string]: unknown
}

// ─── Submit / upload result shapes ────────────────────────────────────────
export interface SubmitAssignmentResult {
  name?: string
  status?: string
  message?: string
  [key: string]: unknown
}

export interface SubmitAssignmentError {
  error: string
}

export interface UploadFileSuccess {
  file_url: string
  file_name?: string
}

export interface UploadFileError {
  error: string
}

export type SubmitAssignmentReturn = SubmitAssignmentResult | SubmitAssignmentError | undefined
export type UploadFileReturn = UploadFileSuccess | UploadFileError

export interface UseAssignmentsReturn {
  assignments: Ref<StudentAssignment[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchAssignments: () => Promise<StudentAssignment[] | undefined>
  submitAssignment: (
    assignmentName: string,
    submissionFile: string,
    submissionText?: string | null
  ) => Promise<SubmitAssignmentReturn>
  uploadFile: (file: File) => Promise<UploadFileReturn>
}

export const useAssignments = (): UseAssignmentsReturn => {
  const assignments: Ref<StudentAssignment[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const fetchAssignments = async (): Promise<StudentAssignment[] | undefined> => {
    loading.value = true
    error.value = null
    try {
      const res = await call<StudentAssignment[]>(
        'vidyaan.api_folder.assignments.get_student_assignments'
      )
      assignments.value = res || []
      return res
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to load assignments'
    } finally {
      loading.value = false
    }
  }

  const submitAssignment = async (
    assignmentName: string,
    submissionFile: string,
    submissionText: string | null = null
  ): Promise<SubmitAssignmentReturn> => {
    try {
      const params: Record<string, string> = {
        assignment: assignmentName,
        submission_file: submissionFile,
      }
      if (submissionText) params.submission_text = submissionText
      const res = await call<SubmitAssignmentResult>(
        'vidyaan.api_folder.assignments.submit_student_assignment',
        params
      )
      return res
    } catch (err) {
      return { error: (err as Error).message ?? 'Failed to submit assignment' }
    }
  }

  const uploadFile = async (file: File): Promise<UploadFileReturn> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_private', '1')

    try {
      const res = await callMultipart<UploadFileSuccess>('upload_file', formData)
      return res
    } catch (err) {
      return { error: (err as Error).message }
    }
  }

  return { assignments, loading, error, fetchAssignments, submitAssignment, uploadFile }
}
