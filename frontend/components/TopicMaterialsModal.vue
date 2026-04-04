<template>
  <AppModal 
    v-if="isOpen" 
    :model-value="isOpen" 
    @update:model-value="$event ? null : emit('close')" 
    :title="`Materials: ${topicTitle}`" 
    max-width="max-w-3xl"
  >
    <div v-if="materials.length === 0" class="py-16 text-center">
      <i class="fa fa-inbox text-4xl text-slate-300 dark:text-slate-600 mb-4 block"></i>
      <p class="text-sm text-slate-500 dark:text-slate-400">No materials found for this topic.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="material in materials"
        :key="material.name"
        class="group bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-700/50 p-5 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all"
      >
        <div class="flex flex-col sm:flex-row gap-4 items-start">
          <!-- Icon && Title -->
          <div class="flex items-start gap-3 flex-1 min-w-0">
            <div class="w-10 h-10 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center flex-shrink-0 mt-0.5">
              <i class="fa text-lg text-slate-600 dark:text-slate-400" :class="getFileIcon(material.file)"></i>
            </div>
            <div class="flex-1 min-w-0">
              <button @click="emit('view-details', material)" class="font-black text-sm text-slate-900 dark:text-slate-100 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors cursor-pointer block truncate">{{ material.title }}</button>
              <div class="flex flex-wrap gap-2 items-center mt-1 text-xs text-slate-600 dark:text-slate-400">
                <span class="inline-block px-2 py-0.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700">{{ material.course }}</span>
                <span v-if="material.category" class="inline-block px-2 py-0.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700">{{ material.category }}</span>
                <span class="inline-block px-2 py-0.5 bg-slate-200 dark:bg-slate-600 rounded text-slate-600 dark:text-slate-400">{{ material.upload_date || 'N/A' }}</span>
              </div>
              <p v-if="material.description" class="text-xs text-slate-500 dark:text-slate-500 mt-2 line-clamp-2">{{ material.description }}</p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-2 w-full sm:w-auto flex-wrap sm:flex-nowrap justify-end">
            <a :href="getFileUrl(material.file)" target="_blank" class="text-xs font-bold px-3 py-2 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-900/50 hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-colors flex items-center gap-1 whitespace-nowrap">
              <i class="fa fa-eye"></i>
              <span class="hidden sm:inline">Preview</span>
            </a>
            <a :href="getFileUrl(material.file, true)" class="text-xs font-bold px-3 py-2 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-900/50 hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors flex items-center gap-1 whitespace-nowrap">
              <i class="fa fa-download"></i> 
              <span class="hidden sm:inline">Download</span>
            </a>
            <button @click="emit('edit', material)" class="text-xs font-bold px-3 py-2 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors flex items-center gap-1 whitespace-nowrap">
              <i class="fa fa-edit"></i> 
              <span class="hidden sm:inline">Edit</span>
            </button>
            <button @click="emit('delete', material)" class="text-xs font-bold px-3 py-2 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-900/50 hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors flex items-center gap-1 whitespace-nowrap">
              <i class="fa fa-trash"></i> 
              <span class="hidden sm:inline">Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppModal>
</template>

<script setup>
import AppModal from '~/components/ui/AppModal.vue'

defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  topicTitle: {
    type: String,
    default: ''
  },
  materials: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'view-details', 'edit', 'delete'])

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
</script>
