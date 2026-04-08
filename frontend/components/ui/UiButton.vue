<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center gap-2 font-bold rounded-2xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-slate-900 select-none',
      sizeClass,
      variantClass,
      (disabled || loading) ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer',
    ]"
    v-bind="$attrs"
  >
    <i v-if="loading" class="fa-solid fa-circle-notch fa-spin"></i>
    <i v-else-if="icon" :class="icon"></i>
    <span v-if="loading && loadingText">{{ loadingText }}</span>
    <slot v-else />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  loadingText?: string
  disabled?: boolean
  icon?: string
  type?: 'button' | 'submit' | 'reset'
}>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  type: 'button',
})

const sizeClass = computed(() => {
  const map: Record<string, string> = {
    sm: 'text-xs px-4 py-2 rounded-xl',
    md: 'text-sm px-5 py-2.5',
    lg: 'text-base px-7 py-3.5',
  }
  return map[props.size]
})

const variantClass = computed(() => {
  const map: Record<string, string> = {
    primary:
      'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-md hover:shadow-indigo-200 dark:hover:shadow-indigo-900 focus:ring-indigo-500',
    secondary:
      'bg-transparent border-2 border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 focus:ring-slate-400',
    danger:
      'bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white shadow-md hover:shadow-rose-200 dark:hover:shadow-rose-900 focus:ring-rose-500',
    ghost:
      'bg-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 focus:ring-slate-400',
  }
  return map[props.variant]
})
</script>
