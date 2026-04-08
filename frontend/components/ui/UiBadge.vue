<template>
  <span
    :class="[
      'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest',
      variantClass,
    ]"
  >
    <i v-if="icon" :class="[icon, 'text-[9px]']"></i>
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  variant?: 'info' | 'success' | 'warning' | 'danger' | 'neutral' | 'indigo' | 'cyan'
  icon?: string
}>(), {
  variant: 'neutral',
})

const variantClass = computed(() => {
  const map: Record<string, string> = {
    info:    'bg-sky-100 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300',
    success: 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300',
    warning: 'bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300',
    danger:  'bg-rose-100 dark:bg-rose-900/40 text-rose-700 dark:text-rose-300',
    neutral: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300',
    indigo:  'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300',
    cyan:    'bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300',
  }
  return map[props.variant]
})
</script>
