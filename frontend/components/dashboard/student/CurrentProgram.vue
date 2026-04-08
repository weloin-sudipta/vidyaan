<template>
<div class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 overflow-hidden group transition-colors">

    <!-- HEADER -->
    <div class="p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">

        <div class="space-y-2">

            <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
                <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                    Active Enrollment
                </p>
            </div>

            <h2 class="text-2xl font-black text-slate-800 dark:text-white">
                {{ programData?.name || 'Loading Program...' }}
            </h2>

            <p class="text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 px-3 py-1 rounded-lg inline-block transition-colors">
                Semester {{ programData?.semester }} • Full-Time
            </p>

        </div>

        <button
            @click="showModal = true"
            class="px-6 py-3 bg-slate-900 dark:bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-600 dark:hover:bg-indigo-500 transition-all shadow-lg dark:shadow-none active:scale-95">

            Curriculum Details

        </button>

    </div>


    <!-- PROGRAM STATS -->
    <div class="px-8 pb-8 grid grid-cols-1 md:grid-cols-2 gap-8">

        <!-- SYLLABUS PROGRESS -->
        <div class="p-6 bg-slate-50 dark:bg-slate-800/50 rounded-[2rem] border border-slate-100 dark:border-slate-700/50 transition-colors">

            <div class="flex justify-between items-end mb-4">

                <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase">
                    Syllabus Completion
                </span>

                <span class="text-xl font-black text-slate-800 dark:text-slate-200">
                    {{ completion }}%
                </span>

            </div>

            <div class="w-full bg-slate-200 dark:bg-slate-700 h-3 rounded-full overflow-hidden transition-colors">

                <div
                    class="bg-indigo-500 h-full rounded-full transition-all duration-1000"
                    :style="{ width: completion + '%' }">
                </div>

            </div>

            <p class="text-[10px] mt-2 text-slate-400 dark:text-slate-500 font-semibold">
                {{ completedSubjects }} / {{ totalSubjects }} Subjects Completed
            </p>

        </div>


        <!-- NEXT BREAK -->
        <div class="p-6 bg-rose-50 dark:bg-rose-900/10 rounded-[2rem] border border-rose-100 dark:border-rose-900/30 flex items-center gap-5 transition-colors">

            <div class="w-12 h-12 bg-white dark:bg-slate-900 border border-transparent dark:border-rose-900/50 rounded-2xl flex items-center justify-center text-rose-500 shadow-sm dark:shadow-none transition-colors">
                <i class="fa fa-hourglass-half text-rose-500 dark:text-rose-400"></i>
            </div>

            <div>

                <p class="text-[10px] font-black text-rose-400 dark:text-rose-500 uppercase tracking-widest">
                    Next Major Break
                </p>

                <p class="text-sm font-black text-rose-900 dark:text-rose-200">
                    {{ programData?.endDate }}
                </p>

                <p class="text-[9px] font-bold text-rose-600 dark:text-rose-400">
                    {{ daysRemaining }} Days Remaining
                </p>

            </div>

        </div>

    </div>


    <!-- EXTRA STATS -->
    <div class="px-8 pb-8 grid grid-cols-3 gap-4">

        <div class="bg-indigo-50 dark:bg-indigo-900/10 rounded-2xl p-4 text-center transition-colors">
            <p class="text-[9px] font-black text-indigo-400 dark:text-indigo-500 uppercase">
                Subjects
            </p>
            <p class="text-lg font-black text-indigo-700 dark:text-indigo-300">
                {{ totalSubjects }}
            </p>
        </div>

        <div class="bg-green-50 dark:bg-green-900/10 rounded-2xl p-4 text-center transition-colors">
            <p class="text-[9px] font-black text-green-400 dark:text-green-500 uppercase">
                Credits
            </p>
            <p class="text-lg font-black text-green-700 dark:text-green-300">
                {{ totalCredits }}
            </p>
        </div>

        <div class="bg-purple-50 dark:bg-purple-900/10 rounded-2xl p-4 text-center transition-colors">
            <p class="text-[9px] font-black text-purple-400 dark:text-purple-500 uppercase">
                GPA
            </p>
            <p class="text-lg font-black text-purple-700 dark:text-purple-300">
                {{ gpa }}
            </p>
        </div>

    </div>

</div>
</template>


<script setup>

import { ref, computed } from 'vue'

const props = defineProps({
  programData: {
    type: Object,
    default: () => ({})
  }
})

const showModal = ref(false)

/* SUBJECT STATS */

const totalSubjects = computed(() =>
props.programData?.subjects?.length || 0
)

const completedSubjects = computed(() =>
Math.floor(totalSubjects.value * 0.78)
)

const completion = computed(() =>
totalSubjects.value
? Math.round((completedSubjects.value / totalSubjects.value) * 100)
: 0
)

/* CREDITS */

const totalCredits = computed(() =>
props.programData?.subjects?.reduce((sum, s) => sum + (s.credits || 0), 0) || 0
)

/* GPA (mock example) */

const gpa = computed(() => "3.7")

/* DAYS REMAINING */

const daysRemaining = computed(() => {

if (!props.programData?.endDate) return 0

const end = new Date(props.programData.endDate)
const today = new Date()

const diff = end - today

return Math.max(Math.ceil(diff / (1000 * 60 * 60 * 24)), 0)

})

</script>