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
            <span class="text-xs font-medium text-slate-400">overall</span>
          </div>
        </div>
      </HeroHeader>

      <div class="flex items-center gap-2 overflow-x-auto no-scrollbar pb-2">
        <button v-for="tab in ['Active', 'Submitted', 'Overdue', 'Graded']"
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
        <div v-for="i in 3" :key="i"
          class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 flex flex-col lg:flex-row lg:items-center gap-6 animate-pulse">
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

      <div v-else-if="error"
        class="bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800/40 rounded-2xl p-5 text-sm font-bold text-rose-600 dark:text-rose-400 flex items-center gap-3">
        <i class="fa fa-exclamation-circle"></i>
        {{ error }}
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
                <p :class="task.is_overdue ? 'text-rose-500' : 'text-slate-600 dark:text-slate-300'"
                  class="text-sm font-bold flex items-center gap-2">
                  <i class="far fa-clock opacity-50"></i>
                  {{ formatDate(task.due_date) }}
                </p>
              </div>
            </div>

            <!-- Graded score display -->
            <div v-if="task.my_submission?.status === 'Graded'" class="flex flex-col items-center">
              <p class="text-[10px] text-slate-400 uppercase font-bold tracking-tighter">Latest Score</p>
              <p class="text-sm font-black text-green-600 dark:text-green-400">
                {{ task.my_submission.score }} / {{ task.max_score }}
              </p>
              <p v-if="task.my_submissions && task.my_submissions.length > 1" class="text-[10px] text-slate-400 mt-1">
                {{ task.my_submissions.length }} submissions
              </p>
            </div>
            <div class="flex items-center gap-3 ml-auto lg:ml-0">
              <a v-if="task.assignment_file"
                :href="getFileUrl(task.assignment_file)"
                target="_blank"
                class="w-10 h-10 flex items-center justify-center rounded-xl border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                title="Download Resources">
                <i class="fas fa-cloud-arrow-down"></i>
              </a>

              <button v-if="resolvedStatus(task) === 'Active'"
                @click.stop="handleSubmit(task)"
                class="px-6 py-2.5 bg-slate-900 dark:bg-indigo-600 hover:bg-indigo-600 dark:hover:bg-indigo-500 text-white text-sm font-bold rounded-xl transition-all shadow-md active:scale-95">
                {{ task.my_submissions && task.my_submissions.length > 0 ? 'Submit Another' : 'Submit Task' }}
              </button>

              <div v-else
                class="px-4 py-2 rounded-xl text-xs font-black uppercase tracking-tight"
                :class="statusChipClass(resolvedStatus(task))">
                {{ resolvedStatus(task) }}
              </div>
            </div>
          </div>
        </transition-group>

        <div v-if="filteredAssignments.length === 0"
          class="flex flex-col items-center justify-center py-24 bg-white dark:bg-slate-900 rounded-3xl border-2 border-dashed border-slate-200 dark:border-slate-800">
          <i class="fas fa-folder-open text-4xl text-slate-200 dark:text-slate-800 mb-4"></i>
          <p class="text-slate-500 dark:text-slate-400 font-bold tracking-tight">Nothing to show in {{ activeTab }}</p>
          <p v-if="assignments.length === 0" class="text-xs text-slate-400 dark:text-slate-500 mt-2 max-w-sm text-center">
            If you expect to see an assignment, ask your teacher to publish it from the teacher portal.
          </p>
        </div>
      </div>
    </div>

    <!-- Submit Modal -->
    <AppModal v-model="showSubmitModal" :title="activeTask?.my_submissions?.length > 0 ? 'Submit Another Version' : 'Upload Submission'">
      <div v-if="activeTask" class="p-2 space-y-6">
        <div class="bg-indigo-50 dark:bg-indigo-500/5 p-4 rounded-2xl border border-indigo-100 dark:border-indigo-500/10">
          <h3 class="font-bold text-slate-800 dark:text-white">{{ activeTask.title }}</h3>
          <p class="text-xs text-indigo-600 dark:text-indigo-400 font-medium">{{ activeTask.course_name }}</p>
          <p v-if="activeTask.my_submissions && activeTask.my_submissions.length > 0" class="text-xs text-slate-500 dark:text-slate-400 mt-2">
            You have already submitted {{ activeTask.my_submissions.length }} version{{ activeTask.my_submissions.length > 1 ? 's' : '' }}
          </p>
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

        <div v-if="submitError"
          class="bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800/40 rounded-xl p-4 text-sm font-bold text-rose-600 dark:text-rose-400">
          {{ submitError }}
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3 w-full">
          <button @click="showSubmitModal = false"
            class="flex-1 px-4 py-3 rounded-xl font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">Cancel</button>
          <button @click="performSubmit" :disabled="!selectedFile || submitting"
            class="flex-1 px-4 py-3 bg-indigo-600 disabled:opacity-30 text-white rounded-xl font-bold shadow-lg shadow-indigo-200 dark:shadow-none transition-all flex items-center justify-center gap-2">
            <i v-if="submitting" class="fa fa-spinner fa-spin"></i>
            {{ submitting ? 'Uploading...' : 'Upload & Submit' }}
          </button>
        </div>
      </template>
    </AppModal>

    <!-- Details Modal -->
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
            <p class="text-[10px] font-black text-slate-400 uppercase mb-1">Status</p>
            <p class="text-sm font-bold text-slate-700 dark:text-slate-200">
              {{ resolvedStatus(selectedAssignment) }}
            </p>
          </div>
        </div>

        <!-- Submission result if graded -->
        <div v-if="selectedAssignment.my_submission?.status === 'Graded'"
          class="p-4 rounded-2xl bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800/40">
          <p class="text-[10px] font-black text-green-600 dark:text-green-400 uppercase mb-2">Latest Result</p>
          <p class="text-lg font-black text-green-700 dark:text-green-300">
            {{ selectedAssignment.my_submission.score }} / {{ selectedAssignment.max_score }} pts
          </p>
          <p v-if="selectedAssignment.my_submission.remarks" class="text-xs text-green-600 dark:text-green-400 mt-2 font-medium">
            {{ selectedAssignment.my_submission.remarks }}
          </p>
        </div>

        <!-- Submission History -->
        <div v-if="selectedAssignment.my_submissions && selectedAssignment.my_submissions.length > 0"
          class="space-y-3">
          <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Your Submissions ({{ selectedAssignment.my_submissions.length }})</p>
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div v-for="submission in selectedAssignment.my_submissions.slice().reverse()"
              :key="submission.id"
              class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div :class="[
                    'w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black',
                    submission.status === 'Graded' ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' :
                    submission.status === 'Submitted' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' :
                    'bg-slate-100 dark:bg-slate-800 text-slate-400'
                  ]">
                    <i v-if="submission.status === 'Graded'" class="fa fa-check-circle"></i>
                    <i v-else-if="submission.status === 'Submitted'" class="fa fa-clock-o"></i>
                    <i v-else class="fa fa-file-o"></i>
                  </div>
                  <div>
                    <p class="text-xs font-bold text-slate-700 dark:text-slate-200">
                      Submitted {{ formatDate(submission.submitted_on) }}
                    </p>
                    <p v-if="submission.status === 'Graded'" class="text-[10px] text-green-600 dark:text-green-400 font-medium">
                      Score: {{ submission.score }}/{{ selectedAssignment.max_score }} pts
                    </p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <a v-if="submission.submission_file" :href="getFileUrl(submission.submission_file)" target="_blank"
                    class="text-indigo-500 dark:text-indigo-400 hover:text-indigo-700 text-xs font-bold">
                    <i class="fa fa-file-text-o"></i> View
                  </a>
                  <span :class="[
                    'px-2 py-1 rounded text-[10px] font-black uppercase',
                    submission.status === 'Graded' ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' :
                    submission.status === 'Submitted' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' :
                    'bg-slate-100 dark:bg-slate-800 text-slate-400'
                  ]">
                    {{ submission.status }}
                  </span>
                </div>
              </div>
              <div v-if="submission.remarks" class="mt-2 p-2 rounded bg-white dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600">
                <p class="text-[10px] text-slate-600 dark:text-slate-300 font-medium">{{ submission.remarks }}</p>
              </div>
            </div>
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
        <button @click="showDetailsModal = false"
          class="w-full py-3 rounded-xl font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">Close</button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import AppModal from '~/components/ui/AppModal.vue'
import { useAssignments } from '~/composables/academics/useAssignments'

const config = useRuntimeConfig()

const { assignments, loading, error, fetchAssignments, submitAssignment, uploadFile } = useAssignments()

const activeTab = ref('Active')
const showSubmitModal = ref(false)
const activeTask = ref(null)
const selectedFile = ref(null)
const showDetailsModal = ref(false)
const selectedAssignment = ref(null)
const submitting = ref(false)
const submitError = ref(null)

onMounted(() => fetchAssignments())

// Derive a display status from the new shape
const resolvedStatus = (task) => {
  const submissionStatus = task.my_submission?.status
  if (submissionStatus) {
    if (submissionStatus === 'Pending') return 'Active'
    if (submissionStatus === 'Late') return 'Submitted'
    return submissionStatus
  }
  if (task.is_overdue) return 'Overdue'
  // Map API statuses to display tabs
  const apiStatus = task.status?.toLowerCase()
  if (apiStatus === 'published' || apiStatus === 'active') return 'Active'
  return task.status || 'Active'
}

const filteredAssignments = computed(() => {
  return assignments.value.filter(a => resolvedStatus(a) === activeTab.value)
})

const getTabCount = (tab) => assignments.value.filter(a => resolvedStatus(a) === tab).length

const completionRate = computed(() => {
  const total = assignments.value.length
  const done = assignments.value.filter(a => ['Submitted', 'Graded'].includes(resolvedStatus(a))).length
  return total ? Math.round((done / total) * 100) : 0
})

const handleSubmit = (task) => {
  // Navigate to details where submission is handled with full context
  navigateTo(`/academics/assignments/${task.name}`)
}

const openDetails = (task) => {
  navigateTo(`/academics/assignments/${task.name}`)
}

const onFileChange = (e) => { selectedFile.value = e.target.files[0] }

const performSubmit = async () => {
  if (!selectedFile.value) {
    submitError.value = 'Please choose a file before submitting.'
    return
  }
  submitting.value = true
  submitError.value = null
  try {
    const uploaded = await uploadFile(selectedFile.value)
    if (!uploaded || 'error' in uploaded) {
      submitError.value = (uploaded && 'error' in uploaded && uploaded.error) || 'Upload failed.'
      return
    }
    if (!uploaded.file_url) {
      submitError.value = 'Upload succeeded but no file URL was returned. Please retry.'
      return
    }
    const res = await submitAssignment(activeTask.value.name, uploaded.file_url)
    if (!res || 'error' in res) {
      submitError.value = (res && 'error' in res && res.error) || 'Submission failed.'
      return
    }
    showSubmitModal.value = false
    selectedFile.value = null
    await fetchAssignments()
  } catch (err) {
    submitError.value = err?.message || 'Unexpected error during submission.'
  } finally {
    submitting.value = false
  }
}

const statusChipClass = (status) => {
  switch (status) {
    case 'Submitted': return 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
    case 'Graded':    return 'bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400'
    case 'Overdue':   return 'bg-rose-100 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400'
    default:          return 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
  }
}

const formatDate = (d) => {
  if (!d) return '--'
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
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
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: scale(0.98); }
</style>
