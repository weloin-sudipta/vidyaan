import { call } from '~/composable/useFrappeFetch'

export const fetchStudents = async (userEmail) => {
  try {
    const response = await call(
      'vidyaan.api_folder.student.get_student_by_institute',
      userEmail ? { user_email: userEmail } : {}
    )

    const list = response?.message ?? response ?? []
    return Array.isArray(list) ? list : []

  } catch (error) {
    console.error('Error fetching students:', error)
    throw error
  }
}