<template>
  <main class="flex-1 overflow-y-auto p-4 lg:p-10 custom-scrollbar bg-[#f8fafc] dark:bg-slate-950 transition-colors duration-300">
    <div class="max-w-[1400px] mx-auto space-y-8">

      <HeroHeader 
        title="Assignments" 
        subtitle="Manage and distribute coursework"
        icon="fa fa-tasks"
        :searchable="true"
        v-model:search="searchQuery"
        searchPlaceholder="Filter assignments..."
      >
        <button @click="showUploadModal = true" class="btn-primary flex items-center gap-3">
            <i class="fa fa-plus text-indigo-200"></i> Create New
        </button>
      </HeroHeader>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="item in filteredAssignments" :key="item.id" 
             class="group bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all relative overflow-hidden">
            
            <div class="flex justify-between items-start mb-6">
                <div class="flex gap-2">
                    <span v-for="prog in item.programs" :key="prog" class="px-3 py-1 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-500 text-[9px] font-black uppercase rounded-lg">
                        {{ prog }}
                    </span>
                </div>
                <button class="text-slate-300 hover:text-slate-600 dark:hover:text-slate-400"><i class="fa fa-ellipsis-h"></i></button>
            </div>

            <h3 class="text-lg font-black text-slate-800 dark:text-slate-100 mb-2 leading-tight group-hover:text-indigo-600 transition-colors">
                {{ item.title }}
            </h3>
            <p class="text-xs text-slate-400 line-clamp-2 mb-6 font-medium">{{ item.description }}</p>

            <div class="flex items-center justify-between pt-6 border-t border-slate-50 dark:border-slate-800">
                <div class="flex flex-col">
                    <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest">Due Date</span>
                    <span class="text-xs font-bold text-slate-700 dark:text-slate-300">{{ item.dueDate }}</span>
                </div>
                <div class="text-right">
                    <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest">Submissions</span>
                    <p class="text-xs font-black text-indigo-600">{{ item.submissions }} / {{ item.totalStudents }}</p>
                </div>
            </div>

            <div class="mt-4 w-full h-1 bg-slate-50 dark:bg-slate-800 rounded-full overflow-hidden">
                <div class="h-full bg-indigo-500" :style="{ width: (item.submissions / item.totalStudents * 100) + '%' }"></div>
            </div>
        </div>
      </div>

      <div v-if="filteredAssignments.length === 0" class="py-20 text-center">
          <i class="fa fa-folder-open-o text-slate-200 dark:text-slate-800 text-6xl mb-4"></i>
          <p class="text-slate-400 font-bold uppercase tracking-widest text-sm">No assignments found</p>
      </div>
    </div>

    <Transition name="slide-fade">
      <div v-if="showUploadModal" class="fixed inset-0 z-[100] flex justify-end">
        <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showUploadModal = false"></div>
        
        <div class="relative w-full max-w-2xl bg-white dark:bg-slate-900 h-full shadow-2xl flex flex-col transition-colors border-l dark:border-slate-800">
            
            <div class="p-8 border-b dark:border-slate-800 flex justify-between items-center bg-slate-50/50 dark:bg-slate-800/50">
                <div>
                    <h2 class="text-2xl font-black text-slate-800 dark:text-white">New Assignment</h2>
                    <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Global Distribution</p>
                </div>
                <button @click="showUploadModal = false" class="w-10 h-10 rounded-2xl bg-white dark:bg-slate-800 border dark:border-slate-700 text-slate-400 hover:text-rose-500 transition-all flex items-center justify-center shadow-sm">
                    <i class="fa fa-times"></i>
                </button>
            </div>

            <div class="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
                
                <div class="space-y-4">
                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Target Programs</label>
                    <div class="grid grid-cols-2 gap-3">
                        <button v-for="p in teacherPrograms" :key="p.id" 
                                @click="toggleProgram(p.id)"
                                :class="form.selectedPrograms.includes(p.id) ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-slate-50 dark:bg-slate-800 border-transparent text-slate-500'"
                                class="p-4 rounded-2xl border-2 text-left transition-all active:scale-95">
                            <p class="text-xs font-black">{{ p.name }}</p>
                            <p class="text-[9px] opacity-60 font-bold uppercase">{{ p.batch }}</p>
                        </button>
                    </div>
                </div>

                <div class="space-y-6">
                    <div class="space-y-2">
                        <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Assignment Title</label>
                        <input v-model="form.title" type="text" class="form-input" placeholder="e.g. Data Structures Mid-Term">
                    </div>
                    <div class="space-y-2">
                        <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Submission Deadline</label>
                        <div class="grid grid-cols-2 gap-4">
                            <input v-model="form.dueDate" type="date" class="form-input">
                            <input v-model="form.marks" type="number" class="form-input" placeholder="Total Marks">
                        </div>
                    </div>
                </div>

                <div class="border-2 border-dashed border-slate-100 dark:border-slate-800 rounded-[2.5rem] p-12 text-center group hover:border-indigo-500/50 transition-all cursor-pointer bg-slate-50/50 dark:bg-slate-800/30">
                    <div class="w-16 h-16 bg-white dark:bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm group-hover:scale-110 transition-transform">
                        <i class="fa fa-cloud-upload text-indigo-500 text-2xl"></i>
                    </div>
                    <p class="text-xs font-black text-slate-700 dark:text-slate-200">Upload Attachments</p>
                    <p class="text-[9px] text-slate-400 uppercase font-bold mt-1 tracking-tighter">Support: PDF, ZIP, DOCX (Max 20MB)</p>
                </div>
            </div>

            <div class="p-8 border-t dark:border-slate-800">
                <button @click="publishAssignment" class="btn-primary w-full py-5 text-sm font-black flex items-center justify-center gap-4">
                    <i class="fa fa-paper-plane text-indigo-200"></i> Publish to Students
                </button>
            </div>
        </div>
      </div>
    </Transition>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'

const showUploadModal = ref(false)
const searchQuery = ref('')

const teacherPrograms = [
    { id: 'CS-A', name: 'B.Tech CS (Section A)', batch: '2022-26' },
    { id: 'CS-B', name: 'B.Tech CS (Section B)', batch: '2022-26' },
    { id: 'MDS', name: 'Masters Data Sci', batch: '2023-25' }
]

const form = ref({
    selectedPrograms: [],
    title: '',
    dueDate: '',
    marks: 100
})

const assignments = ref([
    { 
        id: 1, 
        title: 'Linear Data Structures Lab', 
        description: 'Implement Stack and Queue using Linked List. Include time complexity analysis for each operation.',
        programs: ['CS-A', 'CS-B'],
        dueDate: 'April 05, 2026',
        submissions: 32,
        totalStudents: 120
    },
    { 
        id: 2, 
        title: 'Project Proposal: Web App', 
        description: 'Submit your team project idea with UI/UX mockups and DB Schema design.',
        programs: ['MDS'],
        dueDate: 'March 29, 2026',
        submissions: 15,
        totalStudents: 15
    }
])

const filteredAssignments = computed(() => {
    if (!searchQuery.value) return assignments.value
    return assignments.value.filter(a => a.title.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const toggleProgram = (id) => {
    if (form.value.selectedPrograms.includes(id)) {
        form.value.selectedPrograms = form.value.selectedPrograms.filter(p => p !== id)
    } else {
        form.value.selectedPrograms.push(id)
    }
}

const publishAssignment = () => {
    if (!form.value.title || form.value.selectedPrograms.length === 0) {
        alert('Title and Program targets are required!')
        return
    }
    alert('Broadcasting assignment to chosen programs...')
    showUploadModal.value = false
}
</script>

<style scoped>
.btn-primary {
  /* Increased padding from p-3 to px-10 py-4.5 and text-xs */
  @apply px-10 py-4 bg-indigo-600 text-white rounded-2xl text-[12px] font-black uppercase tracking-[0.25em] shadow-2xl shadow-indigo-200/50 hover:bg-indigo-700 hover:-translate-y-1 transition-all active:scale-95;
}

.form-input {
    @apply w-full bg-slate-50 dark:bg-slate-800 border-none rounded-2xl p-4 text-sm font-bold outline-none focus:ring-4 focus:ring-indigo-500/10 dark:text-white transition-all;
}

.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-fade-enter-from, .slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { @apply bg-slate-200 dark:bg-slate-800 rounded-full; }
</style>