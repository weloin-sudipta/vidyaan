<template>
  <div class="p-6 lg:p-10 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">

    <!-- ── Header ──────────────────────────────────────────────────────────── -->
    <HeroHeader title="Mark Entry" subtitle="Speed Grader" icon="fa fa-calculator">
      <div class="flex flex-wrap gap-3 items-center">

        <!-- Exam selector -->
        <div class="relative">
          <i class="fa fa-file-text-o absolute left-3 top-1/2 -translate-y-1/2 text-indigo-400 text-xs pointer-events-none"></i>
          <select
            v-model="selectedExam"
            :disabled="loading"
            class="pl-9 pr-8 h-10 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-bold text-slate-700 dark:text-slate-200 outline-none shadow-sm appearance-none min-w-[220px] disabled:opacity-50"
          >
            <option value="">— Select Exam —</option>
            <option v-for="exam in exams" :key="exam.name" :value="exam.name">
              {{ exam.assessment_name }} · {{ exam.course }}
            </option>
          </select>
        </div>

        <!-- Save button -->
        <!-- <button
          @click="handleSave"
          :disabled="saving || !selectedExam || students.length === 0"
          class="h-10 px-6 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl text-xs font-black uppercase tracking-widest transition-colors shadow-lg shadow-emerald-100 dark:shadow-none flex items-center gap-2"
        >
          <i :class="saving ? 'fa fa-spinner fa-spin' : 'fa fa-save'"></i>
          {{ saving ? 'Saving…' : 'Save Marks' }}
        </button> -->

      </div>
    </HeroHeader>

    <!-- ── Exams loading ────────────────────────────────────────────────────── -->
    <div v-if="loading" class="mt-8 space-y-3">
      <div class="h-14 rounded-2xl bg-slate-100 dark:bg-slate-800 animate-pulse" />
      <div v-for="n in 5" :key="n"
        class="h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 animate-pulse"
        :style="`opacity:${1 - n * 0.15}`"
      />
    </div>

    <template v-else>

      <!-- ── No exam selected ───────────────────────────────────────────────── -->
      <div v-if="!selectedExam" class="mt-20 flex flex-col items-center gap-3 text-slate-400">
        <div class="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
          <i class="fa fa-mouse-pointer text-2xl"></i>
        </div>
        <p class="text-sm font-bold">Select an exam above to begin entering marks</p>
      </div>

      <div v-else-if="activePlan" class="mt-6 space-y-6">

        <!-- ── Plan Info Cards ─────────────────────────────────────────────── -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div
            v-for="info in planInfoCards"
            :key="info.label"
            class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl px-4 py-3 shadow-sm"
          >
            <span class="block text-[8px] font-black uppercase tracking-widest text-slate-400 mb-1">{{ info.label }}</span>
            <span class="text-xs font-black text-slate-700 dark:text-slate-200 truncate block">{{ info.value }}</span>
          </div>
        </div>

        <!-- ── Students loading ───────────────────────────────────────────── -->
        <div v-if="studentsLoading" class="space-y-3">
          <div v-for="n in 4" :key="n"
            class="h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 animate-pulse"
            :style="`opacity:${1 - n * 0.2}`"
          />
        </div>

        <template v-else>

          <!-- ── Grading error ───────────────────────────────────────────── -->
          <div
            v-if="gradingError"
            class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl px-5 py-4 text-sm font-bold text-red-600 dark:text-red-400 flex items-center gap-3"
          >
            <i class="fa fa-exclamation-triangle"></i> {{ gradingError }}
          </div>

          <!-- ── Toast ──────────────────────────────────────────────────── -->
          <Transition name="fade">
            <div
              v-if="toast.msg"
              :class="[
                'flex items-center gap-3 rounded-2xl px-5 py-3 text-sm font-bold border',
                toast.type === 'success'
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800/50 text-emerald-700 dark:text-emerald-400'
                  : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800/50 text-red-700 dark:text-red-400'
              ]"
            >
              <i :class="toast.type === 'success' ? 'fa fa-check-circle text-emerald-500' : 'fa fa-exclamation-circle text-red-500'"></i>
              {{ toast.msg }}
            </div>
          </Transition>

          <!-- ── Marks Table ─────────────────────────────────────────────── -->
          <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden">

            <!-- Table Head -->
            <div
              class="grid border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50"
              style="grid-template-columns: 2.5fr 1fr 1fr 2fr"
            >
              <div class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Student</div>
              <div class="px-4 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-center border-l border-slate-100 dark:border-slate-800">
                Score / {{ activePlan.maximum_assessment_score || 100 }}
              </div>
              <div class="px-4 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-center border-l border-slate-100 dark:border-slate-800">Grade</div>
              <div class="px-4 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 border-l border-slate-100 dark:border-slate-800">Remarks</div>
            </div>

            <!-- Table Rows -->
            <div
              v-for="(student, i) in students"
              :key="student.student"
              class="grid border-b border-slate-50 dark:border-slate-800/50 last:border-0 hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors"
              style="grid-template-columns: 2.5fr 1fr 1fr 2fr"
            >
              <!-- Student name + ID -->
              <div class="px-6 py-4 flex items-center gap-3">
                <div
                  class="w-9 h-9 rounded-xl flex items-center justify-center text-white text-xs font-black flex-shrink-0"
                  :class="avatarColor(i)"
                >
                  {{ initials(student.student_name) }}
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-black text-slate-800 dark:text-slate-100 truncate">{{ student.student_name }}</p>
                  <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest truncate">{{ student.student }}</p>
                </div>
                <!-- Already graded badge -->
                <span
                  v-if="student.result_id"
                  class="ml-auto flex-shrink-0 text-[8px] font-black uppercase tracking-widest bg-indigo-50 dark:bg-indigo-900/30 text-indigo-500 border border-indigo-100 dark:border-indigo-800 px-2 py-0.5 rounded-full"
                >Graded</span>
              </div>

              <!-- Score input -->
              <div class="px-4 py-4 flex items-center border-l border-slate-100 dark:border-slate-800">
                <div class="relative w-full">
                  <input
                    v-model.number="student.score"
                    type="number"
                    :min="0"
                    :max="activePlan.maximum_assessment_score || 100"
                    class="w-full bg-slate-100 dark:bg-slate-800 text-center text-sm font-black px-3 py-2.5 rounded-xl border-2 border-transparent focus:border-indigo-400 dark:focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 outline-none transition-all"
                    :class="scoreClass(student.score)"
                    placeholder="0"
                  />
                  <span
                    v-if="isFail(student.score)"
                    class="absolute -top-2 -right-1 bg-red-500 text-white text-[7px] font-black rounded-full px-1.5 py-0.5 uppercase leading-none"
                  >Fail</span>
                </div>
              </div>

              <!-- Grade (read-only from Frappe) -->
              <div class="px-4 py-4 flex items-center justify-center border-l border-slate-100 dark:border-slate-800">
                <span
                  v-if="student.grade"
                  class="text-sm font-black px-3 py-1 rounded-xl"
                  :class="gradeClass(student.grade)"
                >{{ student.grade }}</span>
                <span v-else class="text-xs font-bold text-slate-300 dark:text-slate-600">—</span>
              </div>

              <!-- Remarks input -->
              <div class="px-4 py-4 flex items-center border-l border-slate-100 dark:border-slate-800">
                <input
                  v-model="student.comment"
                  type="text"
                  class="w-full bg-slate-100 dark:bg-slate-800 text-xs font-bold text-slate-700 dark:text-slate-200 px-4 py-2.5 rounded-xl border-2 border-transparent focus:border-indigo-400 dark:focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 outline-none transition-all"
                  placeholder="Add remarks…"
                />
              </div>
            </div>

            <!-- Empty state -->
            <div v-if="students.length === 0" class="py-16 text-center text-slate-400">
              <i class="fa fa-users text-3xl mb-3 block"></i>
              <p class="text-sm font-bold">No students found for this exam</p>
            </div>

          </div>

          <!-- ── Bottom save bar ─────────────────────────────────────────── -->
          <div
            v-if="students.length > 0"
            class="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl px-6 py-4 shadow-sm"
          >
            <div class="flex items-center gap-6 text-xs font-bold text-slate-500">
              <span>
                <span class="text-indigo-600 dark:text-indigo-400 font-black text-base">{{ gradedCount }}</span>
                / {{ students.length }} marked
              </span>
              <span v-if="alreadySavedCount > 0" class="text-emerald-600 dark:text-emerald-400">
                <i class="fa fa-check-circle mr-1"></i>{{ alreadySavedCount }} already in Frappe
              </span>
            </div>
            <button
              @click="handleSave"
              :disabled="saving || students.length === 0"
              class="w-full sm:w-auto h-10 px-8 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-colors shadow-lg shadow-emerald-100 dark:shadow-none flex items-center justify-center gap-2"
            >
              <i :class="saving ? 'fa fa-spinner fa-spin' : 'fa fa-paper-plane'"></i>
              {{ saving ? 'Submitting…' : 'Submit All Results' }}
            </button>
          </div>

        </template>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import { useTeacherExams } from '~/composable/useTeacherExams'
import { useGrading }      from '~/composable/useGreading'   // ← your exact path

// ── Exam dropdown ───────────────────────────────────────────────────────────
const { exams, loading, fetchTeacherExams } = useTeacherExams()

// ── Grading composable ──────────────────────────────────────────────────────
const {
  plan: gradingPlan,
  students,
  loading: studentsLoading,
  saving,
  error: gradingError,
  fetchExamStudents,
  submitExamResults,
} = useGrading()

// ── Local state ─────────────────────────────────────────────────────────────
const selectedExam = ref('')
const toast = ref({ msg: '', type: 'success' })

// activePlan — prefer the detailed plan from grading API,
// fall back to the summary from exams list while students are loading
const activePlan = computed(() =>
  gradingPlan.value ?? exams.value.find(e => e.name === selectedExam.value) ?? null
)

// ── When exam changes → fetch students via grading composable ───────────────
watch(selectedExam, async (examName) => {
  if (!examName) return
  await fetchExamStudents(examName)
})

// ── Submit all results ──────────────────────────────────────────────────────
const handleSave = async () => {
  try {
    await submitExamResults(selectedExam.value)
    showToast('All results submitted to Frappe!', 'success')
  } catch {
    showToast('Failed to submit results. Please try again.', 'error')
  }
}

const showToast = (msg, type = 'success') => {
  toast.value = { msg, type }
  setTimeout(() => toast.value = { msg: '', type: 'success' }, 4000)
}

// ── Stats ────────────────────────────────────────────────────────────────────
const gradedCount = computed(() =>
  students.value.filter(s => s.score !== '' && s.score !== null && s.score !== undefined).length
)
const alreadySavedCount = computed(() =>
  students.value.filter(s => s.result_id).length
)

// ── Plan info cards ──────────────────────────────────────────────────────────
const planInfoCards = computed(() => {
  if (!activePlan.value) return []
  return [
    { label: 'Course',    value: activePlan.value.course },
    { label: 'Program',   value: activePlan.value.program },
    { label: 'Date',      value: formatDate(activePlan.value.schedule_date) },
    { label: 'Max Score', value: activePlan.value.maximum_assessment_score || 100 },
  ]
})

// ── Helpers ──────────────────────────────────────────────────────────────────
const avatarColors = [
  'bg-indigo-500','bg-violet-500','bg-blue-500',
  'bg-emerald-500','bg-rose-500','bg-amber-500','bg-cyan-500',
]
const avatarColor = (i) => avatarColors[i % avatarColors.length]

const initials = (name = '') =>
  name.trim().split(/\s+/).slice(0, 2).map(w => w[0]?.toUpperCase() ?? '').join('')

const maxScore = computed(() => activePlan.value?.maximum_assessment_score || 100)

const isFail = (score) =>
  score !== '' && score !== null && score !== undefined && Number(score) < maxScore.value * 0.4

const scoreClass = (score) => {
  if (score === '' || score === null || score === undefined) return ''
  if (Number(score) < maxScore.value * 0.4)   return 'text-red-500'
  if (Number(score) >= maxScore.value * 0.75) return 'text-emerald-600 dark:text-emerald-400'
  return ''
}

const gradeClass = (grade) => {
  if (!grade) return ''
  const g = grade.toUpperCase()
  if (['A+', 'A'].includes(g))  return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
  if (['B+', 'B'].includes(g))  return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
  if (['C+', 'C'].includes(g))  return 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
  if (['D', 'E'].includes(g))   return 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
  return 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
}

const formatDate = (d) =>
  d ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'

// ── Init ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await fetchTeacherExams()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>