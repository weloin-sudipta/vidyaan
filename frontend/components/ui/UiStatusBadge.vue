<template>
  <span :class="computedClasses">
    <slot>{{ status }}</slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: 'md' // 'sm', 'md', 'lg'
  }
})

const computedClasses = computed(() => {
  const baseClasses = 'inline-flex items-center justify-center font-black uppercase tracking-wider rounded-xl transition-colors'
  
  let sizeClasses = ''
  if (props.size === 'sm') {
    sizeClasses = 'px-2 py-0.5 text-[9px]'
  } else if (props.size === 'md') {
    sizeClasses = 'px-3 py-1 text-[10px]'
  } else if (props.size === 'lg') {
    sizeClasses = 'px-4 py-2 text-xs'
  }

  const s = props.status?.toLowerCase() || ''
  let colorClasses = 'bg-slate-100 text-slate-500' // default

  if (['approved', 'success', 'present', 'p', 'completed', 'active'].includes(s)) {
    colorClasses = 'bg-green-100 text-green-600'
  } else if (['pending', 'in progress', 'leave', 'l', 'warning'].includes(s)) {
    colorClasses = 'bg-amber-100 text-amber-600'
  } else if (['rejected', 'absent', 'a', 'failed', 'error', 'overdue'].includes(s)) {
    colorClasses = 'bg-red-100 text-red-600'
  } else if (['info', 'new'].includes(s)) {
    colorClasses = 'bg-blue-100 text-blue-600'
  } else if (s === 'past') {
    colorClasses = 'bg-slate-100 text-slate-400 border border-slate-200'
  } else {
    // try to guess some generic categories
    if (['math', 'science', 'general'].includes(s)) {
       colorClasses = 'bg-purple-50 text-purple-600 border border-purple-100'
    } else {
       colorClasses = 'bg-indigo-50 text-indigo-600 border border-indigo-100' // default tags
    }
  }

  return `${baseClasses} ${sizeClasses} ${colorClasses}`
})
</script>
