<template>
    <NuxtLayout>
        <NuxtPage />
        <ToastContainer />
    </NuxtLayout>
</template>

<script setup>
import ToastContainer from '~/components/ToastContainer.vue';
</script>

<style>
.animate-in {
  opacity: 0;
  animation: slideUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>