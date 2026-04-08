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

import { ref, type Ref } from 'vue'
import { createResource } from './useFrappeFetch'

// ─── Teacher exam / course shapes ─────────────────────────────────────────
export interface TeacherExamRecord {
  name?: string
  exam_name?: string
  course?: string
  date?: string
  start_time?: string
  end_time?: string
  [key: string]: unknown
}

export interface InstructorLogEntry {
  name?: string
  course?: string
  academic_year?: string
  academic_term?: string
  [key: string]: unknown
}

interface TeacherCoursesResponse {
  instructor_log?: InstructorLogEntry[]
  [key: string]: unknown
}

export interface UseTeacherExamsReturn {
  exams: Ref<TeacherExamRecord[]>
  courses: Ref<InstructorLogEntry[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchTeacherExams: () => Promise<TeacherExamRecord[] | undefined>
  fetchTeacherCourses: () => Promise<TeacherCoursesResponse | undefined>
}

export const useTeacherExams = (): UseTeacherExamsReturn => {
  const exams: Ref<TeacherExamRecord[]> = ref([])
  const courses: Ref<InstructorLogEntry[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  // ── Fetch all exams for the logged-in instructor ──────────────────────────
  const fetchTeacherExams = async (): Promise<TeacherExamRecord[] | undefined> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<TeacherExamRecord[]>({
        url: 'vidyaan.api_folder.teacher_grading.get_my_exams',
      })
      const res = await resource.submit()
      console.log(res)

      exams.value = res || []
      return res
    } catch (err) {
      console.error('Failed to load exams:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  // ── Fetch instructor profile + instructor logs (courses) ──────────────────
  const fetchTeacherCourses = async (): Promise<TeacherCoursesResponse | undefined> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<TeacherCoursesResponse>({
        url: 'vidyaan.api_folder.teacher_grading.get_my_courses',
      })
      const res = await resource.submit()
      // res = { instructor fields..., instructor_log: [...] }
      courses.value = res?.instructor_log || []
      return res
    } catch (err) {
      console.error('Failed to load courses:', err)
      error.value = (err as Error).message || 'Unknown error'
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
