<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>

    <div class="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-[2rem] shadow-2xl dark:shadow-none border border-slate-200 dark:border-slate-800 overflow-hidden transition-colors">

      <div class="p-6 border-b border-slate-100 dark:border-slate-800 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-black text-slate-800 dark:text-slate-100 transition-colors">New Application</h2>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Choose application type</p>
          </div>
          <button @click="$emit('close')" class="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <i class="fa fa-times"></i>
          </button>
        </div>
      </div>

      <div class="p-4 space-y-2 max-h-[50vh] overflow-y-auto">
        <button v-for="t in types" :key="t.key" @click="$emit('select', t.key)"
          class="w-full flex items-center gap-4 p-4 rounded-2xl border border-slate-100 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-indigo-700 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/10 transition-all text-left group">
          <div :class="iconBg(t.color)" class="w-11 h-11 rounded-xl flex items-center justify-center text-white shrink-0">
            <i :class="t.icon" class="text-lg"></i>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-black text-slate-800 dark:text-slate-100 transition-colors">{{ t.label }}</p>
            <p class="text-[10px] font-bold text-slate-400 mt-0.5">{{ t.description }}</p>
          </div>
          <i class="fa fa-chevron-right text-slate-300 dark:text-slate-600 group-hover:text-indigo-500 transition-colors"></i>
        </button>

        <div v-if="!types.length" class="p-8 text-center">
          <i class="fa fa-lock text-slate-200 dark:text-slate-700 text-4xl mb-3 block transition-colors"></i>
          <p class="text-xs font-black text-slate-400 uppercase">No application types available</p>
          <p class="text-[10px] text-slate-400 mt-1">Your administrator hasn't set up any application workflows yet.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ types: { type: Array, default: () => [] } })
defineEmits(['close', 'select'])

const iconBg = (color) => ({
  blue: 'bg-blue-600',
  purple: 'bg-purple-600',
  indigo: 'bg-indigo-600',
}[color] || 'bg-slate-600')
</script>
