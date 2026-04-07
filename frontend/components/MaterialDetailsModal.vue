<template>
    <AppModal :model-value="isOpen" @update:model-value="$event ? null : closeModal()"
        :title="`${material?.title || 'Material Details'}`" max-width="max-w-2xl">
        <div class="space-y-6">

            <!-- File Preview Section -->
            <div v-if="material?.file"
                class="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center gap-3">
                        <div
                            class="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center">
                            <i class="fa" :class="getFileIcon(material.file)"
                                style="color: var(--color-indigo-600); font-size: 1.5rem;"></i>
                        </div>
                        <div>
                            <p
                                class="text-xs font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-1">
                                File</p>
                            <p class="text-sm font-black text-slate-800 dark:text-slate-200 truncate max-w-xs">
                                {{ material.file_name || getFileName(material.file) }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- File Details Grid -->
                <div class="grid grid-cols-3 gap-4 mb-4">
                    <div>
                        <p
                            class="text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-1">
                            Type</p>
                        <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ material.file_type || 'FILE'
                            }}</p>
                    </div>
                    <div>
                        <p
                            class="text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-1">
                            Size</p>
                        <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ material.file_size || '-' }}
                        </p>
                    </div>
                    <div>
                        <p
                            class="text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-1">
                            Uploaded</p>
                        <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ material.upload_date || '-'
                            }}</p>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="flex gap-2 pt-4 border-t border-slate-200 dark:border-slate-700">
                    <a :href="getFileUrl(material.file)" target="_blank"
                        class="flex-1 text-sm font-black text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 px-4 py-2 rounded-lg hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors flex items-center justify-center gap-2">
                        <i class="fa fa-eye"></i> Preview
                    </a>
                    <a :href="getFileUrl(material.file, true)"
                        class="flex-1 text-sm font-black text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 px-4 py-2 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors flex items-center justify-center gap-2">
                        <i class="fa fa-download"></i> Download
                    </a>
                </div>
            </div>

            <!-- Description Section -->
            <div v-if="material?.description">
                <p class="text-xs font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-3">
                    Description</p>
                <div
                    class="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                    <p class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                        {{ material.description }}
                    </p>
                </div>
            </div>

            <!-- Topic Section -->
            <div v-if="material?.topic || material?.topic_name">
                <p class="text-xs font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-3">Topic
                </p>
                <div
                    class="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 p-4 rounded-xl">
                    <p class="text-sm font-bold text-indigo-900 dark:text-indigo-200">
                        <i class="fa fa-link mr-2"></i>{{ material.topic_name || material.topic }}
                    </p>
                </div>
            </div>

            <!-- Course Section -->
            <div v-if="material?.course">
                <p class="text-xs font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-3">Course
                </p>
                <div
                    class="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                    <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ material.course_name ||
                        material.course }}</p>
                </div>
            </div>

            <!-- Metadata Section -->
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <p class="text-xs font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-2">
                        Category</p>
                    <div class="bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <span class="text-xs font-bold text-slate-700 dark:text-slate-300">{{ material.category || '-'
                            }}</span>
                    </div>
                </div>
                <div>
                    <p class="text-xs font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-2">
                        Upload Date</p>
                    <div class="bg-slate-100 dark:bg-slate-800 px-3 py-2 rounded-lg">
                        <span class="text-xs font-bold text-slate-700 dark:text-slate-300">{{ material.upload_date ||
                            '-' }}</span>
                    </div>
                </div>
            </div>

            <!-- Course and Category Info -->
            <div class="text-xs text-slate-500 dark:text-slate-400">
                <p><strong>Course:</strong> {{ material?.course }}</p>
                <p><strong>Category:</strong> {{ material?.category }}</p>
            </div>
        </div>

        <!-- Footer with Action Buttons -->
        <template #footer>
            <button v-if="!readonly" @click="$emit('edit', material)"
                class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl text-sm font-black uppercase tracking-widest transition-colors flex items-center justify-center gap-2">
                <i class="fa fa-edit"></i> Edit
            </button>
            <button v-if="!readonly" @click="$emit('delete', material)"
                class="flex-1 bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-xl text-sm font-black uppercase tracking-widest transition-colors flex items-center justify-center gap-2">
                <i class="fa fa-trash"></i> Delete
            </button>
            <button @click="closeModal"
                class="flex-1 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 px-6 py-2 rounded-xl text-sm font-black uppercase tracking-widest transition-colors">
                Close
            </button>
        </template>
    </AppModal>
</template>

<script setup>
import AppModal from '~/components/ui/AppModal.vue'

defineProps({
    isOpen: {
        type: Boolean,
        default: false
    },
    material: {
        type: Object,
        default: null
    },
    readonly: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['close', 'edit', 'delete'])

const closeModal = () => {
    emit('close')
}

const getFileIcon = (fileUrl) => {
    if (!fileUrl) return 'fa-file-o'
    const ext = fileUrl.split('.').pop().toLowerCase()
    const iconMap = {
        pdf: 'fa-file-pdf-o',
        doc: 'fa-file-word-o',
        docx: 'fa-file-word-o',
        ppt: 'fa-file-powerpoint-o',
        pptx: 'fa-file-powerpoint-o',
        xls: 'fa-file-excel-o',
        xlsx: 'fa-file-excel-o',
        jpg: 'fa-file-image-o',
        jpeg: 'fa-file-image-o',
        png: 'fa-file-image-o',
        gif: 'fa-file-image-o',
        mp4: 'fa-file-video-o',
        mp3: 'fa-file-audio-o',
        zip: 'fa-file-archive-o',
        txt: 'fa-file-text-o'
    }
    return iconMap[ext] || 'fa-file-o'
}

const getFileName = (filePath) => {
    if (!filePath) return 'Unknown'
    return filePath.split('/').pop()
}

const getFileUrl = (filePath, isDownload = false) => {
    if (!filePath) return ''
    if (filePath.startsWith('http')) return filePath

    if (isDownload) {
        return `/api/method/frappe.utils.file_manager.download_file?file_url=${encodeURIComponent(filePath)}`
    }

    return filePath
}
</script>

<style scoped>
.custom-scrollbar {
    scrollbar-color: #cbd5e1 #f1f5f9;
}

.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

@media (prefers-color-scheme: dark) {
    .custom-scrollbar {
        scrollbar-color: #475569 #1e293b;
    }

    .custom-scrollbar::-webkit-scrollbar-track {
        background: #1e293b;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: #475569;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
}
</style>
