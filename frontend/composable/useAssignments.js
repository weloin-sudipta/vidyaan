import { ref } from 'vue'
import { call } from '~/composable/useFrappeFetch'

export const useAssignments = () => {
  const assignments = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchAssignments = async () => {
    loading.value = true
    error.value = null
    try {
      const res = await call('vidyaan.api_folder.assignments.get_student_assignments')
      assignments.value = res || []
      return res
    } catch (err) {
      error.value = err.message ?? 'Failed to load assignments'
    } finally {
      loading.value = false
    }
  }

  const submitAssignment = async (assignmentName, submissionFile, submissionText = null) => {
    try {
      const params = {
        assignment: assignmentName,
        submission_file: submissionFile,
      }
      if (submissionText) params.submission_text = submissionText
      const res = await call('vidyaan.api_folder.assignments.submit_student_assignment', params)
      return res
    } catch (err) {
      return { error: err.message ?? 'Failed to submit assignment' }
    }
  }

  const uploadFile = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_private', 1)

    try {
      const res = await $fetch('/api/method/upload_file', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })
      return res.message
    } catch (err) {
      return { error: err.message }
    }
  }

  return { assignments, loading, error, fetchAssignments, submitAssignment, uploadFile }
}
