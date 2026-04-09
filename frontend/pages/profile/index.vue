<template>
  <div>
    <component v-if="profileComponent" :is="profileComponent" />
    <div v-else class="flex items-center justify-center h-64">
      <p class="text-slate-400 dark:text-slate-500 font-bold text-sm">Loading profile…</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { shallowRef, onMounted, defineAsyncComponent } from 'vue'
import { useUserProfile } from '~/composables/student/useUserProfile'

const { userRole, isAuthenticated, loadProfile } = useUserProfile()

const profileComponent = shallowRef<object | null>(null)

const StudentProfile = defineAsyncComponent(() => import('~/components/profile/StudentProfileView.vue'))
const TeacherProfile = defineAsyncComponent(() => import('~/components/profile/TeacherProfileView.vue'))

onMounted(async () => {
  if (!isAuthenticated.value || !userRole.value) {
    await loadProfile()
  }
  const role = (userRole.value ?? '').toLowerCase()
  if (role === 'teacher' || role === 'instructor') {
    profileComponent.value = TeacherProfile
  } else {
    profileComponent.value = StudentProfile
  }
})
</script>
