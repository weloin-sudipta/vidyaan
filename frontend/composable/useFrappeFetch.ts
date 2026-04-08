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

export async function call<T>(method: string, params?: FrappeParams): Promise<T> {
  const result = await $fetch<FrappeMethodEnvelope<T>>(`/api/method/${method}`, {
    method: 'POST',
    body: params,
    credentials: 'include',
  })
  return result.message
}

export async function callMultipart<T>(
  method: string,
  formData: FormData
): Promise<T> {
  const result = await $fetch<FrappeMethodEnvelope<T>>(`/api/method/${method}`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  })
  return result.message
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
