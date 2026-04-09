<template>
  <div v-if="detail" class="max-w-7xl mx-auto px-4 py-12 animate-in fade-in">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-12">
      
      <div class="lg:col-span-8 space-y-8">
        <button @click="router.back()" class="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
          <i class="fa fa-arrow-left"></i> Back
        </button>

        <div class="space-y-4">
          <span :class="detail.type === 'Notice' ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400' : 'bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400'" 
                class="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-colors">
            {{ detail.category || detail.type }}
          </span>
          <h1 class="text-4xl font-black text-slate-900 dark:text-slate-100 transition-colors">{{ detail.title }}</h1>
          <p class="text-slate-500 dark:text-slate-400 text-lg mt-2 transition-colors">{{ detail.description }}</p>
          <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 transition-colors">{{ detail.date }}</span>
        </div>

        <div v-if="detail.attachments && detail.attachments.length" class="space-y-4">
           <h3 class="text-xs font-black uppercase text-slate-400 dark:text-slate-500 transition-colors">Attached Documents</h3>
           <div v-for="file in detail.attachments" :key="file.file_url" 
                class="p-4 border border-slate-100 dark:border-slate-800 rounded-2xl flex items-center justify-between bg-slate-50 dark:bg-slate-800/50 transition-colors">
              <div class="flex items-center gap-3">
                 <i class="fa fa-file-pdf-o text-indigo-500 dark:text-indigo-400"></i>
                 <span class="text-xs font-bold text-slate-700 dark:text-slate-300 transition-colors">{{ file.file_name }}</span>
              </div>
              <a :href="getFileUrl(file.file_url)" target="_blank" class="text-indigo-600 dark:text-indigo-400 text-xs font-black uppercase hover:underline transition-colors">View PDF</a>
           </div>
        </div>
      </div>

    </div>
  </div>

  <div v-else class="h-screen flex items-center justify-center">
     <div class="flex flex-col items-center gap-4">
        <i class="fa fa-circle-o-notch fa-spin text-indigo-600 text-2xl"></i>
        <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Loading Content...</p>
     </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotices } from '~/composables/academics/useNotices'

const config = useRuntimeConfig()

const route = useRoute()
const router = useRouter()

const { detail, fetchDetail } = useNotices()

onMounted(() => {
  fetchDetail(route.params.slug)
})

const getFileUrl = (filePath, isDownload = false) => {
  if (!filePath) return ''
  if (filePath.startsWith('http')) return filePath

  if (isDownload) {
    return `${config.public.apiBaseUrl}/api/method/frappe.utils.file_manager.download_file?file_url=${encodeURIComponent(filePath)}`
  }

  return `${config.public.apiBaseUrl}${filePath}`
}
</script>