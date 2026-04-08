import { ref, type Ref } from 'vue'
import { createResource, callMultipart, type FrappeParams } from '~/composables/api/useFrappeFetch'

// ─── Local shapes ─────────────────────────────────────────────────────────
export interface StudyMaterial {
  name?: string
  title?: string
  course?: string
  topic?: string
  category?: string
  upload_date?: string
  description?: string
  file?: string
  [key: string]: unknown
}

export interface StudyMaterialFormData {
  title: string
  course: string
  topic?: string
  category?: string
  upload_date?: string
  description?: string
  file?: File | null
  [key: string]: unknown
}

export interface StudyMaterialMutationResponse {
  success?: boolean
  message?: string
  data?: StudyMaterial[] | StudyMaterial
  materials?: StudyMaterial[]
  result?: StudyMaterial[]
  [key: string]: unknown
}

export interface UseStudyMaterialsReturn {
  materials: Ref<StudyMaterial[]>
  teacherMaterials: Ref<StudyMaterial[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchMaterials: (filters?: FrappeParams) => Promise<StudyMaterialMutationResponse | undefined>
  createMaterial: (formData: StudyMaterialFormData) => Promise<StudyMaterialMutationResponse>
  updateMaterial: (
    name: string,
    formData: StudyMaterialFormData
  ) => Promise<StudyMaterialMutationResponse>
  deleteMaterial: (name: string) => Promise<StudyMaterialMutationResponse>
  fetchMaterialsByTeacher: () => Promise<StudyMaterialMutationResponse | undefined>
}

/**
 * Unwraps a study-material API response into a flat array, tolerating the
 * various envelope shapes the backend has returned over time. The `mode`
 * argument preserves the exact lookup order each call site historically
 * relied on:
 *   - 'student' → data → array → message → result   (used by fetchMaterials)
 *   - 'teacher' → materials → data → message → result → array
 *                                                  (used by fetchMaterialsByTeacher)
 */
const extractMaterials = (
  res: StudyMaterialMutationResponse | StudyMaterial[] | undefined | null,
  mode: 'student' | 'teacher'
): StudyMaterial[] => {
  if (!res) return []
  if (mode === 'student') {
    if (!Array.isArray(res) && Array.isArray(res.data)) return res.data as StudyMaterial[]
    if (Array.isArray(res)) return res
    if (!Array.isArray(res) && Array.isArray(res.message)) return res.message as StudyMaterial[]
    if (!Array.isArray(res) && Array.isArray(res.result)) return res.result
    return []
  }
  // teacher
  if (!Array.isArray(res) && Array.isArray(res.materials)) return res.materials
  if (!Array.isArray(res) && Array.isArray(res.data)) return res.data as StudyMaterial[]
  if (!Array.isArray(res) && Array.isArray(res.message)) return res.message as StudyMaterial[]
  if (!Array.isArray(res) && Array.isArray(res.result)) return res.result
  if (Array.isArray(res)) return res
  return []
}

export const useStudyMaterials = (): UseStudyMaterialsReturn => {
  const materials: Ref<StudyMaterial[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const teacherMaterials: Ref<StudyMaterial[]> = ref([])

  const fetchMaterials = async (
    filters: FrappeParams = {}
  ): Promise<StudyMaterialMutationResponse | undefined> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<StudyMaterialMutationResponse>({
        url: 'vidyaan.api_folder.study_materials.get_study_materials',
        params: filters,
      })
      const res = await resource.submit(filters)

      console.log('API Response in composable:', res)

      materials.value = extractMaterials(res, 'student')
      console.log('Materials set to:', materials.value)
      console.log('Materials count:', materials.value.length)

      return res
    } catch (err) {
      console.error('Failed to load study materials:', err)
      error.value = (err as Error).message || 'Unknown error'
      materials.value = []
    } finally {
      loading.value = false
    }
  }

  const createMaterial = async (
    formData: StudyMaterialFormData
  ): Promise<StudyMaterialMutationResponse> => {
    loading.value = true
    error.value = null

    try {
      console.log('Form data coming from modal:', formData)

      const fd = new FormData()
      fd.append('title', formData.title)
      fd.append('course', formData.course)

      if (formData.topic) fd.append('topic', formData.topic)
      if (formData.category) fd.append('category', formData.category)
      if (formData.upload_date) fd.append('upload_date', formData.upload_date)
      if (formData.description) fd.append('description', formData.description)
      if (formData.file instanceof File) fd.append('file', formData.file)

      const res = await callMultipart<StudyMaterialMutationResponse>(
        'vidyaan.api_folder.study_materials.create_study_material',
        fd
      )

      if (res?.success) {
        return res
      } else {
        throw new Error(res?.message || 'Failed to create study material')
      }
    } catch (err) {
      console.error('Failed to create study material:', err)
      error.value = (err as Error).message || 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateMaterial = async (
    name: string,
    formData: StudyMaterialFormData
  ): Promise<StudyMaterialMutationResponse> => {
    loading.value = true
    error.value = null

    try {
      const fd = new FormData()
      fd.append('name', name)
      fd.append('title', formData.title)
      fd.append('course', formData.course)

      if (formData.topic) fd.append('topic', formData.topic)
      if (formData.category) fd.append('category', formData.category)
      if (formData.upload_date) fd.append('upload_date', formData.upload_date)
      if (formData.description) fd.append('description', formData.description)
      if (formData.file instanceof File) fd.append('file', formData.file)

      const res = await callMultipart<StudyMaterialMutationResponse>(
        'vidyaan.api_folder.study_materials.update_study_material',
        fd
      )

      if (res?.success) {
        return res
      } else {
        throw new Error(res?.message || 'Failed to update study material')
      }
    } catch (err) {
      console.error('Failed to update study material:', err)
      error.value = (err as Error).message || 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMaterialsByTeacher = async (): Promise<
    StudyMaterialMutationResponse | undefined
  > => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<StudyMaterialMutationResponse>({
        url: 'vidyaan.api_folder.study_materials.get_materials_by_teacher',
      })
      const res = await resource.submit()
      console.log('Teacher API response:', res)

      teacherMaterials.value = extractMaterials(res, 'teacher')
      console.log('Teacher materials set to:', teacherMaterials.value)
      console.log('Teacher materials count:', teacherMaterials.value.length)

      return res
    } catch (err) {
      console.error('Failed to load study materials by teacher:', err)
      error.value = (err as Error).message || 'Unknown error'
      teacherMaterials.value = []
    } finally {
      loading.value = false
    }
  }

  const deleteMaterial = async (name: string): Promise<StudyMaterialMutationResponse> => {
    loading.value = true
    error.value = null

    try {
      const fd = new FormData()
      fd.append('name', name)

      const res = await callMultipart<StudyMaterialMutationResponse>(
        'vidyaan.api_folder.study_materials.delete_study_material',
        fd
      )

      if (res?.success) {
        return res
      } else {
        throw new Error(res?.message || 'Failed to delete study material')
      }
    } catch (err) {
      console.error('Failed to delete study material:', err)
      error.value = (err as Error).message || 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    materials,
    teacherMaterials,
    loading,
    error,
    fetchMaterials,
    createMaterial,
    updateMaterial,
    deleteMaterial,
    fetchMaterialsByTeacher,
  }
}
