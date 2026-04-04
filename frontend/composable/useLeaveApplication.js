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


import { ref } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

export const useLeaveApplication = () => {
    const leave = ref([])
    const my_applications = ref([])
    const loading = ref(false)
    const error = ref(null)

    const submitLeave = async ({ from_date, to_date, reason }) => {
        loading.value = true
        error.value = null
        try {
            const resource = createResource({
                url: 'vidyaan.api_folder.leave_application.apply_leave',
            })

            const res = await resource.submit({
                from_date: from_date,
                to_date: to_date,     
                reason: reason || "Medical Leave for testing"
            })

            leave.value = res ? [res, ...leave.value] : leave.value
            return res
        } catch (err) {
            error.value = err.message || 'Unknown error'
        } finally {
            loading.value = false
        }
    }

    const fetchApplications = async () => {
        loading.value = true,
        error.value = null
        try {
            const resource = createResource({
                url: "vidyaan.api_folder.leave_application.get_my_applications",
            });
            const res = await resource.fetch();
            console.log(res.applications);

            my_applications.value = res?.applications || [];
        } catch (error) {
            console.error("Failed to load allExams:", err);
            error.value = err.message || "Unknown error";
        } finally {
            loading.value = false
        }
    }

    return { leave, loading, error, submitLeave, my_applications, fetchApplications }
}

