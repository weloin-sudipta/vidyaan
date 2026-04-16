import { ref, type Ref } from 'vue'
import { call } from '~/composables/api/useFrappeFetch'

// ─── Local shapes ─────────────────────────────────────────────────────────
export interface Course {
  name: string
  course_name?: string
  course_code?: string
  [key: string]: unknown
}

export interface StudentGroup {
  name: string
  student_group_name?: string
  course?: string
  [key: string]: unknown
}

export interface AssignmentTargetGroup {
  student_group: string
  student_group_name?: string
  [key: string]: unknown
}

export interface AcademicYear {
  name: string
  academic_year_name?: string
  [key: string]: unknown
}

export interface Program {
  name: string
  program_name?: string
  [key: string]: unknown
}

export interface AssignmentListItem {
  name: string
  title?: string
  course?: string
  course_name?: string
  due_date?: string
  status?: string
  max_score?: number
  total_submissions?: number
  graded_count?: number
  creation?: string
  [key: string]: unknown
}

export interface AssignmentSubmissionRow {
  name?: string
  student: string
  student_name?: string
  status?: string
  submission_file?: string
  submission_text?: string
  submitted_on?: string
  score?: number | string
  remarks?: string
  [key: string]: unknown
}

export interface AssignmentDetail {
  name: string
  title?: string
  course?: string
  topic?: string
  description?: string
  due_date?: string
  max_score?: number
  status?: string
  assignment_file?: string
  target_groups?: AssignmentTargetGroup[]
  submissions?: AssignmentSubmissionRow[]
  all_submissions?: any[]
  messages?: any[]
  [key: string]: unknown
}

export interface CreateAssignmentPayload {
  title: string
  course: string
  topic?: string
  description?: string
  due_date?: string
  max_score?: number
  assignment_file?: string
  target_groups?: AssignmentTargetGroup[] | string[]
  [key: string]: unknown
}

export interface AssignmentMutationSuccess {
  success: true
  name: string
  [key: string]: unknown
}

export interface AssignmentMutationError {
  error: string
}

export type AssignmentMutationResult =
  | AssignmentMutationSuccess
  | AssignmentMutationError
  | undefined

export interface UseTeacherAssignmentsReturn {
  courses: Ref<Course[]>
  studentGroups: Ref<StudentGroup[]>
  academicYears: Ref<AcademicYear[]>
  programs: Ref<Program[]>
  assignments: Ref<AssignmentListItem[]>
  currentAssignment: Ref<AssignmentDetail | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchCourses: () => Promise<void>
  fetchStudentGroups: (course?: string | null) => Promise<void>
  fetchAcademicYears: () => Promise<void>
  fetchPrograms: () => Promise<void>
  fetchAssignments: (course?: string | null, status?: string | null, academicYear?: string | null, program?: string | null) => Promise<void>
  fetchAssignmentDetail: (
    name: string,
    studentId?: string | null
  ) => Promise<AssignmentDetail | AssignmentMutationError | undefined>
  createAssignment: (payload: CreateAssignmentPayload) => Promise<AssignmentMutationResult>
  updateAssignment: (
    name: string,
    payload: CreateAssignmentPayload
  ) => Promise<AssignmentMutationResult>
  publishAssignment: (name: string) => Promise<AssignmentMutationResult>
  deleteAssignment: (name: string) => Promise<AssignmentMutationResult>
  closeAssignment: (name: string) => Promise<AssignmentMutationResult>
  gradeSubmission: (
    submissionId: string,
    score: number | string,
    remarks?: string
  ) => Promise<AssignmentMutationResult>
  addComment: (name: string, content: string, studentId?: string) => Promise<{ success: boolean; comment: any } | undefined>
  updateComment: (commentName: string, content: string) => Promise<{ success: boolean; content: string } | undefined>
  deleteComment: (commentName: string) => Promise<{ success: boolean } | undefined>
  requestResubmission: (name: string, studentId: string, message?: string) => Promise<AssignmentMutationResult>
}

export const useTeacherAssignments = (): UseTeacherAssignmentsReturn => {
  const courses: Ref<Course[]> = ref([])
  const studentGroups: Ref<StudentGroup[]> = ref([])
  const academicYears: Ref<AcademicYear[]> = ref([])
  const programs: Ref<Program[]> = ref([])
  const assignments: Ref<AssignmentListItem[]> = ref([])
  const currentAssignment: Ref<AssignmentDetail | null> = ref(null)
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const fetchCourses = async (): Promise<void> => {
    try {
      const res = await call<Course[]>('vidyaan.api_folder.assignments.get_instructor_courses')
      courses.value = res || []
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to load courses'
    }
  }

  const fetchStudentGroups = async (course: string | null = null): Promise<void> => {
    try {
      const res = await call<StudentGroup[]>(
        'vidyaan.api_folder.assignments.get_instructor_student_groups',
        { course }
      )
      studentGroups.value = res || []
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to load student groups'
    }
  }

  const fetchAcademicYears = async (): Promise<void> => {
    try {
      const res = await call<AcademicYear[]>('vidyaan.api_folder.assignments.get_instructor_academic_years')
      academicYears.value = res || []
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to load academic years'
    }
  }

  const fetchPrograms = async (): Promise<void> => {
    try {
      const res = await call<Program[]>('vidyaan.api_folder.assignments.get_instructor_programs')
      programs.value = res || []
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to load programs'
    }
  }

  const fetchAssignments = async (
    course: string | null = null,
    status: string | null = null,
    academicYear: string | null = null,
    program: string | null = null
  ): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const params: Record<string, string> = {}
      if (course) params.course = course
      if (status) params.status = status
      if (academicYear) params.academic_year = academicYear
      if (program) params.program = program
      const res = await call<AssignmentListItem[]>(
        'vidyaan.api_folder.assignments.get_instructor_assignments',
        params
      )
      assignments.value = res || []
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to load assignments'
    } finally {
      loading.value = false
    }
  }

  const fetchAssignmentDetail = async (
    name: string,
    studentId: string | null = null
  ): Promise<AssignmentDetail | AssignmentMutationError | undefined> => {
    loading.value = true
    error.value = null
    try {
      const params: Record<string, string> = { name }
      if (studentId) params.student_id = studentId
      const res = await call<AssignmentDetail>(
        'vidyaan.api_folder.assignments.get_assignment_detail',
        params
      )
      currentAssignment.value = res || null
      return res
    } catch (err) {
      const message = (err as Error).message ?? 'Failed to load assignment detail'
      error.value = message
      return { error: message }
    } finally {
      loading.value = false
    }
  }

  const createAssignment = async (
    payload: CreateAssignmentPayload
  ): Promise<AssignmentMutationResult> => {
    try {
      const res = await call<AssignmentMutationSuccess>(
        'vidyaan.api_folder.assignments.create_assignment',
        { data: payload }
      )
      return res
    } catch (err) {
      return { error: (err as Error).message ?? 'Failed to create assignment' }
    }
  }

  const updateAssignment = async (
    name: string,
    payload: CreateAssignmentPayload
  ): Promise<AssignmentMutationResult> => {
    try {
      const res = await call<AssignmentMutationSuccess>(
        'vidyaan.api_folder.assignments.update_assignment',
        { name, data: payload }
      )
      return res
    } catch (err) {
      return { error: (err as Error).message ?? 'Failed to update assignment' }
    }
  }

  const publishAssignment = async (name: string): Promise<AssignmentMutationResult> => {
    try {
      const res = await call<AssignmentMutationSuccess>(
        'vidyaan.api_folder.assignments.publish_assignment',
        { name }
      )
      return res
    } catch (err) {
      return { error: (err as Error).message ?? 'Failed to publish assignment' }
    }
  }

  const deleteAssignment = async (name: string): Promise<AssignmentMutationResult> => {
    try {
      const res = await call<AssignmentMutationSuccess>(
        'vidyaan.api_folder.assignments.delete_assignment',
        { name }
      )
      return res
    } catch (err) {
      return { error: (err as Error).message ?? 'Failed to delete assignment' }
    }
  }

  const closeAssignment = async (name: string): Promise<AssignmentMutationResult> => {
    try {
      const res = await call<AssignmentMutationSuccess>(
        'vidyaan.api_folder.assignments.close_assignment',
        { name }
      )
      return res
    } catch (err) {
      return { error: (err as Error).message ?? 'Failed to close assignment' }
    }
  }

  const gradeSubmission = async (
    submissionId: string,
    score: number | string,
    remarks: string = ''
  ): Promise<AssignmentMutationResult> => {
    try {
      const res = await call<AssignmentMutationSuccess>(
        'vidyaan.api_folder.assignments.grade_submission',
        {
          submission_id: submissionId,
          score,
          remarks,
        }
      )
      return res
    } catch (err) {
      return { error: (err as Error).message ?? 'Failed to save grade' }
    }
  }

  const addComment = async (name: string, content: string, studentId?: string) => {
    try {
      const params: Record<string, string> = { name, content }
      if (studentId) params.student_id = studentId
      const res = await call<{ success: boolean; comment: any }>(
        'vidyaan.api_folder.assignments.add_assignment_comment',
        params
      )
      return res
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to add comment'
    }
  }

  const updateComment = async (commentName: string, content: string) => {
    try {
      const res = await call<{ success: boolean; content: string }>(
        'vidyaan.api_folder.assignments.update_assignment_comment',
        { comment_name: commentName, content }
      )
      return res
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to update comment'
    }
  }

  const deleteComment = async (commentName: string) => {
    try {
      const res = await call<{ success: boolean }>(
        'vidyaan.api_folder.assignments.delete_assignment_comment',
        { comment_name: commentName }
      )
      return res
    } catch (err) {
      error.value = (err as Error).message ?? 'Failed to delete comment'
    }
  }

  const requestResubmission = async (name: string, studentId: string, message?: string) => {
    try {
      const res = await call<AssignmentMutationSuccess>(
        'vidyaan.api_folder.assignments.request_resubmission',
        { assignment: name, student_id: studentId, message }
      )
      return res
    } catch (err) {
      return { error: (err as Error).message ?? 'Failed to request resubmission' }
    }
  }

  return {
    courses,
    studentGroups,
    academicYears,
    programs,
    assignments,
    currentAssignment,
    loading,
    error,
    fetchCourses,
    fetchStudentGroups,
    fetchAcademicYears,
    fetchPrograms,
    fetchAssignments,
    fetchAssignmentDetail,
    createAssignment,
    updateAssignment,
    publishAssignment,
    deleteAssignment,
    closeAssignment,
    gradeSubmission,
    addComment,
    updateComment,
    deleteComment,
    requestResubmission,
  }
}
