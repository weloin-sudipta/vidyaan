<template>
  <div class="bg-white rounded-[2.5rem] p-8 border border-slate-100 shadow-sm">
    
    <div class="flex justify-between items-center mb-6">
      <h3 class="font-black text-lg text-slate-800">Recommended For You</h3>
      <i class="fa fa-lightbulb text-indigo-500"></i>
    </div>

    <div class="space-y-5">
      <div 
        v-for="book in recommendedBooks" 
        :key="book.id"
        class="flex items-center gap-4 p-4 rounded-2xl hover:bg-slate-50 transition"
      >
        <div class="w-12 h-16 bg-slate-200 rounded-lg flex items-center justify-center text-slate-400">
          <i class="fa fa-book"></i>
        </div>

        <div class="flex-1">
          <h4 class="text-sm font-bold text-slate-800 leading-tight">
            {{ book.title }}
          </h4>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            {{ book.category }}
          </p>
        </div>

        <button 
          class="text-[10px] font-black text-indigo-600 hover:underline"
          @click="$emit('select', book)"
        >
          View
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({
  recommendedBooks: {
    type: Array,
    default: () => []
  }
})
</script>