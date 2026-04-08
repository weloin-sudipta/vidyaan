<template>
  <div class="min-h-screen bg-[#F8FAFC] dark:bg-black p-4 lg:p-10 font-sans text-slate-900 dark:text-slate-100 transition-colors">
    <div class="max-w-[1440px] mx-auto space-y-8">

      <HeroHeader title="My Students" subtitle="Program Enrollments Directory" icon="fa fa-users" />

      <!-- Search + Filters bar -->
      <div class="animate-in">
        <div
          class="bg-white dark:bg-slate-800 rounded-[2.5rem] p-4 border border-slate-200/60 dark:border-slate-700 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4 transition-colors"
        >
          <div class="flex items-center gap-4 ml-2">
            <div class="w-12 h-12 bg-indigo-50 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center text-xl transition-colors">
              <i class="fa fa-search"></i>
            </div>
            <div>
              <h2 class="text-2xl font-black text-slate-800 dark:text-slate-100 tracking-tight transition-colors">
                Student Search
              </h2>
              <p class="text-xs font-black text-slate-400 dark:text-slate-400 uppercase tracking-widest transition-colors">
                Find by name, ID or program
              </p>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <div class="relative w-full sm:w-72">
              <input
                v-model="search"
                type="text"
                placeholder="Start typing to filter..."
                class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-100 dark:border-slate-600 rounded-2xl py-3.5 px-6 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:bg-white focus:dark:bg-slate-800 focus:ring-4 focus:ring-indigo-500/10 transition-all"
              />
              <button
                v-if="search"
                @click="search = ''"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-rose-500 transition-colors"
                aria-label="Clear search"
              >
                <i class="fa fa-times text-xs"></i>
              </button>
            </div>

            <select
              v-model="selectedProgram"
              class="bg-slate-50 dark:bg-slate-700 border border-slate-100 dark:border-slate-600 rounded-2xl py-3.5 px-5 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-all"
            >
              <option value="">All Programs</option>
              <option v-for="prog in uniquePrograms" :key="prog" :value="prog">{{ prog }}</option>
            </select>

            <select
              v-model="selectedTerm"
              class="bg-slate-50 dark:bg-slate-700 border border-slate-100 dark:border-slate-600 rounded-2xl py-3.5 px-5 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-all"
            >
              <option value="">All Terms</option>
              <option v-for="term in uniqueTerms" :key="term" :value="term">{{ term }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Result count -->
      <div v-if="!loading" class="flex items-center justify-between px-2">
        <p class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500">
          Showing
          <span class="text-indigo-600 dark:text-indigo-400">{{ filtered.length }}</span>
          of {{ enrollments.length }} students
        </p>
        <button
          v-if="search || selectedProgram || selectedTerm"
          @click="clearFilters"
          class="text-[11px] font-black uppercase tracking-widest text-indigo-500 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
        >
          Clear filters
        </button>
      </div>

      <!-- Loading Skeleton -->
      <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <UiSkeleton height="h-64" v-for="i in 8" :key="i" class="rounded-[2.2rem]" />
      </div>

      <!-- Empty -->
      <div
        v-else-if="filtered.length === 0"
        class="bg-white dark:bg-slate-800 border border-slate-200/60 dark:border-slate-700 rounded-[2.2rem] p-12 text-center transition-colors"
      >
        <div class="w-16 h-16 mx-auto rounded-2xl bg-indigo-50 dark:bg-indigo-900/40 text-indigo-500 dark:text-indigo-300 flex items-center justify-center text-2xl mb-4">
          <i class="fa fa-user-slash"></i>
        </div>
        <p class="text-sm font-black uppercase tracking-widest text-slate-500 dark:text-slate-300">
          No students found
        </p>
        <button
          @click="clearFilters"
          class="mt-3 text-xs font-black text-indigo-500 hover:text-indigo-700 dark:hover:text-indigo-300 uppercase tracking-widest"
        >
          Clear filters
        </button>
      </div>

      <!-- Cards Grid -->
      <div
        v-else
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 animate-in"
      >
        <div
          v-for="enr in filtered"
          :key="enr.name"
          class="bg-white dark:bg-slate-800 rounded-[2.2rem] p-5 border border-slate-100 dark:border-slate-700 shadow-sm hover:shadow-xl hover:border-indigo-100/50 dark:hover:border-indigo-500/50 transition-all duration-500 group relative overflow-hidden flex flex-col justify-between"
        >
          <!-- Decorative blob -->
          <div
            class="absolute -right-6 -top-6 w-20 h-20 bg-slate-50 dark:bg-slate-700/50 rounded-full group-hover:bg-indigo-50/50 dark:group-hover:bg-indigo-900/40 transition-colors duration-500"
          ></div>

          <div class="relative z-10">
            <div class="flex justify-between items-center mb-4">
              <div class="relative">
                <!-- Avatar -->
                <div
                  class="h-16 w-16 rounded-2xl bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border-2 border-white shadow-sm group-hover:scale-105 transition-transform duration-500 font-black text-lg uppercase tracking-wide overflow-hidden"
                >
                  <img
                    v-if="enr.image"
                    :src="enr.image"
                    alt="avatar"
                    class="w-full h-full object-cover rounded-2xl"
                  />
                  <span v-else>{{ initials(enr.student_name) }}</span>
                </div>
                <div
                  class="absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 bg-emerald-500 border-2 border-white rounded-full shadow-sm"
                ></div>
              </div>

              <span
                class="px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest border shadow-sm bg-cyan-50 text-cyan-600 border-cyan-100 dark:bg-cyan-900/30 dark:text-cyan-300 dark:border-cyan-800"
              >
                Student
              </span>
            </div>

            <div class="space-y-1.5">
              <h3
                class="text-base font-black text-slate-900 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors leading-tight truncate"
                :title="enr.student_name"
              >
                {{ enr.student_name }}
              </h3>
              <p
                class="text-[11px] text-slate-400 dark:text-slate-300 font-black uppercase tracking-widest flex items-center gap-2 transition-colors truncate"
                :title="enr.program"
              >
                <span class="w-2 h-[1px] bg-indigo-300 dark:bg-indigo-500 shrink-0"></span>
                {{ enr.program || '—' }}
              </p>
            </div>

            <div class="mt-3 mb-4 space-y-2">
              <div class="flex items-center gap-2">
                <div
                  class="w-6 h-6 rounded-lg bg-slate-50 dark:bg-slate-700 flex items-center justify-center transition-colors"
                >
                  <i class="fa fa-calendar-o text-[11px] text-slate-400 dark:text-slate-300"></i>
                </div>
                <span class="text-xs font-bold text-slate-500 dark:text-slate-400 truncate">
                  {{ enr.academic_term || '—' }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <div
                  class="w-6 h-6 rounded-lg bg-slate-50 dark:bg-slate-700 flex items-center justify-center transition-colors"
                >
                  <i class="fa fa-clock-o text-[11px] text-slate-400 dark:text-slate-300"></i>
                </div>
                <span class="text-xs font-bold text-slate-500 dark:text-slate-400 truncate">
                  Enrolled {{ formatDate(enr.enrollment_date) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Footer chips -->
          <div class="pt-3 border-t border-slate-50 dark:border-slate-700 transition-colors">
            <div class="flex flex-wrap gap-1 items-center">
              <span
                v-if="enr.academic_year"
                class="px-2.5 py-1 text-[10px] font-black text-slate-500 dark:text-slate-300 bg-slate-50 dark:bg-slate-700 border border-slate-100 dark:border-slate-600 rounded-md group-hover:bg-white dark:group-hover:bg-slate-600 transition-colors"
              >
                {{ enr.academic_year }}
              </span>
              <span
                class="px-2.5 py-1 text-[10px] font-black text-slate-500 dark:text-slate-300 bg-slate-50 dark:bg-slate-700 border border-slate-100 dark:border-slate-600 rounded-md group-hover:bg-white dark:group-hover:bg-slate-600 transition-colors truncate max-w-[120px]"
                :title="enr.student"
              >
                {{ enr.student }}
              </span>
              <span
                class="ml-auto text-[10px] font-black text-slate-300 dark:text-slate-500 uppercase tracking-widest"
                :title="enr.name"
              >
                #{{ shortId(enr.name) }}
              </span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import UiSkeleton from '~/components/ui/UiSkeleton.vue'
import { fetchStudents } from '~/composables/student/useStudent'

// ── state ──────────────────────────────────────────────────────────────────
const loading = ref(true)
const enrollments = ref([])
const search = ref('')
const selectedProgram = ref('')
const selectedTerm = ref('')

// ── helpers ────────────────────────────────────────────────────────────────
const initials = (name = '') => {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0][0].toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

const formatDate = (d) =>
  d
    ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
    : '—'

const shortId = (id = '') => {
  if (!id) return ''
  const m = id.match(/(\d+)$/)
  return m ? m[1] : id.slice(-5)
}

const clearFilters = () => {
  search.value = ''
  selectedProgram.value = ''
  selectedTerm.value = ''
}

// ── filter options ─────────────────────────────────────────────────────────
const uniquePrograms = computed(() =>
  [...new Set(enrollments.value.map((e) => e.program).filter(Boolean))]
)
const uniqueTerms = computed(() =>
  [...new Set(enrollments.value.map((e) => e.academic_term).filter(Boolean))]
)

// ── filtered list ──────────────────────────────────────────────────────────
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return enrollments.value.filter((e) => {
    const matchSearch =
      !q ||
      e.student_name?.toLowerCase().includes(q) ||
      e.student?.toLowerCase().includes(q) ||
      e.program?.toLowerCase().includes(q)
    const matchProgram = !selectedProgram.value || e.program === selectedProgram.value
    const matchTerm = !selectedTerm.value || e.academic_term === selectedTerm.value
    return matchSearch && matchProgram && matchTerm
  })
})

// ── fetch ──────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    enrollments.value = await fetchStudents()
  } catch (err) {
    console.error('Failed to load enrollments:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.animate-in {
  animation: fadeUp 0.4s ease-out both;
}
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
