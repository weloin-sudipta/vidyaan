import { ref } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

export const useAssignments = () => {
  const assignments = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchAssignments = async () => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.assignments.get_assignments',
      })
      const res = await resource.submit()
      console.log(res);

      assignments.value = res || []
      return res
    } catch (err) {
      console.error('Failed to load assignments:', err)
      error.value = err.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  const submitAssignment = async (assignmentName, submissionFile) => {
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.assignments.submit_assignment',
      })
      const res = await resource.submit({
        assignment_name: assignmentName,
        submission_file: submissionFile,
      })
      return res
    } catch (err) {
      console.error('Failed to submit assignment:', err)
      return { error: err.message || 'Unknown error' }
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
      console.error('Upload failed:', err)
      return { error: err.message }
    }
  }

  return { assignments, loading, error, fetchAssignments, submitAssignment, uploadFile }
}
