<template>
  <nav
    class="sticky top-4 z-40 mx-6 mt-4 p-4 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-xl shadow-sm border border-gray-100 dark:border-slate-800 flex items-center justify-between flex-shrink-0 transition-colors duration-300">

    <!-- Search Box -->
    <div class="flex items-center flex-1 max-w-md">
      <div class="relative w-full group">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <i class="fa fa-search text-gray-400 group-focus-within:text-indigo-600 transition-colors duration-200"></i>
        </div>
        <input
          type="text"
          placeholder="Search (Ctrl+/)"
          class="block w-full pl-10 pr-12 py-2.5 bg-white dark:bg-slate-800 border border-transparent rounded-xl text-sm text-gray-700 dark:text-slate-200 
                 placeholder-gray-400 dark:placeholder-slate-500 shadow-sm transition-all duration-300
                 hover:bg-gray-50 dark:hover:bg-slate-700
                 focus:bg-white dark:focus:bg-slate-800 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 focus:outline-none"
        />
        <div class="absolute inset-y-0 right-0 pr-3 hidden md:flex items-center pointer-events-none">
          <kbd class="px-1.5 py-0.5 text-[10px] font-semibold text-gray-400 dark:text-slate-500 bg-gray-100 dark:bg-slate-800/80 border border-gray-200 dark:border-slate-700 rounded-md transition-colors">
            ⌘ /
          </kbd>
        </div>
      </div>
    </div>

    <!-- Notification, Dark Mode, Profile -->
    <div class="flex items-center gap-4">
      <!-- Notification -->
      <div class="relative">
        <button @click="isNotifOpen = !isNotifOpen"
          class="relative p-2 text-gray-500 hover:bg-indigo-50 hover:text-indigo-600 rounded-full transition duration-300">
          <span class="absolute w-2 h-2 bg-red-500 border-2 border-white rounded-full top-2 right-2"></span>
          <i class="fa fa-bell-o text-xl"></i>
        </button>

        <div v-if="isNotifOpen"
          class="absolute right-0 mt-3 w-80 md:w-96 bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-gray-100 dark:border-slate-800 overflow-hidden z-50 animate-fade-in-up transition-colors">
          <div class="p-4 border-b border-gray-50 dark:border-slate-800 flex justify-between items-center bg-white dark:bg-slate-900 transition-colors">
            <h6 class="text-sm font-bold text-gray-800 dark:text-slate-100 transition-colors">Notifications</h6>
            <button class="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase hover:underline transition-colors">Mark all as read</button>
          </div>
          <div class="max-h-[400px] overflow-y-auto custom-scrollbar">
            <div v-if="notifications.length > 0">
              <div v-for="notif in notifications" :key="notif.id"
                   class="p-4 flex gap-4 hover:bg-gray-50 dark:hover:bg-slate-800/50 cursor-pointer border-b border-gray-50 dark:border-slate-800/50 last:border-0 transition-colors">
                <div :class="['w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-colors', notif.bg]">
                  <i :class="['fa text-white', notif.icon]"></i>
                </div>
                <div class="flex-1">
                  <p class="text-xs font-bold text-gray-800 dark:text-slate-200 mb-1 transition-colors">{{ notif.title }}</p>
                  <p class="text-[11px] text-gray-500 dark:text-slate-400 line-clamp-2 leading-relaxed transition-colors">{{ notif.message }}</p>
                  <p class="text-[9px] text-gray-400 dark:text-slate-500 mt-2 font-medium transition-colors"><i class="fa fa-clock-o mr-1"></i>{{ notif.time }}</p>
                </div>
                <div v-if="!notif.read" class="w-2 h-2 bg-indigo-500 dark:bg-indigo-400 rounded-full mt-1 transition-colors"></div>
              </div>
            </div>
            <div v-else class="p-10 text-center">
              <i class="fa fa-bell-slash-o text-gray-200 dark:text-slate-700 text-4xl mb-3 transition-colors"></i>
              <p class="text-xs text-gray-400 dark:text-slate-500 font-medium transition-colors">All caught up!</p>
            </div>
          </div>
          <button
            class="w-full p-3 text-center text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50/50 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-slate-700/50 transition-colors">
            View All Notifications
          </button>
        </div>
      </div>

      <!-- Dark Mode Toggle (3-Way) -->
      <div class="flex items-center gap-1 bg-gray-100 dark:bg-slate-900/50 p-1 rounded-full border border-gray-200 dark:border-slate-800 ml-2 shadow-inner transition-colors">
        <button @click="colorMode.preference = 'light'" title="Light Mode"
          :class="colorMode.preference === 'light' ? 'bg-white shadow-sm text-indigo-600 dark:bg-slate-700 dark:text-indigo-400' : 'text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200'"
          class="p-1.5 rounded-full transition-all duration-300 w-8 h-8 flex items-center justify-center">
          <i class="fa fa-sun-o"></i>
        </button>
        <button @click="colorMode.preference = 'system'" title="System Mode"
          :class="colorMode.preference === 'system' ? 'bg-white shadow-sm text-indigo-600 dark:bg-slate-700 dark:text-indigo-400' : 'text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200'"
          class="p-1.5 rounded-full transition-all duration-300 w-8 h-8 flex items-center justify-center">
          <i class="fa fa-desktop"></i>
        </button>
        <button @click="colorMode.preference = 'dark'" title="Dark Mode"
          :class="colorMode.preference === 'dark' ? 'bg-white shadow-sm text-indigo-600 dark:bg-slate-700 dark:text-indigo-400' : 'text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200'"
          class="p-1.5 rounded-full transition-all duration-300 w-8 h-8 flex items-center justify-center">
          <i class="fa fa-moon-o"></i>
        </button>
      </div>

      <!-- Profile -->
      <div class="flex items-center gap-3 pl-2">
        <ClientOnly>
          <div class="flex items-center gap-3">
            <div class="flex-col items-end hidden sm:flex">
              <span class="text-sm font-semibold text-gray-700 dark:text-slate-200 transition-colors">{{ profileData.fullName || 'User' }}</span>
              <span class="text-xs text-gray-400 dark:text-slate-500 uppercase transition-colors">{{ userRole || 'User' }}</span>
            </div>
            <div class="w-10 h-10 font-bold text-white bg-indigo-500 border-2 border-white dark:border-slate-800 rounded-full shadow-sm flex items-center justify-center transition-colors">
              {{ profileData.firstName?.charAt(0) ? profileData.firstName.charAt(0) + (profileData.lastName?.charAt(0) || '') : 'U' }}
            </div>
          </div>
          <template #fallback>
            <div class="flex items-center gap-3">
              <div class="flex-col items-end hidden sm:flex space-y-1">
                <span class="h-4 w-20 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></span>
                <span class="h-3 w-12 bg-slate-200 dark:bg-slate-700 rounded animate-pulse"></span>
              </div>
              <div class="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-full animate-pulse border-2 border-white dark:border-slate-800"></div>
            </div>
          </template>
        </ClientOnly>
      </div>
    </div>
  </nav>

  <div v-if="isNotifOpen" @click="isNotifOpen = false" class="fixed inset-0 z-30 bg-transparent"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserProfile } from '~/composable/useUserProfile'

const colorMode = useColorMode()
const { profileData, userRole, loadProfile } = useUserProfile()
const isNotifOpen = ref(false)

const notifications = ref([
  {
    id: 1,
    title: 'New Exam Scheduled',
    message: 'The Mid-term schedule for Advanced UI/UX has been published.',
    time: '5 min ago',
    icon: 'fa-calendar',
    bg: 'bg-indigo-500',
    read: false
  },
  {
    id: 2,
    title: 'Fee Payment Successful',
    message: 'Your payment was successful.',
    time: '2 hours ago',
    icon: 'fa-check-circle',
    bg: 'bg-emerald-500',
    read: true
  }
])

onMounted(async () => {
  await loadProfile()
})
</script>