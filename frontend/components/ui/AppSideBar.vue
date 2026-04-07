<template>
  <aside
    class="relative flex flex-col h-full transition-all duration-500 ease-in-out bg-gradient-to-b from-white dark:from-slate-900 via-white dark:via-slate-900 to-indigo-50/40 dark:to-indigo-900/10 backdrop-blur-xl border-r border-gray-200/60 dark:border-slate-800 shadow-xl shadow-indigo-100/40 dark:shadow-none z-50 group flex-shrink-0"
    :class="[isExpanded ? 'w-[270px]' : 'w-[85px]']" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
    
    <div class="flex items-center justify-between px-6 h-20 flex-shrink-0">
      <div class="flex items-center gap-3 overflow-hidden">
        <div
          class="flex-shrink-0 w-10 h-10 bg-gradient-to-tr from-indigo-600 to-purple-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-300/40 transition-transform duration-300 group-hover:scale-110">
          <i class="fa fa-graduation-cap"></i>
        </div>

        <transition name="fade">
          <span v-show="isExpanded"
            class="font-bold text-xl text-gray-800 dark:text-white whitespace-nowrap tracking-wide">
            {{ $config.public.appName }}
          </span>
        </transition>
      </div>

      <button v-show="isExpanded" @click="toggleSidebar"
        class="p-2 text-gray-400 dark:text-gray-500 transition rounded-full hover:bg-indigo-100 dark:hover:bg-slate-800 hover:text-indigo-600 dark:hover:text-indigo-400 duration-300">
        <i class="fa fa-angle-double-left text-xl" :class="{ 'rotate-180': isCollapsed }"></i>
      </button>
    </div>

    <nav class="flex-1 px-4 mt-4 space-y-1 overflow-y-auto custom-scrollbar">
      <ClientOnly>
        <template v-for="(item, index) in navItems" :key="item.name || item.header">

          <div v-if="item.header && isExpanded"
            class="px-4 mt-6 mb-2 text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400/80 dark:text-indigo-400/50">
            {{ item.header }}
          </div>

          <div v-if="!item.header" class="relative group/item">
            <div v-if="isActive(item)" class="absolute left-0 top-2 h-8 w-1 rounded-r-full bg-indigo-600 shadow-md"></div>

            <!-- Parent item with children -->
            <div v-if="item.children" 
              @click="toggleDropdown(item)"
              :class="[
                isActive(item)
                  ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 shadow-md shadow-indigo-100/60 dark:shadow-none'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-white dark:hover:bg-slate-800 hover:shadow-md hover:shadow-indigo-100/40 dark:hover:shadow-none hover:text-indigo-600 dark:hover:text-indigo-300',
                'flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-300 hover:-translate-y-0.5 cursor-pointer'
              ]">
              <div class="flex items-center gap-4">
                <span
                  class="w-6 text-center text-lg transition-all duration-300 group-hover/item:scale-110 group-hover/item:text-indigo-600">
                  <i :class="item.icon"></i>
                </span>

                <span v-show="isExpanded" class="font-medium whitespace-nowrap tracking-wide">
                  {{ item.name }}
                </span>
              </div>

              <i v-if="isExpanded"
                class="fa fa-angle-down transition-transform duration-300 text-xs text-gray-400"
                :class="{ 'rotate-180 text-indigo-600': item.isOpen }"></i>
            </div>

            <!-- Parent item without children (direct link) -->
            <NuxtLink v-else
              :to="item.route"
              :class="[
                isActive(item)
                  ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 shadow-md shadow-indigo-100/60 dark:shadow-none'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-white dark:hover:bg-slate-800 hover:shadow-md hover:shadow-indigo-100/40 dark:hover:shadow-none hover:text-indigo-600 dark:hover:text-indigo-300',
                'flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-300 hover:-translate-y-0.5'
              ]">
              <div class="flex items-center gap-4">
                <span
                  class="w-6 text-center text-lg transition-all duration-300 group-hover/item:scale-110 group-hover/item:text-indigo-600">
                  <i :class="item.icon"></i>
                </span>

                <span v-show="isExpanded" class="font-medium whitespace-nowrap tracking-wide">
                  {{ item.name }}
                </span>
              </div>
            </NuxtLink>

            <!-- Dropdown children -->
            <transition name="expand">
              <div v-if="item.children && item.isOpen && isExpanded" class="overflow-hidden">
                <div class="mt-2 ml-4 pl-6 border-l border-indigo-100 space-y-1 my-2">
                  <NuxtLink 
                    v-for="sub in item.children" 
                    :key="sub.name" 
                    :to="sub.route" 
                    @click="handleChildClick(item)"
                    :class="[
                      route.path === sub.route
                        ? 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10'
                        : 'text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-300 hover:bg-indigo-50/60 dark:hover:bg-slate-800',
                      'block px-4 py-2 text-sm font-medium rounded-lg transition-all duration-300 hover:translate-x-1'
                    ]">
                    {{ sub.name }}
                  </NuxtLink>
                </div>
              </div>
            </transition>
          </div>
        </template>
      </ClientOnly>

      <div class="pt-4 mt-4 border-t border-gray-100 dark:border-slate-800">
        <div class="relative group/item">
          <button @click="handleLogout" :disabled="isLoggingOut"
            class="w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-300 text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-500/10 hover:text-red-500 dark:hover:text-red-400 hover:shadow-md dark:hover:shadow-none hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed">
            <div class="flex items-center gap-4">
              <span
                class="w-6 text-center text-lg transition-all duration-300 group-hover/item:scale-110 group-hover/item:text-red-500">
                <i :class="isLoggingOut ? 'fa fa-spinner fa-spin' : 'fa fa-sign-out'"></i>
              </span>
              <span v-show="isExpanded" class="font-medium whitespace-nowrap tracking-wide">
                {{ isLoggingOut ? 'Logging out...' : 'Logout' }}
              </span>
            </div>
          </button>
        </div>
      </div>
    </nav>

    <div v-show="isExpanded"
      class="p-4 border-t border-gray-100 dark:border-slate-800 text-[10px] text-gray-400 dark:text-gray-500 text-center uppercase tracking-widest font-bold">
      © 2026 <b>{{ $config.public.appName }}</b>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { logout } from '~/composable/useAuth'
import { useUserProfile } from '~/composable/useUserProfile'

const { userRole, loadProfile } = useUserProfile() 
const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const isHovered = ref(false)
const isLoggingOut = ref(false)
let hoverTimeout = null

const isExpanded = computed(() => {
  return !isCollapsed.value || isHovered.value
})

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleMouseEnter = () => {
  if (hoverTimeout) clearTimeout(hoverTimeout)
  hoverTimeout = setTimeout(() => {
    isHovered.value = true
  }, 50)
}

const handleMouseLeave = () => {
  if (hoverTimeout) clearTimeout(hoverTimeout)
  isHovered.value = false
}

const toggleDropdown = (item) => {
  if (item.children) {
    item.isOpen = !item.isOpen
  }
}

const handleChildClick = (parentItem) => {
  // Optional: Keep parent dropdown open after clicking child
  // parentItem.isOpen = true
}

const handleLogout = async () => {
  if (isLoggingOut.value) return
  try {
    isLoggingOut.value = true
    await logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  } finally {
    isLoggingOut.value = false
  }
}

// Reactive nav items with proper state management
const navItems = ref([])

const updateNavItems = () => {
  if (userRole.value === 'teacher') {
    navItems.value = [
      { header: 'Main Menu' },
      { name: 'Dashboard', icon: 'fa fa-th-large', route: '/' },
      { name: 'Notice & News', icon: 'fa fa-bullhorn', route: '/notices' },
     // { name: 'Events', icon: 'fa fa-calendar-alt', route: '/events' },

      { header: 'Academic Life' },
      {
        name: 'Academics',
        icon: 'fa fa-book-open',
        isOpen: false,
        children: [
          { name: 'Attendance', route: '/teacher/academics/attendance' },
          { name: 'Assignments', route: '/teacher/academics/assignments' },
          { name: 'Lesson Planning', route: '/teacher/academics/lesson-planning' },
          { name: 'My Classes', route: '/teacher/academics/my-classes' },
          // { name: 'Study Materials', route: '/academics/study-materials' }
        ]
      },

      { header: 'Grading' },
      {
        name: 'Grading',
        icon: 'fa fa-chart-line',
        isOpen: false,
        children: [
          { name: 'Mark Entry', route: '/teacher/grading/mark-entry' },
          { name: 'Performance', route: '/teacher/grading/performance' },
        ]
      },
      { name: 'Applications', icon: 'fa fa-file-pen', route: '/teacher/applications' },
      { name: 'Students', icon: 'fa fa-users', route: '/teacher/students' },
      { name: 'My Profile', icon: 'fa fa-user-circle', route: '/teacher/profile' },
    ]
  } else {
    // Student / other roles
    navItems.value = [
      { header: 'Main Menu' },
      { name: 'Dashboard', icon: 'fa fa-th-large', route: '/' },
      { name: 'Notice & News', icon: 'fa fa-bullhorn', route: '/notices' },
     // { name: 'Events', icon: 'fa fa-calendar', route: '/events' },

      { header: 'Academic Life' },
      {
        name: 'Academics',
        icon: 'fa fa-graduation-cap',
        isOpen: false,
        children: [
          { name: 'Subjects', route: '/academics/subjects' },
          { name: 'Study Materials', route: '/academics/study-materials' },
          { name: 'Timetable', route: '/academics/timetable' },
          { name: 'Assignments', route: '/academics/assignments' },
        ]
      },
      { name: 'Attendance', icon: 'fa fa-calendar-check-o', route: '/attendance' },
      {
        name: 'Examination',
        icon: 'fa fa-file-text-o',
        isOpen: false,
        children: [
          { name: 'Schedule', route: '/exam/schedule' },
          { name: 'Results', route: '/exam/result' },
        ]
      },

      { header: 'Administrative Services' },
      { name: 'Applications', icon: 'fa fa-file-pen', route: '/applications/' },
      { name: 'Library', icon: 'fa fa-book', route: '/library' },

      { header: 'Personal' },
      { name: 'Faculty', icon: 'fa-solid fa-book-open-reader', route: '/faculty' },
      { name: 'My Profile', icon: 'fa fa-user-circle-o', route: '/profile' },
    ]
  }
}


const isActive = (item) => {
  if (item.route && item.route === route.path) return true
  if (item.children) {
    return item.children.some(child => {
      // Exact match
      if (child.route === route.path) return true
      // For nested routes (e.g., /teacher/academics/attendance matches /teacher/academics)
      if (route.path.startsWith(child.route + '/')) return true
      return false
    })
  }
  return false
}

// Auto-expand parent items when a child route is active
const expandActiveParents = () => {
  navItems.value.forEach(item => {
    if (item.children && isActive(item)) {
      item.isOpen = true
    }
  })
}

// Watch for route changes to update active states
watch(() => route.path, () => {
  expandActiveParents()
}, { immediate: true })

// Watch for userRole changes
watch(userRole, () => {
  updateNavItems()
  expandActiveParents()
}, { immediate: true })

onMounted(() => {
  updateNavItems()
  expandActiveParents()
  loadProfile()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.4s cubic-bezier(.4, 0, .2, 1);
  max-height: 400px;
  opacity: 1;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-5px);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* Dark mode scrollbar */
@media (prefers-color-scheme: dark) {
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #334155;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #475569;
  }
}

/* Rotate animation for collapse button */
.rotate-180 {
  transform: rotate(180deg);
}

/* Prevent text selection on double click */
.no-select {
  user-select: none;
  -webkit-user-select: none;
}
</style>