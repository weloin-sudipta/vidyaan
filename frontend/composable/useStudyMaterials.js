import { ref, toRaw } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

export const useStudyMaterials = () => {
  const materials = ref([])
  const loading = ref(false)
  const error = ref(null)
  const teacherMaterials = ref([])

  const fetchMaterials = async (filters = {}) => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.study_materials.get_study_materials',
        params: filters
      })
      const res = await resource.submit(filters)

      console.log('API Response in composable:', res)

      // Handle different response structures
      let materialsData = []

      // Check if response has data property
      if (res?.data && Array.isArray(res.data)) {
        materialsData = res.data
      }
      // Check if response itself is an array
      else if (Array.isArray(res)) {
        materialsData = res
      }
      // Check if response has message property with data
      else if (res?.message && Array.isArray(res.message)) {
        materialsData = res.message
      }
      // Check if response has result property
      else if (res?.result && Array.isArray(res.result)) {
        materialsData = res.result
      }

      materials.value = materialsData
      console.log('Materials set to:', materials.value)
      console.log('Materials count:', materials.value.length)

      return res
    } catch (err) {
      console.error('Failed to load study materials:', err)
      error.value = err.message || 'Unknown error'
      materials.value = []
    } finally {
      loading.value = false
    }
  }

  const createMaterial = async (formData) => {
    loading.value = true
    error.value = null

    try {
      console.log("Form data coming from modal:", formData)

      const fd = new FormData()
      fd.append('title', formData.title)
      fd.append('course', formData.course)

      if (formData.topic) fd.append('topic', formData.topic)
      if (formData.category) fd.append('category', formData.category)
      if (formData.upload_date) fd.append('upload_date', formData.upload_date)
      if (formData.description) fd.append('description', formData.description)
      if (formData.file instanceof File) fd.append('file', formData.file)

      const response = await fetch('/api/method/vidyaan.api_folder.study_materials.create_study_material', {
        method: 'POST',
        body: fd,
        credentials: 'include',
      })

      const json = await response.json()
      const res = json?.message ?? json

      if (res?.success) {
        return res
      } else {
        throw new Error(res?.message || 'Failed to create study material')
      }
    } catch (err) {
      console.error('Failed to create study material:', err)
      error.value = err.message || 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateMaterial = async (name, formData) => {
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

      const response = await fetch('/api/method/vidyaan.api_folder.study_materials.update_study_material', {
        method: 'POST',
        body: fd,
        credentials: 'include',
      })

      const json = await response.json()
      const res = json?.message ?? json

      if (res?.success) {
        return res
      } else {
        throw new Error(res?.message || 'Failed to update study material')
      }
    } catch (err) {
      console.error('Failed to update study material:', err)
      error.value = err.message || 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMaterialsByTeacher = async () => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.study_materials.get_materials_by_teacher'
      })
      const res = await resource.submit()
      console.log('Teacher API response:', res)

      let materialsData = []

      // API returns { success: true, materials: [...] }
      if (res?.materials && Array.isArray(res.materials)) {
        materialsData = res.materials
      } else if (res?.data && Array.isArray(res.data)) {
        materialsData = res.data
      } else if (res?.message && Array.isArray(res.message)) {
        materialsData = res.message
      } else if (res?.result && Array.isArray(res.result)) {
        materialsData = res.result
      } else if (Array.isArray(res)) {
        materialsData = res
      }

      teacherMaterials.value = materialsData
      console.log('Teacher materials set to:', teacherMaterials.value)
      console.log('Teacher materials count:', teacherMaterials.value.length)

      return res
    } catch (err) {
      console.error('Failed to load study materials by teacher:', err)
      error.value = err.message || 'Unknown error'
      teacherMaterials.value = []
    } finally {
      loading.value = false
    }
  }

  const deleteMaterial = async (name) => {
    loading.value = true
    error.value = null

    try {
      const fd = new FormData()
      fd.append('name', name)

      const response = await fetch('/api/method/vidyaan.api_folder.study_materials.delete_study_material', {
        method: 'POST',
        body: fd,
        credentials: 'include',
      })

      const json = await response.json()
      const res = json?.message ?? json

      if (res?.success) {
        return res
      } else {
        throw new Error(res?.message || 'Failed to delete study material')
      }
    } catch (err) {
      console.error('Failed to delete study material:', err)
      error.value = err.message || 'Unknown error'
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
    fetchMaterialsByTeacher
  }
}