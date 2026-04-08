<template>
  <AppModal :model-value="isOpen" @update:model-value="$event ? null : emit('close')"
    :title="`${props.mode === 'edit' ? 'Edit Study Material' : 'Upload Study Material'}`" max-width="max-w-3xl">
    <!-- Form Content -->
    <form @submit.prevent="handleSubmit" class="space-y-6">

      <!-- Section 1: Basic Information -->
      <div class="space-y-4">
        <h4
          class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
          <i class="fa fa-info-circle mr-2 text-indigo-500"></i>Basic Information
        </h4>

        <!-- Title (Required) -->
        <div>
          <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
            Title <span class="text-red-500">*</span>
          </label>
          <input type="text" v-model="formData.title"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all placeholder-slate-400 dark:placeholder-slate-500"
            placeholder="Enter study material title" required />
        </div>

        <!-- Course & Topic Row -->
        <div class="grid grid-cols-2 gap-4">
          <!-- Course (Required - Pre-selected) -->
          <div>
            <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
              Course <span class="text-red-500">*</span>
            </label>
            <select v-model="formData.course" @change="onCourseChange"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              required :disabled="!!preselectedCourse">
              <option v-if="!preselectedCourse" value="">Select a course</option>
              <option v-for="course in courses" :key="course.name" :value="course.name">
                {{ course.course_name }}
              </option>
            </select>
            <p v-if="preselectedCourse" class="text-xs text-slate-400 mt-2">
              <i class="fa fa-lock mr-1"></i>Pre-selected from current view
            </p>
          </div>

          <!-- Topic (Optional) -->
          <div>
            <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
              Topic <span class="text-slate-400 text-[10px] font-normal">(Optional)</span>
            </label>
            <select v-model="selectedTopicValue" @change="handleTopicChange"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              :disabled="!!preselectedTopic">
              <option value="">Select a topic</option>
              <option v-for="topic in availableTopics" :key="topic.name" :value="topic.topic_name || topic.name">
                {{ topic.topic_name || topic.name }}
              </option>
            </select>
            <p v-if="preselectedTopicName" class="text-xs text-indigo-500 mt-2">
              <i class="fa fa-link mr-1"></i>Pre-selected for this material
            </p>
          </div>
        </div>
      </div>

      <!-- Section 2: Content Details -->
      <div class="space-y-4">
        <h4
          class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
          <i class="fa fa-file-o mr-2 text-blue-500"></i>Content Details
        </h4>

        <!-- Category & Upload Date Row -->
        <div class="grid grid-cols-2 gap-4">
          <!-- Category -->
          <div>
            <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
              Category <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
            </label>
            <select v-model="formData.category"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all">
              <option value="">Select a category</option>
              <option value="Lecture Notes">Lecture Notes</option>
              <option value="Syllabus">Syllabus</option>
              <option value="Question Bank">Question Bank</option>
              <option value="Lab Manuals">Lab Manuals</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <!-- Upload Date -->
          <div>
            <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
              Upload Date <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
            </label>
            <input type="date" v-model="formData.upload_date"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all" />
          </div>
        </div>

        <!-- Description (Optional) -->
        <div>
          <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-2">
            Description <span class="text-slate-400 text-[10px] font-normal">(optional)</span>
          </label>
          <textarea v-model="formData.description" rows="2"
            class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all resize-none placeholder-slate-400 dark:placeholder-slate-500"
            placeholder="Add a detailed description of the study material..."></textarea>
        </div>
      </div>

      <!-- Section 3: File Upload -->
      <div class="space-y-4">
        <h4
          class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 pb-3 border-b border-slate-100 dark:border-slate-800">
          <i class="fa fa-cloud-upload mr-2 text-green-500"></i>File Upload
        </h4>

        <!-- File Upload (Required) -->
        <div>
          <label class="block text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-3">
            File <span class="text-red-500">*</span>
          </label>
          <div class="relative">
            <input type="file" ref="fileInput" @change="handleFileChange" class="hidden"
              accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.mp4,.zip" />
            <div @click="$refs.fileInput.click()"
              class="w-full px-6 py-4 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 cursor-pointer hover:border-indigo-300 dark:hover:border-indigo-500 hover:bg-slate-100 dark:hover:bg-slate-700/30 transition-all">
              <div class="flex items-center justify-center gap-4">
                <div
                  class="inline-flex items-center justify-center w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg shrink-0">
                  <i class="fa fa-cloud-upload text-lg text-indigo-600 dark:text-indigo-400"></i>
                </div>
                <div class="text-left">
                  <p class="text-sm font-bold text-slate-700 dark:text-slate-300 mb-1">
                    {{ fileSelected ? fileSelected.name : 'Click to upload or drag and drop' }}
                  </p>
                  <p class="text-xs text-slate-500 dark:text-slate-400">
                    PDF, DOC, PPT, Images, MP4 (Max 50MB)
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error"
        class="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-start gap-3">
        <i class="fa fa-exclamation-circle text-red-600 dark:text-red-400 mt-0.5"></i>
        <p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
      </div>
    </form>

    <!-- Submit Buttons -->
    <template #footer>
      <button type="button" @click="emit('close')"
        class="flex-1 px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
        Cancel
      </button>
      <button type="submit" @click="handleSubmit" :disabled="loading"
        class="flex-1 px-6 py-3 rounded-xl bg-indigo-600 dark:bg-indigo-500 text-white text-sm font-bold hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
        <i v-if="loading" class="fa fa-spinner fa-spin"></i>
        {{ loading ? (props.mode === 'edit' ? 'Saving...' : 'Uploading...') : (props.mode === 'edit' ? 'Save Changes' :
        'Upload Material') }}
      </button>
    </template>
  </AppModal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import AppModal from '~/components/ui/AppModal.vue'
import { useStudyMaterials } from '~/composables/useStudyMaterials'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  preselectedCourse: {
    type: String,
    default: null
  },
  preselectedTopic: {
    type: String,
    default: null
  },
  preselectedTopicName: {
    type: String,
    default: null
  },
  mode: {
    type: String,
    default: 'create'
  },
  material: {
    type: Object,
    default: null
  },
  courses: {
    type: Array,
    required: true
  },
  topics: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'success'])

const { createMaterial, updateMaterial, loading: createLoading, error: createError } = useStudyMaterials()
const loading = computed(() => createLoading.value)
const error = ref(null)
const fileSelected = ref(null)
const fileInput = ref(null)
const selectedTopicValue = ref('')

const formData = ref({
  title: '',
  course: props.preselectedCourse || '',
  topic: '',
  category: '',
  file: null,
  upload_date: new Date().toISOString().split('T')[0],
  description: ''
})

// Available topics based on selected course
const availableTopics = computed(() => {
  if (!formData.value.course) return []
  const selectedCourse = props.courses.find(c => c.name === formData.value.course)
  return selectedCourse?.topics || []
})

// Handle course change
const onCourseChange = () => {
  // Reset topic when course changes
  if (!props.preselectedTopic) {
    selectedTopicValue.value = ''
    formData.value.topic = ''
  }
}

// Watch for course changes
watch(() => formData.value.course, (newCourse) => {
  if (!props.preselectedTopic) {
    selectedTopicValue.value = ''
    formData.value.topic = ''
  }
})

// Watch for error from composable
watch(() => createError.value, (newError) => {
  if (newError) {
    error.value = newError
  }
})

// Handle topic selection - store the actual topic name/value
const handleTopicChange = () => {
  formData.value.topic = selectedTopicValue.value
}

// Handle file selection
const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      error.value = 'File size must be less than 50MB'
      fileSelected.value = null
      formData.value.file = null
      return
    }

    fileSelected.value = file
    formData.value.file = file
    error.value = null
  }
}

// Handle form submission
const handleSubmit = async () => {
  error.value = null

  // Validate required fields
  if (!formData.value.title.trim()) {
    error.value = 'Title is required'
    return
  }

  if (!formData.value.course) {
    error.value = 'Course is required'
    return
  }

  if (props.mode === 'create' && !formData.value.file) {
    error.value = 'File is required'
    return
  }

  try {
    console.log('Submitting form data:', {
      mode: props.mode,
      title: formData.value.title,
      course: formData.value.course,
      topic: formData.value.topic,
      category: formData.value.category,
      upload_date: formData.value.upload_date,
      description: formData.value.description,
      file: formData.value.file?.name
    })

    let result
    if (props.mode === 'edit' && props.material && props.material.name) {
      result = await updateMaterial(props.material.name, formData.value)
    } else {
      result = await createMaterial(formData.value)
    }

    if (result?.success) {
      emit('success', result.data || result)
      resetForm()
      emit('close')
    } else {
      error.value = result?.message || (props.mode === 'edit' ? 'Failed to update study material' : 'Failed to upload study material')
    }
  } catch (err) {
    console.error('Submission error:', err)
    error.value = err.message || 'An error occurred while uploading'
  }
}

// Close modal and reset form
const closeModal = () => {
  resetForm()
  emit('close')
}

// Reset form data
const resetForm = () => {
  formData.value = {
    title: '',
    course: props.preselectedCourse || '',
    topic: '',
    category: '',
    file: null,
    upload_date: new Date().toISOString().split('T')[0],
    description: ''
  }
  selectedTopicValue.value = ''
  fileSelected.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  error.value = null
}

// Reset when modal opens with new preselected course/topic
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    if (props.mode === 'edit' && props.material) {
      formData.value = {
        title: props.material.title || '',
        course: props.material.course || props.preselectedCourse || '',
        topic: props.material.topic || props.preselectedTopicName || '',
        category: props.material.category || '',
        file: null, // optional new file
        upload_date: props.material.upload_date || new Date().toISOString().split('T')[0],
        description: props.material.description || ''
      }
      selectedTopicValue.value = props.material.topic || props.preselectedTopicName || ''
      fileSelected.value = null
    } else {
      formData.value.course = props.preselectedCourse || ''

      if (props.preselectedTopicName) {
        selectedTopicValue.value = props.preselectedTopicName
        formData.value.topic = props.preselectedTopicName
      } else {
        selectedTopicValue.value = ''
        formData.value.topic = ''
      }

      // Reset other fields but keep course and topic if preselected
      formData.value.title = ''
      formData.value.category = ''
      formData.value.file = null
      formData.value.upload_date = new Date().toISOString().split('T')[0]
      formData.value.description = ''
      fileSelected.value = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    error.value = null
  }
})
</script>

<style scoped>
/* Smooth animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.fixed {
  animation: fadeIn 0.2s ease-out;
}

/* Custom scrollbar for modal */
.overflow-y-auto {
  scrollbar-width: thin;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>