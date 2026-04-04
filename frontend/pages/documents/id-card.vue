
<template>
  <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

    <HeroHeader
      title="Identity Cards"
      subtitle="Official Academic & Library Access"
      icon="fa fa-address-card"
    />

    <!-- GRID -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8 justify-items-center py-8">

      <div
        v-for="card in cards"
        :key="card.type"
        class="relative group w-full max-w-[320px]"
      >

        <!-- CARD -->
        <div
          class="w-full bg-[#FDFDFD] border-t-[12px] rounded-3xl shadow-xl p-6 sm:p-8 transition-all duration-500 group-hover:shadow-indigo-200/40 group-hover:-translate-y-2"
          :class="card.borderColor"
        >

          <!-- HEADER -->
          <div class="text-center mb-6">
            <h4 class="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 mb-1">
              {{ card.institution }}
            </h4>
            <div class="h-1 w-12 mx-auto rounded-full" :class="card.accentBg"></div>
          </div>

          <!-- PHOTO -->
          <div
            class="relative w-28 sm:w-32 h-36 sm:h-40 bg-slate-50 mx-auto rounded-2xl overflow-hidden border-4 border-white shadow-inner mb-6 flex items-center justify-center"
          >
            <i class="fa fa-user text-slate-200 text-5xl"></i>

            <div
              class="absolute bottom-0 inset-x-0 py-1.5 text-center backdrop-blur-md"
              :class="card.badgeBg"
            >
              <span class="text-[8px] font-black text-white uppercase tracking-tighter">
                {{ card.status }}
              </span>
            </div>
          </div>

          <!-- NAME -->
          <div class="text-center space-y-1 mb-6">
            <h2 class="text-xl sm:text-2xl font-black text-slate-900 tracking-tight leading-none">
              Sudipta Ghosh
            </h2>
            <p class="text-[10px] font-bold uppercase tracking-widest" :class="card.accentText">
              {{ card.role }}
            </p>
          </div>

          <!-- INFO -->
          <div class="grid grid-cols-2 border-y border-slate-100 py-5 gap-4">
            <div class="text-center border-r border-slate-100">
              <p class="text-[9px] font-black text-slate-400 uppercase mb-1">Pass ID</p>
              <p class="text-xs font-mono font-bold text-slate-800">
                {{ card.idNumber }}
              </p>
            </div>

            <div class="text-center">
              <p class="text-[9px] font-black text-slate-400 uppercase mb-1">Valid Thru</p>
              <p class="text-xs font-bold text-slate-800 uppercase">
                {{ card.expiry }}
              </p>
            </div>
          </div>

          <!-- QR -->
          <div class="mt-6 flex flex-col items-center">
            <div
              class="p-3 sm:p-4 bg-white border-2 border-slate-50 rounded-2xl shadow-sm mb-2 group-hover:scale-110 transition-transform duration-500"
            >
              <i class="fa fa-qrcode text-4xl sm:text-5xl text-slate-800"></i>
            </div>

            <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest group-hover:text-slate-600">
              Scan for verification
            </p>
          </div>

        </div>

        <!-- SIDE ICON -->
        <div
          class="absolute top-1/2 -right-3 sm:-right-4 h-10 w-7 sm:h-12 sm:w-8 rounded-lg -z-10 shadow-lg flex items-center justify-center text-white text-[10px] transition-all group-hover:right-[-18px]"
          :class="card.accentBg"
        >
          <i :class="card.bookmarkIcon"></i>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import HeroHeader from "~/components/ui/HeroHeader.vue"

const cards = ref([
  {
    type: "library",
    institution: "Central Library",
    status: "Verified Member",
    role: "Software Developer",
    idNumber: "LIB-2026-X",
    expiry: "Dec 2026",
    bookmarkIcon: "fa fa-bookmark",
    borderColor: "border-indigo-600",
    accentBg: "bg-indigo-600",
    badgeBg: "bg-indigo-600/90",
    accentText: "text-indigo-500"
  },
  {
    type: "school",
    institution: "Ignis IT Academy",
    status: "Active Scholar",
    role: "CS Department",
    idNumber: "CRTI-B-992",
    expiry: "Aug 2027",
    bookmarkIcon: "fa fa-graduation-cap",
    borderColor: "border-emerald-500",
    accentBg: "bg-emerald-500",
    badgeBg: "bg-emerald-500/90",
    accentText: "text-emerald-600"
  }
])
</script>
