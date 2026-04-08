import { ref, type Ref } from 'vue'
import { createResource } from './useFrappeFetch'
import { useToast } from './useToast'
import { parseFrappeError } from './utils/parseFrappeError'
import type {
  BookRequestRecord,
  BookRequestStatus,
} from './types/api'

// ─── Local shapes ─────────────────────────────────────────────────────────
export interface BookRequestInput {
  name?: string
  id?: string
  title?: string
  library?: string
  requestId?: string | null
  [key: string]: unknown
}

export interface BookRequestSubmitResponse {
  request_id?: string
  name?: string
  [key: string]: unknown
}

export interface UseBookRequestReturn {
  requestedBooks: Ref<Set<string>>
  bookRequestMap: Ref<Record<string, string>>
  /** NOTE: typo preserved from original .js file. */
  requeststatus: Ref<Record<string, BookRequestStatus | string>>
  loading: Ref<boolean>
  error: Ref<string | null>
  successMessage: Ref<string | null>
  requestBook: (bookData: BookRequestInput) => Promise<BookRequestSubmitResponse | undefined>
  cancelRequest: (
    bookId: string,
    explicitRequestName?: string | null
  ) => Promise<unknown | undefined>
  isBookRequested: (bookId: string) => boolean
  getButtonText: (bookId: string) => string
  getButtonStatus: (bookId: string) => string
  toggleBookRequest: (bookData: BookRequestInput) => Promise<void>
  loadUserRequests: () => Promise<BookRequestRecord[] | undefined>
  init: () => Promise<void>
}

export const useBookRequest = (): UseBookRequestReturn => {
  const { addToast } = useToast()
  const requestedBooks: Ref<Set<string>> = ref(new Set<string>()) // Only books with PENDING requests
  const bookRequestMap: Ref<Record<string, string>> = ref({}) // book ID → request doc name
  const requeststatus: Ref<Record<string, BookRequestStatus | string>> = ref({}) // book ID → real request status locally tracked for UI
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const successMessage: Ref<string | null> = ref(null)

  // ─── Request a book ────────────────────────────────────────────────────────
  const requestBook = async (
    bookData: BookRequestInput
  ): Promise<BookRequestSubmitResponse | undefined> => {
    loading.value = true
    error.value = null
    successMessage.value = null

    try {
      const resource = createResource<BookRequestSubmitResponse>({
        url: 'vidyaan.library.api.request_book',
      })

      const res = await resource.submit({
        book: bookData.name || bookData.id,
        library: bookData.library,
      })

      if (resource.error.value) {
        throw resource.error.value
      }

      const bookId = (bookData.name || bookData.id) as string

      // Mark as pending locally so the button flips immediately
      requestedBooks.value.add(bookId)
      if (res && (res.request_id || res.name)) {
        bookRequestMap.value[bookId] = (res.request_id || res.name) as string
      }
      requeststatus.value[bookId] = 'Pending'

      successMessage.value = `Book "${bookData.title}" requested successfully!`
      addToast(`Book "${bookData.title}" requested successfully!`, 'success')
      console.log('Book request created:', res)

      return res
    } catch (err) {
      console.error('Failed to request book:', err)

      const errMsg = parseFrappeError(err, 'Failed to request book.')
      error.value = errMsg
      addToast(errMsg, 'error')
    } finally {
      loading.value = false
    }
  }

  // ─── Cancel a book request ─────────────────────────────────────────────────
  const cancelRequest = async (
    bookId: string,
    explicitRequestName: string | null = null
  ): Promise<unknown | undefined> => {
    loading.value = true
    error.value = null
    successMessage.value = null

    try {
      const request_name = explicitRequestName || bookRequestMap.value[bookId]
      if (!request_name) {
        throw new Error('Could not find the original request ID to cancel.')
      }

      const resource = createResource<unknown>({
        url: 'vidyaan.library.api.cancel_request',
      })

      const res = await resource.submit({
        request_name: request_name,
      })

      if (resource.error.value) {
        throw resource.error.value
      }

      // Remove from pending set immediately so button flips back
      requestedBooks.value.delete(bookId)
      delete bookRequestMap.value[bookId]
      delete requeststatus.value[bookId]

      successMessage.value = 'Book request cancelled successfully!'
      addToast('Book request cancelled successfully!', 'success')
      console.log('Book request cancelled:', res)

      return res
    } catch (err) {
      console.error('Failed to cancel request:', err)

      const errMsg = parseFrappeError(err, 'Failed to cancel request.')
      error.value = errMsg
      addToast(errMsg, 'error')
    } finally {
      loading.value = false
    }
  }

  // ─── Core check: only returns true for PENDING requests ───────────────────
  // `requestedBooks` is populated exclusively from get_all_pending_requests,
  // so this naturally returns false for Approved / Issued / Cancelled books.
  const isBookRequested = (bookId: string): boolean => {
    return requestedBooks.value.has(bookId)
  }

  const getButtonText = (bookId: string): string =>
    isBookRequested(bookId) ? 'Cancel Request' : 'Request Book'
  const getButtonStatus = (bookId: string): string =>
    isBookRequested(bookId) ? 'cancel' : 'request'

  const toggleBookRequest = async (bookData: BookRequestInput): Promise<void> => {
    const bookId = (bookData.name || bookData.id) as string
    if (isBookRequested(bookId)) {
      await cancelRequest(bookId, bookData.requestId ?? null)
    } else {
      await requestBook(bookData)
    }
  }

  // ─── Load PENDING requests from the dedicated API ─────────────────────────
  // Uses get_all_pending_requests which already filters status == "Pending",
  // so requestedBooks will never contain Approved/Issued/Cancelled entries.
  const loadUserRequests = async (): Promise<BookRequestRecord[] | undefined> => {
    loading.value = true
    error.value = null

    try {
      const resource = createResource<BookRequestRecord[]>({
        url: 'vidyaan.library.api.get_my_requests',
      })

      const res = await resource.fetch()

      if (res && Array.isArray(res)) {
        // Deduplicate to only keep the latest request per book ID
        const latestRequests: BookRequestRecord[] = []
        const seenBooks = new Set<string>()
        res.forEach(req => {
          if (!seenBooks.has(req.book)) {
            seenBooks.add(req.book)
            latestRequests.push(req)
          }
        })

        // Keep track of pending requests for responsive UI buttons
        const pendingRequests = latestRequests.filter(
          r => r.status === 'Pending' || r.status === 'Approved'
        )
        requestedBooks.value = new Set(pendingRequests.map(r => r.book))

        bookRequestMap.value = {}
        requeststatus.value = {}
        latestRequests.forEach(req => {
          bookRequestMap.value[req.book] = req.name
          requeststatus.value[req.book] = req.status
        })
      }

      console.log('Pending requests loaded:', [...requestedBooks.value])
      return res
    } catch (err) {
      console.error('Failed to load pending requests:', err)
      console.warn('Could not load existing requests - continuing anyway')
    } finally {
      loading.value = false
    }
  }

  const init = async (): Promise<void> => {
    await loadUserRequests()
  }

  return {
    requestedBooks,
    bookRequestMap,
    requeststatus,
    loading,
    error,
    successMessage,
    requestBook,
    cancelRequest,
    isBookRequested,
    getButtonText,
    getButtonStatus,
    toggleBookRequest,
    loadUserRequests,
    init,
  }
}

// ─── Standalone helper (used outside the composable if needed) ─────────────────
export const getPendingRequest = async (): Promise<BookRequestRecord[] | undefined> => {
  const requestResource = createResource<BookRequestRecord[]>({
    url: 'vidyaan.library.api.get_my_requests',
  })
  const request = await requestResource.fetch() // fetch, not submit — no body needed
  return request
}
