/**
 * Shared API type definitions for Vidyaan frontend composables.
 *
 * Only shapes used by 2+ composables live here. Single-use shapes
 * stay inline in their composable file.
 *
 * No `any` allowed. Prefer named interfaces, generics, and
 * discriminated unions over loose object types.
 */

// ─────────────────────────────────────────────────────────────────────────────
// Frappe primitives
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Standard Frappe REST/RPC envelope.  Most `/api/method/...` endpoints
 * return JSON in the form `{ message: T }`.
 */
export interface FrappeMethodEnvelope<T> {
  message: T
}

/**
 * Standard Frappe `/api/resource/...` envelope: `{ data: T }`.
 */
export interface FrappeResourceEnvelope<T> {
  data: T
}

/**
 * Frappe error shape as it surfaces through `$fetch` rejections.
 *
 * `_server_messages` is a JSON-encoded string containing an array of
 * JSON-encoded message objects.  Helpers in composables decode it lazily.
 *
 * Used by: useBookRequest, useLibraryAdmin, usePdf.
 */
export interface FrappeErrorData {
  _server_messages?: string
  exc_type?: string
  message?: string
}

export interface FrappeFetchError extends Error {
  data?: FrappeErrorData
  statusCode?: number
}

// ─────────────────────────────────────────────────────────────────────────────
// Generic API envelopes
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Discriminated union for endpoints that explicitly return
 * `{ success: true | false, ... }`.  Used by event/notice/study-material
 * endpoints.
 */
export type ApiResult<T> =
  | ({ success: true } & T)
  | { success: false; message?: string; error?: string }

/**
 * Lightweight ack used by mutation endpoints (study materials,
 * grading row save, etc).
 */
export interface MutationAck {
  success: boolean
  message?: string
  error?: string
}

// ─────────────────────────────────────────────────────────────────────────────
// Auth (used by useFrappeFetch + useAuth + useUserProfile)
// ─────────────────────────────────────────────────────────────────────────────

export interface LoginResponse {
  message?: string
  home_page?: string
  full_name?: string
}

export interface LogoutResponse {
  message?: string
}

/**
 * `frappe.auth.get_logged_user` returns `{ message: "<email>" }`.
 * The composable unwraps and returns the email string itself.
 */
export type LoggedUser = string

// ─────────────────────────────────────────────────────────────────────────────
// User profile (useUserProfile + useProfile)
// ─────────────────────────────────────────────────────────────────────────────

export interface UserInfo {
  email: string
  first_name?: string
  last_name?: string
  full_name?: string
  user_image?: string
  role?: string
}

// ─────────────────────────────────────────────────────────────────────────────
// PDF service (usePdf + useTimetable)
// ─────────────────────────────────────────────────────────────────────────────

export interface PdfGenerationResult {
  file_url: string
  student_name?: string
  exam_type?: string
  filename?: string
}

// ─────────────────────────────────────────────────────────────────────────────
// Library — book request flow (useBookRequest + useLibraryBooks + useLibraryAdmin)
// ─────────────────────────────────────────────────────────────────────────────

export type BookRequestStatus = 'Pending' | 'Approved' | 'Rejected' | 'Cancelled' | 'Issued'

export interface BookRequestRecord {
  name: string
  book: string
  library?: string
  status: BookRequestStatus
  request_id?: string
}

export interface BookIssueRecord {
  name: string
  book: string
  status?: string
  due_date?: string
}
