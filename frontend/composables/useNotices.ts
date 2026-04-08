import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { call } from '~/composables/useFrappeFetch'

export interface Notice {
  name?: string
  title?: string
  slug?: string
  category?: string
  content?: string
  published_on?: string
  image?: string
  pinned?: boolean
  [key: string]: unknown
}

export interface NewsItem {
  name?: string
  title?: string
  [key: string]: unknown
}

export interface TopicItem {
  name?: string
  title?: string
  [key: string]: unknown
}

interface ApprovedNoticesResponse {
  pinNotices?: Notice[]
  notices?: Notice[]
  tags?: string[]
  news?: NewsItem[]
  topics?: TopicItem[]
}

export interface UseNoticesReturn {
  pinNotices: Ref<Notice[]>
  notices: Ref<Notice[]>
  tags: Ref<string[]>
  news: Ref<NewsItem[]>
  topics: Ref<TopicItem[]>
  selectedTag: Ref<string>
  filteredNotices: ComputedRef<Notice[]>
  detail: Ref<Notice | null>
  fetchNotices: () => Promise<void>
  fetchDetail: (slug: string) => Promise<void>
}

export function useNotices(): UseNoticesReturn {
  const pinNotices: Ref<Notice[]> = ref([])
  const notices: Ref<Notice[]> = ref([])
  const tags: Ref<string[]> = ref(['All'])
  const news: Ref<NewsItem[]> = ref([])
  const topics: Ref<TopicItem[]> = ref([])
  const selectedTag: Ref<string> = ref('All')
  const detail: Ref<Notice | null> = ref(null)

  const filteredNotices: ComputedRef<Notice[]> = computed(() => {
    if (selectedTag.value === 'All') return notices.value
    return notices.value.filter(n => n.category === selectedTag.value)
  })

  const fetchNotices = async (): Promise<void> => {
    try {
      const res = await call<ApprovedNoticesResponse>(
        'vidyaan.api_folder.notices.get_approved_notices'
      )
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

  const fetchDetail = async (slug: string): Promise<void> => {
    if (!slug) return
    try {
      const res = await call<Notice>('vidyaan.api_folder.notices.get_notice', { slug })
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
