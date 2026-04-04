<template>
    <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

        <HeroHeader title="Certificates" subtitle="My Outstanding Achievements" icon="fa fa-award" />

        <div class="flex gap-3 overflow-x-auto no-scrollbar pb-2">
            <button v-for="tag in ['All', 'Course', 'Workshop', 'Achievement']" :key="tag"
                class="px-5 py-2.5 bg-white/50 backdrop-blur-md rounded-2xl text-[10px] font-black uppercase tracking-widest border border-slate-200 text-slate-500 hover:bg-indigo-600 hover:text-white hover:border-indigo-600 hover:shadow-lg hover:shadow-indigo-200 transition-all duration-300">
                {{ tag }}
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">

            <div v-for="doc in certificates" :key="doc.id"
                class="group relative flex flex-col bg-white border border-slate-200 rounded-[2.5rem] shadow-sm hover:shadow-2xl transition-all duration-500 overflow-hidden">
                
                <div class="absolute top-0 right-0 p-8 opacity-[0.03] group-hover:opacity-10 transition-opacity">
                    <i class="fa fa-shield-halved text-8xl -rotate-12"></i>
                </div>

                <div class="p-8">
                    <div class="flex justify-between items-start mb-6">
                        <div class="flex items-center gap-1.5 px-3 py-1 bg-indigo-50 rounded-full border border-indigo-100">
                            <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
                            <span class="text-[9px] font-black uppercase tracking-wider text-indigo-700">Official ID</span>
                        </div>
                        <i class="fa fa-certificate text-slate-200 group-hover:text-indigo-500 transition-colors"></i>
                    </div>

                    <h3 class="text-lg font-black text-slate-800 leading-tight mb-2 min-h-[3.5rem] group-hover:text-indigo-600 transition-colors">
                        {{ doc.title }}
                    </h3>

                    <div class="flex items-center gap-2">
                        <div class="h-px w-8 bg-slate-200"></div>
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                            {{ doc.date }}
                        </p>
                    </div>
                </div>

                <div class="relative flex items-center px-4">
                    <div class="absolute left-0 -ml-3 w-6 h-6 rounded-full bg-slate-50 border-r border-slate-200"></div>
                    <div class="w-full border-t border-dashed border-slate-200"></div>
                    <div class="absolute right-0 -mr-3 w-6 h-6 rounded-full bg-slate-50 border-l border-slate-200"></div>
                </div>

                <div class="p-6 pt-4 flex items-center justify-between gap-4">
                    <button class="flex items-center gap-2 text-[11px] font-black uppercase tracking-tighter text-slate-500 hover:text-indigo-600 transition">
                        <i class="fa fa-expand"></i>
                        Full View
                    </button>

                    <button class="group/btn relative overflow-hidden flex items-center gap-2 px-6 py-3 bg-slate-900 rounded-2xl text-white text-xs font-bold transition-all hover:pr-8 hover:bg-indigo-600">
                        <span>Download</span>
                        <i class="fa fa-arrow-right absolute right-[-20px] group-hover/btn:right-3 transition-all"></i>
                    </button>
                </div>

            </div>

        </div>
    </div>
</template>

<script setup>
import { ref } from "vue"
import HeroHeader from "~/components/ui/HeroHeader.vue"

const certificates = ref([
    {
        id: 1,
        title: "Python Programming Certificate",
        date: "12 March 2026",
        preview: ""
    },
    {
        id: 2,
        title: "Web Development Workshop",
        date: "10 March 2026",
        preview: ""
    },
    {
        id: 3,
        title: "AI Hackathon Participation",
        date: "05 March 2026",
        preview: ""
    }
])
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>