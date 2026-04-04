<template>
  <!-- blank loader (very fast redirect) -->
  <div class="h-screen w-screen bg-[#f8fafc]"></div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useError, clearError } from '#app'
import { useRouter } from 'vue-router'

const error = useError()
const router = useRouter()

onMounted(() => {
  const code = error.value?.statusCode || 500

  let path = '/error/default'

  if (code === 404) {
    path = '/error/404'
  } else if (code === 500) {
    path = '/error/500'
  }

  // clear nuxt error state before navigation
  clearError({ redirect: path })

  // fallback (just in case)
  router.replace(path)
})
</script>