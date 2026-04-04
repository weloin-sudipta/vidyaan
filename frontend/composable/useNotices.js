import { ref, computed } from 'vue'
import { call } from '~/composable/useFrappeFetch'

export function useNotices() {
    const pinNotices = ref([])
    const notices = ref([])
    const tags = ref(['All'])
    const news = ref([])
    const topics = ref([])
    const selectedTag = ref('All')
    const detail = ref(null)

    const filteredNotices = computed(() => {
        if (selectedTag.value === 'All') return notices.value
        return notices.value.filter(n => n.category === selectedTag.value)
    })

    const fetchNotices = async () => {
        try {
            const res = await call('vidyaan.api_folder.notices.get_approved_notices')
            if (res) {
                pinNotices.value = res.pinNotices || []
                notices.value = res.notices || []
                tags.value = res.tags || ['All']
                news.value = res.news || []
                topics.value = res.topics || []
            }
        } catch (err) {
            console.error('Failed to load news & notices:', err)
        }
    }

    const fetchDetail = async (slug) => {
        if (!slug) return
        try {
            const res = await call('vidyaan.api_folder.notices.get_notice', { slug })
            detail.value = res || null
        } catch (err) {
            console.error('Failed to fetch notice', err)
        }
    }

    return {
        pinNotices,
        notices,
        tags,
        news,
        topics,
        selectedTag,
        filteredNotices,
        detail,
        fetchNotices,
        fetchDetail,
    }
}