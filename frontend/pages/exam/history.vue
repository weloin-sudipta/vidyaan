<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans text-slate-900 dark:text-slate-100 transition-colors">
    <div class="max-w-[1440px] mx-auto space-y-6">

      <!-- HEADER -->
      <HeroHeader
        :title="`Result History - ${studentMeta.student_name || 'Student'}`"
        :subtitle="`${filteredResults.length} Results Found`"
        icon="fa fa-history"
      >
        <button @click="$router.back()"
          class="px-5 py-3 bg-slate-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-700 flex items-center gap-2">
          <i class="fa fa-arrow-left"></i> Back
        </button>
      </HeroHeader>

      <!-- FILTERS & SEARCH -->
      <div class="bg-white dark:bg-slate-900 rounded-[2rem] p-6 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none">

        <div class="flex flex-col lg:flex-row gap-4 items-start lg:items-center">

          <!-- SEARCH -->
          <div class="flex-1">
            <UiSearchFilterBar
              v-model="searchQuery"
              placeholder="Search courses..."
              class="w-full"
            />
          </div>

          <!-- FILTER DROPDOWNS -->
          <div class="flex flex-wrap gap-3">

            <!-- ACADEMIC YEAR -->
            <UiSelect
              v-model="filters.academic_year"
              :options="filterOptions.academic_years"
              placeholder="All Years"
              class="min-w-[140px]"
            />

            <!-- COURSE -->
            <UiSelect
              v-model="filters.course"
              :options="filterOptions.courses"
              placeholder="All Courses"
              class="min-w-[140px]"
            />

            <!-- EXAM TYPE -->
            <UiSelect
              v-model="filters.assessment_group"
              :options="filterOptions.assessment_groups"
              placeholder="All Exams"
              class="min-w-[140px]"
            />

            <!-- CLEAR FILTERS -->
            <button
              @click="clearFilters"
              class="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded-xl text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              Clear Filters
            </button>

          </div>

        </div>

      </div>

      <!-- LOADING STATE -->
      <div v-if="loading" class="space-y-4">
        <UiSkeleton height="h-32" v-for="i in 5" :key="i" class="rounded-[2rem]" />
      </div>

      <!-- RESULTS TIMELINE -->
      <div v-else-if="filteredResults.length > 0" class="space-y-4">

        <div v-for="result in filteredResults" :key="result.name" class="bg-white dark:bg-slate-900 rounded-[2rem] p-6 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none">

          <!-- TIMELINE HEADER -->
          <div class="flex items-center justify-between mb-4">

            <div class="flex items-center gap-4">

              <!-- TIMELINE DOT -->
              <div class="w-4 h-4 bg-indigo-500 rounded-full flex-shrink-0"></div>

              <!-- COURSE INFO -->
              <div>
                <h3 class="text-lg font-black text-slate-800 dark:text-slate-200">
                  {{ result.course || 'Unknown Course' }}
                </h3>
                <p class="text-sm text-slate-500 dark:text-slate-400">
                  {{ result.assessment_group || 'Exam' }} • {{ result.academic_year || 'N/A' }}
                  <span v-if="result.academic_term"> • {{ result.academic_term }}</span>
                </p>
              </div>

            </div>

            <!-- GRADE BADGE -->
            <div class="flex items-center gap-4">

              <div :class="['px-4 py-2 rounded-xl text-white text-sm font-bold', getGradeColor(result.grade)]">
                {{ result.grade || 'N/A' }}
              </div>

              <div class="text-right">
                <p class="text-sm font-bold text-slate-800 dark:text-slate-200">
                  {{ result.total_score || 0 }}/{{ result.maximum_score || 0 }}
                </p>
                <p class="text-xs text-slate-500 dark:text-slate-400">
                  {{ getPercentage(result) }}%
                </p>
              </div>

            </div>

          </div>

          <!-- EXPANDABLE DETAILS -->
          <div class="border-t border-slate-100 dark:border-slate-800 pt-4">

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">

              <div>
                <p class="text-slate-500 dark:text-slate-400 uppercase text-xs tracking-widest">Assessment Plan</p>
                <p class="font-medium">{{ result.assessment_plan || 'N/A' }}</p>
              </div>

              <div>
                <p class="text-slate-500 dark:text-slate-400 uppercase text-xs tracking-widest">Grading Scale</p>
                <p class="font-medium">{{ result.grading_scale || 'N/A' }}</p>
              </div>

              <div>
                <p class="text-slate-500 dark:text-slate-400 uppercase text-xs tracking-widest">Student Group</p>
                <p class="font-medium">{{ result.student_group || 'N/A' }}</p>
              </div>

            </div>

          </div>

        </div>

      </div>

      <!-- NO RESULTS -->
      <div v-else class="text-center py-20">
        <i class="fa fa-search text-6xl text-slate-300 dark:text-slate-600 mb-4"></i>
        <h3 class="text-xl font-bold text-slate-600 dark:text-slate-400 mb-2">No Results Found</h3>
        <p class="text-slate-500 dark:text-slate-500 mb-6">
          No results match your current filters. Try adjusting your search or clearing filters.
        </p>
        <button @click="clearFilters" class="px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors">
          Clear All Filters
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import UiSearchFilterBar from '~/components/ui/UiSearchFilterBar.vue'
import UiSelect from '~/components/ui/UiSelect.vue'
import UiSkeleton from '~/components/ui/UiSkeleton.vue'
import { useFilteredExamResults } from '~/composables/academics/useExaminations'

// REACTIVE STATE
const loading = ref(true)
const allResults = ref([])
const searchQuery = ref('')
const filters = ref({
  academic_year: '',
  course: '',
  assessment_group: ''
})

// FETCH DATA
onMounted(async () => {
  try {
    const data = await useFilteredExamResults()
    allResults.value = data || []
  } catch (e) {
    console.error('Failed to load results:', e)
  } finally {
    loading.value = false
  }
})

// FILTER OPTIONS
const filterOptions = computed(() => {
  const years = new Set()
  const courses = new Set()
  const groups = new Set()

  allResults.value.forEach(result => {
    if (result.academic_year) years.add(result.academic_year)
    if (result.course) courses.add(result.course)
    if (result.assessment_group) groups.add(result.assessment_group)
  })

  return {
    academic_years: Array.from(years).sort().reverse().map(y => ({ label: y, value: y })),
    courses: Array.from(courses).sort().map(c => ({ label: c, value: c })),
    assessment_groups: Array.from(groups).sort().map(g => ({ label: g, value: g }))
  }
})

// FILTERED RESULTS
const filteredResults = computed(() => {
  let results = allResults.value

  // Apply filters
  if (filters.value.academic_year) {
    results = results.filter(r => r.academic_year === filters.value.academic_year)
  }
  if (filters.value.course) {
    results = results.filter(r => r.course === filters.value.course)
  }
  if (filters.value.assessment_group) {
    results = results.filter(r => r.assessment_group === filters.value.assessment_group)
  }

  // Apply search
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    results = results.filter(r =>
      (r.course || '').toLowerCase().includes(query) ||
      (r.assessment_group || '').toLowerCase().includes(query)
    )
  }

  return results
})

// STUDENT META
const studentMeta = computed(() => {
  if (!allResults.value.length) return {}
  const first = allResults.value[0]
  return {
    student_name: first.student_name,
    academic_year: first.academic_year
  }
})

// UTILITIES
const getGradeColor = (grade) => {
  if (!grade) return 'bg-slate-400'
  grade = grade.toUpperCase()

  if (['A', 'A+', 'O'].includes(grade)) return 'bg-emerald-500'
  if (['B', 'B+'].includes(grade)) return 'bg-indigo-500'
  if (['C', 'C+'].includes(grade)) return 'bg-amber-500'
  return 'bg-rose-500'
}

const getPercentage = (result) => {
  const score = result.total_score || 0
  const max = result.maximum_score || 0
  return max ? Math.round((score / max) * 100) : 0
}

const clearFilters = () => {
  filters.value = {
    academic_year: '',
    course: '',
    assessment_group: ''
  }
  searchQuery.value = ''
}

// WATCH FILTERS FOR DEBUGGING
watch(filteredResults, (newResults) => {
  console.log('Filtered results:', newResults.length, 'of', allResults.value.length)
})
</script>

<style scoped>
/* Timeline styling */
.timeline-dot {
  position: relative;
}

.timeline-dot::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 20px;
  bottom: -20px;
  width: 2px;
  background: #e2e8f0;
}

.dark .timeline-dot::before {
  background: #374151;
}
</style>