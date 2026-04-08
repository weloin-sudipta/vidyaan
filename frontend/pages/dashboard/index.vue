<template>
  <!-- Loading while we determine the role -->
  <div v-if="isLoading" class="flex items-center justify-center h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300">
    <div class="relative text-center">
      <div class="w-24 h-24 mx-auto mb-6 relative">
        <div class="absolute inset-0 border-4 border-dashed border-indigo-300 rounded-full animate-spin"></div>
        <div class="absolute inset-0 border-4 border-transparent border-t-indigo-600 border-r-indigo-600 rounded-full animate-spin"></div>
      </div>
      <p class="text-sm font-bold text-slate-600 dark:text-slate-300">
        Loading Dashboard…
      </p>
    </div>
  </div>

  <!-- Role-based dashboard rendering (lazy loaded) -->
  <component v-else-if="dashboardComponent" :is="dashboardComponent" />

  <!-- Fallback: unknown role -->
  <div v-else class="flex items-center justify-center h-screen">
    <p class="text-slate-400 font-bold">No dashboard available for your role.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, onMounted, defineAsyncComponent } from 'vue'
import { useUserProfile } from '~/composables/useUserProfile'

definePageMeta({ middleware: 'auth' })

const { userRole, isAuthenticated, loadProfile } = useUserProfile()

const isLoading = ref(true)
const dashboardComponent = shallowRef<object | null>(null)

// Lazy load each role's dashboard to avoid bundling all three together
const StudentDashboard = defineAsyncComponent(() => import('~/components/dashboard/StudentDashboardView.vue'))
const TeacherDashboard = defineAsyncComponent(() => import('~/components/dashboard/TeacherDashboardView.vue'))
const AdminDashboard   = defineAsyncComponent(() => import('~/components/dashboard/AdminDashboardView.vue'))

onMounted(async () => {
  if (!isAuthenticated.value || !userRole.value) {
    await loadProfile()
  }

  const role = (userRole.value ?? '').toLowerCase()

  if (role === 'student') {
    dashboardComponent.value = StudentDashboard
  } else if (role === 'teacher' || role === 'instructor') {
    dashboardComponent.value = TeacherDashboard
  } else if (role === 'admin' || role === 'institute admin' || role === 'system administrator') {
    dashboardComponent.value = AdminDashboard
  } else {
    // Unknown role — fall back to student dashboard
    dashboardComponent.value = StudentDashboard
  }

  isLoading.value = false
})
</script>
