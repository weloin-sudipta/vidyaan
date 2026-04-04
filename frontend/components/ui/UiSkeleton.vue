<template>
  <div :class="['relative overflow-hidden bg-slate-200/50 dark:bg-slate-800/80 rounded-2xl', height, width]">
    <div class="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/80 dark:via-slate-700/50 to-transparent animate-shimmer"></div>
  </div>
</template>

<script setup>
defineProps({
  height: {
    type: String,
    default: 'h-4'
  },
  width: {
    type: String,
    default: 'w-full'
  }
})
</script>

<style scoped>
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}
.animate-shimmer {
  animation: shimmer 1.5s infinite;
}
</style>
