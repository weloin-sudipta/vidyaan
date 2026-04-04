<template>
  <div class="p-6 lg:p-10 max-w-6xl mx-auto">

    <!-- Header -->
    <HeroHeader title="My Students" subtitle="Program Enrollments" icon="fa fa-users">
      <div class="flex gap-3 flex-wrap">

        <!-- Search -->
        <div class="bg-white dark:bg-slate-900 rounded-xl flex items-center px-4 border border-slate-200 dark:border-slate-800 h-10">
          <i class="fa fa-search text-slate-400 text-xs"></i>
          <input
            v-model="search"
            type="text"
            placeholder="Search by name or ID..."
            class="w-48 bg-transparent border-none text-xs outline-none ml-2 text-slate-700 dark:text-slate-200"
          />
          <button v-if="search" @click="search = ''" class="ml-1 text-slate-400 hover:text-slate-600">
            <i class="fa fa-times text-xs"></i>
          </button>
        </div>

        <!-- Program filter -->
        <select
          v-model="selectedProgram"
          class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 text-xs font-medium text-slate-700 dark:text-slate-200 h-10"
        >
          <option value="">All Programs</option>
          <option v-for="prog in uniquePrograms" :key="prog" :value="prog">{{ prog }}</option>
        </select>

        <!-- Term filter -->
        <select
          v-model="selectedTerm"
          class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 text-xs font-medium text-slate-700 dark:text-slate-200 h-10"
        >
          <option value="">All Terms</option>
          <option v-for="term in uniqueTerms" :key="term" :value="term">{{ term }}</option>
        </select>

      </div>
    </HeroHeader>

    <!-- Result count -->
    <p v-if="!loading" class="mt-4 text-xs text-slate-500">
      Showing <span class="font-semibold text-slate-900 dark:text-white">{{ filtered.length }}</span>
      of {{ enrollments.length }} students
    </p>

    <!-- Loading -->
    <div v-if="loading" class="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="n in 6" :key="n" class="rounded-2xl bg-slate-100 dark:bg-slate-800 animate-pulse h-56"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="filtered.length === 0" class="mt-20 text-center text-slate-400">
      <i class="fa fa-user-slash text-3xl mb-3"></i>
      <p class="text-sm font-medium">No students found</p>
      <button @click="clearFilters" class="text-xs text-indigo-500 mt-2 hover:underline">
        Clear filters
      </button>
    </div>

    <!-- Profile Cards -->
    <div v-else class="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

      <div
        v-for="enr in filtered"
        :key="enr.name"
        class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all"
      >

        <!-- Profile Header -->
        <div class="flex items-center gap-4 mb-5">
          <div class="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-bold text-slate-600 dark:text-slate-300">
            {{ initials(enr.student_name) }}
          </div>

          <div class="min-w-0">
            <h4 class="text-sm font-semibold text-slate-900 dark:text-white truncate">
              {{ enr.student_name }}
            </h4>
            <p class="text-xs text-slate-500 truncate">
              {{ enr.student }}
            </p>
          </div>
        </div>

        <!-- Details -->
        <div class="space-y-3 text-xs">

          <div class="flex justify-between">
            <span class="text-slate-400">Program</span>
            <span class="font-medium text-slate-700 dark:text-slate-200">{{ enr.program }}</span>
          </div>

          <div class="flex justify-between">
            <span class="text-slate-400">Academic Year</span>
            <span class="font-medium text-slate-700 dark:text-slate-200">{{ enr.academic_year }}</span>
          </div>

          <div class="flex justify-between">
            <span class="text-slate-400">Term</span>
            <span class="font-medium text-slate-700 dark:text-slate-200">{{ enr.academic_term }}</span>
          </div>

          <div class="flex justify-between">
            <span class="text-slate-400">Enrolled On</span>
            <span class="font-medium text-slate-700 dark:text-slate-200">
              {{ formatDate(enr.enrollment_date) }}
            </span>
          </div>

        </div>

        <!-- Footer ID -->
        <div class="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center">
          <span class="text-[10px] text-slate-400">ID</span>
          <span class="text-[10px] font-medium text-slate-500">{{ enr.name }}</span>
        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import { fetchStudents } from '~/composable/useStudent'

// ── state ──────────────────────────────────────────────────────────────────────
const loading      = ref(true)
const enrollments  = ref([])   // raw API array — stored as-is, no mapping needed
const search       = ref('')
const selectedProgram = ref('')
const selectedTerm    = ref('')

// ── accent colours ─────────────────────────────────────────────────────────────
const accents = ['bg-indigo-500','bg-violet-500','bg-blue-500','bg-emerald-500','bg-rose-500','bg-amber-500','bg-cyan-500','bg-pink-500']
const accentBg = (i) => accents[i % accents.length]

// ── helpers ────────────────────────────────────────────────────────────────────
const initials = (name = '') =>
  name.trim().split(/\s+/).slice(0, 2).map(w => w[0]?.toUpperCase() ?? '').join('')

const formatDate = (d) =>
  d ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'

const clearFilters = () => {
  search.value = ''
  selectedProgram.value = ''
  selectedTerm.value = ''
}

// ── filter options (derived from real data) ────────────────────────────────────
const uniquePrograms = computed(() =>
  [...new Set(enrollments.value.map(e => e.program).filter(Boolean))]
)
const uniqueTerms = computed(() =>
  [...new Set(enrollments.value.map(e => e.academic_term).filter(Boolean))]
)

// ── filtered list ──────────────────────────────────────────────────────────────
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()

  return enrollments.value.filter(e => {
    // search: match student_name OR student ID OR program
    const matchSearch =
      !q ||
      e.student_name?.toLowerCase().includes(q) ||
      e.student?.toLowerCase().includes(q) ||
      e.program?.toLowerCase().includes(q)

    // program dropdown filter
    const matchProgram = !selectedProgram.value || e.program === selectedProgram.value

    // term dropdown filter
    const matchTerm = !selectedTerm.value || e.academic_term === selectedTerm.value

    return matchSearch && matchProgram && matchTerm
  })
})

// ── fetch ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    // fetchStudents composable already unwraps { message: [...] }
    // and always returns a plain array
    enrollments.value = await fetchStudents()
  } catch (err) {
    console.error('Failed to load enrollments:', err)
  } finally {
    loading.value = false
  }
})
</script>