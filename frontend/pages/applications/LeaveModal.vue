<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>

    <div class="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-[2rem] shadow-2xl dark:shadow-none border border-slate-200 dark:border-slate-800 overflow-hidden transition-colors">

      <div class="p-6 border-b border-slate-100 dark:border-slate-800 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-black text-slate-800 dark:text-slate-100 transition-colors">Leave Application</h2>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Apply for leave of absence</p>
          </div>
          <button @click="$emit('close')" class="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <i class="fa fa-times"></i>
          </button>
        </div>
      </div>

      <div class="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">From Date *</label>
            <input v-model="form.from_date" type="date"
              class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors" />
          </div>
          <div>
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">To Date *</label>
            <input v-model="form.to_date" type="date"
              class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors" />
          </div>
        </div>

        <div v-if="leaveDays > 0" class="flex items-center gap-2 px-4 py-2.5 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl transition-colors">
          <i class="fa fa-calendar text-indigo-500"></i>
          <span class="text-xs font-black text-indigo-600 dark:text-indigo-400 transition-colors">{{ leaveDays }} day{{ leaveDays > 1 ? 's' : '' }} of leave</span>
        </div>

        <div>
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Attendance Based On *</label>
          <select v-model="form.attendance_based_on" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors">
            <option value="Student Group">Student Group</option>
            <option value="Course Schedule">Course Schedule</option>
          </select>
        </div>

        <div v-if="form.attendance_based_on === 'Student Group'">
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Student Group *</label>
          <select v-model="form.student_group" @change="onStudentGroupChange"
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors">
            <option value="" disabled>Select your student group...</option>
            <option v-for="group in leaveOptions.student_groups" :key="group.value" :value="group.value">{{ group.label }}</option>
          </select>
          <p v-if="form.student_group" class="text-xs text-indigo-600 dark:text-indigo-400 mt-2">
            Applying for leave from: <strong>{{ form.student_group }}</strong>
          </p>
        </div>

        <div v-if="form.attendance_based_on === 'Course Schedule'">
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Course Schedule *</label>
          <select v-model="form.course_schedule"
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors">
            <option value="" disabled>
              {{ loadingSchedules ? 'Loading schedules...' : 'Select a course schedule...' }}
            </option>
            <option v-for="schedule in filteredCourseSchedules" :key="schedule.value" :value="schedule.value">
              {{ schedule.label }}
            </option>
          </select>
          <p v-if="form.from_date && form.to_date && !loadingSchedules && filteredCourseSchedules.length === 0" class="text-xs text-amber-600 dark:text-amber-400 mt-2">
            No course schedules found in the selected date range
          </p>
        </div>

        <div>
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Reason</label>
          <textarea v-model="form.reason" rows="3" placeholder="Reason for leave..."
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 resize-none transition-colors"></textarea>
        </div>
      </div>

      <div class="p-6 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3 transition-colors">
        <button @click="$emit('close')"
          class="px-6 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-black uppercase tracking-wider hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
          Cancel
        </button>
        <button @click="submit" :disabled="submitting || !isValid"
          class="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-xs font-black uppercase tracking-wider hover:bg-blue-700 transition-all disabled:opacity-50">
          {{ submitting ? 'Submitting...' : 'Submit Leave' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { call } from '~/composables/api/useFrappeFetch'
import { useToast } from '~/composables/ui/useToast'

const emit = defineEmits(['close', 'submitted'])
const { addToast } = useToast()
const submitting = ref(false)
const loadingSchedules = ref(false)

const leaveOptions = ref({ student_groups: [], course_schedules: [] })
const filteredCourseSchedules = ref([])

const form = ref({ 
  from_date: '', 
  to_date: '', 
  reason: '',
  attendance_based_on: 'Student Group',
  student_group: '',
  course_schedule: ''
})

onMounted(async () => {
  try {
    const res = await call('vidyaan.api_folder.applications.get_leave_options')
    if (res) leaveOptions.value = res
    // Auto-select first group if only one available
    if (res && res.student_groups && res.student_groups.length === 1) {
      form.value.student_group = res.student_groups[0].value
    }
  } catch (err) {
    console.error('Failed to load leave options', err)
  }
})

// Watch for date changes to filter course schedules
watch(
  () => ({ from_date: form.value.from_date, to_date: form.value.to_date }),
  async () => {
    if (form.value.attendance_based_on === 'Course Schedule' && form.value.from_date && form.value.to_date) {
      await loadFilteredSchedules()
    }
  }
)

// Handle student group selection - just for UI feedback
const onStudentGroupChange = () => {
  // Clear course schedule selection if group changes
  form.value.course_schedule = ''
  filteredCourseSchedules.value = []
  
  // If switching to Course Schedule, reload filtered schedules
  if (form.value.attendance_based_on === 'Course Schedule' && form.value.from_date && form.value.to_date && form.value.student_group) {
    loadFilteredSchedules()
  }
}

// Load course schedules filtered by date range
const loadFilteredSchedules = async () => {
  if (!form.value.student_group || !form.value.from_date || !form.value.to_date) {
    filteredCourseSchedules.value = []
    return
  }
  
  loadingSchedules.value = true
  try {
    const res = await call('vidyaan.api_folder.applications.get_filtered_course_schedules', {
      student_group: form.value.student_group,
      from_date: form.value.from_date,
      to_date: form.value.to_date
    })
    if (res) filteredCourseSchedules.value = res
  } catch (err) {
    console.error('Failed to load filtered schedules', err)
  } finally {
    loadingSchedules.value = false
  }
}

const isValid = computed(() => {
  if (!form.value.from_date || !form.value.to_date || form.value.from_date > form.value.to_date) return false
  if (form.value.attendance_based_on === 'Course Schedule' && !form.value.course_schedule) return false
  if (form.value.attendance_based_on === 'Student Group' && leaveOptions.value.student_groups.length && !form.value.student_group) return false
  return true
})

const leaveDays = computed(() => {
  if (!form.value.from_date || !form.value.to_date) return 0
  const diff = (new Date(form.value.to_date) - new Date(form.value.from_date)) / (1000 * 60 * 60 * 24) + 1
  return Math.max(0, Math.round(diff))
})

const submit = async () => {
  submitting.value = true
  try {
    await call('vidyaan.api_folder.applications.submit_leave', {
      from_date: form.value.from_date,
      to_date: form.value.to_date,
      reason: form.value.reason || undefined,
      attendance_based_on: form.value.attendance_based_on,
      student_group: form.value.attendance_based_on === 'Student Group' ? (form.value.student_group || undefined) : undefined,
      course_schedule: form.value.attendance_based_on === 'Course Schedule' ? (form.value.course_schedule || undefined) : undefined
    })
    addToast('Leave application submitted!', 'success')
    emit('submitted')
  } catch (err) {
    let msg = 'Failed to submit leave.'
    if (err?.data?._server_messages) {
      try { msg = JSON.parse(JSON.parse(err.data._server_messages)[0]).message } catch {}
    }
    addToast(msg, 'error')
  } finally { submitting.value = false }
}
</script>
