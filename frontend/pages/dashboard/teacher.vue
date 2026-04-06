<template>
  <main class="flex-1 overflow-y-auto p-6 lg:p-10 custom-scrollbar bg-transparent transition-colors duration-300">

    <div class="relative bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 lg:p-12 overflow-hidden shadow-sm dark:shadow-none border border-transparent dark:border-slate-800 mb-10 transition-all">
      
      <div v-if="loading" class="animate-pulse flex flex-col lg:flex-row justify-between items-center gap-8">
        <div class="flex-1 space-y-4">
          <div class="h-4 w-24 bg-slate-200 dark:bg-slate-800 rounded"></div>
          <div class="h-12 w-64 bg-slate-200 dark:bg-slate-800 rounded"></div>
          <div class="h-4 w-80 bg-slate-200 dark:bg-slate-800 rounded"></div>
        </div>
        <div class="w-64 h-64 bg-slate-100 dark:bg-slate-800 rounded-full"></div>
      </div>

      <div v-else class="relative z-10 flex flex-col lg:flex-row justify-between items-center gap-8 animate-in">
        <div class="max-w-xl text-center lg:text-left">
          <span class="text-indigo-500 dark:text-indigo-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4 block">
            Faculty Control Center
          </span>
          
          <h1 class="text-3xl lg:text-5xl font-black text-slate-900 dark:text-white leading-tight mb-4 transition-colors">
            Hello, <br />
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-purple-500">
                Prof. {{ instructorName || 'Educator' }}!
            </span>
          </h1>

          <p class="text-slate-500 dark:text-slate-400 text-sm font-medium leading-relaxed mb-6">
            You have {{ todayClasses.length }} classes scheduled today. 
            {{ todayClasses.length > 0 ? 'Your first session starts soon.' : 'You have a clear schedule today.' }}
          </p>
          
          <div class="flex gap-8 justify-center lg:justify-start border-t border-slate-100 dark:border-slate-800 pt-6">
            <div>
              <p class="text-2xl font-black text-slate-800 dark:text-slate-200">{{ todayClasses.length }}</p>
              <p class="text-[10px] uppercase font-bold text-slate-400 tracking-widest">Classes Today</p>
            </div>
            <div class="border-l border-slate-100 dark:border-slate-800 pl-8">
              <p class="text-2xl font-black text-slate-800 dark:text-slate-200">
                {{ totalStudentsCount }}
              </p>
              <p class="text-[10px] uppercase font-bold text-slate-400 tracking-widest">Total Students</p>
            </div>
          </div>
        </div>

        <img src="~/assets/images/student-walking-nobg.gif" alt="Teacher" class="w-80 lg:w-[380px] object-contain relative z-10" />
      </div>
      
      <div class="absolute -right-20 -top-20 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-3xl"></div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-12 gap-8">
       <div class="xl:col-span-8 space-y-8">
          <DailyRoutine 
            v-if="todayClasses && todayClasses.length > 0" 
            :classes="todayClassesPreview" 
            :loading="loading" 
          />
          <div v-else-if="!loading" class="p-8 bg-white dark:bg-slate-900 rounded-[2.5rem] text-center border border-dashed border-slate-200 dark:border-slate-800">
            <p class="text-slate-400 font-bold uppercase text-[10px] tracking-widest">No classes scheduled for today</p>
          </div>

          <TeacherDashboardPendingTasks />
       </div>
       
       <div class="xl:col-span-4 space-y-8">
         <CampusNotice v-if="notices && notices.length > 0" :notices="notices" />
         <AcademicCalendar />
       </div>
    </div>

  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DailyRoutine from '~/components/dashboard/teacher/DailyRoutine.vue'
import TeacherDashboardPendingTasks from '~/components/dashboard/teacher/TeacherDashboardPendingTasks.vue'
import AcademicCalendar from '~/components/dashbaord/academicCalendar.vue'
import CampusNotice from '~/components/dashbaord/campusNotice.vue'
import { useTeacherClasses } from '~/composable/useTeacherClasses'
import { useNotices } from '~/composable/useNotices'

const { fetchclassSchedule } = useTeacherClasses()
const { notices: allNotices, fetchNotices } = useNotices()

// UI States
const loading = ref(true)
const instructorName = ref('')

// Data Stores
const todayClasses = ref([])
const notices = computed(() => allNotices.value.slice(0, 3))
const todayClassesPreview = computed(() => todayClasses.value.slice(0, 3))

// Calculated Properties
const totalStudentsCount = computed(() => {
    return todayClasses.value.reduce((acc, curr) => acc + (curr.studentCount || 0), 0)
})

// Initialization Logic
onMounted(async () => {
    try {
        loading.value = true
        const response = await fetchclassSchedule()
        
        // Debugging log to verify incoming data
        console.log("Class Schedule Data:", response)

        if (response && response.classes) {
            // Map Instructor Name
            instructorName.value = response.instructor || 'Educator'

            // Map Class Data correctly based on your JSON structure
            todayClasses.value = response.classes.map(cls => ({
                id: cls.name,
                subject: cls.course_name || cls.course, // Use course_name from JSON
                title: cls.course_name,
                // Time formatting HH:mm
                time: `${cls.from_time.split(':').slice(0,2).join(':')} - ${cls.to_time.split(':').slice(0,2).join(':')}`,
                // Room logic: Take last segment of the room ID
                room: cls.room ? cls.room.split('-').pop() : 'N/A', 
                section: cls.student_group,
                studentCount: cls.total_students || 0,
                // Classes need a theme color for the UI; providing a default
                color: '#6366f1' 
            }))
        }
        
        // Load campus notices
        await fetchNotices()
    } catch (error) {
        console.error("Dashboard Initialization Error:", error)
    } finally {
        loading.value = false
    }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
    width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
}
.animate-in {
  animation: fadeIn 0.8s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>