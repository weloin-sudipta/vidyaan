<template>
  <!-- LOADING SCREEN -->
  <div v-if="isLoading">
    <div class="flex items-center justify-center h-screen bg-[#f5f5f9] dark:bg-slate-950 transition-colors duration-300">

      <div class="relative text-center">

        <!-- Loader Ring -->
        <div class="w-24 h-24 mx-auto mb-6 relative">
          <div class="absolute inset-0 border-4 border-dashed border-indigo-300 rounded-full animate-spin"></div>
          <div class="absolute inset-0 border-4 border-transparent border-t-indigo-600 border-r-indigo-600 rounded-full animate-spin"></div>
        </div>

        <!-- Role Info -->
        <p class="text-sm font-bold text-slate-600 dark:text-slate-300 mb-3">
          Loading {{ userRole || '...' }} Dashboard
        </p>

        <!-- Progress Bar -->
        <div class="w-64 h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden mx-auto">
          <div
            class="h-full bg-indigo-600 transition-all duration-300"
            :style="{ width: loadingStep + '%' }"
          ></div>
        </div>

      </div>

    </div>
  </div>

  <!-- DASHBOARD -->
  <component v-else :is="currentComponent" />
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Dashboards
import StudentDashboard from '~/pages/dashboard/student.vue'
import TeacherDashboard from '~/pages/dashboard/teacher.vue'

// Composable
import { useUserProfile } from '~/composable/useUserProfile'

const { userRole, loadProfile } = useUserProfile()

const isLoading = ref(true)
const loadingStep = ref(0)
const currentComponent = ref(null)

onMounted(async () => {
  try {
    // Step 1: Load user role from API
    await loadProfile()

    // Step 2: Animate loader progress
    const interval = setInterval(() => {
      if (loadingStep.value < 100) {
        loadingStep.value += 5
      } else {
        clearInterval(interval)
      }
    }, 50)

    // Step 3: Wait for UX + ensure role is available
    setTimeout(() => {
      isLoading.value = false

      // Step 4: Role-based dashboard selection (roles are normalized to lowercase)
      if (userRole.value === 'student') {
        currentComponent.value = StudentDashboard
      } 
      else if (userRole.value === 'teacher') {
        currentComponent.value = TeacherDashboard
      } 
      else {
        console.warn('Unknown role:', userRole.value)
        currentComponent.value = StudentDashboard // fallback
      }

    }, 500)

  } catch (err) {
    console.error('Error loading profile:', err)
    isLoading.value = false
    currentComponent.value = StudentDashboard // safe fallback
  }
})
</script>

<style scoped>
</style>