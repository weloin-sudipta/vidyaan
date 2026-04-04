import { ref, type Ref } from 'vue'

interface ResourceOptions<T = any> {
  url: string
  params?: Record<string, any>
  auto?: boolean
  onSuccess?: (data: T) => void
  onError?: (error: any) => void
}

interface Resource<T = any> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<any>
  params: Record<string, any>
  fetch: (params?: Record<string, any>) => Promise<T | undefined>
  submit: (params?: Record<string, any>) => Promise<T | undefined>
  reload: () => Promise<T | undefined>
  reset: () => void
}

export function createResource<T = any>(options: ResourceOptions<T>): Resource<T> {
  const data: Ref<T | null> = ref(null)
  const loading = ref(false)
  const error: Ref<any> = ref(null)
  let currentParams = { ...(options.params || {}) }

  const execute = async (params?: Record<string, any>): Promise<T | undefined> => {
    if (params) {
      currentParams = { ...currentParams, ...params }
    }

    loading.value = true
    error.value = null

    try {
      await new Promise(resolve => setTimeout(resolve, 800)); // Smooth skeleton visibility delay
      const result = await $fetch<{ message: T }>(`/api/method/${options.url}`, {
        method: 'POST',
        body: currentParams,
        credentials: 'include',
      })

      data.value = result.message
      options.onSuccess?.(result.message)
      return result.message
    } catch (err) {
      error.value = err
      options.onError?.(err)
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

export function createListResource<T = any>(options: {
  doctype: string
  fields?: string[]
  filters?: Record<string, any>
  orderBy?: string
  limit?: number
  auto?: boolean
  onSuccess?: (data: T[]) => void
  onError?: (error: any) => void
}) {
  const data: Ref<T[]> = ref([])
  const loading = ref(false)
  const error: Ref<any> = ref(null)

  const execute = async (): Promise<T[] | undefined> => {
    loading.value = true
    error.value = null

    try {
      await new Promise(resolve => setTimeout(resolve, 800)); // Smooth skeleton visibility delay
      const params: Record<string, any> = {}
      if (options.fields) params.fields = JSON.stringify(options.fields)
      if (options.filters) params.filters = JSON.stringify(options.filters)
      if (options.orderBy) params.order_by = options.orderBy
      if (options.limit) params.limit_page_length = options.limit

      const result = await $fetch<{ data: T[] }>(
        `/api/resource/${options.doctype}`,
        { credentials: 'include', params }
      )

      data.value = result.data
      options.onSuccess?.(result.data)
      return result.data
    } catch (err) {
      error.value = err
      options.onError?.(err)
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

export function createDocumentResource<T = any>(options: {
  doctype: string
  name: string
  fields?: string[]
  auto?: boolean
  onSuccess?: (data: T) => void
  onError?: (error: any) => void
}) {
  const data: Ref<T | null> = ref(null)
  const loading = ref(false)
  const error: Ref<any> = ref(null)

  const execute = async (): Promise<T | undefined> => {
    loading.value = true
    error.value = null

    try {
      await new Promise(resolve => setTimeout(resolve, 800)); // Smooth skeleton visibility delay
      const params: Record<string, any> = {}
      if (options.fields) params.fields = JSON.stringify(options.fields)

      const result = await $fetch<{ data: T }>(
        `/api/resource/${options.doctype}/${options.name}`,
        { credentials: 'include', params }
      )

      data.value = result.data
      options.onSuccess?.(result.data)
      return result.data
    } catch (err) {
      error.value = err
      options.onError?.(err)
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

export async function call<T = any>(method: string, params?: Record<string, any>): Promise<T> {
  const result = await $fetch<{ message: T }>(`/api/method/${method}`, {
    method: 'POST',
    body: params,
    credentials: 'include',
  })
  return result.message
}

export const auth = {
  login: (usr: string, pwd: string) =>
    $fetch('/api/method/login', {
      method: 'POST',
      body: { usr, pwd },
      credentials: 'include',
    }),

  logout: () =>
    $fetch('/api/method/logout', {
      method: 'POST',
      credentials: 'include',
    }),

  getLoggedUser: async () => {
    const data = await $fetch<{ message: string }>('/api/method/frappe.auth.get_logged_user', {
      credentials: 'include',
    })
    return data.message
  },
}

 