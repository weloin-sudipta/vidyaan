<template>
  <main class="flex-1 overflow-y-auto p-6 lg:p-10 custom-scrollbar bg-[#f8fafc] dark:bg-slate-950 transition-colors">

    <!-- Header -->
    <div class="relative bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 lg:p-10 shadow-md dark:shadow-none mb-8 border border-slate-100 dark:border-slate-800 overflow-hidden transition-colors">
      <div class="relative z-10 flex flex-col lg:flex-row justify-between items-center gap-6">
        <div class="max-w-xl text-center lg:text-left">
          <span class="text-indigo-400 text-[10px] font-black uppercase tracking-[0.3em] mb-3 block">Request Desk</span>
          <h1 class="text-3xl lg:text-4xl font-black text-black dark:text-white leading-tight mb-2 transition-colors">
            My <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-500">Applications</span>
          </h1>
          <p class="text-slate-400 text-sm font-medium">Submit, track, and manage all your applications.</p>
        </div>
        <button @click="showTypeSelector = true"
          class="px-8 py-4 bg-slate-900 dark:bg-indigo-600 text-white rounded-2xl font-bold text-sm hover:scale-105 transition-all shadow-lg uppercase tracking-wider">
          <i class="fa fa-plus mr-2"></i> New Application
        </button>
      </div>
      <div class="absolute -right-16 -top-16 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl"></div>
    </div>

    <!-- Filter tabs -->
    <div class="flex gap-2 mb-6 overflow-x-auto no-scrollbar">
      <button v-for="f in filterTabs" :key="f.id" @click="activeFilter = f.id" :class="[
        activeFilter === f.id
          ? 'bg-slate-900 dark:bg-indigo-600 text-white shadow-lg'
          : 'bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700',
        'px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all whitespace-nowrap'
      ]">
        {{ f.label }}
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">

      <!-- Applications list -->
      <div class="lg:col-span-8 space-y-5">

        <div v-if="loading && !myApps.length" class="space-y-4">
          <UiSkeleton v-for="i in 3" :key="i" height="h-40" class="rounded-[2rem]" />
        </div>

        <!-- Application cards with timeline -->
        <div v-for="app in displayedApps" :key="app.name"
          class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm dark:shadow-none hover:shadow-md transition-all overflow-hidden">

          <!-- Card header -->
          <div class="p-6 pb-4">
            <div class="flex justify-between items-start">
              <div>
                <div class="flex items-center gap-2 mb-1.5">
                  <span :class="typeBadgeClass(app.key)" class="px-2.5 py-0.5 text-[8px] font-black uppercase tracking-wider rounded-md border transition-colors">
                    {{ app.type }}
                  </span>
                  <span v-if="app.priority && app.priority !== 'Medium'" :class="priorityClass(app.priority)"
                    class="px-2 py-0.5 text-[8px] font-black uppercase tracking-wider rounded-md border transition-colors">
                    {{ app.priority }}
                  </span>
                </div>
                <h4 class="text-base font-black text-slate-800 dark:text-slate-100 transition-colors">{{ app.subject }}</h4>
                <p class="text-[10px] font-bold text-slate-400 mt-0.5">{{ app.name }} &middot; {{ fmtDate(app.date) }}</p>
              </div>
              <span :class="statusClass(app.status)"
                class="px-3 py-1 text-[9px] font-black uppercase tracking-wider rounded-lg border shrink-0 transition-colors">
                {{ app.status }}
              </span>
            </div>
            <p v-if="app.description" class="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-2 transition-colors">
              {{ stripHtml(app.description) }}
            </p>
          </div>

          <!-- Workflow timeline -->
          <div v-if="app.workflow_steps && app.workflow_steps.length > 1"
            class="px-6 pb-5 pt-2 border-t border-slate-50 dark:border-slate-800/50 transition-colors">
            <div class="relative flex items-center justify-between">
              <!-- Progress line background -->
              <div class="absolute left-5 right-5 h-0.5 bg-slate-100 dark:bg-slate-800 top-4 transition-colors"></div>
              <!-- Progress line filled -->
              <div class="absolute left-5 h-0.5 top-4 transition-all duration-500 rounded-full"
                :class="isTerminal(app.status) ? (isApproved(app.status) ? 'bg-green-500' : 'bg-red-500') : 'bg-indigo-500'"
                :style="{ width: progressWidth(app) }"></div>

              <div v-for="(step, i) in app.workflow_steps" :key="i"
                class="relative z-10 flex flex-col items-center" :style="{ width: `${100 / app.workflow_steps.length}%` }">

                <!-- Step dot -->
                <div :class="stepDotClass(step.state, app.status, app.workflow_steps, i)"
                  class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-black transition-all duration-300 border-2">
                  <i v-if="isStepDone(step.state, app.status, app.workflow_steps, i)" class="fa fa-check"></i>
                  <i v-else-if="isStepCurrent(step.state, app.status)" class="fa fa-circle text-[6px]"></i>
                  <span v-else>{{ i + 1 }}</span>
                </div>

                <!-- Step label -->
                <span class="text-[8px] font-black uppercase tracking-wider mt-1.5 text-center leading-tight max-w-[70px] transition-colors"
                  :class="isStepActive(step.state, app.status, app.workflow_steps, i) ? 'text-slate-700 dark:text-slate-200' : 'text-slate-400 dark:text-slate-600'">
                  {{ step.state }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty -->
        <div v-if="!loading && !filteredApps.length"
          class="bg-white dark:bg-slate-900 rounded-[2rem] p-12 border border-dashed border-slate-200 dark:border-slate-800 text-center transition-colors">
          <i class="fa fa-inbox text-slate-200 dark:text-slate-700 text-5xl mb-4 block transition-colors"></i>
          <p class="text-sm font-black text-slate-400 uppercase">No applications found</p>
          <p class="text-[10px] text-slate-400 mt-1">Click "New Application" to get started</p>
        </div>

        <div v-if="visibleLimit < filteredApps.length" class="flex justify-center pt-2">
          <button @click="visibleLimit += 5"
            class="px-8 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 rounded-xl font-bold text-xs hover:border-indigo-500 transition-all">
            Load More <i class="fa fa-chevron-down ml-2 text-[9px]"></i>
          </button>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-white dark:bg-slate-900 rounded-[2rem] p-6 border border-slate-100 dark:border-slate-800 shadow-sm dark:shadow-none transition-colors">
          <h4 class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Summary</h4>
          <div class="grid grid-cols-2 gap-3">
            <div v-for="s in summaryCards" :key="s.label" class="text-center p-3 rounded-xl transition-colors" :class="s.bg">
              <p class="text-2xl font-black transition-colors" :class="s.textColor">{{ s.count }}</p>
              <p class="text-[9px] font-bold text-slate-400 uppercase">{{ s.label }}</p>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-br from-slate-900 to-slate-800 rounded-[2rem] p-6 text-white">
          <h4 class="text-sm font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-500 mb-3">
            How it works
          </h4>
          <ul class="space-y-3 text-slate-300 text-xs">
            <li class="flex gap-2"><i class="fa fa-check-circle text-indigo-400 mt-0.5 shrink-0"></i><span>Choose an application type and fill the form.</span></li>
            <li class="flex gap-2"><i class="fa fa-check-circle text-indigo-400 mt-0.5 shrink-0"></i><span>Your application goes through approval steps set by admin.</span></li>
            <li class="flex gap-2"><i class="fa fa-check-circle text-indigo-400 mt-0.5 shrink-0"></i><span>Track progress in real-time with the timeline below each card.</span></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Type selector modal -->
    <TypeSelector v-if="showTypeSelector" :types="availableTypes" @close="showTypeSelector = false" @select="onTypeSelected" />

    <!-- Form modals -->
    <NocModal v-if="activeModal === 'noc'" @close="activeModal = null" @submitted="onSubmitted" />
    <RequestModal v-if="activeModal === 'request'" @close="activeModal = null" @submitted="onSubmitted" />
    <LeaveModal v-if="activeModal === 'leave'" @close="activeModal = null" @submitted="onSubmitted" />
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from '~/composables/api/useFrappeFetch'
import TypeSelector from './TypeSelector.vue'
import NocModal from './NocModal.vue'
import RequestModal from './RequestModal.vue'
import LeaveModal from './LeaveModal.vue'

const loading = ref(false)
const myApps = ref([])
const availableTypes = ref([])
const visibleLimit = ref(10)
const activeFilter = ref('all')
const showTypeSelector = ref(false)
const activeModal = ref(null)

const onTypeSelected = (key) => {
  showTypeSelector.value = false
  activeModal.value = key
}

const onSubmitted = () => {
  activeModal.value = null
  fetchApps()
}

const fetchApps = async () => {
  loading.value = true
  try {
    myApps.value = (await call('vidyaan.api_folder.applications.get_my_applications')) || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const fetchTypes = async () => {
  try {
    availableTypes.value = (await call('vidyaan.api_folder.applications.get_available_application_types')) || []
  } catch (e) { console.error(e) }
}

onMounted(() => { fetchApps(); fetchTypes() })

const filterTabs = computed(() => [
  { id: 'all', label: 'All' },
  { id: 'noc', label: 'NOC' },
  { id: 'leave', label: 'Leave' },
  { id: 'request', label: 'Requests' },
])

const filteredApps = computed(() => {
  if (activeFilter.value === 'all') return myApps.value
  return myApps.value.filter(a => a.key === activeFilter.value)
})

const displayedApps = computed(() => filteredApps.value.slice(0, visibleLimit.value))

const pendingStatuses = ['Pending', 'Open', 'In Progress', 'In Review', 'Draft', 'Pending Approval']
const approvedStatuses = ['Approved', 'Resolved', 'Closed']
const rejectedStatuses = ['Rejected', 'Cancelled']

const summaryCards = computed(() => [
  { label: 'Total', count: myApps.value.length, bg: 'bg-slate-50 dark:bg-slate-800', textColor: 'text-slate-800 dark:text-slate-100' },
  { label: 'Pending', count: myApps.value.filter(a => pendingStatuses.includes(a.status)).length, bg: 'bg-amber-50 dark:bg-amber-900/20', textColor: 'text-amber-600' },
  { label: 'Approved', count: myApps.value.filter(a => approvedStatuses.includes(a.status)).length, bg: 'bg-green-50 dark:bg-green-900/20', textColor: 'text-green-600' },
  { label: 'Rejected', count: myApps.value.filter(a => rejectedStatuses.includes(a.status)).length, bg: 'bg-red-50 dark:bg-red-900/20', textColor: 'text-red-600' },
])

// ─── Helpers ──────────────────────────────────────────────────────────────────

const fmtDate = (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : ''
const stripHtml = (h) => h ? h.replace(/<[^>]*>/g, '').slice(0, 150) : ''
const isTerminal = (s) => approvedStatuses.includes(s) || rejectedStatuses.includes(s)
const isApproved = (s) => approvedStatuses.includes(s)

const stepIndex = (status, steps) => {
  const idx = steps.findIndex(s => s.state === status)
  return idx >= 0 ? idx : -1
}

const progressWidth = (app) => {
  const steps = app.workflow_steps
  if (!steps.length) return '0%'
  const idx = stepIndex(app.status, steps)
  if (idx < 0) return '0%'
  if (isTerminal(app.status)) return '100%'
  const pct = Math.round((idx / (steps.length - 1)) * 100)
  return `${Math.min(pct, 100)}%`
}

const isStepDone = (state, status, steps, i) => {
  if (isTerminal(status)) return isApproved(status) || i < steps.length - 1
  const currentIdx = stepIndex(status, steps)
  return i < currentIdx
}

const isStepCurrent = (state, status) => state === status

const isStepActive = (state, status, steps, i) => {
  const currentIdx = stepIndex(status, steps)
  return i <= currentIdx || isTerminal(status)
}

const stepDotClass = (state, status, steps, i) => {
  if (isStepDone(state, status, steps, i)) {
    return isApproved(status) || !isTerminal(status)
      ? 'bg-green-500 border-green-500 text-white'
      : 'bg-red-500 border-red-500 text-white'
  }
  if (isStepCurrent(state, status)) {
    if (rejectedStatuses.includes(status)) return 'bg-red-500 border-red-500 text-white'
    if (approvedStatuses.includes(status)) return 'bg-green-500 border-green-500 text-white'
    return 'bg-indigo-500 border-indigo-500 text-white animate-pulse'
  }
  return 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-400'
}

const typeBadgeClass = (key) => ({
  noc: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 border-purple-100 dark:border-purple-800/50',
  leave: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800/50',
  request: 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 border-indigo-100 dark:border-indigo-800/50',
}[key] || 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700')

const priorityClass = (p) => ({
  Urgent: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/50',
  High: 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50',
}[p] || '')

const statusClass = (s) => {
  if (approvedStatuses.includes(s)) return 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/50'
  if (rejectedStatuses.includes(s)) return 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/50'
  if (pendingStatuses.includes(s)) return 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50'
  return 'bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700'
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
