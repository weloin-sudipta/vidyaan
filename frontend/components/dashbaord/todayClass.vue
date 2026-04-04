<template>
  <div class="space-y-6 bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none relative overflow-hidden group transition-colors">
    <div class="flex items-center justify-between px-2">
      <h3 class="text-xl font-black text-slate-800 dark:text-slate-100 tracking-tight">Today's Schedule</h3>
      <NuxtLink
        to="/academics/timetable"
        class="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-800 transition-colors px-3 py-1.5 rounded-full flex items-center gap-1.5"
      >
        Full Schedule <i class="fa fa-arrow-right text-[9px]"></i>
      </NuxtLink>
    </div>

    <div v-if="todayClasses && todayClasses.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="(cls, i) in todayClasses"
        :key="i"
        class="relative p-5 rounded-[2rem] border flex items-center gap-4 transition-all overflow-hidden"
        :class="{
          'bg-green-50 border-green-200 shadow-sm shadow-green-100 dark:bg-green-900/20 dark:border-green-700/50 dark:shadow-none': getStatus(cls) === 'live',
          'bg-slate-50 border-slate-100 opacity-60 dark:bg-slate-800/40 dark:border-slate-700': getStatus(cls) === 'done',
          'bg-white border-slate-100 hover:shadow-xl dark:bg-slate-900 dark:border-slate-800 dark:hover:shadow-xl': getStatus(cls) === 'upcoming',
        }"
      >

        <!-- ICON BOX -->
        <div
          class="w-12 h-12 rounded-2xl flex flex-col items-center justify-center flex-shrink-0 transition-colors"
          :class="{
            'bg-green-500 shadow-lg shadow-green-200 dark:shadow-none': getStatus(cls) === 'live',
            'bg-slate-200 dark:bg-slate-700': getStatus(cls) === 'done',
            'bg-slate-50 dark:bg-slate-800': getStatus(cls) === 'upcoming',
          }"
        >
          <!-- LIVE -->
          <template v-if="getStatus(cls) === 'live'">
            <i class="fa fa-clock-o text-white text-sm"></i>
            <span class="text-[7px] font-black uppercase text-white flex items-center gap-0.5 mt-0.5">
              <span class="w-1 h-1 rounded-full bg-white animate-pulse"></span> Live
            </span>
          </template>

          <!-- DONE -->
          <template v-else-if="getStatus(cls) === 'done'">
            <i class="fa fa-check text-slate-400 dark:text-slate-500 text-sm"></i>
            <span class="text-[7px] font-black uppercase mt-0.5 text-slate-400 dark:text-slate-500">Done</span>
          </template>

          <!-- UPCOMING -->
          <template v-else>
            <i class="fa fa-clock-o text-violet-400 dark:text-violet-500 text-sm"></i>
            <span class="text-[7px] font-black uppercase mt-0.5 text-violet-400 dark:text-violet-500">Soon</span>
          </template>
        </div>

        <!-- CONTENT -->
        <div class="flex-1 min-w-0">
          <h4
            class="text-sm font-black truncate"
            :class="{
              'text-green-700 dark:text-green-400': getStatus(cls) === 'live',
              'text-slate-400 line-through dark:text-slate-500': getStatus(cls) === 'done',
              'text-slate-800 dark:text-slate-100': getStatus(cls) === 'upcoming',
            }"
          >
            {{ cls.subject }}
          </h4>
          <p class="text-[10px] font-bold uppercase mt-0.5" :class="{'text-slate-400 dark:text-slate-500': true}">
            {{ cls.startTime || cls.time }}
            <span v-if="cls.endTime"> – {{ cls.endTime }}</span>
            <span v-if="cls.room"> • Room {{ cls.room }}</span>
          </p>
          <span
            v-if="cls.teacher"
            class="text-[9px] font-bold mt-1 block truncate"
            :class="{
              'text-green-500 dark:text-green-400': getStatus(cls) === 'live',
              'text-slate-300 dark:text-slate-500': getStatus(cls) === 'done',
              'text-violet-400 dark:text-violet-500': getStatus(cls) === 'upcoming',
            }"
          >
            <i class="fa fa-user mr-1 opacity-60"></i>{{ cls.teacher }}
          </span>
        </div>

        <!-- LIVE PING DECORATION -->
        <div v-if="getStatus(cls) === 'live'" class="absolute top-3 right-3 w-2 h-2">
          <span class="absolute inset-0 rounded-full bg-green-400 animate-ping opacity-75"></span>
          <span class="absolute inset-0 rounded-full bg-green-500"></span>
        </div>

      </div>
    </div>

    <!-- EMPTY STATE -->
    <div
      v-else
      class="bg-white dark:bg-slate-900 rounded-[2rem] border border-dashed border-slate-200 dark:border-slate-700 p-12 flex flex-col items-center gap-2 text-slate-300 dark:text-slate-500"
    >
      <i class="fa fa-coffee text-2xl"></i>
      <p class="text-[10px] font-black uppercase tracking-widest">No classes today</p>
    </div>
  </div>
</template>
<script setup>
const props = defineProps(['todayClasses'])

const getStatus = (cls) => {
  const now = new Date()
  const toMinutes = (t) => {
    if (!t) return null
    const [h, m] = t.split(':').map(Number)
    return h * 60 + m
  }

  const start = toMinutes(cls.startTime || cls.time)
  const end   = toMinutes(cls.endTime)
  const curr  = now.getHours() * 60 + now.getMinutes()

  if (start === null) return 'upcoming'
  if (end && curr > end) return 'done'
  if (curr >= start && (!end || curr <= end)) return 'live'
  return 'upcoming'
}
</script>