<template>
  <div class="flex items-center justify-center h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300">
    <div class="relative text-center">
      <div class="w-20 h-20 mx-auto mb-5 relative">
        <div class="absolute inset-0 border-4 border-dashed border-indigo-300 rounded-full animate-spin"></div>
        <div class="absolute inset-0 border-4 border-transparent border-t-indigo-600 border-r-indigo-600 rounded-full animate-spin"></div>
      </div>
      <p class="text-sm font-bold text-slate-500 dark:text-slate-400">Redirecting…</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from '#imports'

const router = useRouter()

onMounted(() => {
  router.replace('/dashboard')
})
</script>
