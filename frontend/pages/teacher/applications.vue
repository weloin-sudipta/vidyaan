<template>
  <div class="min-h-screen bg-gray-50 dark:bg-zinc-950 text-gray-900 dark:text-zinc-100 transition-colors duration-300">
    
    <div class="max-w-7xl mx-auto p-4 md:p-8">
      
      <!-- Header Section - Matches My Classes style -->
      <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
        <div>
          <h1 class="text-3xl font-extrabold tracking-tight">Application Portal</h1>
          <p class="text-gray-500 dark:text-zinc-400 mt-1">Manage student leave and activity authorizations</p>
        </div>
        
        <!-- <div class="flex items-center gap-3">
          <div class="hidden md:block text-right">
            <p class="text-sm font-medium">Term 2, 2026</p>
            <p class="text-xs text-gray-500 dark:text-zinc-500">Academic Year</p>
          </div>
          <div class="h-10 w-[1px] bg-gray-200 dark:bg-zinc-800 hidden md:block mx-2"></div>
          
          <button class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-medium shadow-sm transition-all flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            History Log
          </button>
        </div> -->
      </header>

      <!-- Stats Cards - Same style as My Classes -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <div v-for="stat in statItems" :key="stat.label" 
             class="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 p-5 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
          <p class="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-zinc-500">{{ stat.label }}</p>
          <div class="flex items-end justify-between mt-2">
            <h3 class="text-3xl font-bold">{{ stat.value }}</h3>
            <span :class="stat.trendColor" class="text-xs font-medium px-2 py-1 rounded-lg bg-opacity-10 dark:bg-opacity-20">
              {{ stat.trend }}
            </span>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="space-y-4">
        <div class="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-2xl overflow-hidden">
          <div class="p-6 border-b border-gray-100 dark:border-zinc-800">
            <div class="h-6 bg-gray-200 dark:bg-zinc-800 rounded-lg w-48 mb-2"></div>
            <div class="h-4 bg-gray-200 dark:bg-zinc-800 rounded-lg w-64"></div>
          </div>
          <div class="p-6 space-y-4">
            <div v-for="n in 3" :key="n" class="flex items-center gap-4">
              <div class="w-12 h-12 bg-gray-200 dark:bg-zinc-800 rounded-full"></div>
              <div class="flex-1">
                <div class="h-4 bg-gray-200 dark:bg-zinc-800 rounded-lg w-32 mb-2"></div>
                <div class="h-3 bg-gray-200 dark:bg-zinc-800 rounded-lg w-48"></div>
              </div>
              <div class="w-24 h-8 bg-gray-200 dark:bg-zinc-800 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Applications Table Card -->
      <div v-else class="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-2xl shadow-sm overflow-hidden">
        
        <!-- Card Header -->
        <div class="p-6 border-b border-gray-100 dark:border-zinc-800 flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold">Pending Applications</h2>
            <p class="text-xs text-gray-500 dark:text-zinc-500 mt-1">Review and approve student leave and NOC requests</p>
          </div>
          <span v-if="applications.length > 0" class="text-xs bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 px-2.5 py-1 rounded-full font-bold">
            {{ applications.length }} Pending
          </span>
          <span v-else class="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2.5 py-1 rounded-full font-bold">
            All Clear
          </span>
        </div>

        <!-- Table -->
        <div class="overflow-x-auto">
          <table v-if="applications.length > 0" class="w-full text-left">
            <thead>
              <tr class="bg-gray-50/50 dark:bg-zinc-800/50 text-gray-500 dark:text-zinc-400 text-xs uppercase tracking-widest font-semibold">
                <th class="px-6 py-4">Student Info</th>
                <th class="px-6 py-4">Request Type</th>
                <th class="px-6 py-4">Timeline & Reason</th>
                <th class="px-6 py-4">Status</th>
                <th class="px-6 py-4 text-right">Decision</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-zinc-800">
              <tr v-for="item in applications" :key="item.name" class="group hover:bg-gray-50 dark:hover:bg-zinc-800/40 transition-colors">
                <!-- Student Info -->
                <td class="px-6 py-5">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-sm">
                      {{ item.studentInitials }}
                    </div>
                    <div>
                      <div class="font-bold text-sm">{{ item.student_name }}</div>
                      <div class="text-xs text-gray-500 dark:text-zinc-500 leading-tight">{{ item.student }} • {{ item.group_info }}</div>
                    </div>
                  </div>
                </td>
                
                <!-- Request Type -->
                <td class="px-6 py-5">
                  <span v-if="item.app_type === 'Leave'" class="text-[11px] font-black uppercase px-2 py-1 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
                    Leave Application
                  </span>
                  <span v-else class="text-[11px] font-black uppercase px-2 py-1 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border border-purple-200 dark:border-purple-800">
                    NOC Application
                  </span>
                </td>
                
                <!-- Timeline & Reason -->
                <td class="px-6 py-5">
                  <div class="text-sm font-medium">{{ item.date_range || (item.from_date + ' to ' + item.to_date) }}</div>
                  <div v-if="item.app_type === 'Leave'" class="text-[11px] text-gray-400 dark:text-zinc-500">{{ item.total_leave_days }} Day(s)</div>
                  <div v-else class="text-[11px] text-gray-400 dark:text-zinc-500">Type: {{ item.noc_type }}</div>
                  <div class="text-[10px] text-gray-500 dark:text-zinc-400 mt-1 max-w-xs truncate flex items-center gap-1">
                    <span>Reason: {{ item.reason || 'Not specified' }}</span>
                    <a v-if="item.supporting_document" :href="item.supporting_document" target="_blank" class="ml-2 text-indigo-500 hover:text-indigo-600 dark:text-indigo-400 dark:hover:text-indigo-300">
                      <i class="fas fa-paperclip"></i>
                    </a>
                  </div>
                </td>
                
                <!-- Status -->
                <td class="px-6 py-5">
                  <div class="flex items-center gap-1.5">
                    <div class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                    <span class="text-xs font-medium text-amber-600 dark:text-amber-500">Pending Review</span>
                  </div>
                </td>
                
                <!-- Actions -->
                <td class="px-6 py-5">
                  <div class="flex justify-end gap-3">
                    <button 
                      @click="handleAction(item.name, 'Reject', item.app_type)" 
                      :disabled="processing === item.name"
                      class="p-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50"
                      title="Reject"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                    <button 
                      @click="handleAction(item.name, 'Approve', item.app_type)" 
                      :disabled="processing === item.name"
                      class="bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-5 py-2 rounded-lg text-xs font-bold hover:scale-105 transition-transform shadow-md disabled:opacity-50 flex items-center gap-2"
                    >
                      <svg v-if="processing === item.name" class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      {{ processing === item.name ? 'Processing' : 'Approve' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Empty State -->
          <div v-else class="p-12 text-center">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-green-100 dark:bg-green-900/20 rounded-full mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1">All Caught Up!</h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">No pending applications to review</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { call } from '~/composables/api/useFrappeFetch'
import { useToast } from '~/composables/ui/useToast'

const { addToast } = useToast()

const applications = ref([])
const loading = ref(true)
const processingId = ref(null)

const stats = ref({
  pending: 0,
  approved: 0,
  rejected: 0,
  total: 0
})

/* ------------------ TRANSFORMER ------------------ */
const mapApplication = (item) => ({
  app_type: item.app_type,
  name: item.name,
  student: item.student,
  student_name: item.student_name,
  studentInitials: (item.student_name || item.student || 'U')
    .slice(0, 2)
    .toUpperCase(),
  from_date: item.from_date,
  to_date: item.to_date,
  date_range: item.date_range,
  reason: item.reason,
  noc_type: item.noc_type,
  supporting_document: item.supporting_document,
  total_leave_days: item.total_leave_days,
  group_info: item.group_info || 'N/A',
})

/* ------------------ FETCH ------------------ */
const fetchApplications = async () => {
  loading.value = true
  try {
    const [appsRes, statsRes] = await Promise.all([
      call('vidyaan.api_folder.applications.get_teacher_pending_applications'),
      call('vidyaan.api_folder.applications.get_teacher_leave_statistics')
    ])

    applications.value = (appsRes || []).map(mapApplication)

    if (statsRes) {
      stats.value = {
        pending: statsRes.pending || 0,
        approved: statsRes.approved || 0,
        rejected: statsRes.rejected || 0,
        total:
          (statsRes.pending || 0) +
          (statsRes.approved || 0) +
          (statsRes.rejected || 0)
      }
    }

  } catch (err) {
    console.error(err)
    addToast('Failed to load leave applications', 'error')
  } finally {
    loading.value = false
  }
}

/* ------------------ ACTION HANDLER ------------------ */
const handleAction = async (name, action, app_type) => {
  processingId.value = name

  try {
    await call('vidyaan.api_folder.applications.review_application', {
      name,
      action,
      app_type
    })

    addToast(`Application ${action.toLowerCase()}d`, 'success')

    // ⚡ Optimistic UI update (no full reload)
    applications.value = applications.value.filter(app => app.name !== name)

    // update stats locally
    stats.value.pending--
    if (action === 'Approve') stats.value.approved++
    if (action === 'Reject') stats.value.rejected++

  } catch (err) {
    let msg = 'Failed to process application'

    if (err?.data?._server_messages) {
      try {
        msg = JSON.parse(JSON.parse(err.data._server_messages)[0]).message
      } catch {}
    }

    addToast(msg, 'error')
  } finally {
    processingId.value = null
  }
}

onMounted(fetchApplications)

/* ------------------ STATS UI ------------------ */
const statItems = computed(() => [
  {
    label: 'Pending Approvals',
    value: stats.value.pending,
    trend: 'Needs Review',
    color: 'amber'
  },
  {
    label: 'Approved',
    value: stats.value.approved,
    trend: 'Processed',
    color: 'emerald'
  },
  {
    label: 'Rejected',
    value: stats.value.rejected,
    trend: 'Denied',
    color: 'rose'
  },
  {
    label: 'Total Applications',
    value: stats.value.total,
    trend: 'This Year',
    color: 'indigo'
  }
])
</script>

<style scoped>
/* Custom scrollbar matching My Classes */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 99px;
}

.dark ::-webkit-scrollbar-thumb {
  background: #334155;
}

::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #475569;
}

/* Smooth transitions */
* {
  transition: background-color 0.2s ease, border-color 0.2s ease;
}
</style>