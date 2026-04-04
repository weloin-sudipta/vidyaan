<template>
    <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

        <HeroHeader title="Financial Records" subtitle="Tuition & Service Receipts" icon="fa fa-file-invoice-dollar" />

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div v-for="stat in ['Total Paid', 'Pending', 'Scholarship', 'Next Due']" :key="stat" 
                 class="bg-white p-4 rounded-3xl border border-slate-100 shadow-sm">
                <p class="text-[10px] font-black uppercase tracking-widest text-slate-400">{{ stat }}</p>
                <p class="text-lg font-black text-slate-800 tracking-tight">$0.00</p>
            </div>
        </div>

        <div class="space-y-4">
            <div v-for="receipt in receipts" :key="receipt.id"
                class="group flex flex-col md:flex-row md:items-center bg-white border border-slate-200/60 rounded-[2rem] p-2 pr-6 hover:shadow-xl hover:border-emerald-200 transition-all duration-500">
                
                <div class="flex items-center gap-4 p-4 md:border-r border-slate-100 min-w-[180px]">
                    <div class="h-14 w-14 rounded-2xl bg-emerald-50 flex flex-col items-center justify-center text-emerald-600 group-hover:bg-emerald-500 group-hover:text-white transition-colors duration-500">
                        <span class="text-[10px] font-black leading-none uppercase">{{ receipt.month }}</span>
                        <span class="text-xl font-black leading-none mt-1">{{ receipt.day }}</span>
                    </div>
                    <div>
                        <p class="text-[10px] font-black uppercase tracking-widest text-slate-400 leading-none mb-1">Receipt ID</p>
                        <p class="text-xs font-mono font-bold text-slate-600">#{{ receipt.ref }}</p>
                    </div>
                </div>

                <div class="flex-grow p-4">
                    <div class="flex items-center gap-2 mb-1">
                        <h3 class="font-black text-slate-800 group-hover:text-emerald-600 transition-colors">
                            {{ receipt.title }}
                        </h3>
                        <span class="px-2 py-0.5 rounded-md bg-slate-100 text-[9px] font-black uppercase text-slate-500">
                            {{ receipt.method }}
                        </span>
                    </div>
                    <p class="text-xs text-slate-400 font-medium">
                        Processed at {{ receipt.time }} • {{ receipt.category }}
                    </p>
                </div>

                <div class="p-4 flex items-center justify-between md:justify-end gap-8">
                    <div class="text-right">
                        <p class="text-[10px] font-black uppercase tracking-widest text-emerald-500 leading-none mb-1">Amount Paid</p>
                        <p class="text-xl font-black text-slate-900 tracking-tighter">${{ receipt.amount }}</p>
                    </div>

                    <div class="flex gap-2">
                        <button class="h-10 w-10 flex items-center justify-center rounded-xl bg-slate-50 text-slate-400 hover:bg-emerald-50 hover:text-emerald-600 transition-all">
                            <i class="fa fa-eye text-sm"></i>
                        </button>
                        <button class="h-10 px-5 flex items-center gap-2 rounded-xl bg-slate-900 text-white text-[11px] font-black uppercase tracking-widest hover:bg-emerald-600 hover:shadow-lg hover:shadow-emerald-100 transition-all">
                            <i class="fa fa-download"></i>
                            PDF
                        </button>
                    </div>
                </div>

            </div>
        </div>

    </div>
</template>

<script setup>
import { ref } from "vue"
import HeroHeader from "~/components/ui/HeroHeader.vue"

const receipts = ref([
    {
        id: 1,
        ref: "RCP-99281",
        title: "Spring Semester Tuition",
        month: "MAR",
        day: "12",
        time: "14:20 PM",
        amount: "2,450.00",
        method: "Visa •••• 4242",
        category: "Academic Fees"
    },
    {
        id: 2,
        ref: "RCP-99245",
        title: "Lab & Library Access",
        month: "MAR",
        day: "08",
        time: "09:15 AM",
        amount: "120.00",
        method: "Bank Transfer",
        category: "Service Fees"
    },
    {
        id: 3,
        ref: "RCP-98110",
        title: "Campus Housing - Block B",
        month: "FEB",
        day: "28",
        time: "11:45 AM",
        amount: "850.00",
        method: "PayPal",
        category: "Accommodation"
    }
])
</script>