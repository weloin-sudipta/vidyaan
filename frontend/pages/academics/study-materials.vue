<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans text-slate-900 dark:text-slate-100 transition-colors">
    <div class="max-w-[1440px] mx-auto space-y-6">

      <HeroHeader
        title="Document Repository"
        subtitle="Download Syllabus, Notes & Previous Papers"
        icon="fa fa-file-text"
        searchable
        v-model:search="searchQuery"
        searchPlaceholder="Search by file name or subject..."
      />

      <!-- ── Filters Row ───────────────────────────────────────────── -->
      <div class="flex float-end flex-wrap gap-3 mt-2">

        <!-- Course Filter -->
        <select v-model="selectedCourse" class="filter-select">
          <option value="">All Courses</option>
          <option v-for="c in courses" :key="c" :value="c">
            {{ c }}
          </option>
        </select>

        <!-- Topic Filter -->
        <select v-model="selectedTopic" class="filter-select">
          <option value="">All Topics</option>
          <option v-for="t in topics" :key="t" :value="t">
            {{ t }}
          </option>
        </select>

      </div>

      <!-- ── Category Tabs ─────────────────────────────────────────── -->
      <div class="flex gap-3 overflow-x-auto no-scrollbar pb-2">
        <button
          v-for="cat in categories"
          :key="cat.name"
          @click="activeCategory = cat.name"
          :class="[
            activeCategory === cat.name
              ? 'bg-slate-900 dark:bg-indigo-600 text-white shadow-xl shadow-slate-200 dark:shadow-none'
              : 'bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800',
            'px-6 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest border transition-all flex items-center gap-3 whitespace-nowrap'
          ]"
        >
          <i :class="['fa', cat.icon]"></i>
          {{ cat.name }}
        </button>
      </div>

      <!-- ── Loading ───────────────────────────────────────────────── -->
      <div v-if="loading" class="grid grid-cols-1 gap-4 mt-6">
        <UiSkeleton height="h-24" v-for="i in 3" :key="i" />
      </div>

      <!-- ── Files ─────────────────────────────────────────────────── -->
      <div v-else class="grid grid-cols-1 gap-4 animate-in">
        <UiCard
          v-for="file in filteredFiles"
          :key="file.name"
          padding="p-5"
          rounded="rounded-[2rem]"
          class="group hover:border-indigo-300 dark:hover:border-indigo-600/50 transition-all flex flex-col md:flex-row items-center gap-6"
        >

          <div
            :class="['w-16 h-16 rounded-2xl flex items-center justify-center text-2xl shrink-0', getFileBgColor(file.file_type)]"
          >
            <i :class="['fa text-white', getFileIcon(file.file_type)]"></i>
          </div>

          <div class="flex-1 text-center md:text-left">
            <div class="flex flex-col md:flex-row md:items-center gap-2 mb-1">
              <h3 class="text-base font-black text-slate-800 dark:text-slate-200 tracking-tight">
                {{ file.title }}
              </h3>

              <span
                class="px-2 py-0.5 bg-slate-50 dark:bg-slate-800/50 text-slate-400 text-[9px] font-black uppercase rounded border border-slate-100 dark:border-slate-700/50"
              >
                {{ file.file_type || 'FILE' }}
              </span>
            </div>

            <div class="flex flex-wrap justify-center md:justify-start gap-4">
              <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">
                {{ file.course_name || file.course }}
              </span>

              <span v-if="file.topic_name" class="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">
                {{ file.topic_name }}
              </span>

              <span v-if="file.file_size" class="text-[10px] font-bold text-slate-300 uppercase tracking-widest">
                <i class="fa fa-database mr-1"></i> {{ file.file_size }}
              </span>

              <span v-if="file.upload_date" class="text-[10px] font-bold text-slate-300 uppercase tracking-widest">
                <i class="fa fa-calendar-o mr-1"></i> {{ formatDate(file.upload_date) }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-3 shrink-0">
            <a
              v-if="file.file"
              :href="getFileUrl(file.file)"
              target="_blank"
              class="w-12 h-12 flex items-center justify-center bg-slate-50 dark:bg-slate-800 rounded-xl hover:bg-slate-900 dark:hover:bg-slate-700 hover:text-white transition-all"
            >
              <i class="fa fa-eye"></i>
            </a>

            <a
              v-if="file.file"
              :href="getFileUrl(file.file, true)"
              class="px-6 py-3 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-700 transition-all"
            >
              <i class="fa fa-download mr-2"></i> Download
            </a>
          </div>

        </UiCard>

        <!-- Empty -->
        <UiCard
          v-if="filteredFiles.length === 0"
          padding="p-20"
          class="border-dashed text-center"
        >
          <i class="fa fa-folder-open-o text-slate-200 dark:text-slate-800 text-6xl mb-4"></i>
          <p class="text-sm font-black text-slate-400 uppercase tracking-widest">
            No documents found
          </p>
        </UiCard>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import { useStudyMaterials } from '~/composable/useStudyMaterials'

const config = useRuntimeConfig()

useSeoMeta({
  title: `Study Materials - ${config.public.appName}`,
})

const { materials, loading, fetchMaterials } = useStudyMaterials()

// ── State ─────────────────────────────────────────────
const activeCategory = ref('All Files')
const searchQuery = ref('')
const selectedCourse = ref('')
const selectedTopic = ref('')

// ── Categories ────────────────────────────────────────
const categories = [
  { name: 'All Files', icon: 'fa-th-large' },
  { name: 'Syllabus', icon: 'fa-map-o' },
  { name: 'Lecture Notes', icon: 'fa-file-text-o' },
  { name: 'Question Bank', icon: 'fa-bank' },
  { name: 'Lab Manuals', icon: 'fa-flask' }
]

// ── Dynamic Filters ───────────────────────────────────
const courses = computed(() =>
  [...new Set(materials.value.map(f => f.course_name || f.course).filter(Boolean))]
)

const topics = computed(() =>
  [...new Set(
    materials.value
      .filter(f => !selectedCourse.value || (f.course_name || f.course) === selectedCourse.value)
      .map(f => f.topic_name)
      .filter(Boolean)
  )]
)

// Reset topic when course changes
watch(selectedCourse, () => {
  selectedTopic.value = ''
})

// ── Filtered Files ────────────────────────────────────
const filteredFiles = computed(() => {
  return materials.value.filter(f => {
    const course = f.course_name || f.course

    const matchesCategory =
      activeCategory.value === 'All Files' || f.category === activeCategory.value

    const matchesCourse =
      !selectedCourse.value || course === selectedCourse.value

    const matchesTopic =
      !selectedTopic.value || f.topic_name === selectedTopic.value

    const matchesSearch =
      f.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (course || '').toLowerCase().includes(searchQuery.value.toLowerCase())

    return matchesCategory && matchesCourse && matchesTopic && matchesSearch
  })
})

// ── Helpers ───────────────────────────────────────────
onMounted(() => {
  fetchMaterials()
})

const getFileIcon = (type) => {
  const map = {
    PDF: 'fa-file-pdf-o',
    DOCX: 'fa-file-word-o',
    DOC: 'fa-file-word-o',
    ZIP: 'fa-file-archive-o',
    XLSX: 'fa-file-excel-o',
    PPT: 'fa-file-powerpoint-o',
    PPTX: 'fa-file-powerpoint-o'
  }
  return map[type] || 'fa-file-o'
}

const getFileBgColor = (type) => {
  const map = {
    PDF: 'bg-red-500',
    DOCX: 'bg-blue-500',
    DOC: 'bg-blue-500',
    ZIP: 'bg-amber-500',
    XLSX: 'bg-green-500',
    PPT: 'bg-orange-500',
    PPTX: 'bg-orange-500'
  }
  return map[type] || 'bg-slate-500'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const getFileUrl = (filePath, isDownload = false) => {
  if (!filePath) return ''

  if (filePath.startsWith('http')) return filePath

  if (isDownload) {
    return `${config.public.apiBaseUrl}/api/method/frappe.utils.file_manager.download_file?file_url=${encodeURIComponent(filePath)}`
  }

  return `${config.public.apiBaseUrl}${filePath}`
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.filter-select {
  @apply h-10 px-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 outline-none shadow-sm min-w-[180px];
}
</style>