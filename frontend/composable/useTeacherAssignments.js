import { ref } from 'vue'
import { createResource, call } from '~/composable/useFrappeFetch'

export const useTeacherAssignments = () => {
  const courses = ref([])
  const templates = ref([])
  const submissions = ref([])
  const studentGroups = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchCourses = async () => {
    try {
      const res = await call('vidyaan.api_folder.assignments.get_instructor_courses')
      courses.value = res || []
    } catch (err) {
      console.error('Failed to fetch courses:', err)
    }
  }

  const fetchStudentGroups = async (course = null) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.get_instructor_student_groups', { course })
      studentGroups.value = res || []
    } catch (err) {
      console.error('Failed to fetch student groups:', err)
    }
  }

  const fetchTemplates = async (course = null) => {
    loading.value = true
    try {
      const res = await call('vidyaan.api_folder.assignments.get_instructor_assignment_templates', { course })
      templates.value = res || []
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const createTemplate = async (templateData) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.create_assignment_template', { data: templateData })
      return res
    } catch (err) {
      return { error: err.message }
    }
  }

  const publishTemplate = async (templateName) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.publish_assignment_template', { template_name: templateName })
      return res
    } catch (err) {
      return { error: err.message }
    }
  }

  const fetchSubmissions = async (templateName) => {
    try {
      const res = await call('vidyaan.api_folder.assignments.get_template_submissions', { template_name: templateName })
      submissions.value = res || []
      return res
    } catch (err) {
      return []
    }
  }

  const gradeAssignment = async (assignmentName, score, remarks = '') => {
    try {
      const res = await call('vidyaan.api_folder.assignments.grade_assignment', {
        assignment_name: assignmentName,
        score,
        remarks
      })
      return res
    } catch (err) {
      return { error: err.message }
    }
  }

  return {
    courses,
    templates,
    submissions,
    studentGroups,
    loading,
    error,
    fetchCourses,
    fetchStudentGroups,
    fetchTemplates,
    createTemplate,
    publishTemplate,
    fetchSubmissions,
    gradeAssignment
  }
}
