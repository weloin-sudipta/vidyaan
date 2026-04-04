import { ref } from 'vue';

const toasts = ref([]);

export const useToast = () => {
    const addToast = (message, type = 'success', duration = 4000) => {
        const id = Date.now() + Math.random().toString(36).substr(2, 9);
        toasts.value.push({ id, message, type });
        if (duration > 0) {
            setTimeout(() => {
                removeToast(id);
            }, duration);
        }
    };

    const removeToast = (id) => {
        toasts.value = toasts.value.filter(t => t.id !== id);
    };

    return { toasts, addToast, removeToast };
};
