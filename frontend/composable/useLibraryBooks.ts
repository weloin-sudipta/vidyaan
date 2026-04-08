import { ref, type Ref } from 'vue'
import { createResource } from './useFrappeFetch'
import { useBookRequest, type UseBookRequestReturn } from './useBookRequest'

// ─── Library shapes ───────────────────────────────────────────────────────
export interface LibraryBook {
  name?: string
  id?: string
  title?: string
  author?: string
  library?: string
  cover_image?: string
  isbn?: string
  available?: boolean
  [key: string]: unknown
}

export interface BookIssueRecord {
  name?: string
  book?: string
  status?: string
  due_date?: string
  [key: string]: unknown
}

export interface BookRequestRecord {
  name?: string
  book?: string
  library?: string
  status?: string
  request_id?: string
  [key: string]: unknown
}

export interface RecommendationSection {
  name?: string
  title?: string
  books?: LibraryBook[]
  [key: string]: unknown
}

interface RecommendationsResponse {
  sections?: RecommendationSection[]
  [key: string]: unknown
}

export interface UseBooksReturn {
  data: Ref<BookIssueRecord[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchData: () => Promise<void>
  requestedBook: Ref<BookRequestRecord[]>
  fetchRequestedBook: () => Promise<void>
  allBooks: Ref<LibraryBook[]>
  fetchAllBooks: () => Promise<void>
  recommendations: Ref<RecommendationSection[]>
  fetchRecommendations: () => Promise<void>
  bookRequest: UseBookRequestReturn
  isBookRequested: UseBookRequestReturn['isBookRequested']
  getButtonText: UseBookRequestReturn['getButtonText']
  toggleBookRequest: UseBookRequestReturn['toggleBookRequest']
  requestBook: UseBookRequestReturn['requestBook']
  cancelRequest: UseBookRequestReturn['cancelRequest']
}

export const useBooks = (): UseBooksReturn => {
  const data: Ref<BookIssueRecord[]> = ref([])
  const requestedBook: Ref<BookRequestRecord[]> = ref([])
  const allBooks: Ref<LibraryBook[]> = ref([])
  const recommendations: Ref<RecommendationSection[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  // Integrate book request composable
  const bookRequest = useBookRequest()

  const fetchAllBooks = async (): Promise<void> => {
    ;(loading.value = true), (error.value = null)
    try {
      const resource = createResource<LibraryBook[]>({
        url: 'vidyaan.library.api.get_catalog',
      })
      const res = await resource.fetch()
      console.log(res)

      allBooks.value = res ?? []
    } catch (err) {
      console.error('Failed to load books:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  const fetchData = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<BookIssueRecord[]>({
        url: 'vidyaan.library.api.get_my_issues',
      })
      const res = await resource.fetch()
      console.log(res)

      data.value = res ?? []
    } catch (err) {
      console.error('Failed to load books:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  const fetchRequestedBook = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<BookRequestRecord[]>({
        url: 'vidyaan.library.api.get_my_requests',
      })
      const res = await resource.fetch()
      console.log(res)

      requestedBook.value = res ?? []
    } catch (err) {
      console.error('Failed to load books:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  const fetchRecommendations = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<RecommendationsResponse>({
        url: 'vidyaan.library.api.get_book_recommendations',
      })
      const res = await resource.fetch()
      console.log('Recommendations:', res)

      recommendations.value = res?.sections || []
    } catch (err) {
      console.error('Failed to load recommendations:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    fetchData,
    requestedBook,
    fetchRequestedBook,
    allBooks,
    fetchAllBooks,
    recommendations,
    fetchRecommendations,
    // Book request composable functions
    bookRequest,
    isBookRequested: bookRequest.isBookRequested,
    getButtonText: bookRequest.getButtonText,
    toggleBookRequest: bookRequest.toggleBookRequest,
    requestBook: bookRequest.requestBook,
    cancelRequest: bookRequest.cancelRequest,
  }
}
