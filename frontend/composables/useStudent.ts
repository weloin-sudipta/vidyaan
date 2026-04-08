import { call } from '~/composables/useFrappeFetch'

export interface Student {
  name: string
  student_name?: string
  student_email_id?: string
  program?: string
  student_batch_name?: string
  image?: string
  [key: string]: unknown
}

interface StudentApiResponse {
  message?: Student[]
}

export const fetchStudents = async (userEmail?: string): Promise<Student[]> => {
  try {
    const response = await call<Student[] | StudentApiResponse>(
      'vidyaan.api_folder.student.get_student_by_institute',
      userEmail ? { user_email: userEmail } : {}
    )

    let list: unknown
    if (Array.isArray(response)) {
      list = response
    } else if (response && typeof response === 'object' && 'message' in response) {
      list = (response as StudentApiResponse).message
    } else {
      list = response ?? []
    }

    return Array.isArray(list) ? (list as Student[]) : []
  } catch (error) {
    console.error('Error fetching students:', error)
    throw error
  }
}
