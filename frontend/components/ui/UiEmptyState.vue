<template>
  <div
    class="flex flex-col items-center justify-center py-16 px-6 text-center bg-white dark:bg-slate-800/60 rounded-2xl border border-dashed border-slate-200 dark:border-slate-700"
  >
    <!-- Icon bubble -->
    <div
      class="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/40 dark:to-purple-900/40 flex items-center justify-center mb-5 shadow-inner"
    >
      <i :class="[icon, 'text-2xl text-indigo-500 dark:text-indigo-400']"></i>
    </div>

    <h3 class="text-base font-black text-slate-700 dark:text-slate-200 mb-2 uppercase tracking-wide">
      {{ title }}
    </h3>

    <p v-if="message" class="text-sm text-slate-400 dark:text-slate-500 max-w-xs leading-relaxed mb-5">
      {{ message }}
    </p>

    <!-- Optional action slot -->
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string
  title?: string
  message?: string
}>(), {
  icon: 'fa-solid fa-inbox',
  title: 'Nothing here yet',
})
</script>
