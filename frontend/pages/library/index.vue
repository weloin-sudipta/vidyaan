<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans transition-colors">
    <div class="max-w-[1440px] mx-auto space-y-6">
      
      <!-- Header -->
      <UiCard as="header" class="flex flex-col md:flex-row justify-between items-center gap-6">
        <div>
          <NuxtLink to="/library/dashboard">
            <h1 class="text-3xl font-black tracking-tight text-slate-800 dark:text-slate-100 transition-colors">Library Management</h1>
          </NuxtLink>
          <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mt-1 transition-colors">Physical Book Tracking System</p>
        </div>

        <!-- Tabs -->
        <div class="flex p-1.5 bg-slate-100 dark:bg-slate-800/50 rounded-2xl overflow-x-auto transition-colors">
          <button @click="currentView = 'issued'" :class="tabClass(currentView === 'issued')">Issued Books</button>
          <button @click="currentView = 'all'" :class="tabClass(currentView === 'all')">All Books</button>
          <button @click="currentView = 'tracking'" :class="tabClass(currentView === 'tracking')">Tracking</button>
          <button @click="currentView = 'recommendations'" :class="tabClass(currentView === 'recommendations')">Recommendations</button>
        </div>
      </UiCard>

      <!-- Tab Content -->
      <transition name="fade" mode="out-in">
        <component 
          :is="
            currentView === 'issued' ? IssuedBooks 
            : currentView === 'all' ? AllBooks 
            : currentView === 'tracking' ? RequestTracking 
            : Recommendations
          " 
        />
      </transition>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import IssuedBooks from './tabs/issuedBooks.vue'
import AllBooks from './tabs/allBooks.vue'
import RequestTracking from './tabs/requestTracking.vue'
import Recommendations from './tabs/recommendations.vue'

const currentView = ref('issued');

const tabClass = (active) => active 
  ? 'px-8 py-2.5 bg-white dark:bg-indigo-600 text-indigo-600 dark:text-white shadow-sm dark:shadow-none rounded-xl text-[10px] font-black uppercase tracking-widest transition-all'
  : 'px-8 py-2.5 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-white/50 dark:hover:bg-slate-800/50 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all';
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>