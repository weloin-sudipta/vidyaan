<!-- pages/lesson-planning.vue -->

<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900 custom-scrollbar">
    <div class="p-6 lg:p-10 max-w-7xl mx-auto">
      <HeroHeader title="Lesson Planning" subtitle="Curriculum Tracking & Material Management" icon="fa fa-map-signs">
        <div class="flex gap-3 flex-wrap">
          <!-- Dynamic Course Dropdown -->
          <div class="relative">
            <select
              v-model="selectedCourse"
              @change="onCourseChange"
              class="bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 px-4 py-2.5 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-700 outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all appearance-none pr-8"
            >
              <option
                v-for="course in courses"
                :key="course.name"
                :value="course.name"
              >
                {{ course.course_name }}
              </option>
            </select>
            <i class="fa fa-chevron-down absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 pointer-events-none text-xs"></i>
          </div>

          <button 
            @click="openModal"
            class="bg-gradient-to-r from-indigo-600 to-blue-600 dark:from-indigo-500 dark:to-blue-500 text-white px-6 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest hover:shadow-lg hover:shadow-indigo-300 dark:hover:shadow-indigo-900 transition-all duration-200 flex items-center gap-2 whitespace-nowrap"
          >
            <i class="fa fa-cloud-upload"></i> 
            <span class="hidden sm:inline">Upload Material</span>
            <span class="sm:hidden">Upload</span>
          </button>
        </div>
      </HeroHeader>

    <!-- Loading -->
    <div v-if="loading" class="mt-12">
      <UiSkeleton height="h-96" class="rounded-[2.5rem]" />
    </div>

    <!-- Content -->
    <div v-else class="mt-12">
      <!-- Topics List Section -->
      <div class="space-y-8">
        <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden">
          <!-- Header -->
          <div class="bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-700/50 px-8 py-6 border-b border-slate-100 dark:border-slate-700">
            <h2 class="text-base font-black uppercase tracking-widest text-slate-700 dark:text-slate-300 flex items-center gap-3">
              <span class="w-2 h-2 bg-indigo-500 rounded-full"></span>
              <i class="fa fa-book text-lg text-indigo-500"></i>
              Course Topics & Materials
            </h2>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 ml-5">Organize your study materials by topic for better curriculum tracking</p>
          </div>

          <!-- Content -->
          <div class="p-8">
            <div v-if="topics.length === 0" class="text-center py-12">
              <i class="fa fa-inbox text-4xl text-slate-300 dark:text-slate-600 mb-4 block"></i>
              <p class="text-sm text-slate-500 dark:text-slate-400">No topics available for this course.</p>
            </div>

            <div v-else class="space-y-6">
              <div
                v-for="(topic, i) in topics"
                :key="topic.name"
                class="relative group"
              >
                <!-- Timeline Style -->
                <div class="flex gap-6">
                  <!-- Timeline Indicator -->
                  <div class="flex flex-col items-center">
                    <div class="w-10 h-10 rounded-full flex items-center justify-center font-black text-sm bg-gradient-to-br from-indigo-100 to-blue-100 dark:from-indigo-900/30 dark:to-blue-900/30 text-indigo-600 dark:text-indigo-400 border-2 border-indigo-200 dark:border-indigo-700 transition-all group-hover:scale-110">
                      {{ i + 1 }}
                    </div>
                    <div v-if="i < topics.length - 1" class="w-1 bg-gradient-to-b from-indigo-300 to-blue-300 dark:from-indigo-600 dark:to-blue-600 mt-2 flex-1 min-h-[200px]"></div>
                  </div>

                  <!-- Topic Card -->
                  <div class="flex-1 pb-6">
                    <div class="bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-800/50 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 group-hover:border-indigo-300 dark:group-hover:border-indigo-600 group-hover:shadow-lg transition-all">
                      
                      <!-- Topic Header -->
                      <div class="flex justify-between items-start mb-4">
                        <div>
                          <span class="inline-block text-xs font-black uppercase tracking-widest text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 px-3 py-1 rounded-full mb-2">
                            Topic {{ i + 1 }}
                          </span>
                          <h4 class="text-lg font-black text-slate-900 dark:text-slate-100">{{ topic.topic_name }}</h4>
                        </div>
                        <button
                          @click="openTopicMaterials(topic.topic_name)"
                          class="text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-700 px-3 py-2 rounded-lg hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-all whitespace-nowrap"
                        >
                          <i class="fa fa-eye mr-1"></i> View All
                        </button>
                      </div>

                      <!-- Topic Description -->
                      <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-4 line-clamp-2">
                        {{ topic.topic || topic.topic_name }}
                      </p>

                      <!-- Materials Section -->
                      <div v-if="getMaterialsForTopic(topic.topic_name).length > 0" class="mb-4">
                        <h5 class="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-3">
                          <i class="fa fa-files-o mr-2"></i>{{ getMaterialsForTopic(topic.topic_name).length }} Materials
                        </h5>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          <button 
                            v-for="material in getMaterialsForTopic(topic.topic_name).slice(0, 4)"
                            :key="material.name"
                            @click="openMaterialDetails(material)"
                            class="text-left text-xs font-bold px-3 py-2 rounded-lg bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-200 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-slate-600 transition-all flex items-center gap-2 group"
                          >
                            <i class="fa text-sm" :class="getFileIcon(material.file)"></i> 
                            <span class="truncate flex-1 group-hover:underline">{{ material.title }}</span>
                          </button>
                        </div>
                        <div v-if="getMaterialsForTopic(topic.topic_name).length > 4" class="text-xs text-indigo-600 dark:text-indigo-400 mt-2 font-bold">
                          +{{ getMaterialsForTopic(topic.topic_name).length - 4 }} more
                        </div>
                      </div>
                      <div v-else class="mb-4 p-3 bg-slate-100 dark:bg-slate-700/30 rounded-lg text-xs text-slate-500 dark:text-slate-400 text-center">
                        No materials yet
                      </div>

                      <!-- Action Buttons -->
                      <div class="flex gap-2 pt-3 border-t border-slate-100 dark:border-slate-700">
                        <button 
                          @click="openModalWithTopic(topic.topic_name)"
                          class="flex-1 text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-700 px-3 py-2 rounded-lg hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-all flex items-center justify-center gap-2"
                        >
                          <i class="fa fa-plus"></i> Add Material
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Uncategorized Materials Section -->
        <div v-if="getMaterialsWithoutTopic().length > 0" class="mt-8 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-yellow-200 dark:border-yellow-900/30 shadow-sm overflow-hidden">
          <!-- Header with Warning -->
          <div class="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 px-8 py-6 border-b border-yellow-200 dark:border-yellow-900/30">
            <h2 class="text-base font-black uppercase tracking-widest text-yellow-700 dark:text-yellow-400 flex items-center gap-3">
              <i class="fa fa-exclamation-triangle text-xl"></i>
              <span>Uncategorized Materials</span>
              <span class="ml-auto text-sm font-bold bg-yellow-200 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-400 px-3 py-1 rounded-full">{{ getMaterialsWithoutTopic().length }}</span>
            </h2>
            <p class="text-xs text-yellow-600 dark:text-yellow-500 mt-2 ml-9">Materials not assigned to any topic. Assign them for better organization.</p>
          </div>

          <!-- Content -->
          <div class="p-8">
            <div class="space-y-4">
              <div
                v-for="material in getMaterialsWithoutTopic()"
                :key="material.name"
                class="group bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/10 dark:to-orange-900/10 p-5 rounded-xl border border-yellow-200 dark:border-yellow-900/30 hover:border-yellow-400 dark:hover:border-yellow-700 hover:shadow-md transition-all"
              >
                <div class="flex flex-col sm:flex-row gap-4 items-start">
                  <!-- Material Info -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start gap-3">
                      <div class="w-10 h-10 rounded-lg bg-white dark:bg-slate-800 border border-yellow-200 dark:border-yellow-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <i class="fa text-lg text-yellow-600 dark:text-yellow-400" :class="getFileIcon(material.file)"></i>
                      </div>
                      <div class="flex-1 min-w-0">
                        <button @click="openMaterialDetails(material)" class="font-black text-sm text-slate-900 dark:text-slate-100 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors cursor-pointer block truncate">{{ material.title }}</button>
                        <div class="flex flex-wrap gap-2 items-center mt-1 text-xs text-slate-600 dark:text-slate-400">
                          <span class="inline-block px-2 py-0.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700">{{ material.course }}</span>
                          <span v-if="material.category" class="inline-block px-2 py-0.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700">{{ material.category }}</span>
                          <span class="inline-block px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-slate-500 dark:text-slate-500">{{ material.upload_date || 'N/A' }}</span>
                        </div>
                        <p v-if="material.description" class="text-xs text-slate-500 dark:text-slate-500 mt-2 line-clamp-2">{{ material.description }}</p>
                      </div>
                    </div>
                  </div>

                  <!-- Action Buttons -->
                  <div class="flex gap-2 w-full sm:w-auto flex-wrap sm:flex-nowrap justify-end">
                    <button 
                      @click="editMaterial(material)" 
                      class="text-xs font-bold px-3 py-2 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors flex items-center gap-1 whitespace-nowrap"
                    >
                      <i class="fa fa-edit"></i> 
                      <span class="hidden sm:inline">Edit</span>
                    </button>
                    <button 
                      @click="deleteMaterial(material)" 
                      class="text-xs font-bold px-3 py-2 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-900/50 hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors flex items-center gap-1 whitespace-nowrap"
                    >
                      <i class="fa fa-trash"></i> 
                      <span class="hidden sm:inline">Delete</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <div v-if="showSuccess" class="fixed bottom-4 right-4 z-50 animate-in slide-in-from-right-4 duration-300">
      <div class="bg-green-500 text-white px-6 py-3 rounded-xl shadow-lg flex items-center gap-2">
        <i class="fa fa-check-circle"></i>
        <span class="text-sm font-medium">Study material uploaded successfully!</span>
      </div>
    </div>

    <!-- Error Toast -->
    <div v-if="showError" class="fixed bottom-4 right-4 z-50 animate-in slide-in-from-right-4 duration-300">
      <div class="bg-red-500 text-white px-6 py-3 rounded-xl shadow-lg flex items-center gap-2">
        <i class="fa fa-exclamation-circle"></i>
        <span class="text-sm font-medium">{{ errorMessage }}</span>
      </div>
    </div>

    <!-- Topic Materials Preview Modal -->
    <TopicMaterialsModal
      :is-open="materialsDialogOpen"
      :topic-title="selectedTopicTitle"
      :materials="selectedTopicMaterials"
      @close="closeTopicMaterials"
      @view-details="openMaterialDetails"
      @edit="editMaterial"
      @delete="deleteMaterial"
    />

    <!-- Study Material Modal -->
    <StudyMaterialModal
      :is-open="modalOpen"
      :mode="modalMode"
      :material="materialToEdit"
      :preselected-course="selectedCourse"
      :preselected-topic-name="preselectedTopicName"
      :courses="courses"
      :topics="topics"
      @close="closeModal"
      @success="onMaterialUploaded"
    />

    <!-- Material Details Modal -->
    <MaterialDetailsModal
      :is-open="detailsModalOpen"
      :material="selectedMaterial"
      @close="closeMaterialDetails"
      @edit="handleMaterialDetailsEdit"
      @delete="handleMaterialDetailsDelete"
    />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import StudyMaterialModal from '~/components/StudyMaterialModal.vue'
import MaterialDetailsModal from '~/components/MaterialDetailsModal.vue'
import TopicMaterialsModal from '~/components/TopicMaterialsModal.vue'
import { useCourseTopics } from '~/composable/useCourseTopics'
import { useStudyMaterials } from '~/composable/useStudyMaterials'

const { fetchCourseTopics } = useCourseTopics()
const { materials, teacherMaterials, fetchMaterials, fetchMaterialsByTeacher, deleteMaterial: deleteMaterialAPI, loading: materialsLoading } = useStudyMaterials()

const loading = ref(true)
const courses = ref([])
const selectedCourse = ref(null)
const modalOpen = ref(false)
const modalMode = ref('create')
const materialToEdit = ref(null)
const preselectedTopicName = ref(null)
const materialsDialogOpen = ref(false)
const selectedTopicTitle = ref('')
const selectedTopicMaterials = ref([])
const showSuccess = ref(false)
const showError = ref(false)
const errorMessage = ref('')
const detailsModalOpen = ref(false)
const selectedMaterial = ref(null)

/**
 * Fetch data
 */
const loadData = async () => {
  try {
    const res = await fetchCourseTopics()
    courses.value = res || []

    if (courses.value.length > 0) {
      selectedCourse.value = courses.value[0].name
      // Fetch materials for the selected course
      await fetchMaterials({ course: selectedCourse.value })
    }
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

/**
 * Handle course change
 */
const onCourseChange = async () => {
  loading.value = true
  await fetchMaterials({ course: selectedCourse.value })
  loading.value = false
}

/**
 * Selected course object
 */
const selectedCourseData = computed(() => {
  return courses.value.find(c => c.name === selectedCourse.value)
})

/**
 * Topics of selected course
 */
const topics = computed(() => {
  return selectedCourseData.value?.topics || []
})

/**
 * Get materials for a specific topic (teacher data source)
 */
const getMaterialsForTopic = (topicName) => {
  if (!topicName) return teacherMaterials.value.filter(m => !m.topic)
  return teacherMaterials.value.filter(m => m.topic === topicName)
}

/**
 * Get materials without a topic
 */
const getMaterialsWithoutTopic = () => {
  return teacherMaterials.value.filter(m => !m.topic || m.topic === '' || m.topic === null)
}

const openTopicMaterials = (topicName) => {
  selectedTopicTitle.value = topicName || 'Uncategorized'
  selectedTopicMaterials.value = getMaterialsForTopic(topicName)
  materialsDialogOpen.value = true
}

const closeTopicMaterials = () => {
  materialsDialogOpen.value = false
  selectedTopicTitle.value = ''
  selectedTopicMaterials.value = []
}

const openMaterialDetails = (material) => {
  selectedMaterial.value = material
  detailsModalOpen.value = true
}

const closeMaterialDetails = () => {
  detailsModalOpen.value = false
  selectedMaterial.value = null
}

const handleMaterialDetailsEdit = async (material) => {
  closeMaterialDetails()
  editMaterial(material)
}

const handleMaterialDetailsDelete = async (material) => {
  closeMaterialDetails()
  await deleteMaterial(material)
}

const deleteMaterial = async (material) => {
  if (!confirm(`Delete study material '${material.title}'?`)) return
  try {
    await deleteMaterialAPI(material.name)
    teacherMaterials.value = teacherMaterials.value.filter(m => m.name !== material.name)
    selectedTopicMaterials.value = selectedTopicMaterials.value.filter(m => m.name !== material.name)
    // No need to refetch since we updated locally
  } catch (err) {
    console.error('Failed to delete material', err)
    handleError('Could not delete material.')
  }
}

/**
 * Get file icon based on file type
 */
const getFileIcon = (fileUrl) => {
  if (!fileUrl) return 'fa-file-o'
  const ext = fileUrl.split('.').pop().toLowerCase()
  const iconMap = {
    pdf: 'fa-file-pdf-o',
    doc: 'fa-file-word-o',
    docx: 'fa-file-word-o',
    ppt: 'fa-file-powerpoint-o',
    pptx: 'fa-file-powerpoint-o',
    xls: 'fa-file-excel-o',
    xlsx: 'fa-file-excel-o',
    jpg: 'fa-file-image-o',
    jpeg: 'fa-file-image-o',
    png: 'fa-file-image-o',
    mp4: 'fa-file-video-o',
    zip: 'fa-file-archive-o'
  }
  return iconMap[ext] || 'fa-file-o'
}

const getFileUrl = (filePath, isDownload = false) => {
  if (!filePath) return ''
  if (filePath.startsWith('http')) return filePath

  if (isDownload) {
    return `/api/method/frappe.utils.file_manager.download_file?file_url=${encodeURIComponent(filePath)}`
  }

  return filePath
}

/**
 * Open modal (without topic pre-selection)
 */
const openModal = () => {
  modalMode.value = 'create'
  materialToEdit.value = null
  preselectedTopicName.value = null
  modalOpen.value = true
}

/**
 * Open modal with specific topic pre-selected
 * This is called when clicking the "Add Material" button on a topic
 */
const openModalWithTopic = (topicName) => {
  modalMode.value = 'create'
  materialToEdit.value = null
  preselectedTopicName.value = topicName
  modalOpen.value = true
}

const editMaterial = (material) => {
  modalMode.value = 'edit'
  materialToEdit.value = material
  preselectedTopicName.value = material.topic || null
  modalOpen.value = true
}

/**
 * Close modal
 */
const closeModal = () => {
  modalOpen.value = false
  // Don't reset preselectedTopic immediately to allow modal to use it
  setTimeout(() => {
    preselectedTopicName.value = null
  }, 300)
}

/**
 * Handle successful material upload
 */
const onMaterialUploaded = async (materialData) => {
  // Show success message
  showSuccess.value = true
  setTimeout(() => {
    showSuccess.value = false
  }, 3000)

  // Refresh materials lists
  await Promise.all([
    fetchMaterials({ course: selectedCourse.value }),
    fetchMaterialsByTeacher()
  ])

  // Close edit context if any
  modalMode.value = 'create'
  materialToEdit.value = null
  preselectedTopicName.value = null
}

/**
 * Handle error
 */
const handleError = (message) => {
  errorMessage.value = message
  showError.value = true
  setTimeout(() => {
    showError.value = false
  }, 3000)
}

onMounted(() => {
  fetchMaterialsByTeacher()
  loadData()
})
</script>

<style scoped>
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Smooth animations */
.animate-in {
  animation-duration: 0.5s;
  animation-fill-mode: both;
}

.fade-in {
  animation-name: fadeIn;
}

.slide-in-from-bottom-4 {
  animation-name: slideInFromBottom;
}

.slide-in-from-right-4 {
  animation-name: slideInFromRight;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideInFromBottom {
  from {
    transform: translateY(1rem);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slideInFromRight {
  from {
    transform: translateX(1rem);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>