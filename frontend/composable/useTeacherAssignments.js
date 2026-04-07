import { ref } from 'vue'
import { call } from '~/composable/useFrappeFetch'

export const useTeacherAssignments = () => {
  const courses = ref([])
  const studentGroups = ref([])
  const assignments = ref([])
  const currentAssignment = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchCourses = async () => {
    try {
      const res = await call('vidyaan.api_folder.assignments.get_instructor_courses')
      courses.value = res || []
    } catch (err) {
      error.value = err.message ?? 'Failed to load courses'
    }
  }

  const fetchStudentGroups = async (course = null) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.get_instructor_student_groups', { course })
      studentGroups.value = res || []
    } catch (err) {
      error.value = err.message ?? 'Failed to load student groups'
    }
  }

  const fetchAssignments = async (course = null, status = null) => {
    loading.value = true
    error.value = null
    try {
      const params = {}
      if (course) params.course = course
      if (status) params.status = status
      const res = await call('vidyaan.api_folder.assignments.get_instructor_assignments', params)
      assignments.value = res || []
    } catch (err) {
      error.value = err.message ?? 'Failed to load assignments'
    } finally {
      loading.value = false
    }
  }

  const fetchAssignmentDetail = async (name) => {
    loading.value = true
    error.value = null
    try {
      const res = await call('vidyaan.api_folder.assignments.get_assignment_detail', { name })
      currentAssignment.value = res || null
      return res
    } catch (err) {
      error.value = err.message ?? 'Failed to load assignment detail'
      return { error: err.message }
    } finally {
      loading.value = false
    }
  }

  const createAssignment = async (payload) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.create_assignment', { data: payload })
      return res
    } catch (err) {
      return { error: err.message ?? 'Failed to create assignment' }
    }
  }

  const updateAssignment = async (name, payload) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.update_assignment', { name, data: payload })
      return res
    } catch (err) {
      return { error: err.message ?? 'Failed to update assignment' }
    }
  }

  const publishAssignment = async (name) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.publish_assignment', { name })
      return res
    } catch (err) {
      return { error: err.message ?? 'Failed to publish assignment' }
    }
  }

  const deleteAssignment = async (name) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.delete_assignment', { name })
      return res
    } catch (err) {
      return { error: err.message ?? 'Failed to delete assignment' }
    }
  }

  const closeAssignment = async (name) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.close_assignment', { name })
      return res
    } catch (err) {
      return { error: err.message ?? 'Failed to close assignment' }
    }
  }

  const gradeSubmission = async (assignment, student, score, remarks = '') => {
    try {
      const res = await call('vidyaan.api_folder.assignments.grade_submission', {
        assignment,
        student,
        score,
        remarks,
      })
      return res
    } catch (err) {
      return { error: err.message ?? 'Failed to save grade' }
    }
  }

  return {
    courses,
    studentGroups,
    assignments,
    currentAssignment,
    loading,
    error,
    fetchCourses,
    fetchStudentGroups,
    fetchAssignments,
    fetchAssignmentDetail,
    createAssignment,
    updateAssignment,
    publishAssignment,
    deleteAssignment,
    closeAssignment,
    gradeSubmission,
  }
}
