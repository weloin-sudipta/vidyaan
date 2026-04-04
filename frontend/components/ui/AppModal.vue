<template>
  <Transition name="fade">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[100] flex items-center justify-center min-h-screen p-4 sm:p-6 overflow-y-auto"
    >
      
      <!-- Overlay -->
      <div 
        class="absolute inset-0 bg-slate-900/20 backdrop-blur-[3px]"
        @click="close"
      ></div>

      <!-- Modal Box -->
      <Transition name="zoom">
        <div
          :class="[
            'relative w-full mx-auto flex flex-col overflow-hidden',
            'bg-white/95 dark:bg-slate-900/95 backdrop-blur-2xl',
            'border border-white/50 dark:border-slate-800/50',
            'rounded-2xl sm:rounded-[2rem]',
            'shadow-[0_20px_60px_-15px_rgba(0,0,0,0.2)] dark:shadow-[0_20px_60px_-15px_rgba(0,0,0,0.6)]',
            maxWidth
          ]"
          :style="{ maxHeight: 'calc(100vh - 2rem)' }"
        >
          
          <!-- Header -->
          <div class="px-4 sm:px-8 py-4 sm:py-6 border-b border-slate-100/50 dark:border-slate-800/50 flex justify-between items-center bg-white/60 dark:bg-slate-900/60">
            <h3 class="text-sm sm:text-xl font-black tracking-tight text-slate-800 dark:text-white uppercase">
              {{ title }}
            </h3>

            <button 
              @click="close" 
              class="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30 transition-all flex items-center justify-center"
            >
              <i class="fa fa-times text-sm sm:text-lg"></i>
            </button>
          </div>

          <!-- Body -->
          <div class="p-4 sm:p-8 overflow-y-auto custom-scrollbar flex-1">
            <slot />
          </div>

          <!-- Footer -->
          <div 
            v-if="$slots.footer" 
            class="p-4 sm:p-6 bg-slate-50/60 dark:bg-slate-800/60 border-t border-slate-100/50 dark:border-slate-800/50 flex flex-col sm:flex-row justify-end gap-3 rounded-b-2xl sm:rounded-b-[2rem]"
          >
            <slot name="footer" />
          </div>

        </div>
      </Transition>

    </div>
  </Transition>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  title: {
    type: String,
    default: "Modal Title"
  },
  maxWidth: {
    type: String,
    default: "max-w-2xl"
  }
})

const emit = defineEmits(["update:modelValue"])

const close = () => {
  emit("update:modelValue", false)
}
</script>

<style scoped>
/* Fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Zoom */
.zoom-enter-active {
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.zoom-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}

/* Scrollbar */
.custom-scrollbar::-webkit-scrollbar { 
  width: 6px; 
}
.custom-scrollbar::-webkit-scrollbar-track { 
  background: transparent; 
}
.custom-scrollbar::-webkit-scrollbar-thumb { 
  background: #cbd5e1; 
  border-radius: 9999px; 
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb { 
  background: #334155; 
}
</style>