<template>
    <main class="flex-1 overflow-y-auto p-4 lg:p-10 custom-scrollbar bg-[#f8fafc] dark:bg-slate-950 transition-colors duration-300">
        <div class="max-w-[1400px] mx-auto space-y-8">
            
            <HeroHeader 
                title="Attendance Register" 
                subtitle="Academic Session 2025-26"
                icon="fa fa-id-badge"
                :searchable="true"
                v-model:search="searchQuery"
                searchPlaceholder="Search student name or roll..."
            >
                <div class="flex gap-2">
                    <button @click="viewMode = 'grid'" 
                        :class="viewMode === 'grid' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'bg-white dark:bg-slate-800 text-slate-400'"
                        class="w-12 h-12 rounded-2xl flex items-center justify-center transition-all border dark:border-slate-700">
                        <i class="fa fa-th-large"></i>
                    </button>
                    <button @click="viewMode = 'list'" 
                        :class="viewMode === 'list' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'bg-white dark:bg-slate-800 text-slate-400'"
                        class="w-12 h-12 rounded-2xl flex items-center justify-center transition-all border dark:border-slate-700">
                        <i class="fa fa-list"></i>
                    </button>
                </div>
            </HeroHeader>

            <div class="flex items-center gap-4 overflow-x-auto no-scrollbar pb-2">
                <div class="shrink-0 text-[10px] font-black text-slate-400 uppercase tracking-widest mr-2">Your Schedule:</div>
                <button v-for="session in teacherSessions" :key="session.id" @click="activeSession = session"
                    :class="[
                        activeSession.id === session.id
                            ? 'bg-emerald-500 text-white shadow-xl shadow-emerald-200'
                            : 'bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-800'
                    ]" 
                    class="px-6 py-3 rounded-2xl border transition-all flex items-center gap-3 whitespace-nowrap active:scale-95">
                    <span :class="session.isLive ? 'bg-white animate-pulse' : 'bg-slate-300'" class="w-1.5 h-1.5 rounded-full"></span>
                    <span class="text-[11px] font-black uppercase tracking-widest">{{ session.subject }}</span>
                </button>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
                
                <div class="lg:col-span-4 space-y-6">
                    <div class="bg-white dark:bg-slate-900 rounded-[3rem] p-8 border border-slate-100 dark:border-slate-800 shadow-xl shadow-slate-200/50 dark:shadow-none relative overflow-hidden group">
                        <div class="relative z-10 flex flex-col items-center">
                            <h3 class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-8">Section Saturation</h3>
                            
                            <div class="relative w-48 h-48 mb-8">
                                <svg class="w-full h-full transform -rotate-90">
                                    <circle cx="96" cy="96" r="88" fill="transparent" stroke="currentColor" stroke-width="12" class="text-slate-50 dark:text-slate-800" />
                                    <circle cx="96" cy="96" r="88" fill="transparent" stroke="currentColor" stroke-width="12"
                                        stroke-dasharray="552" :stroke-dashoffset="552 - (attendancePercentage / 100 * 552)"
                                        class="text-emerald-500 transition-all duration-1000 ease-out" stroke-linecap="round" />
                                </svg>
                                <div class="absolute inset-0 flex flex-col items-center justify-center">
                                    <span class="text-5xl font-black text-slate-800 dark:text-white tracking-tighter">{{ attendancePercentage }}%</span>
                                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Marked Present</span>
                                </div>
                            </div>

                            <div class="grid grid-cols-2 gap-4 w-full">
                                <div class="bg-emerald-50 dark:bg-emerald-900/10 p-5 rounded-3xl text-center border border-emerald-100 dark:border-emerald-500/20 transition-colors">
                                    <p class="text-3xl font-black text-emerald-600">{{ presentCount }}</p>
                                    <p class="text-[9px] font-black text-emerald-400 uppercase tracking-widest mt-1">Present</p>
                                </div>
                                <div class="bg-rose-50 dark:bg-rose-900/10 p-5 rounded-3xl text-center border border-rose-100 dark:border-rose-500/20 transition-colors">
                                    <p class="text-3xl font-black text-rose-600">{{ absentCount }}</p>
                                    <p class="text-[9px] font-black text-rose-400 uppercase tracking-widest mt-1">Absent</p>
                                </div>
                            </div>
                        </div>
                        <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-emerald-500/5 rounded-full blur-3xl"></div>
                    </div>

                    <div class="space-y-3">
                        <button @click="markAllPresent" class="w-full py-5 bg-slate-900 dark:bg-white dark:text-slate-900 text-white rounded-[2rem] font-black text-xs uppercase tracking-widest flex items-center justify-center gap-3 hover:scale-[1.02] transition-all active:scale-95">
                            <i class="fa fa-check-circle text-emerald-400"></i> Mark Everyone Present
                        </button>
                    </div>
                </div>

                <div class="lg:col-span-8 bg-white dark:bg-slate-900 rounded-[3rem] p-8 lg:p-12 border border-slate-100 dark:border-slate-800 shadow-sm transition-colors">
                    
                    <div class="flex justify-between items-center mb-10">
                        <p class="text-xs font-bold text-slate-400">Showing {{ filteredStudents.length }} students in <span class="text-slate-800 dark:text-white">{{ activeSession.subject }}</span></p>
                        <span v-if="searchQuery" class="text-[10px] font-black text-indigo-500 uppercase">Filtered by: "{{ searchQuery }}"</span>
                    </div>

                    <div v-if="viewMode === 'grid'" class="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-6">
                        <div v-for="student in filteredStudents" :key="student.id" @click="toggleStatus(student)" 
                             :class="[
                                student.status === 'P' ? 'bg-emerald-500 border-emerald-500 scale-[1.02] shadow-emerald-100 dark:shadow-none' :
                                student.status === 'A' ? 'bg-rose-500 border-rose-500 scale-[1.02] shadow-rose-100 dark:shadow-none' :
                                'bg-slate-50 dark:bg-slate-800 border-slate-100 dark:border-slate-700'
                             ]" 
                             class="relative p-6 rounded-[2.5rem] border-2 transition-all cursor-pointer flex flex-col items-center group active:scale-95 overflow-hidden">
                            
                            <img :src="student.avatar" :class="student.status ? 'border-white/40' : 'border-transparent'"
                                class="w-16 h-16 rounded-3xl border-4 shadow-md transition-all object-cover mb-4" />

                            <p :class="student.status ? 'text-white' : 'text-slate-800 dark:text-slate-200'" class="text-[11px] font-black text-center leading-tight">
                                {{ student.name }}
                            </p>
                            <p :class="student.status ? 'text-white/60' : 'text-slate-400'" class="text-[9px] font-bold uppercase tracking-tighter mt-1">
                                #{{ student.roll }}
                            </p>

                            <div v-if="student.status" class="absolute top-2 right-2">
                                <i :class="student.status === 'P' ? 'fa fa-check' : 'fa fa-times'" class="text-white text-[10px]"></i>
                            </div>
                        </div>
                    </div>

                    <div v-else class="space-y-4">
                        <div v-for="student in filteredStudents" :key="student.id" @click="toggleStatus(student)"
                            :class="student.status === 'P' ? 'border-emerald-200 bg-emerald-50/20' : student.status === 'A' ? 'border-rose-200 bg-rose-50/20' : 'border-transparent bg-slate-50 dark:bg-slate-800/50'"
                            class="flex items-center justify-between p-5 rounded-[2rem] border-2 transition-all cursor-pointer group">
                            <div class="flex items-center gap-5">
                                <img :src="student.avatar" class="w-12 h-12 rounded-2xl" />
                                <div>
                                    <p class="text-sm font-black text-slate-800 dark:text-slate-200 transition-colors">{{ student.name }}</p>
                                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ student.roll }}</span>
                                </div>
                            </div>
                            <div class="flex gap-2">
                                <div v-if="student.status === 'P'" class="w-10 h-10 rounded-xl bg-emerald-500 text-white flex items-center justify-center text-xs shadow-lg shadow-emerald-200 dark:shadow-none"><i class="fa fa-check"></i></div>
                                <div v-else-if="student.status === 'A'" class="w-10 h-10 rounded-xl bg-rose-500 text-white flex items-center justify-center text-xs shadow-lg shadow-rose-200 dark:shadow-none"><i class="fa fa-times"></i></div>
                                <div v-else class="w-10 h-10 rounded-xl bg-white dark:bg-slate-700 flex items-center justify-center text-slate-300"><i class="fa fa-circle-o"></i></div>
                            </div>
                        </div>
                    </div>

                    <div class="mt-12 flex flex-col sm:flex-row items-center justify-between gap-6 border-t border-slate-100 dark:border-slate-800 pt-10 transition-colors">
                        <p class="text-[11px] font-bold text-slate-400 italic">Verify entries before finalizing for the Frappe ledger.</p>
                        <button @click="submitAttendance"
                            class="w-full sm:w-auto px-12 py-5 bg-indigo-600 text-white rounded-[2rem] font-black text-[11px] uppercase tracking-[0.3em] shadow-2xl shadow-indigo-100 dark:shadow-none hover:-translate-y-2 transition-all active:scale-95">
                            Finalize Register
                        </button>
                    </div>
                </div>

            </div>
        </div>
    </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'

const searchQuery = ref('')
const viewMode = ref('grid')
const activeSession = ref({ id: 1, subject: 'Advanced Algorithms', time: '10:00 AM', isLive: true })

const teacherSessions = [
    { id: 1, subject: 'Algo-Design', time: '10:00 AM', isLive: true },
    { id: 2, subject: 'Fullstack Dev', time: '01:00 PM', isLive: false },
    { id: 3, subject: 'Thesis Lab', time: '03:30 PM', isLive: false },
]

const students = ref([
    { id: 1, name: 'Aditya Raj', roll: 'CS2601', avatar: 'https://i.pravatar.cc/150?u=1', status: null },
    { id: 2, name: 'Sudipta Ghosh', roll: 'CS2602', avatar: 'https://i.pravatar.cc/150?u=2', status: 'P' },
    { id: 3, name: 'Ankita Paul', roll: 'CS2603', avatar: 'https://i.pravatar.cc/150?u=3', status: null },
    { id: 4, name: 'Rohan Das', roll: 'CS2604', avatar: 'https://i.pravatar.cc/150?u=4', status: null },
    { id: 5, name: 'Sneha Roy', roll: 'CS2605', avatar: 'https://i.pravatar.cc/150?u=5', status: 'A' },
    { id: 6, name: 'Vikram Singh', roll: 'CS2606', avatar: 'https://i.pravatar.cc/150?u=6', status: null },
    { id: 7, name: 'Priya Sharma', roll: 'CS2607', avatar: 'https://i.pravatar.cc/150?u=7', status: null },
    { id: 8, name: 'Arjun Mehra', roll: 'CS2608', avatar: 'https://i.pravatar.cc/150?u=8', status: 'P' },
])

// FILTER LOGIC
const filteredStudents = computed(() => {
    if (!searchQuery.value) return students.value
    return students.value.filter(s => 
        s.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
        s.roll.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
})

const presentCount = computed(() => students.value.filter(s => s.status === 'P').length)
const absentCount = computed(() => students.value.filter(s => s.status === 'A').length)
const attendancePercentage = computed(() => {
    if (students.value.length === 0) return 0
    return Math.round((presentCount.value / students.value.length) * 100)
})

const toggleStatus = (student) => {
    if (!student.status) student.status = 'P'
    else if (student.status === 'P') student.status = 'A'
    else student.status = null
}

const markAllPresent = () => {
    students.value.forEach(s => s.status = 'P')
}

const submitAttendance = () => {
    alert('Attendance Finalized for: ' + activeSession.value.subject)
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>