// import { createResource } from "./useFrappeFetch"

// export const useTeacherExams = () => {
//   const exams = ref([])
//   const loading = ref(false)
//   const error = ref(null)

//   const fetchTeacherExams = async (month, year) => {
//     loading.value = true
//     error.value = null
//     try {
//       const resource = createResource({
//         url: 'maxedu.api_folder.teacher-greading.get_my_exams',
//       })
//       const res = await resource.submit();
//       exams.value = res || []
//       console.log(res);
      
//       return res
//     } catch (err) {
//       console.error('Failed to load exams:', err)
//       error.value = err.message || 'Unknown error'
//     } finally {
//       loading.value = false
//     }
//   }

//   return { exams, loading, error, fetchTeacherExams }
// }



import { ref } from 'vue'
import { createResource } from './useFrappeFetch'

export const useTeacherExams = () => {
  const exams = ref([])
  const courses = ref([])
  const loading = ref(false)
  const error = ref(null)

  // ── Fetch all exams for the logged-in instructor ──────────────────────────
  const fetchTeacherExams = async () => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.teacher_grading.get_my_exams',
      })
      const res = await resource.submit()
      console.log(res);
      
      exams.value = res || []
      return res
    } catch (err) {
      console.error('Failed to load exams:', err)
      error.value = err.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  // ── Fetch instructor profile + instructor logs (courses) ──────────────────
  const fetchTeacherCourses = async () => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.teacher_grading.get_my_courses',
      })
      const res = await resource.submit()
      // res = { instructor fields..., instructor_log: [...] }
      courses.value = res?.instructor_log || []
      return res
    } catch (err) {
      console.error('Failed to load courses:', err)
      error.value = err.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return {
    exams,
    courses,
    loading,
    error,
    fetchTeacherExams,
    fetchTeacherCourses,
  }
}