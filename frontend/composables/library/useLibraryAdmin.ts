import { ref, type Ref } from 'vue'
import { createResource, type FrappeParams } from '~/composables/api/useFrappeFetch'
import { useToast } from '~/composables/ui/useToast'
import { parseFrappeError } from './utils/parseFrappeError'

// ─── Local shapes ─────────────────────────────────────────────────────────
export interface LibraryStats {
  total_books?: number
  total_issues?: number
  total_requests?: number
  total_members?: number
  [key: string]: unknown
}

export interface LibraryInventoryItem {
  name?: string
  title?: string
  author?: string
  isbn?: string
  available_copies?: number
  total_copies?: number
  [key: string]: unknown
}

export interface LibraryIssueRecord {
  name: string
  book?: string
  member?: string
  status?: string
  due_date?: string
  [key: string]: unknown
}

export interface LibraryRequestRecord {
  name: string
  book?: string
  member?: string
  status?: string
  request_date?: string
  [key: string]: unknown
}

export interface LibraryMemberRecord {
  name?: string
  member_name?: string
  email?: string
  [key: string]: unknown
}

export interface ReturnBookResult {
  fine_amount?: number
  [key: string]: unknown
}

export interface RenewalResult {
  new_due_date?: string
  [key: string]: unknown
}

export interface IssueFromRequestResult {
  issue?: string
  [key: string]: unknown
}

export interface UseLibraryAdminReturn {
  loading: Ref<boolean>
  error: Ref<string | null>
  stats: Ref<LibraryStats | null>
  inventory: Ref<LibraryInventoryItem[]>
  issues: Ref<LibraryIssueRecord[]>
  requests: Ref<LibraryRequestRecord[]>
  members: Ref<LibraryMemberRecord[]>
  fetchStats: () => Promise<void>
  fetchInventory: () => Promise<void>
  fetchIssues: (status?: string | null) => Promise<void>
  fetchRequests: (status?: string | null) => Promise<void>
  fetchMembers: () => Promise<void>
  returnBook: (issueName: string) => Promise<ReturnBookResult | undefined>
  approveRequest: (requestName: string) => Promise<void>
  rejectRequest: (requestName: string, remarks?: string) => Promise<void>
  approveRenewal: (issueName: string) => Promise<RenewalResult | undefined>
  issueFromRequest: (requestName: string) => Promise<IssueFromRequestResult | undefined>
}

export const useLibraryAdmin = (): UseLibraryAdminReturn => {
  const { addToast } = useToast()
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const stats: Ref<LibraryStats | null> = ref(null)
  const inventory: Ref<LibraryInventoryItem[]> = ref([])
  const issues: Ref<LibraryIssueRecord[]> = ref([])
  const requests: Ref<LibraryRequestRecord[]> = ref([])
  const members: Ref<LibraryMemberRecord[]> = ref([])

  const _fetch = async <T>(url: string, params: FrappeParams = {}): Promise<T | undefined> => {
    const resource = createResource<T>({ url })
    return await resource.fetch(params)
  }

  const _submit = async <T>(url: string, params: FrappeParams = {}): Promise<T | undefined> => {
    const resource = createResource<T>({ url })
    return await resource.submit(params)
  }

  // ─── Data fetchers ──────────────────────────────────────────────────────────

  const fetchStats = async (): Promise<void> => {
    try {
      const res = await _fetch<LibraryStats>('vidyaan.library.api.get_library_stats')
      stats.value = res ?? null
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const fetchInventory = async (): Promise<void> => {
    loading.value = true
    try {
      const res = await _fetch<LibraryInventoryItem[]>('vidyaan.library.api.get_inventory')
      inventory.value = res ?? []
    } catch (err) {
      error.value = (err as Error).message || 'Failed to load inventory'
    } finally {
      loading.value = false
    }
  }

  const fetchIssues = async (status: string | null = null): Promise<void> => {
    loading.value = true
    try {
      const params: FrappeParams = status ? { status } : {}
      const res = await _fetch<LibraryIssueRecord[]>('vidyaan.library.api.get_all_issues', params)
      issues.value = res ?? []
    } catch (err) {
      error.value = (err as Error).message || 'Failed to load issues'
    } finally {
      loading.value = false
    }
  }

  const fetchRequests = async (status: string | null = null): Promise<void> => {
    loading.value = true
    try {
      const params: FrappeParams = status ? { status } : {}
      const res = await _fetch<LibraryRequestRecord[]>(
        'vidyaan.library.api.get_all_requests',
        params
      )
      requests.value = res ?? []
    } catch (err) {
      error.value = (err as Error).message || 'Failed to load requests'
    } finally {
      loading.value = false
    }
  }

  const fetchMembers = async (): Promise<void> => {
    loading.value = true
    try {
      const res = await _fetch<LibraryMemberRecord[]>('vidyaan.library.api.get_all_members')
      members.value = res ?? []
    } catch (err) {
      error.value = (err as Error).message || 'Failed to load members'
    } finally {
      loading.value = false
    }
  }

  // ─── Actions ────────────────────────────────────────────────────────────────

  const returnBook = async (issueName: string): Promise<ReturnBookResult | undefined> => {
    try {
      const res = await _submit<ReturnBookResult>('vidyaan.library.api.return_book', {
        issue_name: issueName,
      })
      const fine = res?.fine_amount || 0
      addToast(
        fine > 0 ? `Book returned. Fine: ₹${fine}` : 'Book returned successfully.',
        'success'
      )
      return res
    } catch (err) {
      addToast(parseFrappeError(err, 'Failed to return book'), 'error')
    }
  }

  const approveRequest = async (requestName: string): Promise<void> => {
    try {
      await _submit<unknown>('vidyaan.library.api.approve_request', { request_name: requestName })
      addToast('Request approved.', 'success')
    } catch (err) {
      addToast(parseFrappeError(err, 'Failed to approve request'), 'error')
    }
  }

  const rejectRequest = async (requestName: string, remarks: string = ''): Promise<void> => {
    try {
      await _submit<unknown>('vidyaan.library.api.reject_request', {
        request_name: requestName,
        remarks,
      })
      addToast('Request rejected.', 'success')
    } catch (err) {
      addToast(parseFrappeError(err, 'Failed to reject request'), 'error')
    }
  }

  const approveRenewal = async (issueName: string): Promise<RenewalResult | undefined> => {
    try {
      const res = await _submit<RenewalResult>('vidyaan.library.api.approve_renewal', {
        issue_name: issueName,
      })
      addToast(`Renewal approved. New due: ${res?.new_due_date || 'extended'}`, 'success')
      return res
    } catch (err) {
      addToast(parseFrappeError(err, 'Failed to approve renewal'), 'error')
    }
  }

  const issueFromRequest = async (
    requestName: string
  ): Promise<IssueFromRequestResult | undefined> => {
    try {
      const res = await _submit<IssueFromRequestResult>('vidyaan.library.api.issue_from_request', {
        request_name: requestName,
      })
      addToast('Book issued successfully.', 'success')
      return res
    } catch (err) {
      addToast(parseFrappeError(err, 'Failed to issue book'), 'error')
    }
  }

  return {
    loading,
    error,
    stats,
    inventory,
    issues,
    requests,
    members,
    fetchStats,
    fetchInventory,
    fetchIssues,
    fetchRequests,
    fetchMembers,
    returnBook,
    approveRequest,
    rejectRequest,
    approveRenewal,
    issueFromRequest,
  }
}
