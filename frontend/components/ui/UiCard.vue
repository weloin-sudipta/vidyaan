<template>
  <component :is="as" :class="computedClasses">
    <slot></slot>
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'default', // 'default', 'dark', 'light', 'transparent'
  },
  padding: {
    type: String,
    default: 'p-8', // e.g., 'p-6', 'p-4', 'p-12', 'none'
  },
  rounded: {
    type: String,
    default: 'rounded-[2.5rem]', // e.g., 'rounded-2xl', 'rounded-3xl', 'none'
  },
  as: {
    type: String,
    default: 'div', // e.g., 'header', 'section', 'article', 'form'
  }
})

const computedClasses = computed(() => {
  const baseClasses = 'shadow-sm'
  
  let variantClasses = ''
  if (props.variant === 'default') {
    variantClasses = 'bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800'
  } else if (props.variant === 'dark') {
    variantClasses = 'bg-slate-900 dark:bg-black border-none shadow-xl text-white'
  } else if (props.variant === 'light') {
    variantClasses = 'bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700'
  } else if (props.variant === 'transparent') {
    variantClasses = 'bg-transparent border border-slate-200/60 dark:border-slate-800'
  }

  const paddingClass = props.padding === 'none' ? '' : props.padding
  const roundedClass = props.rounded === 'none' ? '' : props.rounded

  return [baseClasses, variantClasses, paddingClass, roundedClass]
})
</script>
