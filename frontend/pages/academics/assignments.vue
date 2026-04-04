<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300 p-4 lg:p-8">
    <div class="max-w-6xl mx-auto space-y-8">
      
      <HeroHeader 
        title="Assignments" 
        subtitle="Track your progress and upcoming deadlines" 
        icon="fas fa-graduation-cap"
        class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm"
      >
        <div class="hidden md:flex flex-col items-end px-6 border-l border-slate-200 dark:border-slate-800">
          <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Completion</span>
          <div class="flex items-baseline gap-1">
            <span class="text-2xl font-black text-indigo-600 dark:text-indigo-400">{{ completionRate }}%</span>
            <span class="text-xs font-medium text-slate-400">weekly</span>
          </div>
        </div>
      </HeroHeader>

      <div class="flex items-center gap-2 overflow-x-auto no-scrollbar pb-2">
        <button v-for="tab in ['Active', 'Submitted', 'Overdue', 'Evaluated']"
          :key="tab"
          @click="activeTab = tab"
          :class="[
            activeTab === tab
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200 dark:shadow-none'
              : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-900',
            'px-5 py-2.5 rounded-2xl text-xs font-bold transition-all duration-200 flex items-center gap-3 whitespace-nowrap'
          ]">
          {{ tab }}
          <span :class="activeTab === tab ? 'bg-white/20' : 'bg-slate-100 dark:bg-slate-800'" 
                class="px-2 py-0.5 rounded-lg text-[10px]">
            {{ getTabCount(tab) }}
          </span>
        </button>
      </div>

      <div v-if="loading" class="grid gap-4">
        <div v-for="i in 3" :key="i" class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-col lg:flex-row lg:items-center gap-6 animate-pulse">
          <div class="flex items-center gap-5 lg:w-1/3">
            <div class="w-14 h-14 rounded-2xl bg-slate-200 dark:bg-slate-800"></div>
            <div class="space-y-2">
              <div class="h-2 w-16 bg-slate-200 dark:bg-slate-800 rounded"></div>
              <div class="h-4 w-40 bg-slate-200 dark:bg-slate-800 rounded"></div>
            </div>
          </div>
          <div class="flex-1 space-y-2">
            <div class="h-2 w-12 bg-slate-200 dark:bg-slate-800 rounded"></div>
            <div class="h-4 w-24 bg-slate-200 dark:bg-slate-800 rounded"></div>
          </div>
          <div class="flex gap-3">
            <div class="w-10 h-10 rounded-xl bg-slate-200 dark:bg-slate-800"></div>
            <div class="w-28 h-10 rounded-xl bg-slate-200 dark:bg-slate-800"></div>
          </div>
        </div>
      </div>

      <div v-else class="grid gap-4">
        <transition-group name="list">
          <div v-for="task in filteredAssignments"
            :key="task.name"
            class="group bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-col lg:flex-row lg:items-center gap-6 hover:shadow-xl hover:shadow-slate-200/50 dark:hover:shadow-none transition-all duration-300">

            <div class="flex items-center gap-5 lg:w-1/3">
              <div class="w-14 h-14 flex-shrink-0 flex items-center justify-center rounded-2xl bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
                <i class="fas fa-file-lines text-xl"></i>
              </div>
              <div>
                <p class="text-[10px] font-black text-indigo-500 uppercase tracking-widest mb-1">{{ task.course_name }}</p>
                <h3 @click="openDetails(task)"
                  class="text-base font-bold text-slate-800 dark:text-slate-100 cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors line-clamp-1">
                  {{ task.title }}
                </h3>
              </div>
            </div>

            <div class="flex-1 flex items-center">
              <div class="flex flex-col">
                <p class="text-[10px] text-slate-400 uppercase font-bold tracking-tighter">Deadline</p>
                <p :class="activeTab === 'Overdue' ? 'text-rose-500' : 'text-slate-600 dark:text-slate-300'" class="text-sm font-bold flex items-center gap-2">
                  <i class="far fa-clock opacity-50"></i>
                  {{ formatDate(task.due_date) }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3 ml-auto lg:ml-0">
              <a v-if="task.assignment_file"
                :href="safeUrl(task.assignment_file)"
                target="_blank"
                class="w-10 h-10 flex items-center justify-center rounded-xl border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                title="Download Resources">
                <i class="fas fa-cloud-arrow-down"></i>
              </a>

              <button v-if="task.status === 'Active'"
                @click.stop="handleSubmit(task)"
                class="px-6 py-2.5 bg-slate-900 dark:bg-indigo-600 hover:bg-indigo-600 dark:hover:bg-indigo-500 text-white text-sm font-bold rounded-xl transition-all shadow-md active:scale-95">
                Submit Task
              </button>

              <div v-else class="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs font-black uppercase tracking-tight">
                {{ task.status }}
              </div>
            </div>
          </div>
        </transition-group>

        <div v-if="filteredAssignments.length === 0" class="flex flex-col items-center justify-center py-24 bg-white dark:bg-slate-900 rounded-3xl border-2 border-dashed border-slate-200 dark:border-slate-800">
          <i class="fas fa-folder-open text-4xl text-slate-200 dark:text-slate-800 mb-4"></i>
          <p class="text-slate-500 dark:text-slate-400 font-bold tracking-tight">Nothing to show in {{ activeTab }}</p>
        </div>
      </div>
    </div>

    <AppModal v-model="showSubmitModal" title="Upload Submission">
      <div v-if="activeTask" class="p-2 space-y-6">
        <div class="bg-indigo-50 dark:bg-indigo-500/5 p-4 rounded-2xl border border-indigo-100 dark:border-indigo-500/10">
          <h3 class="font-bold text-slate-800 dark:text-white">{{ activeTask.title }}</h3>
          <p class="text-xs text-indigo-600 dark:text-indigo-400 font-medium">{{ activeTask.course_name }}</p>
        </div>

        <div class="relative group">
          <input type="file" @change="onFileChange" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" />
          <div class="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-8 text-center group-hover:border-indigo-400 dark:group-hover:border-indigo-600 transition-all bg-slate-50/50 dark:bg-slate-900/50">
            <i class="fas fa-cloud-upload text-3xl text-slate-300 mb-3 group-hover:text-indigo-500"></i>
            <p class="text-sm font-bold text-slate-600 dark:text-slate-300">
              {{ selectedFile ? selectedFile.name : 'Choose a file or drag it here' }}
            </p>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3 w-full">
          <button @click="showSubmitModal=false" class="flex-1 px-4 py-3 rounded-xl font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">Cancel</button>
          <button @click="performSubmit" :disabled="!selectedFile" class="flex-1 px-4 py-3 bg-indigo-600 disabled:opacity-30 text-white rounded-xl font-bold shadow-lg shadow-indigo-200 dark:shadow-none transition-all">
            Upload & Submit
          </button>
        </div>
      </template>
    </AppModal>

    <AppModal v-model="showDetailsModal" title="Task Overview" maxWidth="max-w-xl">
      <div v-if="selectedAssignment" class="space-y-6">
        <div class="flex flex-col gap-1">
          <span class="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em]">{{ selectedAssignment.course_name }}</span>
          <h2 class="text-2xl font-black text-slate-800 dark:text-white">{{ selectedAssignment.title }}</h2>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
            <p class="text-[10px] font-black text-slate-400 uppercase mb-1">Due Date</p>
            <p class="text-sm font-bold text-rose-500">{{ formatDate(selectedAssignment.due_date) }}</p>
          </div>
          <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
            <p class="text-[10px] font-black text-slate-400 uppercase mb-1">Current Status</p>
            <p class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ selectedAssignment.status }}</p>
          </div>
        </div>

        <div class="space-y-2">
          <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Instructions</p>
          <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            {{ selectedAssignment.description || 'No specific instructions provided.' }}
          </p>
        </div>
      </div>
      <template #footer>
        <button @click="showDetailsModal=false" class="w-full py-3 rounded-xl font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">Close</button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import AppModal from '~/components/ui/AppModal.vue'
import { useAssignments } from '~/composable/useAssignments'

const { assignments, loading, fetchAssignments, submitAssignment, uploadFile } = useAssignments()

const activeTab = ref('Active')
const showSubmitModal = ref(false)
const activeTask = ref(null)
const selectedFile = ref(null)
const showDetailsModal = ref(false)
const selectedAssignment = ref(null)

onMounted(() => fetchAssignments())

const filteredAssignments = computed(() => assignments.value.filter(a => a.status === activeTab.value))
const getTabCount = (tab) => assignments.value.filter(a => a.status === tab).length
const completionRate = computed(() => {
  const total = assignments.value.length
  const done = assignments.value.filter(a => ['Submitted', 'Evaluated'].includes(a.status)).length
  return total ? Math.round((done / total) * 100) : 0
})

const handleSubmit = (task) => { activeTask.value = task; showSubmitModal.value = true; }
const openDetails = (task) => { selectedAssignment.value = task; showDetailsModal.value = true; }
const onFileChange = (e) => { selectedFile.value = e.target.files[0]; }

const performSubmit = async () => {
  const uploaded = await uploadFile(selectedFile.value)
  await submitAssignment(activeTask.value.name, uploaded.file_url)
  showSubmitModal.value = false
  selectedFile.value = null
  fetchAssignments()
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
const safeUrl = (url) => url ? (url.startsWith('http') ? url : 'https://' + url) : '#'
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: scale(0.98); }
</style>