<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 p-4 lg:p-8">
    <div class="max-w-7xl mx-auto">
      
      <!-- Back Link -->
      <NuxtLink to="/academics/assignments" class="inline-flex items-center gap-2 text-slate-500 hover:text-indigo-600 transition-colors mb-6 group">
        <i class="fas fa-arrow-left text-xs group-hover:-translate-x-1 transition-transform"></i>
        <span class="text-xs font-bold uppercase tracking-widest">Back to Assignments</span>
      </NuxtLink>

      <div v-if="loading && !assignment" class="flex justify-center py-20">
        <i class="fa fa-spinner fa-spin text-indigo-500 text-3xl"></i>
      </div>

      <div v-else-if="error && !assignment" class="bg-rose-50 dark:bg-rose-900/20 p-6 rounded-2xl border border-rose-200 dark:border-rose-800 text-rose-600 dark:text-rose-400 font-bold">
        {{ error }}
      </div>

      <div v-else-if="assignment" class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        <!-- Main Content -->
        <div class="xl:col-span-2 space-y-8">
          
          <!-- Assignment Info Card -->
          <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-200 dark:border-slate-800 p-8 lg:p-12 shadow-sm">
            <div class="space-y-6">
              <div class="flex flex-wrap items-center gap-3">
                <span class="px-4 py-1 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-full text-[10px] font-black uppercase tracking-widest border border-indigo-100 dark:border-indigo-800/50">
                  {{ assignment.course_name }}
                </span>
                <span v-if="assignment.my_student_status" :class="statusBadgeClass(assignment.my_student_status.status)" 
                      class="px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border">
                  {{ assignment.my_student_status.status }}
                </span>
              </div>

              <h1 class="text-4xl font-black text-slate-800 dark:text-white tracking-tight leading-tight">
                {{ assignment.title }}
              </h1>

              <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-slate-50 dark:bg-slate-800/40 p-4 rounded-2xl border border-white dark:border-slate-700/50 shadow-inner">
                  <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Due Date</p>
                  <p class="text-xs font-black text-slate-700 dark:text-slate-200">{{ formatDate(assignment.due_date) }}</p>
                </div>
                <div class="bg-slate-50 dark:bg-slate-800/40 p-4 rounded-2xl border border-white dark:border-slate-700/50 shadow-inner">
                  <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Max Score</p>
                  <p class="text-xs font-black text-slate-700 dark:text-slate-200">{{ assignment.max_score }} pts</p>
                </div>
                <div v-if="assignment.my_student_status?.status === 'Graded'" class="bg-green-50 dark:bg-green-900/20 p-4 rounded-2xl border border-green-100 dark:border-green-800/40 shadow-inner">
                  <p class="text-[10px] font-bold text-green-600 dark:text-green-400 uppercase tracking-widest mb-1">Your Grade</p>
                  <p class="text-xs font-black text-green-700 dark:text-green-300">{{ assignment.my_student_status.score }} / {{ assignment.max_score }}</p>
                </div>
              </div>

              <div class="prose dark:prose-invert max-w-none">
                <h4 class="text-xs font-black uppercase tracking-widest text-slate-400 mb-4 border-b pb-2">Instructions</h4>
                <div v-html="assignment.description || 'No specific instructions provided.'" class="text-slate-600 dark:text-slate-300 text-sm leading-relaxed"></div>
              </div>

              <div v-if="assignment.assignment_file" class="pt-4">
                <a :href="getFileUrl(assignment.assignment_file)" target="_blank"
                   class="inline-flex items-center gap-3 px-6 py-4 bg-slate-900 text-white rounded-2xl hover:bg-slate-800 transition-all shadow-lg active:scale-95">
                  <i class="fas fa-file-download"></i>
                  <span class="text-xs font-black uppercase tracking-widest">Download Master File</span>
                </a>
              </div>
            </div>
          </div>

          <!-- Submission Timeline -->
          <div class="space-y-4">
            <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 pl-4 flex items-center gap-2">
              <i class="fas fa-history text-indigo-500"></i>
              Submission History
            </h3>
            
            <div v-if="assignment.all_submissions && assignment.all_submissions.length === 0" 
                 class="bg-white dark:bg-slate-900 rounded-[2.5rem] border-2 border-dashed border-slate-200 dark:border-slate-800 p-12 text-center">
              <i class="fas fa-cloud-upload-alt text-4xl text-slate-200 dark:text-slate-800 mb-4"></i>
              <p class="text-sm font-bold text-slate-400">You haven't submitted anything yet.</p>
            </div>

            <div v-else class="space-y-4">
              <div v-for="(sub, index) in assignment.all_submissions" :key="sub.id" 
                   class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 flex items-center justify-between group hover:shadow-lg transition-all duration-300">
                <div class="flex items-center gap-6">
                  <div class="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-slate-400 group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/40 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                    <span class="text-xs font-black">v{{ assignment.all_submissions.length - index }}</span>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-slate-700 dark:text-slate-200">
                      Submitted on {{ formatDateTime(sub.submitted_on) }}
                    </p>
                    <div class="flex items-center gap-3 mt-1">
                      <span :class="statusBadgeClass(sub.status)" class="text-[10px] font-black uppercase px-2 py-0.5 rounded border">{{ sub.status }}</span>
                      <a v-if="sub.submission_file" :href="getFileUrl(sub.submission_file)" target="_blank" class="text-indigo-500 text-[10px] font-bold hover:underline">View Work</a>
                    </div>
                  </div>
                </div>

                <div v-if="sub.status === 'Graded'" class="text-right">
                  <p class="text-lg font-black text-green-600 dark:text-green-400">{{ sub.score }}</p>
                  <p class="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Points</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar (Messaging & Actions) -->
        <div class="space-y-8 flex flex-col h-[80vh]">
          
          <!-- Actions -->
          <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200 dark:border-slate-800 shadow-sm shrink-0">
            <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 mb-6 flex items-center gap-2">
              <i class="fas fa-bolt text-indigo-500"></i> Actions
            </h3>
            
            <div class="space-y-4">
              <button 
                @click="openSubmitModal"
                :disabled="assignment.my_student_status?.status === 'Graded' && !resubmissionRequested"
                class="w-full py-4 bg-indigo-600 text-white rounded-2xl font-black text-xs uppercase tracking-widest shadow-lg shadow-indigo-100 dark:shadow-none hover:bg-indigo-700 transition-all disabled:opacity-30 flex items-center justify-center gap-3 active:scale-95"
              >
                <i class="fas fa-paper-plane"></i>
                {{ assignment.all_submissions?.length > 0 ? 'Resubmit Version' : 'Submit Task' }}
              </button>
              
              <p v-if="resubmissionRequested" class="text-[10px] font-bold text-rose-500 text-center animate-pulse">
                Teacher has requested a resubmission
              </p>
            </div>
          </div>

          <!-- messaging -->
          <AssignmentChat 
            :messages="assignment.messages || []" 
            :sending="sendingComment"
            @send="postComment"
            @refresh="loadData"
            class="flex-1"
          />

        </div>
      </div>
    </div>

    <!-- Submit Modal -->
    <AppModal v-model="showSubmitModal" :title="assignment?.all_submissions?.length > 0 ? 'Submit Another Version' : 'Upload Submission'">
      <div v-if="assignment" class="p-2 space-y-6">
        <div class="bg-indigo-50 dark:bg-indigo-500/5 p-4 rounded-2xl border border-indigo-100 dark:border-indigo-500/10">
          <h3 class="font-bold text-slate-800 dark:text-white">{{ assignment.title }}</h3>
          <p v-if="assignment.all_submissions && assignment.all_submissions.length > 0" class="text-xs text-slate-500 dark:text-slate-400 mt-2">
            This will be version {{ assignment.all_submissions.length + 1 }}
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
      </div>
      <template #footer>
        <div class="flex gap-3 w-full">
          <button @click="showSubmitModal = false" class="flex-1 px-4 py-3 rounded-xl font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">Cancel</button>
          <button @click="performSubmit" :disabled="!selectedFile || submitting" 
                  class="flex-1 px-4 py-3 bg-indigo-600 disabled:opacity-30 text-white rounded-xl font-bold shadow-lg shadow-indigo-200 dark:shadow-none transition-all flex items-center justify-center gap-2 active:scale-95">
            <i v-if="submitting" class="fa fa-spinner fa-spin"></i>
            {{ submitting ? 'Uploading...' : 'Submit Version' }}
          </button>
        </div>
      </template>
    </AppModal>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'nuxt/app'
import { useAssignments } from '~/composables/academics/useAssignments'
import AssignmentChat from '~/components/academics/AssignmentChat.vue'
import AppModal from '~/components/ui/AppModal.vue'
import { useToast } from '~/composables/ui/useToast'

const route = useRoute()
const assignmentId = route.params.id as string
const { addToast } = useToast()

const { fetchAssignmentDetail, addComment, submitAssignment, uploadFile, loading, error } = useAssignments()

const assignment = ref<any>(null)
const sendingComment = ref(false)
const showSubmitModal = ref(false)
const selectedFile = ref<File | null>(null)
const submitting = ref(false)

const loadData = async () => {
  const res = await fetchAssignmentDetail(assignmentId)
  if (res) assignment.value = res
}

onMounted(() => loadData())

const resubmissionRequested = computed(() => {
  if (!assignment.value?.messages) return false
  // Check for the specific keyword in teacher comments
  return assignment.value.messages.some((m: any) => 
    !m.is_me && m.content.toLowerCase().includes('resubmit')
  )
})

const postComment = async (content: string) => {
  if (!content.trim()) return
  sendingComment.value = true
  try {
    const res = await addComment(assignmentId, content)
    if (res?.success) {
      if (!assignment.value.messages) assignment.value.messages = []
      assignment.value.messages.push(res.comment)
    }
  } finally {
    sendingComment.value = false
  }
}

const openSubmitModal = () => {
  selectedFile.value = null
  showSubmitModal.value = true
}

const onFileChange = (e: any) => {
  selectedFile.value = e.target.files[0]
}

const performSubmit = async () => {
  if (!selectedFile.value) return
  submitting.value = true
  try {
    const uploaded = await uploadFile(selectedFile.value)
    if (uploaded && 'file_url' in uploaded) {
      const res = await submitAssignment(assignmentId, uploaded.file_url)
      if (res && !('error' in res)) {
        addToast('Assignment submitted successfully', 'success')
        showSubmitModal.value = false
        await loadData()
      } else if (res && 'error' in res) {
        addToast(res.error, 'error')
      }
    }
  } finally {
    submitting.value = false
  }
}

const statusBadgeClass = (status: string) => {
  switch (status) {
    case 'Graded': return 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 border-green-200 dark:border-green-800/50'
    case 'Submitted': return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800/50'
    case 'Late': return 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-800/50'
    default: return 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700'
  }
}

const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '--'
const formatDateTime = (d: string) => d ? new Date(d).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '--'

const getFileUrl = (path: string) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const config = useRuntimeConfig()
  return `${config.public.apiBaseUrl}${path}`
}
</script>
