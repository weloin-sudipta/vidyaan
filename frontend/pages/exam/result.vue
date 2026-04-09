<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans text-slate-900 dark:text-slate-100 transition-colors">
    <div class="max-w-[1440px] mx-auto space-y-6">

      <!-- HEADER -->
      <HeroHeader 
        :title="studentMeta.student_name || 'Performance Hub'" 
        :subtitle="`${studentMeta.academic_term || 'Consolidated Result'}`" 
        icon="fa fa-pie-chart"
      >
        <!-- <button @click="openDownloadModal('Semester Result')"
          class="px-5 py-3 bg-slate-900 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-800 flex items-center gap-2">
          <i class="fa fa-file-pdf-o"></i> Result PDF
        </button>

        <button @click="openDownloadModal('Academic Certificate')"
          class="px-5 py-3 bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg hover:bg-indigo-700 flex items-center gap-2">
          <i class="fa fa-certificate"></i> Certificate
        </button> -->
      </HeroHeader>

      <!-- LOADING STATE -->
      <div v-if="loading" class="space-y-4">
        <UiSkeleton height="h-24" v-for="i in 3" :key="i" class="rounded-[2rem]" />
      </div>

      <!-- GROUPED RESULTS -->
      <div v-else class="space-y-4 animate-in">

        <div v-for="(group, assessmentGroup) in groupedResults" :key="assessmentGroup">

          <!-- GROUP HEADER -->
          <div
            @click="toggleGroup(assessmentGroup)"
            class="cursor-pointer bg-white dark:bg-slate-900 rounded-[2rem] p-6 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none hover:border-indigo-300 dark:hover:border-indigo-500/50 transition-all flex items-center justify-between group"
          >

            <div class="flex items-center gap-4">

              <div
                class="w-12 h-12 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center text-xl transition-colors group-hover:bg-indigo-600 group-hover:text-white dark:group-hover:bg-indigo-500"
              >
                <i :class="expandedGroups.includes(assessmentGroup) ? 'fa fa-folder-open' : 'fa fa-folder'"></i>
              </div>

              <div>
                <h2 class="text-xl font-black text-slate-800 dark:text-slate-200 tracking-tight transition-colors">
                  {{ assessmentGroup }} <span>{{ group.results.length }} Subjects</span>
                </h2>

                <p class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">
                  {{ group.program }} • {{ group.academic_term }}
                </p>
              </div>

              <div class="flex items-center gap-4">
                <div class="text-center">
                  <p class="text-[9px] text-slate-400 dark:text-slate-500 uppercase transition-colors">Total Score</p>
                  <p class="text-lg font-black text-slate-800 dark:text-white transition-colors">
                    {{ group.total }}
                    <span class="text-slate-300 dark:text-slate-600 text-sm">/{{ group.max }}</span>
                  </p>
                </div>

                <div class="text-center">
                  <p class="text-[9px] text-slate-400 dark:text-slate-500 uppercase transition-colors">Percentage</p>
                  <p class="text-lg font-black text-indigo-600 dark:text-indigo-400 transition-colors">
                    {{ group.percentage }}%
                  </p>
                </div>
              </div>

            </div>

            <div class="flex items-center gap-4">
              <div
                class="text-slate-300 dark:text-slate-600 transition-transform duration-300"
                :class="{ 'rotate-180': expandedGroups.includes(assessmentGroup) }"
              >
                <i class="fa fa-chevron-down"></i>
              </div>
            </div>

          </div>

          <!-- SUBJECT LIST -->
          <transition name="expand">
            <div v-if="expandedGroups.includes(assessmentGroup)" class="overflow-hidden">

              <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-200 dark:border-slate-800 shadow-sm dark:shadow-none mt-3 ml-4 md:ml-12 overflow-hidden transition-colors">

                <!-- TABLE -->
                <div class="overflow-x-auto">
                  <table class="w-full text-left">

                    <thead>
                      <tr class="bg-slate-50 dark:bg-slate-800/50 transition-colors">
                        <th class="p-4 text-xs">Course</th>
                        <th class="p-4 text-center text-xs">Grade</th>
                        <th class="p-4 text-xs">Performance</th>
                        <th class="p-4 text-center text-xs">Scale</th>
                        <th class="p-4 text-right text-xs">Marks</th>
                      </tr>
                    </thead>

                    <tbody>
                      <tr v-for="sub in group.subjects" :key="sub.id" class="border-t border-slate-100 dark:border-slate-800/50 transition-colors">

                        <td class="p-4 font-bold">
                          {{ sub.name }}
                        </td>

                        <td class="p-4 text-center">
                          <span :class="['px-3 py-1 rounded text-white text-xs', sub.color]">
                            {{ sub.grade }}
                          </span>
                        </td>

                        <td class="p-4 w-[200px]">
                          <div class="h-2 bg-slate-100 dark:bg-slate-800 rounded transition-colors">
                            <div
                              class="h-2 rounded"
                              :class="sub.color"
                              :style="{ width: sub.percentage + '%' }"
                            ></div>
                          </div>
                        </td>

                        <td class="p-4 text-center text-xs font-bold">
                          {{ sub.scale }}
                        </td>

                        <td class="p-4 text-right font-bold">
                          {{ sub.marks }}/{{ sub.max }}
                        </td>

                      </tr>
                    </tbody>

                  </table>
                </div>

              </div>

            </div>
          </transition>

        </div>

        <div
          v-if="Object.keys(groupedResults).length === 0"
          class="text-center py-20 text-slate-400 dark:text-slate-500 font-bold uppercase text-sm tracking-widest transition-colors"
        >
          No results available.
        </div>

      </div>

      <!-- FOOTER NOTE -->
      <div v-if="!loading && results.length > 0" class="bg-indigo-50 dark:bg-indigo-900/20 rounded-2xl p-6 border border-indigo-100 dark:border-indigo-900/30 flex gap-4 transition-colors">
        <i class="fa fa-info-circle text-indigo-600 dark:text-indigo-400"></i>
        <p class="text-xs text-slate-800 dark:text-slate-200 transition-colors">
          Transcript for <b>{{ studentMeta.student_name }}</b> as of {{ new Date().toLocaleDateString() }}
        </p>
      </div>

    </div>

    <!-- MODAL -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black/50">
      <div class="bg-white p-6 rounded-2xl w-[300px] text-center">
        <h3 class="font-bold mb-4">{{ downloadType }}</h3>
        <button @click="handleDownload"
          class="w-full py-3 bg-indigo-600 text-white rounded-xl">
          Download
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'
import { useExamResults } from '~/composables/academics/useExaminations'

const results = ref([])
const showModal = ref(false)
const downloadType = ref('')
const loading = ref(true)
const expandedGroups = ref([])

/* FETCH */
onMounted(async () => {
  try {
    const data = await useExamResults()
    console.log("API 👉", data)

    if (Array.isArray(data)) {
      results.value = data
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

/* META */
const studentMeta = computed(() => {
  if (!results.value.length) return {}

  const first = results.value[0]

  const total = results.value.reduce((s, r) => s + (r.total_score || 0), 0)
  const max = results.value.reduce((s, r) => s + (r.maximum_score || 0), 0)

  return {
    student_name: first.student_name,
    academic_term: first.academic_term,
    academic_year: first.academic_year,
    program: first.program,
    assessment_group: first.assessment_group,
    student_id: first.student,
    total,
    max,
    percentage: max ? Math.round((total / max) * 100) : 0
  }
})

/* GROUP RESULTS BY ASSESSMENT GROUP */
const groupedResults = computed(() => {
  return results.value.reduce((groups, result) => {
    const assessmentGroup = result.assessment_group || 'Ungrouped'

    if (!groups[assessmentGroup]) {
      const groupResults = results.value.filter(r => r.assessment_group === assessmentGroup)
      const total = groupResults.reduce((s, r) => s + (r.total_score || 0), 0)
      const max = groupResults.reduce((s, r) => s + (r.maximum_score || 0), 0)

      groups[assessmentGroup] = {
        program: result.program,
        academic_term: result.academic_term,
        results: groupResults,
        total,
        max,
        percentage: max ? Math.round((total / max) * 100) : 0,
        subjects: groupResults.map(r => ({
          id: r.name,
          name: r.course || '-',
          grade: r.grade || '-',
          marks: r.total_score || 0,
          max: r.maximum_score || 0,
          percentage: r.maximum_score
            ? Math.round((r.total_score / r.maximum_score) * 100)
            : 0,
          scale: r.grading_scale || '-',
          color: getColor(r.grade)
        }))
      }
    }

    return groups
  }, {})
})

/* TOGGLE GROUP */
const toggleGroup = (assessmentGroup) => {
  const index = expandedGroups.value.indexOf(assessmentGroup)

  if (index > -1) {
    expandedGroups.value.splice(index, 1)
  } else {
    expandedGroups.value.push(assessmentGroup)
  }
}

/* COLOR */
const getColor = (g) => {
  if (!g) return 'bg-slate-400'
  g = g.toUpperCase()

  if (['A', 'A+', 'O'].includes(g)) return 'bg-emerald-500'
  if (['B', 'B+'].includes(g)) return 'bg-indigo-500'
  if (['C', 'C+'].includes(g)) return 'bg-amber-500'
  return 'bg-rose-500'
}

/* MODAL */
const openDownloadModal = (type) => {
  downloadType.value = type
  showModal.value = true
}

/* DOWNLOAD */
const handleDownload = () => {
  console.log("Downloading:", downloadType.value)
  showModal.value = false
}
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
