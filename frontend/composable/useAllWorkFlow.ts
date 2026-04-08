import { ref, type Ref } from 'vue'
import { createResource } from './useFrappeFetch'

export interface Workflow {
  name: string
  workflow_name?: string
  document_type?: string
  is_active?: number | boolean
  states?: unknown[]
  transitions?: unknown[]
  [key: string]: unknown
}

export interface UseWorkflowReturn {
  loading: Ref<boolean>
  error: Ref<string | null>
  workflows: Ref<Workflow[]>
  fetchWorkflow: () => Promise<void>
}

export const useWorkflow = (): UseWorkflowReturn => {
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const workflows: Ref<Workflow[]> = ref([])

  const fetchWorkflow = async (): Promise<void> => {
    loading.value = true
    error.value = null
    console.log('call')

    try {
      const resource = createResource<Workflow[]>({
        url: 'vidyaan.api_folder.leave_application.get_all_workflow',
      })

      const res = await resource.fetch()
      console.log(res)

      workflows.value = res ?? []
    } catch (err) {
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { loading, error, workflows, fetchWorkflow }
}
