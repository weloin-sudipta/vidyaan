// import { ref } from 'vue'
// import { createResource } from '~/composable/useFrappeFetch'

// export const useLeaveApplication = () => {
//   const leave = ref([])
//   const loading = ref(false)
//   const error = ref(null)

//   const fetchLeaveData = async () => {
//     loading.value = true
//     error.value = null
//     try {
//       const resource = createResource({
//           url: 'vidyaan.api_folder.leave_application.apply_leave',
//       })
//       const res = await resource.submit()
//       leave.value = res || []
//       console.log(res);

//       return res
//     } catch (err) {
//       console.error('Failed to load study materials:', err)
//       error.value = err.message || 'Unknown error'
//     } finally {
//       loading.value = false
//     }
//   }

//     return { leave, loading, error, fetchLeaveData }
// }

import { ref, type Ref } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

// ─── Leave application shapes ─────────────────────────────────────────────
export interface LeaveApplicationRecord {
  name?: string
  from_date?: string
  to_date?: string
  reason?: string
  status?: string
  [key: string]: unknown
}

export interface SubmitLeaveInput {
  from_date: string
  to_date: string
  reason?: string
}

interface MyApplicationsResponse {
  applications?: LeaveApplicationRecord[]
  [key: string]: unknown
}

export interface UseLeaveApplicationReturn {
  leave: Ref<LeaveApplicationRecord[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  submitLeave: (input: SubmitLeaveInput) => Promise<LeaveApplicationRecord | undefined>
  my_applications: Ref<LeaveApplicationRecord[]>
  fetchApplications: () => Promise<void>
}

export const useLeaveApplication = (): UseLeaveApplicationReturn => {
  const leave: Ref<LeaveApplicationRecord[]> = ref([])
  const my_applications: Ref<LeaveApplicationRecord[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const submitLeave = async ({
    from_date,
    to_date,
    reason,
  }: SubmitLeaveInput): Promise<LeaveApplicationRecord | undefined> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<LeaveApplicationRecord>({
        url: 'vidyaan.api_folder.leave_application.apply_leave',
      })

      const res = await resource.submit({
        from_date: from_date,
        to_date: to_date,
        reason: reason || 'Medical Leave for testing',
      })

      leave.value = res ? [res, ...leave.value] : leave.value
      return res
    } catch (err) {
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  const fetchApplications = async (): Promise<void> => {
    ;(loading.value = true), (error.value = null)
    try {
      const resource = createResource<MyApplicationsResponse>({
        url: 'vidyaan.api_folder.leave_application.get_my_applications',
      })
      const res = await resource.fetch()
      console.log(res?.applications)

      my_applications.value = res?.applications || []
    } catch (err) {
      console.error('Failed to load allExams:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { leave, loading, error, submitLeave, my_applications, fetchApplications }
}
