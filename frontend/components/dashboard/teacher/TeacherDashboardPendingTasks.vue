<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm p-6 lg:p-8 flex flex-col gap-6 transition-colors">
    <div class="flex items-center justify-between border-b border-slate-50 dark:border-slate-800/50 pb-4">
      <div class="flex items-center gap-3">
         <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-400 rounded-2xl flex items-center justify-center text-white text-sm shadow-lg shadow-indigo-200 dark:shadow-none">
           <i class="fa fa-tasks"></i>
         </div>
         <div>
           <h6 class="text-sm font-black text-slate-800 dark:text-slate-200 leading-tight tracking-tight">Pending Tasks</h6>
           <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Tasks Requiring Attention</span>
         </div>
      </div>
      <button @click="refreshTasks" :disabled="loadingTasks" class="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors px-4 py-2 rounded-xl flex items-center gap-2">
         <i class="fa fa-refresh" :class="{ 'animate-spin': loadingTasks }"></i> Refresh
      </button>
    </div>

    <div v-if="tasksError" class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-2xl text-sm font-medium border border-red-100 dark:border-red-800/30 flex items-center gap-3">
        <i class="fa fa-exclamation-circle text-lg"></i>
        <span>{{ tasksError }}</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Attendance Pending Column -->
      <div class="flex flex-col gap-4">
        <div class="flex items-center justify-between">
           <div class="flex items-center gap-2">
              <i class="fa fa-calendar-check-o text-rose-500"></i>
              <h3 class="text-xs font-black uppercase text-slate-700 dark:text-slate-300">Pending Attendance</h3>
           </div>
           <span class="bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 text-[10px] font-bold px-2 py-0.5 rounded-lg">{{ pendingTasks.attendance_pending.length }}</span>
        </div>
        
        <div v-if="loadingTasks" class="space-y-3">
           <div v-for="i in 3" :key="i" class="h-20 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-2xl"></div>
        </div>
        <div v-else-if="pendingTasks.attendance_pending.length === 0" class="h-full flex flex-col items-center justify-center p-6 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl bg-slate-50/50 dark:bg-slate-800/20">
            <div class="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-3">
                <i class="fa fa-check text-slate-400"></i>
            </div>
            <p class="text-[11px] font-bold text-slate-500 uppercase">All caught up!</p>
        </div>
        <div v-else class="flex flex-col gap-3">
          <div v-for="item in pendingTasks.attendance_pending.slice(0, 3)" :key="item.schedule_id" class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-700/50 hover:border-rose-200 dark:hover:border-rose-500/30 transition-all group">
             <div class="flex justify-between items-start mb-2">
                <div>
                   <p class="text-[12px] font-black leading-tight text-slate-800 dark:text-slate-200 group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors">{{ item.course_name }}</p>
                   <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-1"><i class="fa fa-users mr-1"></i> {{ item.batch }} • {{ item.total_students }} Std.</p>
                </div>
             </div>
             <div class="flex justify-between items-center mt-3">
                 <p class="text-[9px] font-bold text-slate-400 bg-white dark:bg-slate-900 px-2 py-1 rounded-lg border border-slate-100 dark:border-slate-800">
                     <i class="fa fa-clock-o text-rose-400 mr-1"></i> {{ item.schedule_date }}
                 </p>
                 <button @click="navigateTo(`/teacher/academics/attendance?schedule=${item.schedule_id}`)" class="px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-sm hover:bg-rose-500 hover:text-white hover:border-transparent transition-all">
                     Mark
                 </button>
             </div>
          </div>
        </div>
      </div>

      <!-- Mark Entry Column -->
      <div class="flex flex-col gap-4">
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
               <i class="fa fa-edit text-amber-500"></i>
               <h3 class="text-xs font-black uppercase text-slate-700 dark:text-slate-300">Pending Grades</h3>
            </div>
            <span class="bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 text-[10px] font-bold px-2 py-0.5 rounded-lg">{{ pendingTasks.mark_entry_pending.length }}</span>
        </div>
        
        <div v-if="loadingTasks" class="space-y-3">
           <div v-for="i in 3" :key="i" class="h-20 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-2xl"></div>
        </div>
        <div v-else-if="pendingTasks.mark_entry_pending.length === 0" class="h-full flex flex-col items-center justify-center p-6 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl bg-slate-50/50 dark:bg-slate-800/20">
            <div class="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-3">
                <i class="fa fa-trophy text-slate-400"></i>
            </div>
            <p class="text-[11px] font-bold text-slate-500 uppercase">Grades Complete</p>
        </div>
        <div v-else class="flex flex-col gap-3">
            <div v-for="item in pendingTasks.mark_entry_pending.slice(0, 3)" :key="item.assessment_id" class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-700/50 hover:border-amber-200 dark:hover:border-amber-500/30 transition-all group">
               <div class="flex justify-between items-start mb-2">
                  <div>
                     <p class="text-[12px] leading-tight font-black text-slate-800 dark:text-slate-200 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">{{ item.assessment_title }}</p>
                     <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-1 truncate">{{ item.course }}</p>
                  </div>
               </div>
               
               <div class="mt-2 text-[10px] font-medium text-slate-500 dark:text-slate-400 flex items-center gap-2">
                   <div class="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                       <div class="h-full bg-amber-400" :style="`width: ${(item.marks_entered_count / item.total_students) * 100}%`"></div>
                   </div>
                   <span class="whitespace-nowrap"><b class="text-amber-600 dark:text-amber-400">{{ item.pending_count }}</b> left</span>
               </div>
               
               <div class="flex justify-between items-center mt-3">
                   <p class="text-[9px] font-bold text-slate-400 bg-white dark:bg-slate-900 px-2 py-1 rounded-lg border border-slate-100 dark:border-slate-800">
                       <i class="fa fa-calendar max-w-[80px] truncate text-amber-400 mr-1"></i> {{ item.assessment_date }}
                   </p>
                   <button @click="navigateTo(`/teacher/grading/mark-entry?assessment=${item.assessment_id}`)" class="px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-sm hover:bg-amber-500 hover:text-white hover:border-transparent transition-all">
                       Grade
                   </button>
               </div>
            </div>
        </div>
      </div>

      <!-- Review Column -->
      <div class="flex flex-col gap-4">
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
               <i class="fa fa-search text-emerald-500"></i>
               <h3 class="text-xs font-black uppercase text-slate-700 dark:text-slate-300">Pending Reviews</h3>
            </div>
            <span class="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded-lg">{{ pendingTasks.review_pending.length }}</span>
        </div>
        
        <div v-if="loadingTasks" class="space-y-3">
           <div v-for="i in 3" :key="i" class="h-20 bg-slate-100 dark:bg-slate-800 animate-pulse rounded-2xl"></div>
        </div>
        <div v-else-if="pendingTasks.review_pending.length === 0" class="h-full flex flex-col items-center justify-center p-6 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl bg-slate-50/50 dark:bg-slate-800/20">
            <div class="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-3">
                <i class="fa fa-folder-open-o text-slate-400"></i>
            </div>
            <p class="text-[11px] font-bold text-slate-500 uppercase">Inbox Zero</p>
        </div>
        <div v-else class="flex flex-col gap-3">
            <div v-for="item in pendingTasks.review_pending.slice(0, 3)" :key="item.submission_id" class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-700/50 hover:border-emerald-200 dark:hover:border-emerald-500/30 transition-all group">
               <div class="flex justify-between items-start mb-2">
                  <div>
                     <p class="text-[12px] leading-tight font-black text-slate-800 dark:text-slate-200 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">{{ item.student_name }}</p>
                     <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-1 truncate max-w-[150px]"><i class="fa fa-file-text-o mr-1"></i> {{ item.assignment_title }}</p>
                  </div>
               </div>
               
               <div class="flex justify-between items-center mt-3">
                   <p class="text-[9px] font-bold text-slate-400 bg-white dark:bg-slate-900 px-2 py-1 rounded-lg border border-slate-100 dark:border-slate-800">
                       <i class="fa fa-clock-o text-emerald-400 mr-1"></i> {{ formatDate(item.submission_date) }}
                   </p>
                   <NuxtLink to="teacher/academics/assignments"><button class="px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-sm hover:bg-emerald-500 hover:text-white hover:border-transparent transition-all">
                       Review
                   </button></NuxtLink>
               </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTeacherDashboard } from '~/composables/useTeacherDashboard'

const router = useRouter()
const { pendingTasks, loadingTasks, tasksError, fetchPendingTasks } = useTeacherDashboard()

let refreshInterval = null

const navigateTo = (path) => {
    router.push(path)
}

const formatDate = (dateStr) => {
    if(!dateStr) return 'N/A'
    try {
        const d = new Date(dateStr)
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
    } catch {
        return dateStr
    }
}

const refreshTasks = () => {
    fetchPendingTasks()
}

onMounted(() => {
    fetchPendingTasks()
    
    // Auto refresh every 5 minutes (300000 ms)
    refreshInterval = setInterval(() => {
        fetchPendingTasks()
    }, 300000)
})

onUnmounted(() => {
    if (refreshInterval) {
        clearInterval(refreshInterval)
    }
})
</script>
