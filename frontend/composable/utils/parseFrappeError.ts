import type { FrappeFetchError } from '../types/api'

/**
 * Parses a Frappe API error into a human-readable message.
 *
 * Frappe wraps server-side exception messages in `data._server_messages`,
 * which is a JSON string containing an array of JSON strings (each one
 * carrying a `{ message: string }` payload). This helper unwraps that
 * envelope and falls back through `data.message`, `data.exc_type`, and
 * the raw `Error.message` before returning the supplied fallback.
 */
export function parseFrappeError(err: unknown, fallback: string): string {
  const fetchErr = err as FrappeFetchError
  const serverMsgs = fetchErr?.data?._server_messages
  if (serverMsgs) {
    try {
      const parsed = JSON.parse(serverMsgs) as string[]
      const first = JSON.parse(parsed[0]) as { message?: string }
      if (first?.message) return first.message
    } catch {
      /* ignore parse failures, fall through */
    }
  }
  return (
    fetchErr?.data?.message ||
    fetchErr?.data?.exc_type ||
    fetchErr?.message ||
    fallback
  )
}
