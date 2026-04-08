<template>
  <div class="bg-white dark:bg-slate-900 rounded-[3rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none relative overflow-hidden group transition-colors">
    
    <div class="flex flex-col items-center mb-5 relative z-10">
      <h3 class="text-[10px] font-black uppercase tracking-[0.4em] text-slate-400 dark:text-slate-500 mb-3">
        Focus Session
      </h3>
      <div class="flex items-center gap-2 px-3 py-1 bg-indigo-50 dark:bg-indigo-900/20 rounded-full transition-colors">
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 dark:bg-indigo-400" :class="{ 'animate-pulse': isActive }"></span>
        <span class="text-[9px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">
          {{ isActive ? 'Deep Work Active' : 'Idle' }}
        </span>
      </div>
    </div>

    <div class="relative flex items-center justify-center mb-10">
      <svg class="w-48 h-48 -rotate-90">
        <circle cx="96" cy="96" r="88" stroke="currentColor" stroke-width="6" fill="transparent" class="text-slate-50 dark:text-slate-800 transition-colors" />
        <circle cx="96" cy="96" r="88" stroke="currentColor" stroke-width="8" fill="transparent"
                stroke-dasharray="552.9" :stroke-dashoffset="progressOffset"
                stroke-linecap="round"
                class="transition-all duration-1000"
                :class="isActive ? 'text-indigo-600 dark:text-indigo-500' : 'text-slate-200 dark:text-slate-600'" />
      </svg>

      <div class="absolute flex flex-col items-center">
        <div class="text-5xl font-black text-slate-900 dark:text-white tracking-tighter tabular-nums">
          {{ formatTime(minutes) }}<span class="text-indigo-600 dark:text-indigo-400 animate-pulse">:</span>{{ formatTime(seconds) }}
        </div>
        <p class="text-[9px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1">Minutes left</p>
      </div>
    </div>

    <div class="flex items-center justify-center gap-4 relative z-10">

  <button @click="resetTimer"
    class="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-slate-800 text-slate-400 dark:text-slate-500 hover:text-rose-500 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-900/20 transition-all flex items-center justify-center">
    <i class="fa fa-refresh"></i>
  </button>

  <button @click="toggleTimer"
    class="h-14 px-8 rounded-[1.5rem] flex items-center gap-3 transition-all active:scale-95 shadow-lg shadow-indigo-100 dark:shadow-none"
    :class="isActive ? 'bg-slate-900 dark:bg-slate-700 text-white' : 'bg-indigo-600 text-white hover:bg-indigo-700 dark:hover:bg-indigo-500'">

    <i class="fa" :class="isActive ? 'fa-pause' : 'fa-play'"></i>

    <span class="text-[10px] font-black uppercase tracking-widest">
      {{ isActive ? 'Pause' : 'Start Focus' }}
    </span>

  </button>

  <!-- +5 MIN BUTTON -->

  <button @click="addFiveMinutes"
    class="h-12 px-4 rounded-2xl bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 hover:bg-slate-700 dark:hover:bg-slate-600 dark:hover:text-white transition-all flex items-center gap-2 text-[10px] font-black uppercase tracking-widest">

    <i class="fa fa-plus"></i>
    5 Min

  </button>

</div>
    <i class="fa fa-stopwatch absolute -right-8 -bottom-8 text-9xl text-slate-50/50 dark:text-slate-800/50 -rotate-12 pointer-events-none group-hover:text-indigo-50 dark:group-hover:text-indigo-900/10 transition-colors"></i>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'

const minutes = ref(25)
const seconds = ref(0)
const isActive = ref(false)
let timer = null

const totalInitialSeconds = ref(25 * 60)

const formatTime = (val) => val.toString().padStart(2, '0')

/* PROGRESS RING */

const progressOffset = computed(() => {
  const currentTotal = (minutes.value * 60) + seconds.value
  return 552.9 - (currentTotal / totalInitialSeconds.value) * 552.9
})


/* TIMER START / PAUSE */

const toggleTimer = () => {

  if (isActive.value) {
    clearInterval(timer)
    isActive.value = false
    return
  }

  isActive.value = true

  timer = setInterval(() => {

    if (seconds.value === 0) {

      if (minutes.value === 0) {
        clearInterval(timer)
        isActive.value = false
        return
      }

      minutes.value--
      seconds.value = 59

    } else {

      seconds.value--

    }

  }, 1000)

}


/* RESET */

const resetTimer = () => {

  clearInterval(timer)
  isActive.value = false
  minutes.value = 25
  seconds.value = 0
  totalInitialSeconds.value = 25 * 60

}


/* ADD +5 MINUTES */

const addFiveMinutes = () => {

  minutes.value += 5
  totalInitialSeconds.value += 5 * 60

}


/* CLEANUP */

onUnmounted(() => {
  clearInterval(timer)
})

</script>

<style scoped>
/* Tabular nums ensure the timer doesn't "jump" when numbers change width */
.tabular-nums {
  font-variant-numeric: tabular-nums;
}
</style>