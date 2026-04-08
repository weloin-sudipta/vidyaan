<template>
  <div class="relative inline-flex shrink-0" :class="sizeWrap">
    <img
      v-if="src"
      :src="src"
      :alt="name"
      :class="['rounded-2xl object-cover ring-2 ring-white dark:ring-slate-700 shadow-md', sizeClass]"
      @error="imgError = true"
    />
    <div
      v-else
      :class="[
        'rounded-2xl flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white font-black ring-2 ring-white dark:ring-slate-700 shadow-md',
        sizeClass,
        initialsTextSize,
      ]"
    >
      {{ initials }}
    </div>

    <!-- Online indicator -->
    <span
      v-if="online"
      :class="[
        'absolute bottom-0 right-0 block rounded-full bg-emerald-400 ring-2 ring-white dark:ring-slate-800',
        dotSize,
      ]"
    ></span>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = withDefaults(defineProps<{
  src?: string
  name?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  online?: boolean
}>(), {
  name: '?',
  size: 'md',
  online: false,
})

const imgError = ref(false)

const initials = computed(() => {
  const parts = (props.name ?? '?').trim().split(/\s+/)
  if (parts.length >= 2) return ((parts[0]?.[0] ?? '') + (parts[parts.length - 1]?.[0] ?? '')).toUpperCase()
  return (parts[0]?.[0] ?? '?').toUpperCase()
})

const sizeMap: Record<string, string> = {
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-14 h-14',
  xl: 'w-20 h-20',
}

const sizeWrap = computed(() => sizeMap[props.size])
const sizeClass = computed(() => sizeMap[props.size])

const initialsTextSize = computed(() => {
  const map: Record<string, string> = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-lg',
    xl: 'text-2xl',
  }
  return map[props.size]
})

const dotSize = computed(() => {
  const map: Record<string, string> = {
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
    lg: 'w-3 h-3',
    xl: 'w-4 h-4',
  }
  return map[props.size]
})
</script>
