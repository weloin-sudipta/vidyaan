<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300 p-4 lg:p-8 font-sans text-slate-900">
    <div class="max-w-6xl mx-auto space-y-8">

      <div v-if="loading" class="animate-pulse space-y-8">
        <div class="h-64 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-200 dark:border-slate-800"></div>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 h-80 bg-white dark:bg-slate-900 rounded-[2.5rem]"></div>
          <div class="h-80 bg-indigo-600/20 rounded-[2.5rem]"></div>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error && !loading" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-[2.5rem] p-8 text-center">
        <p class="text-red-600 dark:text-red-400 font-bold">{{ error }}</p>
        <button @click="fetchTeacherData" class="mt-4 px-6 py-3 bg-red-600 text-white rounded-2xl font-bold hover:bg-red-700 transition-colors">
          Try Again
        </button>
      </div>

      <!-- Main Content -->
      <template v-else-if="user && !loading">
        <header class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm border border-slate-200/60 dark:border-slate-800 p-6 transition-all">
          <div class="flex flex-col md:flex-row items-center gap-8">
            <div class="relative group">
              <div class="w-32 h-32 rounded-[2rem] overflow-hidden ring-4 ring-slate-50 dark:ring-slate-800 shadow-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                <img v-if="teacherProfile.image" :src="teacherProfile.image" class="w-full h-full object-cover" />
                <span v-else class="text-3xl font-black text-indigo-600 dark:text-indigo-400">
                  {{ teacherInitials }}
                </span>
              </div>
              <div class="absolute -bottom-2 -right-2 bg-emerald-500 w-8 h-8 rounded-xl flex items-center justify-center text-white border-4 border-white dark:border-slate-900 shadow-md">
                <i class="fas fa-check text-[10px]"></i>
              </div>
            </div>

            <div class="flex-1 text-center md:text-left">
              <div class="space-y-1 mb-4">
                <h1 class="text-3xl font-black tracking-tight text-slate-800 dark:text-white">
                  {{ teacherProfile.full_name }}
                </h1>
                <p class="text-indigo-600 dark:text-indigo-400 font-bold text-sm tracking-wide">
                  {{ teacherProfile.department || 'Instructor' }} • {{ teacherProfile.institute }}
                </p>
              </div>

              <div class="flex flex-wrap justify-center md:justify-start gap-6">
                <div class="flex flex-col">
                  <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">User Type</span>
                  <span class="font-bold text-slate-700 dark:text-slate-200">{{ teacherProfile.user_type || 'Instructor' }}</span>
                </div>
                <div class="w-px h-8 bg-slate-100 dark:bg-slate-800 hidden md:block" v-if="teacherProfile.birth_date"></div>
                <div class="flex flex-col" v-if="teacherProfile.birth_date">
                  <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Birth Date</span>
                  <span class="font-bold text-slate-700 dark:text-slate-200">{{ formatDate(teacherProfile.birth_date) }}</span>
                </div>
                <div class="w-px h-8 bg-slate-100 dark:bg-slate-800 hidden md:block"></div>
                <div class="flex flex-col">
                  <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Status</span>
                  <span class="text-emerald-500 font-black text-xs uppercase tracking-tighter">
                    {{ teacherProfile.status || 'Active' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="flex gap-2">
              <a :href="`mailto:${teacherProfile.email}`" class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-800 text-slate-400 hover:text-indigo-600 transition-colors border border-slate-200 dark:border-slate-700">
                <i class="fas fa-envelope"></i>
              </a>
              <button class="px-6 py-3 bg-slate-900 dark:bg-indigo-600 text-white rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-indigo-600 transition-all shadow-lg">
                Edit Profile
              </button>
            </div>
          </div>
        </header>

        <main class="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-700">
          
          <!-- Statistics Section -->
          <div class="lg:col-span-3 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-gradient-to-br from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 rounded-2xl p-6 text-white shadow-lg">
              <div class="text-3xl font-black mb-2">{{ assignedCourses.length }}</div>
              <p class="text-sm font-semibold opacity-90">Courses Teaching</p>
            </div>
            <div class="bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-2xl p-6 text-white shadow-lg">
              <div class="text-3xl font-black mb-2">{{ userRoles.length }}</div>
              <p class="text-sm font-semibold opacity-90">User Roles</p>
            </div>
            <div class="bg-gradient-to-br from-green-500 to-green-600 dark:from-green-600 dark:to-green-700 rounded-2xl p-6 text-white shadow-lg">
              <div class="text-3xl font-black mb-2">{{ teacherProfile.status || 'Active' }}</div>
              <p class="text-sm font-semibold opacity-90">Account Status</p>
            </div>
            <div class="bg-gradient-to-br from-amber-500 to-amber-600 dark:from-amber-600 dark:to-amber-700 rounded-2xl p-6 text-white shadow-lg">
              <div class="text-3xl font-black mb-2">{{ teacherProfile.institute }}</div>
              <p class="text-sm font-semibold opacity-90">Institute</p>
            </div>
          </div>

          <div class="lg:col-span-2 space-y-6">
            <!-- Professional Credentials -->
            <!-- <section v-if="hasCredentials" class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm">
              <div class="flex items-center gap-3 mb-8">
                <div class="w-1.5 h-6 bg-indigo-600 dark:bg-indigo-400 rounded-full"></div>
                <h3 class="text-lg font-black text-slate-800 dark:text-white tracking-tight">Professional Information</h3>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div v-if="teacherProfile.gender" class="space-y-1">
                  <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Gender</p>
                  <p class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ teacherProfile.gender }}</p>
                </div>
                <div v-if="teacherProfile.user_type" class="space-y-1">
                  <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">User Type</p>
                  <p class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ teacherProfile.user_type }}</p>
                </div>
                <div v-if="teacherProfile.language" class="space-y-1">
                  <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Language</p>
                  <p class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ teacherProfile.language }}</p>
                </div>
                <div v-if="teacherProfile.time_zone" class="space-y-1">
                  <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Time Zone</p>
                  <p class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ teacherProfile.time_zone }}</p>
                </div>
              </div>
            </section> -->

            <!-- Contact Information -->
            <section class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm">
              <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">Contact Information</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div v-if="teacherProfile.email" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">Work Email</p>
                  <p class="text-xs font-bold dark:text-slate-300 break-all">{{ teacherProfile.email }}</p>
                </div>
                <div v-if="teacherProfile.phone || teacherProfile.mobile_no" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">Phone</p>
                  <p class="text-xs font-bold dark:text-slate-300">{{ teacherProfile.phone || teacherProfile.mobile_no }}</p>
                </div>
                <div v-if="teacherProfile.location" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">Location</p>
                  <p class="text-xs font-bold dark:text-slate-300">{{ teacherProfile.location }}</p>
                </div>
              </div>
            </section>

            <!-- Professional Info -->
            <section v-if="hasCredentials" class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm">
              <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">Professional Information</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div v-if="teacherProfile.gender" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">Gender</p>
                  <p class="text-xs font-bold dark:text-slate-300">{{ teacherProfile.gender }}</p>
                </div>
                <div v-if="teacherProfile.language" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">Language</p>
                  <p class="text-xs font-bold dark:text-slate-300">{{ teacherProfile.language }}</p>
                </div>
                <div v-if="teacherProfile.time_zone" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">Time Zone</p>
                  <p class="text-xs font-bold dark:text-slate-300">{{ teacherProfile.time_zone }}</p>
                </div>
                <div v-if="teacherProfile.user_type" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">User Type</p>
                  <p class="text-xs font-bold dark:text-slate-300">{{ teacherProfile.user_type }}</p>
                </div>
              </div>
            </section>

            <!-- Login Activity -->
            <section v-if="teacherProfile.last_login || teacherProfile.last_active" class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm">
              <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">Activity Information</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div v-if="teacherProfile.last_login" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">Last Login</p>
                  <p class="text-xs font-bold dark:text-slate-300">{{ formatDateTime(teacherProfile.last_login) }}</p>
                </div>
                <div v-if="teacherProfile.last_active" class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800">
                  <p class="text-[9px] font-black text-indigo-500 uppercase mb-1">Last Active</p>
                  <p class="text-xs font-bold dark:text-slate-300">{{ formatDateTime(teacherProfile.last_active) }}</p>
                </div>
              </div>
            </section>
          </div>

          <div class="space-y-6">
            <!-- Workload Stats -->
            <div class="bg-indigo-600 dark:bg-indigo-700 rounded-[2.5rem] p-8 text-white shadow-xl shadow-indigo-100 dark:shadow-none">
              <p class="text-[10px] font-black uppercase tracking-[0.2em] opacity-60 mb-1">Teaching Load</p>
              <h4 class="text-4xl font-black mb-6">{{ assignedCourses.length }}<span class="text-lg opacity-50">courses</span></h4>
              
              <div class="space-y-4 pt-4 border-t border-white/10" v-if="teacherProfile.status">
                <div class="flex justify-between items-center text-xs font-bold">
                  <span class="opacity-70">Account Status</span>
                  <span>{{ teacherProfile.status }}</span>
                </div>
                <div class="w-full bg-indigo-500 rounded-full h-1.5">
                  <div class="bg-white h-1.5 rounded-full transition-all duration-1000" style="width: 100%"></div>
                </div>
              </div>
            </div>

            <!-- Assigned Classes -->
            <div v-if="assignedCourses.length > 0" class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800">
              <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">Assigned Classes</h3>
              <div class="space-y-3">
                <div v-for="course in assignedCourses" :key="course.name" class="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors border border-transparent hover:border-indigo-100 dark:hover:border-indigo-800 cursor-default">
                  <div class="w-8 h-8 rounded-lg bg-white dark:bg-slate-900 flex items-center justify-center text-xs font-black text-indigo-600 shadow-sm">
                    {{ course.program?.substring(0, 2) || course.course?.substring(0, 2) || 'CL' }}
                  </div>
                  <div class="flex-1">
                    <span class="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase block">{{ course.course }}</span>
                    <span class="text-[10px] text-slate-500 dark:text-slate-400">{{ course.program }} • {{ course.academic_term }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- User Roles -->
            <div v-if="userRoles.length > 0" class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800">
              <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-6">User Roles</h3>
              <div class="flex flex-wrap gap-2">
                <span v-for="role in userRoles" :key="role" class="px-3 py-1 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 rounded-lg text-xs font-bold uppercase tracking-wider">
                  {{ role }}
                </span>
              </div>
            </div>
          </div>

        </main>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTeacherDashboard } from '~/composable/useTeacherDashboard'

const { data, fetchTeacherData, error, loading } = useTeacherDashboard()

// Computed properties for data transformation
const instructor = computed(() => data.value?.instructor || {})
const user = computed(() => data.value?.user || {})

const teacherProfile = computed(() => {
  // Merge instructor and user data
  return {
    ...instructor.value,
    // Override with user data for common fields
    full_name: user.value?.full_name || instructor.value?.instructor_name,
    email: user.value?.email || instructor.value?.instructor_email,
    phone: user.value?.phone,
    mobile_no: user.value?.mobile_no,
    location: user.value?.location,
    birth_date: user.value?.birth_date,
    gender: user.value?.gender,
    language: user.value?.language,
    time_zone: user.value?.time_zone,
    last_login: user.value?.last_login,
    last_active: user.value?.last_active,
    user_type: user.value?.user_type,
  }
})

const teacherInitials = computed(() => {
  const name = teacherProfile.value.full_name || ''
  if (!name) return 'TH'
  
  const names = name.split(' ')
  return names.length > 1 
    ? (names[0][0] + names[names.length - 1][0]).toUpperCase() 
    : name.substring(0, 2).toUpperCase()
})

const assignedCourses = computed(() => instructor.value?.instructor_log || [])

const userRoles = computed(() => user.value?.roles?.map(role => role.role) || [])

const hasCredentials = computed(() => {
  return teacherProfile.value.gender || 
         teacherProfile.value.user_type || 
         teacherProfile.value.language || 
         teacherProfile.value.time_zone
})

// Utility functions
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  return new Date(dateTimeString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(fetchTeacherData)
</script>

<style scoped>
.animate-in {
  animation: slideUp 0.6s ease-out forwards;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>