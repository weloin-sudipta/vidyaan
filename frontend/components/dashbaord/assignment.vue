<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2rem] p-6 border border-slate-200 dark:border-slate-800 shadow-sm dark:shadow-none transition-colors">

    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-xs font-black uppercase tracking-wide text-slate-400 dark:text-slate-500">Assignments</h3>
      <NuxtLink to="/academics/assignments" class="text-indigo-500 dark:text-indigo-400 text-xs font-bold hover:underline transition-colors">
        View All
      </NuxtLink>
    </div>

    <!-- Assignment List -->
    <div class="space-y-4">
      <div
        v-for="assignment in assignments"
        :key="assignment.name"
        class="flex justify-between items-center p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-100 dark:border-slate-700/50 transition-colors"
      >

        <!-- Info Section -->
        <div class="flex-1">
          <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ assignment.title }}</p>
          <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">
            Topic: {{ assignment.topic_name || 'N/A' }}
          </p>
          <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">
            Course: {{ assignment.course_name || assignment.course || 'N/A' }}
          </p>
          <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">
            Due: {{ formatDate(assignment.due_date) }}
          </p>
        </div>

        <!-- STATUS BADGE -->
        <span class="text-[9px] font-black uppercase tracking-widest px-2 py-1 rounded-full flex-shrink-0"
          :class="getStatusBadgeClass(assignment.status)">
          {{ assignment.status || 'Pending' }}
        </span>

      </div>

      <div v-if="assignments.length === 0" class="text-center text-sm text-slate-400 dark:text-slate-500 py-6">
        No upcoming assignments
      </div>
    </div>

  </div>
</template>

<script setup>
const props = defineProps({
  assignments: {
    type: Array,
    default: () => []
  }
})

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  return new Date(dateStr).toLocaleDateString('default', { day: '2-digit', month: 'short', year: 'numeric' })
}

const getDotColor = (status) => {
  switch ((status || '').toLowerCase()) {
    case 'submitted': return 'bg-green-500'
    case 'active':    return 'bg-amber-500'
    case 'pending':   return 'bg-slate-400'
    default:          return 'bg-slate-400'
  }
}

const getStatusBadgeClass = (status) => {
  switch ((status || '').toLowerCase()) {
    case 'submitted': return 'bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400'
    case 'active': return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400'
    case 'pending': return 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
    default: return 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
  }
}
</script>