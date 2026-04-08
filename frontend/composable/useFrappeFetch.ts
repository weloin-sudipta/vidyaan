import { ref, type Ref } from 'vue'
import type {
  FrappeFetchError,
  FrappeMethodEnvelope,
  FrappeResourceEnvelope,
  LoggedUser,
  LoginResponse,
  LogoutResponse,
} from './types/api'

// ─────────────────────────────────────────────────────────────────────────────
// Local types
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Free-form param bag passed to Frappe endpoints.  Frappe accepts strings,
 * numbers, booleans, JSON-serialised arrays/objects, and `null`.
 */
export type FrappeParams = Record<string, unknown>

export interface ResourceOptions<T> {
  url: string
  params?: FrappeParams
  auto?: boolean
  onSuccess?: (data: T) => void
  onError?: (error: FrappeFetchError) => void
}

export interface Resource<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<FrappeFetchError | null>
  params: FrappeParams
  fetch: (params?: FrappeParams) => Promise<T | undefined>
  submit: (params?: FrappeParams) => Promise<T | undefined>
  reload: () => Promise<T | undefined>
  reset: () => void
}

export interface ListResourceOptions<T> {
  doctype: string
  fields?: string[]
  filters?: Record<string, unknown>
  orderBy?: string
  limit?: number
  auto?: boolean
  onSuccess?: (data: T[]) => void
  onError?: (error: FrappeFetchError) => void
}

export interface ListResource<T> {
  data: Ref<T[]>
  loading: Ref<boolean>
  error: Ref<FrappeFetchError | null>
  fetch: () => Promise<T[] | undefined>
  reload: () => Promise<T[] | undefined>
}

export interface DocumentResourceOptions<T> {
  doctype: string
  name: string
  fields?: string[]
  auto?: boolean
  onSuccess?: (data: T) => void
  onError?: (error: FrappeFetchError) => void
}

export interface DocumentResource<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<FrappeFetchError | null>
  fetch: () => Promise<T | undefined>
  reload: () => Promise<T | undefined>
}

// ─────────────────────────────────────────────────────────────────────────────
// createResource
// ─────────────────────────────────────────────────────────────────────────────

export function createResource<T>(options: ResourceOptions<T>): Resource<T> {
  const data: Ref<T | null> = ref(null) as Ref<T | null>
  const loading = ref(false)
  const error: Ref<FrappeFetchError | null> = ref(null)
  let currentParams: FrappeParams = { ...(options.params || {}) }

  const execute = async (params?: FrappeParams): Promise<T | undefined> => {
    if (params) {
      currentParams = { ...currentParams, ...params }
    }

    loading.value = true
    error.value = null

    try {
      await new Promise(resolve => setTimeout(resolve, 800)); // Smooth skeleton visibility delay
      const result = await $fetch<FrappeMethodEnvelope<T>>(`/api/method/${options.url}`, {
        method: 'POST',
        body: currentParams,
        credentials: 'include',
      })

      data.value = result.message
      options.onSuccess?.(result.message)
      return result.message
    } catch (err) {
      const fetchErr = err as FrappeFetchError
      error.value = fetchErr
      options.onError?.(fetchErr)
    } finally {
      loading.value = false
    }
  }

  if (options.auto) {
    execute()
  }

  return {
    data,
    loading,
    error,
    params: currentParams,
    fetch: execute,
    submit: execute,
    reload: () => execute(),
    reset: () => {
      data.value = null
      error.value = null
      loading.value = false
    },
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// createListResource
// ─────────────────────────────────────────────────────────────────────────────

export function createListResource<T>(options: ListResourceOptions<T>): ListResource<T> {
  const data: Ref<T[]> = ref([]) as Ref<T[]>
  const loading = ref(false)
  const error: Ref<FrappeFetchError | null> = ref(null)

  const execute = async (): Promise<T[] | undefined> => {
    loading.value = true
    error.value = null

    try {
      await new Promise(resolve => setTimeout(resolve, 800)); // Smooth skeleton visibility delay
      const params: Record<string, string | number> = {}
      if (options.fields) params.fields = JSON.stringify(options.fields)
      if (options.filters) params.filters = JSON.stringify(options.filters)
      if (options.orderBy) params.order_by = options.orderBy
      if (options.limit) params.limit_page_length = options.limit

      const result = await $fetch<FrappeResourceEnvelope<T[]>>(
        `/api/resource/${options.doctype}`,
        { credentials: 'include', params }
      )

      data.value = result.data
      options.onSuccess?.(result.data)
      return result.data
    } catch (err) {
      const fetchErr = err as FrappeFetchError
      error.value = fetchErr
      options.onError?.(fetchErr)
    } finally {
      loading.value = false
    }
  }

  if (options.auto) {
    execute()
  }

  return {
    data,
    loading,
    error,
    fetch: execute,
    reload: execute,
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// createDocumentResource
// ─────────────────────────────────────────────────────────────────────────────

export function createDocumentResource<T>(options: DocumentResourceOptions<T>): DocumentResource<T> {
  const data: Ref<T | null> = ref(null) as Ref<T | null>
  const loading = ref(false)
  const error: Ref<FrappeFetchError | null> = ref(null)

  const execute = async (): Promise<T | undefined> => {
    loading.value = true
    error.value = null

    try {
      await new Promise(resolve => setTimeout(resolve, 800)); // Smooth skeleton visibility delay
      const params: Record<string, string> = {}
      if (options.fields) params.fields = JSON.stringify(options.fields)

      const result = await $fetch<FrappeResourceEnvelope<T>>(
        `/api/resource/${options.doctype}/${options.name}`,
        { credentials: 'include', params }
      )

      data.value = result.data
      options.onSuccess?.(result.data)
      return result.data
    } catch (err) {
      const fetchErr = err as FrappeFetchError
      error.value = fetchErr
      options.onError?.(fetchErr)
    } finally {
      loading.value = false
    }
  }

  if (options.auto) {
    execute()
  }

  return {
    data,
    loading,
    error,
    fetch: execute,
    reload: execute,
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// One-shot RPC call
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Extract a human-readable message from a Frappe error response.
 *
 * Frappe returns thrown errors (frappe.throw / ValidationError) as non-2xx
 * responses with the real message hidden in either:
 *   - `_server_messages` (JSON-encoded array of {message, indicator, ...})
 *   - `exception` (e.g. "frappe.exceptions.ValidationError: <msg>")
 *   - `message` (plain text)
 * The default `$fetch` error only carries "417 Expectation Failed" in
 * `.message`, which is useless to the user. This helper digs out the real
 * message so callers can surface it directly.
 */
function extractFrappeError(err: unknown): string {
  // ofetch FetchError attaches the parsed response body on `.data`
  const fetchErr = err as { data?: Record<string, unknown>; message?: string }
  const data = fetchErr?.data
  if (data) {
    // 1. _server_messages: JSON string of an array of {message, ...}
    const sm = data._server_messages
    if (typeof sm === 'string' && sm.length) {
      try {
        const parsed = JSON.parse(sm) as unknown[]
        const messages: string[] = []
        for (const raw of parsed) {
          if (typeof raw === 'string') {
            try {
              const inner = JSON.parse(raw) as { message?: string }
              if (inner?.message) {
                messages.push(stripHtml(inner.message))
                continue
              }
            } catch {
              /* not JSON, fall through */
            }
            messages.push(stripHtml(raw))
          }
        }
        if (messages.length) return messages.join('\n')
      } catch {
        /* fall through */
      }
    }
    // 2. exception: "frappe.exceptions.ValidationError: <msg>"
    if (typeof data.exception === 'string' && data.exception) {
      const colonIdx = data.exception.indexOf(':')
      const tail = colonIdx >= 0 ? data.exception.slice(colonIdx + 1).trim() : data.exception
      if (tail) return tail
    }
    // 3. plain message
    if (typeof data.message === 'string' && data.message) {
      return stripHtml(data.message)
    }
  }
  return fetchErr?.message || 'Request failed'
}

function stripHtml(s: string): string {
  return s.replace(/<[^>]*>/g, '').trim()
}

/**
 * Wraps a $fetch error so the surfaced `.message` is the real Frappe message
 * instead of "<status> <statusText>". Preserves the original error as `.cause`.
 */
function rethrowFrappeError(err: unknown): never {
  const msg = extractFrappeError(err)
  const wrapped = new Error(msg)
  ;(wrapped as Error & { cause?: unknown }).cause = err
  throw wrapped
}

export async function call<T>(method: string, params?: FrappeParams): Promise<T> {
  try {
    const result = await $fetch<FrappeMethodEnvelope<T>>(`/api/method/${method}`, {
      method: 'POST',
      body: params,
      credentials: 'include',
    })
    return result.message
  } catch (err) {
    rethrowFrappeError(err)
  }
}

export async function callMultipart<T>(
  method: string,
  formData: FormData
): Promise<T> {
  try {
    const result = await $fetch<FrappeMethodEnvelope<T>>(`/api/method/${method}`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    })
    return result.message
  } catch (err) {
    rethrowFrappeError(err)
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Auth helpers — concrete typed responses
// ─────────────────────────────────────────────────────────────────────────────

export const auth = {
  login: (usr: string, pwd: string): Promise<LoginResponse> =>
    $fetch<LoginResponse>('/api/method/login', {
      method: 'POST',
      body: { usr, pwd },
      credentials: 'include',
    }),

  logout: (): Promise<LogoutResponse> =>
    $fetch<LogoutResponse>('/api/method/logout', {
      method: 'POST',
      credentials: 'include',
    }),

  getLoggedUser: async (): Promise<LoggedUser> => {
    const data = await $fetch<FrappeMethodEnvelope<LoggedUser>>(
      '/api/method/frappe.auth.get_logged_user',
      { credentials: 'include' }
    )
    return data.message
  },
}
