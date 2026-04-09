<template>
  <div class="p-6 lg:p-10 max-w-7xl mx-auto custom-scrollbar animate-in fade-in slide-in-from-bottom-4 duration-500">
    
    <header class="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <i class="fa fa-clipboard-list"></i>
          </div>
          <h1 class="text-3xl font-black text-slate-800 dark:text-slate-100 tracking-tight">
            Application Portal
          </h1>
        </div>
        <p class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest ml-1">
          Student Leave & Activity Authorizations
        </p>
      </div>

      <div class="flex items-center gap-4 bg-white dark:bg-slate-900 p-2 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm">
        <div class="px-4 py-1 border-r border-slate-100 dark:border-slate-800">
          <p class="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Academic Year</p>
          <p class="text-xs font-black text-indigo-500">Term 2, 2026</p>
        </div>
        <button class="px-4 py-2 bg-slate-50 dark:bg-slate-800 hover:bg-indigo-500 hover:text-white transition-all rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-600 dark:text-slate-400">
          History Log
        </button>
      </div>
    </header>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
      <div v-for="stat in statItems" :key="stat.label" 
           class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 p-6 rounded-[2rem] shadow-sm hover:shadow-xl transition-all group">
        <p class="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-3 group-hover:text-indigo-500 transition-colors">
          {{ stat.label }}
        </p>
        <div class="flex items-end justify-between">
          <h3 class="text-4xl font-black text-slate-800 dark:text-slate-100 leading-none">
            {{ stat.value }}
          </h3>
          <span :class="stat.trendColor" class="text-[10px] font-black uppercase tracking-tighter px-2 py-1 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
            {{ stat.trend }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="space-y-4">
      <div v-for="n in 3" :key="n" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-[2.5rem] p-8 flex items-center gap-6">
        <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 animate-pulse"></div>
        <div class="flex-1 space-y-3">
          <div class="h-4 bg-slate-100 dark:bg-slate-800 rounded w-1/4 animate-pulse"></div>
          <div class="h-3 bg-slate-100 dark:border-slate-800 rounded w-1/3 animate-pulse"></div>
        </div>
      </div>
    </div>

    <div v-else class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-[2.5rem] shadow-sm overflow-hidden">
      
      <div class="p-8 border-b border-slate-50 dark:border-slate-800/50 flex items-center justify-between">
        <div>
          <h2 class="text-xl font-black text-slate-800 dark:text-slate-100">Action Queue</h2>
          <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1">Pending student requests</p>
        </div>
        <div v-if="applications.length > 0" class="flex items-center gap-2 px-4 py-2 bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 rounded-xl text-[10px] font-black uppercase tracking-widest border border-amber-100 dark:border-amber-800/50">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
          </span>
          {{ applications.length }} Pending
        </div>
      </div>

      <div class="overflow-x-auto">
        <table v-if="applications.length > 0" class="w-full text-left">
          <thead>
            <tr class="text-slate-400 dark:text-slate-500 text-[10px] uppercase font-black tracking-[0.15em] border-b border-slate-50 dark:border-slate-800/50">
              <th class="px-8 py-5">Student Information</th>
              <th class="px-8 py-5">Request Detail</th>
              <th class="px-8 py-5">Period</th>
              <th class="px-8 py-5 text-right">Decision</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/50">
            <tr v-for="item in applications" :key="item.name" class="group hover:bg-slate-50/50 dark:hover:bg-indigo-500/5 transition-all">
              
              <td class="px-8 py-6">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-black text-sm group-hover:bg-indigo-600 group-hover:text-white transition-all duration-300">
                    {{ item.studentInitials }}
                  </div>
                  <div>
                    <div class="font-black text-slate-800 dark:text-slate-100 text-sm mb-0.5">{{ item.student_name }}</div>
                    <div class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-tight">{{ item.group_info }}</div>
                  </div>
                </div>
              </td>
              
              <td class="px-8 py-6">
                <span :class="item.app_type === 'Leave' ? 'text-blue-600 bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800' : 'text-purple-600 bg-purple-50 dark:bg-purple-900/20 border-purple-100 dark:border-purple-800'" 
                      class="text-[10px] font-black uppercase px-3 py-1.5 rounded-lg border">
                  {{ item.app_type }}
                </span>
                <div class="mt-3 text-xs font-bold text-slate-500 dark:text-slate-400 max-w-xs line-clamp-1 group-hover:line-clamp-none transition-all">
                  {{ item.reason || 'No specific reason provided' }}
                </div>
              </td>
              
              <td class="px-8 py-6">
                <div class="text-xs font-black text-slate-700 dark:text-slate-200 mb-1">
                  {{ item.date_range || (item.from_date + ' → ' + item.to_date) }}
                </div>
                <div class="flex items-center gap-2">
                   <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                    {{ item.app_type === 'Leave' ? `${item.total_leave_days} Days` : item.noc_type }}
                  </span>
                  <a v-if="item.supporting_document" :href="getFileUrl(item.supporting_document)" target="_blank" class="text-indigo-500 hover:text-indigo-700">
                    <i class="fa fa-paperclip text-[10px]"></i>
                  </a>
                </div>
              </td>
              
              <td class="px-8 py-6">
                <div class="flex justify-end items-center gap-3">
                  <button 
                    @click="handleAction(item.name, 'Reject', item.app_type)"
                    class="w-10 h-10 flex items-center justify-center rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all border border-transparent hover:border-red-100 dark:hover:border-red-800"
                  >
                    <i class="fa fa-times"></i>
                  </button>
                  <button 
                    @click="handleAction(item.name, 'Approve', item.app_type)"
                    :disabled="processingId === item.name"
                    class="h-10 px-6 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-[10px] font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-lg shadow-slate-200 dark:shadow-none disabled:opacity-50 flex items-center gap-2"
                  >
                    <i v-if="processingId === item.name" class="fa fa-circle-notch animate-spin"></i>
                    {{ processingId === item.name ? 'Processing' : 'Approve' }}
                  </button>
                </div>
              </td>

            </tr>
          </tbody>
        </table>

        <div v-else class="py-24 text-center">
          <div class="w-20 h-20 bg-slate-50 dark:bg-slate-800/50 rounded-[2rem] flex items-center justify-center mx-auto mb-6">
            <i class="fa fa-check-double text-slate-200 dark:text-slate-700 text-3xl"></i>
          </div>
          <h3 class="text-sm font-black text-slate-800 dark:text-slate-200 uppercase tracking-[0.2em]">Inbox Cleared</h3>
          <p class="text-[10px] font-bold text-slate-400 mt-2 uppercase tracking-widest">No pending applications require your attention</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 5px; height: 5px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 99px; }
.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; }

/* Custom utilities for the "Black" aesthetic */
.font-black { font-weight: 900; }
</style>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { call } from '~/composables/api/useFrappeFetch'
import { useToast } from '~/composables/ui/useToast'

const config = useRuntimeConfig()

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

const getFileUrl = (filePath, isDownload = false) => {
  if (!filePath) return ''
  if (filePath.startsWith('http')) return filePath

  if (isDownload) {
    return `${config.public.apiBaseUrl}/api/method/frappe.utils.file_manager.download_file?file_url=${encodeURIComponent(filePath)}`
  }

  return `${config.public.apiBaseUrl}${filePath}`
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