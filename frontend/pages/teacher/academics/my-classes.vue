<template>
  <div class="p-6 lg:p-10 max-w-7xl mx-auto custom-scrollbar animate-in fade-in slide-in-from-bottom-4 duration-500">
    
    <!-- Header -->
    <HeroHeader title="My Classes" subtitle="Assigned Sections" icon="fa fa-users">
      <div class="flex gap-2">
        
        <!-- ✅ Program Filter -->
        <select 
          v-model="selectedProgram"
          class="bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest border border-transparent dark:border-indigo-800 outline-none"
        >
          <option value="">All Programs</option>
          <option v-for="p in programs" :key="p" :value="p">
            {{ p }}
          </option>
        </select>

      </div>
    </HeroHeader>

    <!-- Loading -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
      <UiSkeleton v-for="n in 3" :key="n" height="h-48" class="rounded-[2.5rem]" />
    </div>

    <!-- Classes -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
      
      <div 
        v-for="cls in filteredClasses" 
        :key="cls.id" 
        class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-sm hover:shadow-xl hover:border-indigo-200 dark:hover:border-indigo-500/30 transition-all group cursor-pointer"
      >
        
        <!-- Top -->
        <div class="flex justify-between items-start mb-6">
          <div class="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center group-hover:bg-indigo-500 transition-colors">
            <i class="fa fa-book text-indigo-500 dark:text-indigo-400 group-hover:text-white transition-colors"></i>
          </div>

          <span class="px-3 py-1 bg-slate-50 dark:bg-slate-800 rounded-full text-[10px] font-black uppercase text-slate-500 dark:text-slate-400 tracking-widest border border-slate-100 dark:border-slate-700">
            {{ cls.section }}
          </span>
        </div>

        <!-- Content -->
        <h3 class="text-xl font-black text-slate-800 dark:text-slate-100 mb-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
          {{ cls.subject }}
        </h3>

        <p class="text-xs font-bold text-slate-400 dark:text-slate-500 mb-2">
          {{ cls.program }}
        </p>

        <p class="text-xs font-bold text-slate-400 dark:text-slate-500 mb-3 flex items-center gap-2">
          <i class="fa fa-map-marker"></i> {{ cls.room }}
        </p>

        <p class="text-[10px] text-slate-400 font-bold mb-6">
          {{ cls.from_time }} - {{ cls.to_time }}
        </p>

        <!-- Bottom -->
        <div class="flex justify-between items-end border-t border-slate-50 dark:border-slate-800/50 pt-4">
          <div>
            <span class="block text-[10px] uppercase font-black text-slate-400 tracking-widest mb-1">
              Students
            </span>
            <span class="text-lg font-black text-slate-800 dark:text-slate-200">
              {{ cls.students }}
            </span>
          </div>

          <div class="text-right">
            <span class="block text-[10px] uppercase font-black text-slate-400 tracking-widest mb-1">
              Instructor
            </span>
            <span class="text-xs font-black text-indigo-500">
              {{ cls.instructor }}
            </span>
          </div>
        </div>

      </div>

      <!-- Empty State -->
      <div v-if="filteredClasses.length === 0" class="col-span-full text-center py-20 text-slate-400 font-bold uppercase text-xs tracking-widest">
        No classes found
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import UiSkeleton from '~/components/ui/UiSkeleton.vue'
import { useTeacherClasses } from '~/composable/useTeacherClasses'

const { fetchclassSchedule } = useTeacherClasses()

const loading = ref(true)
const classes = ref([])
const selectedProgram = ref('')

onMounted(async () => {
  const res = await fetchclassSchedule()

  if (res?.success) {
    classes.value = res.classes.map(cls => ({
      id: cls.name,
      subject: cls.course,
      section: cls.student_group,
      room: cls.room,
      students: cls.total_students,
      program: cls.program,
      instructor: cls.instructor_name,
      from_time: cls.from_time,
      to_time: cls.to_time
    }))
  }

  loading.value = false
})

/* ✅ Unique programs */
const programs = computed(() => {
  return [...new Set(classes.value.map(c => c.program))]
})

/* ✅ Filter logic */
const filteredClasses = computed(() => {
  if (!selectedProgram.value) return classes.value
  return classes.value.filter(c => c.program === selectedProgram.value)
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 5px; height: 5px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 99px; }
.dark .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; }
</style>