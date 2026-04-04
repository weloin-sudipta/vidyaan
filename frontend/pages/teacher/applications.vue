<template>
  <div class="min-h-screen bg-gray-50 dark:bg-zinc-950 text-gray-900 dark:text-zinc-100 transition-colors duration-300">
    
    <div class="max-w-7xl mx-auto p-4 md:p-8">
      
      <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
        <div>
          <h1 class="text-3xl font-extrabold tracking-tight">Application Portal</h1>
          <p class="text-gray-500 dark:text-zinc-400 mt-1">Manage student leave and activity authorizations.</p>
        </div>
        
        <div class="flex items-center gap-3">
          <div class="hidden md:block text-right">
            <p class="text-sm font-medium">Term 2, 2026</p>
            <p class="text-xs text-gray-500 dark:text-zinc-500">Academic Year</p>
          </div>
          <div class="h-10 w-[1px] bg-gray-200 dark:bg-zinc-800 hidden md:block mx-2"></div>
          <button class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-medium shadow-sm transition-all">
            History Log
          </button>
        </div>
      </header>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <div v-for="stat in stats" :key="stat.label" 
             class="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 p-5 rounded-2xl shadow-sm">
          <p class="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-zinc-500">{{ stat.label }}</p>
          <div class="flex items-end justify-between mt-2">
            <h3 class="text-3xl font-bold">{{ stat.value }}</h3>
            <span :class="stat.trendColor" class="text-xs font-medium px-2 py-1 rounded-lg bg-opacity-10 dark:bg-opacity-20">
              {{ stat.trend }}
            </span>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-2xl shadow-sm overflow-hidden">
        <div class="p-6 border-b border-gray-100 dark:border-zinc-800 flex items-center justify-between">
          <h2 class="text-lg font-bold">Pending Requests</h2>
          <span class="text-xs bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 px-2.5 py-1 rounded-full font-bold">
            Needs Attention
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-gray-50/50 dark:bg-zinc-800/50 text-gray-500 dark:text-zinc-400 text-xs uppercase tracking-widest font-semibold">
                <th class="px-6 py-4">Student Info</th>
                <th class="px-6 py-4">Request Type</th>
                <th class="px-6 py-4">Timeline</th>
                <th class="px-6 py-4">Status</th>
                <th class="px-6 py-4 text-right">Decision</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-zinc-800">
              <tr v-for="item in applications" :key="item.id" class="group hover:bg-gray-50 dark:hover:bg-zinc-800/40 transition-colors">
                <td class="px-6 py-5">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-sm">
                      {{ item.initials }}
                    </div>
                    <div>
                      <div class="font-bold text-sm">{{ item.name }}</div>
                      <div class="text-xs text-gray-500 dark:text-zinc-500 leading-tight">{{ item.id }} • Grade 11</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-5">
                  <span :class="getTypeStyles(item.type)" class="text-[11px] font-black uppercase px-2 py-1 rounded">
                    {{ item.type }}
                  </span>
                </td>
                <td class="px-6 py-5">
                  <div class="text-sm font-medium">{{ item.date }}</div>
                  <div class="text-[11px] text-gray-400 dark:text-zinc-500">{{ item.days }} Day(s)</div>
                </td>
                <td class="px-6 py-5">
                  <div class="flex items-center gap-1.5">
                    <div class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                    <span class="text-xs font-medium text-amber-600 dark:text-amber-500 italic">Waiting</span>
                  </div>
                </td>
                <td class="px-6 py-5">
                  <div class="flex justify-end gap-3">
                    <button class="p-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20">
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                    <button class="bg-zinc-900 dark:bg-white text-white dark:text-zinc-900 px-4 py-2 rounded-lg text-xs font-bold hover:scale-105 transition-transform shadow-md">
                      Approve
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const stats = [
  { label: 'Total Pending', value: '24', trend: '+12%', trendColor: 'text-blue-600 bg-blue-50' },
  { label: 'Sick Leaves', value: '08', trend: '-2%', trendColor: 'text-red-600 bg-red-50' },
  { label: 'Outstation', value: '04', trend: 'Stable', trendColor: 'text-zinc-600 bg-zinc-50' },
  { label: 'Avg. Response', value: '2h', trend: 'Fast', trendColor: 'text-green-600 bg-green-50' },
];

const applications = [
  { id: 'APP-101', name: 'Marcus Wright', initials: 'MW', type: 'Medical', date: 'Oct 24, 2026', days: 2 },
  { id: 'APP-102', name: 'Elena Fisher', initials: 'EF', type: 'Activity', date: 'Oct 28, 2026', days: 1 },
  { id: 'APP-103', name: 'David Goggins', initials: 'DG', type: 'Personal', date: 'Nov 01, 2026', days: 5 },
];

const getTypeStyles = (type) => {
  switch (type) {
    case 'Medical': return 'bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-800';
    case 'Activity': return 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800';
    default: return 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700';
  }
};
</script>