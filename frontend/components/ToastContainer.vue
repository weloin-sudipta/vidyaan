<template>
  <div class="fixed top-5 right-5 z-50 flex flex-col gap-3 pointer-events-none">
    <TransitionGroup name="toast">
      <div v-for="toast in toasts" :key="toast.id" 
           :class="['pointer-events-auto flex items-center gap-3 px-5 py-4 rounded-2xl shadow-xl border backdrop-blur-md transition-all min-w-[300px] max-w-sm', 
                    toast.type === 'error' ? 'bg-red-50/95 dark:bg-red-900/20 border-red-100 dark:border-red-900/30 text-red-600 dark:text-red-400' : 
                    toast.type === 'success' ? 'bg-emerald-50/95 dark:bg-emerald-900/20 border-emerald-100 dark:border-emerald-900/30 text-emerald-600 dark:text-emerald-400' : 
                    'bg-white/95 dark:bg-slate-800/95 border-slate-100 dark:border-slate-700 text-slate-700 dark:text-slate-100']">
        <i :class="toast.type === 'error' ? 'fa fa-exclamation-circle text-lg' : 'fa fa-check-circle text-lg'"></i>
        <div class="flex flex-col">
            <span class="text-xs font-black uppercase tracking-widest opacity-80 mb-0.5">
                {{ toast.type === 'error' ? 'System Error' : 'Success' }}
            </span>
            <span class="text-sm font-bold tracking-tight leading-snug">{{ toast.message }}</span>
        </div>
        <button @click="removeToast(toast.id)" class="ml-auto hover:opacity-70 transition-opacity p-2">
          <i class="fa fa-times text-xs opacity-60"></i>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '~/composable/useToast';
const { toasts, removeToast } = useToast();
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}
</style>
