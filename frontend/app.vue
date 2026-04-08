<template>
    <NuxtLayout>
        <NuxtPage />
        <ToastContainer />
        <ConfirmDialog
            v-model="open"
            :title="opts.title"
            :message="opts.message"
            :hint="opts.hint"
            :variant="opts.variant"
            :confirm-text="opts.confirmText"
            :cancel-text="opts.cancelText"
            :loading-text="opts.loadingText"
            :confirm-icon="opts.confirmIcon"
            :icon="opts.icon"
            :loading="loading"
            @confirm="_accept"
            @cancel="_cancel"
        />
    </NuxtLayout>
</template>

<script setup lang="ts">
import ToastContainer from '~/components/ToastContainer.vue'
import ConfirmDialog from '~/components/ui/ConfirmDialog.vue'
import { useConfirm } from '~/composables/useConfirm'

const { open, loading, opts, _accept, _cancel } = useConfirm()
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