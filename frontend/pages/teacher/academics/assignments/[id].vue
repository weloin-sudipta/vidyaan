<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 p-4 lg:p-8">
    <div class="max-w-7xl mx-auto">
      
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 bg-white dark:bg-slate-900 p-8 rounded-[2.5rem] border border-slate-200 dark:border-slate-800 shadow-sm">
        <div class="space-y-2">
          <NuxtLink to="/teacher/academics/assignments" class="inline-flex items-center gap-2 text-slate-500 hover:text-indigo-600 transition-colors mb-2 group">
            <i class="fas fa-arrow-left text-[10px] group-hover:-translate-x-1 transition-transform"></i>
            <span class="text-[10px] font-black uppercase tracking-widest">Back to Hub</span>
          </NuxtLink>
          <div class="flex items-center gap-3">
            <h1 class="text-3xl font-black text-slate-800 dark:text-white">{{ assignment?.title || 'Loading...' }}</h1>
            <span v-if="assignment" :class="statusBadgeClass(assignment.status)" class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border">
              {{ assignment.status }}
            </span>
          </div>
          <p v-if="assignment" class="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
            <i class="fas fa-graduation-cap text-indigo-500"></i> {{ assignment.course_name }}
          </p>
        </div>

        <div v-if="assignment" class="flex gap-4">
          <div class="text-center px-6 py-3 bg-slate-50 dark:bg-slate-800 rounded-2xl border border-white dark:border-slate-700 shadow-inner">
            <p class="text-[9px] font-black text-slate-400 uppercase tracking-tighter mb-1">Submissions</p>
            <p class="text-xl font-black text-indigo-600 dark:text-indigo-400">{{ assignment.submission_count || 0 }}</p>
          </div>
          <div class="text-center px-6 py-3 bg-slate-50 dark:bg-slate-800 rounded-2xl border border-white dark:border-slate-700 shadow-inner">
            <p class="text-[9px] font-black text-slate-400 uppercase tracking-tighter mb-1">Graded</p>
            <p class="text-xl font-black text-green-600 dark:text-green-400">{{ assignment.graded_count || 0 }}</p>
          </div>
        </div>
      </div>

      <div v-if="loading && !assignment" class="flex justify-center py-20">
        <i class="fa fa-spinner fa-spin text-indigo-500 text-3xl"></i>
      </div>

      <div v-else-if="assignment" class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Students List Sidebar -->
        <div class="lg:col-span-3 space-y-4">
          <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 pl-4">Students</h3>
          <div class="space-y-2 max-h-[70vh] overflow-y-auto pr-2 no-scrollbar">
            <button 
              v-for="sub in sortedSubmissions" 
              :key="sub.student"
              @click="selectStudent(sub)"
              :class="[
                'w-full text-left p-4 rounded-3xl border transition-all duration-300 flex items-center gap-3',
                selectedStudent?.student === sub.student 
                  ? 'bg-indigo-600 border-indigo-600 text-white shadow-lg shadow-indigo-100 dark:shadow-none' 
                  : 'bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:border-indigo-300 dark:hover:border-indigo-700'
              ]"
            >
              <div :class="['w-10 h-10 rounded-xl flex items-center justify-center font-black text-xs shrink-0', selectedStudent?.student === sub.student ? 'bg-white/20 text-white' : 'bg-slate-100 dark:bg-slate-800 text-indigo-500']">
                {{ sub.student_name?.charAt(0) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-black truncate">{{ sub.student_name }}</p>
                <p :class="['text-[9px] font-bold uppercase tracking-tighter opacity-70', selectedStudent?.student === sub.student ? 'text-white' : 'text-slate-400']">
                  {{ sub.status || 'Pending' }}
                </p>
              </div>
              <div v-if="sub.status === 'Graded'" class="shrink-0">
                <i class="fas fa-check-circle text-[10px]"></i>
              </div>
              <div v-else-if="sub.status === 'Submitted'" class="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></div>
            </button>
          </div>
        </div>

        <!-- Detail & Chat -->
        <div class="lg:col-span-9 space-y-6">
          <div v-if="!selectedStudent" class="h-full flex flex-col items-center justify-center py-32 bg-white dark:bg-slate-900 rounded-[3.5rem] border border-slate-200 dark:border-slate-800 text-slate-400">
            <i class="fas fa-user-graduate text-5xl mb-6 opacity-20"></i>
            <p class="text-sm font-bold uppercase tracking-widest">Select a student to view work</p>
          </div>

          <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-6">
            
            <!-- Student Submissions -->
            <div class="space-y-6">
              <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200 dark:border-slate-800 shadow-sm">
                <div class="flex items-center justify-between mb-8">
                  <div class="flex items-center gap-4">
                    <UiAvatar :name="selectedStudent.student_name" size="lg" />
                    <div>
                      <h2 class="text-xl font-black text-slate-800 dark:text-white">{{ selectedStudent.student_name }}</h2>
                      <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ selectedStudent.student }}</p>
                    </div>
                  </div>
                  <div class="text-right">
                    <button @click="openGradingModal" class="px-6 py-2.5 bg-green-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-green-700 transition-all shadow-md active:scale-95">
                      {{ selectedStudent.status === 'Graded' ? 'Update Grade' : 'Grade Now' }}
                    </button>
                  </div>
                </div>

                <div class="space-y-4">
                  <h4 class="text-[10px] font-black uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    <i class="fas fa-layer-group text-indigo-500"></i>
                    Attempts ({{ filteredStudentSubmissions.length }})
                  </h4>
                  
                  <div v-if="filteredStudentSubmissions.length === 0" class="py-10 text-center opacity-40">
                    <p class="text-xs font-bold uppercase">No submissions recorded</p>
                  </div>

                  <div v-else class="space-y-3">
                    <div v-for="(sub, idx) in filteredStudentSubmissions" :key="sub.id" 
                         class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-white dark:border-slate-700 shadow-inner group transition-all">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                          <div class="w-8 h-8 rounded-lg bg-white dark:bg-slate-700 flex items-center justify-center text-[10px] font-black text-slate-400">
                            v{{ filteredStudentSubmissions.length - idx }}
                          </div>
                          <div>
                            <p class="text-xs font-bold text-slate-700 dark:text-slate-200">{{ formatDateTime(sub.submitted_on) }}</p>
                            <a v-if="sub.submission_file" :href="getFileUrl(sub.submission_file)" target="_blank" class="text-[10px] font-black text-indigo-600 dark:text-indigo-400 hover:underline">
                              <i class="fas fa-file-pdf mr-1"></i> View Submission
                            </a>
                          </div>
                        </div>
                        <div v-if="sub.score !== null" class="text-right">
                          <p class="text-sm font-black text-green-600">{{ sub.score }} <span class="text-[9px] text-slate-400 font-bold uppercase ml-1">pts</span></p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Quick Feedback Actions -->
              <div class="bg-indigo-600 rounded-[2.5rem] p-8 text-white shadow-xl shadow-indigo-200 dark:shadow-none">
                <h3 class="text-[10px] font-black uppercase tracking-widest mb-4 opacity-80">Feedback Actions</h3>
                <div class="grid grid-cols-1 gap-3">
                  <button @click="handleResubmissionRequest" class="w-full py-3 bg-white/10 hover:bg-white/20 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border border-white/20">
                    <i class="fas fa-redo mr-2"></i> Request Resubmission
                  </button>
                </div>
              </div>
            </div>

            <!-- Chat / Communication -->
            <div class="h-full min-h-[500px] flex flex-col relative">
              <div v-if="chatLoading" class="absolute inset-0 bg-white/60 dark:bg-slate-900/60 z-10 flex items-center justify-center backdrop-blur-[2px] rounded-3xl">
                <i class="fa fa-spinner fa-spin text-indigo-500 text-2xl"></i>
              </div>
              <AssignmentChat 
                :messages="assignment.messages || []" 
                :sending="sendingComment"
                @send="postComment"
                @refresh="loadData(selectedStudent.student)"
                class="flex-1"
              />
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Grading Modal -->
    <AppModal v-model="showGradeModal" title="Grade Work">
      <div v-if="selectedStudent" class="space-y-6 p-2">
        <div class="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-2xl border border-white dark:border-slate-700 shadow-inner">
          <div class="flex items-center gap-4 mb-4">
            <UiAvatar :name="selectedStudent.student_name" size="md" />
            <div>
              <p class="text-xs font-black text-slate-700 dark:text-white">{{ selectedStudent.student_name }}</p>
              <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                Grading Latest Version (v{{ filteredStudentSubmissions.length }})
              </p>
            </div>
          </div>
          
          <div class="space-y-2">
            <label class="text-[10px] font-black uppercase tracking-widest text-slate-400">Score (0-{{ assignment?.max_score }})</label>
            <div class="flex items-center gap-4">
              <input v-model.number="gradeForm.score" type="number" :max="assignment?.max_score" min="0" 
                     class="flex-1 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-xl font-black text-indigo-600 outline-none focus:ring-2 focus:ring-indigo-500 transition-all dark:text-white" />
              <span class="text-xl font-black text-slate-300">/ {{ assignment?.max_score }}</span>
            </div>
          </div>

          <div class="mt-4 space-y-2">
            <label class="text-[10px] font-black uppercase tracking-widest text-slate-400">Feedback Remarks</label>
            <textarea v-model="gradeForm.remarks" rows="3" 
                      class="w-full bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 outline-none transition-all resize-none dark:text-white"
                      placeholder="Great job on the research section..."></textarea>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3 w-full">
          <button @click="showGradeModal = false" class="flex-1 px-4 py-3 rounded-xl font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800">Cancel</button>
          <button @click="submitGrade" :disabled="grading" 
                  class="flex-1 px-4 py-3 bg-green-600 text-white rounded-xl font-bold shadow-lg shadow-green-100 dark:shadow-none transition-all flex items-center justify-center gap-2 active:scale-95">
            <i v-if="grading" class="fa fa-spinner fa-spin"></i>
            Submit Grade
          </button>
        </div>
      </template>
    </AppModal>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'nuxt/app'
import { useTeacherAssignments } from '~/composables/teacher/useTeacherAssignments'
import AssignmentChat from '~/components/academics/AssignmentChat.vue'
import AppModal from '~/components/ui/AppModal.vue'
import UiAvatar from '~/components/ui/UiAvatar.vue'
import { useToast } from '~/composables/ui/useToast'
import { useConfirm } from '~/composables/ui/useConfirm'

const route = useRoute()
const assignmentId = route.params.id as string
const { addToast } = useToast()
const { confirm } = useConfirm()

const { 
  fetchAssignmentDetail, 
  gradeSubmission, 
  addComment, 
  requestResubmission,
  loading, 
  currentAssignment: assignment 
} = useTeacherAssignments()

const selectedStudent = ref<any>(null)
const sendingComment = ref(false)
const chatLoading = ref(false)
const showGradeModal = ref(false)
const grading = ref(false)
const gradeForm = ref({ score: 0, remarks: '' })

const loadData = async (studentId: string | null = null) => {
  if (studentId) {
    chatLoading.value = true
    // Clear potentially stale messages/submissions for the new context
    if (assignment.value) {
      assignment.value.messages = []
      assignment.value.all_submissions = []
    }
  }
  await fetchAssignmentDetail(assignmentId, studentId)
  chatLoading.value = false
}

onMounted(() => {
  loadData()
})

// Overall submissions for the side list
const sortedSubmissions = computed(() => {
  if (!assignment.value?.submissions) return []
  return [...assignment.value.submissions].sort((a, b) => {
    // Sort logic: 'Submitted' first, then alphabetical by name
    if (a.status === 'Submitted' && b.status !== 'Submitted') return -1
    if (a.status !== 'Submitted' && b.status === 'Submitted') return 1
    return (a.student_name || '').localeCompare(b.student_name || '')
  })
})

// Specific version submissions for the selected student
const filteredStudentSubmissions = computed(() => {
  if (!assignment.value?.all_submissions || !selectedStudent.value) return []
  return assignment.value.all_submissions.filter((s: any) => s.student === selectedStudent.value.student)
})

const selectStudent = async (sub: any) => {
  selectedStudent.value = sub
  await loadData(sub.student)
  // Initialize grade form with latest submission's score if available
  const latest = filteredStudentSubmissions.value[0]
  gradeForm.value = { 
    score: latest?.score || Number(sub.score) || 0, 
    remarks: latest?.remarks || sub.remarks || '' 
  }
}

const postComment = async (content: string) => {
  if (!selectedStudent.value) return
  sendingComment.value = true
  try {
    const res = await addComment(assignmentId, content, selectedStudent.value.student)
    if (res?.success) {
      if (!assignment.value.messages) assignment.value.messages = []
      assignment.value.messages.push(res.comment)
    }
  } finally {
    sendingComment.value = false
  }
}

const openGradingModal = () => {
  showGradeModal.value = true
}

const submitGrade = async () => {
  if (!selectedStudent.value) return
  grading.value = true
  try {
    // We fetch the latest submission id for this student to grade it
    const latestSub = filteredStudentSubmissions.value[0]
    if (!latestSub) {
      addToast('No submission record found to grade.', 'error')
      return
    }

    const res = await gradeSubmission(
      latestSub.id, 
      gradeForm.value.score, 
      gradeForm.value.remarks
    )
    if (res && !('error' in res)) {
      addToast('Grade saved/updated', 'success')
      showGradeModal.value = false
      await loadData(selectedStudent.value.student)
    } else if (res && 'error' in res) {
      addToast(res.error, 'error')
    }
  } finally {
    grading.value = false
  }
}

const handleResubmissionRequest = async () => {
  if (!selectedStudent.value) return
  const ok = await confirm({
    title: 'Request Resubmission',
    message: `Ask ${selectedStudent.value.student_name} to resubmit? This will post a special comment in the discussion.`,
    variant: 'warning',
    confirmText: 'Yes, Request'
  })
  if (!ok) return

  const res = await requestResubmission(assignmentId, selectedStudent.value.student, 'Please refine your work and resubmit.')
  if (res && !('error' in res)) {
    addToast('Resubmission request sent', 'info')
    await loadData(selectedStudent.value.student)
  }
}

const statusBadgeClass = (status: string) => {
  switch (status) {
    case 'Published': return 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-800/50'
    case 'Closed':    return 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700'
    case 'Graded':    return 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 border-green-200'
    default:          return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border-blue-200'
  }
}

const formatDateTime = (d: string) => d ? new Date(d).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '--'

const getFileUrl = (path: string) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const config = useRuntimeConfig()
  return `${config.public.apiBaseUrl}${path}`
}
</script>
