<template>
  <Transition name="fade">
    <div v-if="modelValue" class="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8">
      
      <div 
        class="absolute inset-0 bg-slate-900/60 backdrop-blur-md"
        @click="close"
      ></div>

      <Transition name="zoom">
        <div
          class="relative bg-white w-full max-w-2xl rounded-[2.5rem] shadow-2xl overflow-hidden border border-slate-200/50 flex flex-col"
        >
          
          <div class="p-8 border-b border-slate-50 flex justify-between items-center bg-slate-50/30">
            <div>
              <p class="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em] mb-1">Resource View</p>
              <h3 class="text-xl font-black text-slate-800 tracking-tight">
                {{ title }}
              </h3>
            </div>

            <button @click="close" class="w-10 h-10 rounded-xl bg-white border border-slate-200 text-slate-400 hover:text-rose-500 hover:border-rose-100 transition-all flex items-center justify-center shadow-sm">
              <i class="fa fa-times"></i>
            </button>
          </div>

          <div class="p-8 max-h-[70vh] overflow-y-auto custom-scrollbar bg-white">
            <slot />
          </div>

          <div v-if="$slots.footer" class="p-8 bg-slate-50/50 border-t border-slate-50 flex justify-end gap-3">
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
    default: "Information"
  }
})

const emit = defineEmits(["update:modelValue"])

const close = () => {
  emit("update:modelValue", false)
}
</script>

<style scoped>
/* High-Performance Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.zoom-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.zoom-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

/* Matching Dashboard Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
</style>