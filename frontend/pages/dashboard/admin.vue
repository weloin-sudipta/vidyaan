<template>
    <main class="flex-1 overflow-y-auto p-6 pt-2 custom-scrollbar">

        <div
            class="relative flex flex-col items-center justify-between p-8 mb-6 overflow-hidden bg-white dark:bg-slate-900 border border-gray-100 dark:border-slate-800 shadow-sm dark:shadow-none rounded-2xl md:flex-row transition-colors">
            <div class="z-10 text-center md:text-left">
                <h2 class="text-2xl font-bold text-indigo-600 dark:text-indigo-400 transition-colors">Welcome to Vidyaan! 🎓</h2>
                <p class="max-w-md mt-2 text-base text-gray-500 dark:text-gray-400 leading-relaxed transition-colors">
                    Hey <strong>{{ username }}</strong>, your student enrollment system is up and running. You
                    have 12 pending tasks today.
                </p>
                <button
                    class="px-6 py-2.5 mt-6 text-sm font-semibold text-white transition bg-indigo-600 rounded-lg shadow-lg hover:bg-indigo-700 shadow-indigo-100">
                    <i class="fa fa-eye mr-2"></i> View Reports
                </button>
            </div>

            <div class="mt-8 md:mt-0 md:mr-6">
                <img src="/student_dash_img.png" alt="Dashboard Welcome" class="h-60 w-auto drop-shadow-lg" />
            </div>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
            <StatCard v-for="stat in stats" :key="stat.label" :label="stat.label" :value="stat.value" :icon="stat.icon"
                :color="stat.color" />
        </div>

        <div
            class="mt-6 p-10 bg-white/50 dark:bg-slate-900/50 border-2 border-dashed border-gray-200 dark:border-slate-800 rounded-2xl flex flex-col items-center justify-center text-gray-400 dark:text-gray-500 min-h-[400px] transition-colors">
            <i class="fa fa-folder-open-o text-4xl mb-2"></i>
            <p>Additional Dashboard Widgets Go Here</p>
        </div>
    </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import StatCard from '~/components/ui/StatCard.vue'

const router = useRouter()

// Example flag (replace this with your real auth data)
// const is_student = true

// onMounted(() => {
//   if (is_student) {
//     router.push('/dashboard/student')
//   }
// })
const username = ref('Sudipta Ghosh')

const stats = [
    { label: 'Total Students', value: '4,285', icon: 'fa fa-graduation-cap', color: 'bg-blue-500' },
    { label: 'Active Courses', value: '124', icon: 'fa fa-book', color: 'bg-indigo-500' },
    { label: 'Revenue', value: '$12,450', icon: 'fa fa-money', color: 'bg-green-500' },
]
</script>

<style>
/* Reset and custom styling */
html,
body {
    margin: 0;
    padding: 0;
    height: 100%;
}

.custom-scrollbar::-webkit-scrollbar {
    width: 5px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
}

.custom-scrollbar:hover::-webkit-scrollbar-thumb {
    background: #cbd5e1;
}

/* Ensure Fa Icons have spacing if text is hidden */
.sidebar-collapsed i {
    margin: 0 auto;
}
</style>