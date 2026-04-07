<template>
  <div class="p-6 lg:p-10 max-w-7xl mx-auto custom-scrollbar animate-in fade-in slide-in-from-bottom-4 duration-500">
    <HeroHeader title="Attendance" subtitle="Daily Register" icon="fa fa-users">
      <div class="flex gap-2 items-center flex-wrap">
        <!-- Date picker -->
        <div class="relative">
          <i class="fa fa-calendar absolute left-3 top-1/2 -translate-y-1/2 text-emerald-400 text-xs pointer-events-none"></i>
          <input
            v-model="selectedDate"
            type="date"
            :max="maxDate"
            class="pl-8 pr-3 h-10 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
        <button
          v-if="selectedDate !== todayStr"
          @click="jumpToToday"
          class="h-10 px-4 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-black uppercase tracking-widest transition-colors"
        >
          Today
        </button>
        <select
          v-if="classes.length"
          v-model="selectedClassIndex"
          class="bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 px-4 h-10 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-800 outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <option v-for="(cls, index) in classes" :key="cls.name" :value="index">
            {{ cls.course_name || cls.course }} ({{ formatTime(cls.from_time) }} - {{ formatTime(cls.to_time) }})
          </option>
        </select>
        <button
          @click="saveAttendance"
          :disabled="saving || !selectedClass"
          class="h-10 bg-emerald-600 dark:bg-emerald-500 text-white px-6 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-emerald-700 dark:hover:bg-emerald-600 transition-colors shadow-lg shadow-emerald-200 dark:shadow-none disabled:opacity-50"
        >
          {{ saving ? 'Saving...' : 'Save Register' }}
        </button>
      </div>
    </HeroHeader>

    <div v-if="loading" class="mt-8">
      <UiSkeleton height="h-[600px]" class="rounded-[2.5rem]" />
    </div>

    <div
      v-else-if="!selectedClass"
      class="mt-8 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl p-10 text-center"
    >
      <i class="fa fa-calendar-times-o text-4xl text-slate-300 dark:text-slate-700 mb-3"></i>
      <p class="text-sm font-bold text-slate-500 dark:text-slate-400">
        No classes scheduled for {{ formatHumanDate(selectedDate) }}.
      </p>
      <button
        v-if="latestAvailableDate && latestAvailableDate !== selectedDate"
        @click="selectedDate = latestAvailableDate"
        class="mt-4 px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-colors"
      >
        View latest available ({{ formatHumanDate(latestAvailableDate) }})
      </button>
    </div>

    <div v-else class="mt-8 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm p-8">

      <!-- Class Info Bar -->
      <div class="flex flex-wrap gap-4 mb-6 text-xs font-bold text-slate-500 dark:text-slate-400">
        <span class="flex items-center gap-1"><i class="fa fa-book text-emerald-500"></i> {{ selectedClass.course }}</span>
        <span class="flex items-center gap-1"><i class="fa fa-clock-o text-emerald-500"></i> {{ formatTime(selectedClass.from_time) }} – {{ formatTime(selectedClass.to_time) }}</span>
        <span class="flex items-center gap-1"><i class="fa fa-map-marker text-emerald-500"></i> {{ selectedClass.room }}</span>
        <span class="flex items-center gap-1"><i class="fa fa-users text-emerald-500"></i> {{ selectedClass.total_students }} Students</span>
      </div>

      <!-- Quick Action Bar -->
      <div class="flex justify-between items-center mb-8 bg-emerald-50 dark:bg-emerald-900/10 p-4 rounded-2xl border border-emerald-100 dark:border-emerald-800/50">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-white dark:bg-slate-800 rounded-xl flex items-center justify-center shadow-sm">
            <i class="fa fa-info-circle text-emerald-500"></i>
          </div>
          <div>
            <h4 class="text-sm font-black text-slate-800 dark:text-slate-200">Mark all present by default?</h4>
            <p class="text-[10px] font-bold text-slate-500 dark:text-slate-400">Save time by only selecting absent students.</p>
          </div>
        </div>
        <button @click="markAll('Present')" class="px-6 py-2 bg-emerald-500 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-emerald-600 transition-colors">
          Mark All Present
        </button>
      </div>

      <!-- Students List -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="student in students"
          :key="student.id"
          class="p-4 rounded-2xl border transition-all cursor-pointer flex items-center justify-between"
          :class="
            student.status === 'Present'
              ? 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800'
              : student.status === 'Absent'
              ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
              : 'bg-slate-50 border-slate-100 dark:bg-slate-800/50 dark:border-slate-700'
          "
          @click="toggleStatus(student)"
        >
          <div class="flex items-center gap-3">
            <!-- Avatar -->
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center text-white text-sm font-black uppercase select-none"
              :style="{ backgroundColor: getAvatarColor(student.name) }"
            >
              {{ getInitials(student.name) }}
            </div>
            <div>
              <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ student.name }}</p>
              <p class="text-[10px] text-slate-400 dark:text-slate-500 font-bold tracking-widest">ID: {{ student.id }}</p>
            </div>
          </div>
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center transition-colors shadow-sm"
            :class="
              student.status === 'Present'
                ? 'bg-emerald-500 text-white'
                : student.status === 'Absent'
                ? 'bg-red-500 text-white'
                : 'bg-white dark:bg-slate-800 text-slate-300 dark:text-slate-600'
            "
          >
            <i
              class="fa text-xs"
              :class="
                student.status === 'Present'
                  ? 'fa-check'
                  : student.status === 'Absent'
                  ? 'fa-times'
                  : 'fa-minus'
              "
            ></i>
          </div>
        </div>
      </div>

      <!-- Summary Footer -->
      <div class="mt-8 flex gap-4 text-xs font-bold">
        <span class="px-4 py-2 bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 rounded-xl">
          Present: {{ presentCount }}
        </span>
        <span class="px-4 py-2 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-xl">
          Absent: {{ absentCount }}
        </span>
        <span class="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded-xl">
          Unmarked: {{ unmarkedCount }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import { useToast } from '~/composable/useToast'
import { useTeacherClasses } from '~/composable/useTeacherClasses'

const {
  fetchclassSchedule,
  saveAttendanceBulk,
  latestAvailableDate,
  todayISO,
} = useTeacherClasses()
const { addToast } = useToast()

const loading = ref(true)
const saving = ref(false)
const classes = ref([])
const selectedClassIndex = ref(0)
const students = ref([])

const todayStr = todayISO()
const selectedDate = ref(todayStr)
const maxDate = todayStr   // can't take attendance for the future

// Currently selected class
const selectedClass = computed(() => classes.value[selectedClassIndex.value] ?? null)

const formatHumanDate = (iso) => {
  if (!iso) return ''
  return new Date(iso + 'T00:00:00').toLocaleDateString('en-IN', {
    weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
  })
}

const jumpToToday = () => { selectedDate.value = todayStr }

// Counts
const presentCount = computed(() => students.value.filter(s => s.status === 'Present').length)
const absentCount = computed(() => students.value.filter(s => s.status === 'Absent').length)
const unmarkedCount = computed(() => students.value.filter(s => !s.status).length)

// Rebuild students list when class changes
watch(selectedClassIndex, () => loadStudents())

// Re-fetch when the date changes
watch(selectedDate, async (d) => {
  loading.value = true
  try {
    const data = await fetchclassSchedule(d)
    classes.value = data?.classes || []
    selectedClassIndex.value = 0
    loadStudents()
  } catch (e) {
    console.error(e)
    addToast('Error', 'Failed to load classes for that date.', 'error')
  } finally {
    loading.value = false
  }
})

function loadStudents() {
  if (!selectedClass.value) {
    students.value = []
    return
  }
  students.value = (selectedClass.value.students || []).map(s => ({
    id: s.student,
    name: s.student_name,
    status: s.status ? (s.status.charAt(0).toUpperCase() + s.status.slice(1).toLowerCase()) : null  // normalize to "Present" or "Absent"
  }))
}

// Get initials from full name e.g. "Edward Thomas" → "ET"
function getInitials(name) {
  if (!name) return '?'
  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0][0].toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

// Deterministic color per name
function getAvatarColor(name) {
  const colors = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899']
  let hash = 0
  for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

// Format "12:00:00" → "12:00 PM"
function formatTime(t) {
  if (!t) return ''
  const [h, m] = t.split(':').map(Number)
  const ampm = h >= 12 ? 'PM' : 'AM'
  const hour = h % 12 || 12
  return `${hour}:${String(m).padStart(2, '0')} ${ampm}`
}

// Toggle individual student status
function toggleStatus(student) {
  if (!student.status || student.status === 'Absent') student.status = 'Present'
  else student.status = 'Absent'
}

// Mark all students as Present or Absent
function markAll(status) {
  students.value.forEach(s => (s.status = status))
  addToast('Success', `All students marked as ${status}.`, 'success')
}

// Save attendance using bulk API
async function saveAttendance() {
  if (!selectedClass.value || students.value.length === 0) {
    addToast('Error', 'No students to mark attendance for.', 'error')
    return
  }

  // Auto-mark unmarked students as Present
  students.value.forEach(s => {
    if (!s.status) s.status = 'Present'
  })

  saving.value = true
  try {
    const res = await saveAttendanceBulk(selectedClass.value.name, students.value)

    if (res?.success?.length) {
      let message = `Attendance saved for ${res.success.length} student(s) on ${formatHumanDate(res.date || selectedDate.value)}.`
      if (res?.failed?.length) {
        message += ` ${res.failed.length} student(s) failed.`
        console.warn('Failed attendance:', res.failed)
      }
      addToast('Success', message, 'success')

      // Refetch the same date so badges update
      const data = await fetchclassSchedule(selectedDate.value)
      classes.value = data?.classes || []
      loadStudents()
    } else if (res?.failed?.length) {
      addToast('Error', `Failed to save attendance for ${res.failed.length} student(s).`, 'error')
    } else {
      addToast('Error', 'Attendance not saved.', 'error')
    }
  } catch (err) {
    console.error(err)
    addToast('Error', 'Failed to save attendance.', 'error')
  } finally {
    saving.value = false
  }
}

// Load classes on mount (today by default)
onMounted(async () => {
  try {
    const data = await fetchclassSchedule(selectedDate.value)
    classes.value = data?.classes || []
    loadStudents()
  } catch (e) {
    console.error(e)
    addToast('Error', 'Failed to load classes.', 'error')
  } finally {
    loading.value = false
  }
})
</script>