import { ref, type Ref } from 'vue'
import { createResource } from './useFrappeFetch'

// ─── Book Issue row from `vidyaan.library.api.get_my_issues` ──────────────
export interface BookIssueRow {
  name?: string
  book?: string
  status?: string
  due_date?: string
  [key: string]: unknown
}

export interface UseBorrowedBooksReturn {
  borrowedBookNames: Ref<Set<string>>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchBorrowedBooks: () => Promise<BookIssueRow[] | undefined>
}

/**
 * useBorrowedBooks
 * ----------------
 * Fetches Book Issue records where status = "Issued" for the logged-in user.
 * Exposes `borrowedBookNames` — a Set of book IDs — so the catalog can
 * simply do  `borrowedBookNames.has(book.name)`  to hide already-issued books.
 */
export const useBorrowedBooks = (): UseBorrowedBooksReturn => {
  const borrowedBookNames: Ref<Set<string>> = ref(new Set<string>())
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const fetchBorrowedBooks = async (): Promise<BookIssueRow[] | undefined> => {
    loading.value = true
    error.value = null

    try {
      const resource = createResource<BookIssueRow[]>({
        url: 'vidyaan.library.api.get_my_issues',
      })

      const res = await resource.fetch()

      if (res && Array.isArray(res)) {
        // `all_borrowed_books` returns Book Issue rows (Book.star selected).
        // The book identifier field is `book` on the Book Issue doctype.
        borrowedBookNames.value = new Set(
          res.map(issue => issue.book).filter((b): b is string => Boolean(b))
        )
      }

      console.log('Borrowed books loaded:', [...borrowedBookNames.value])
      return res
    } catch (err) {
      console.error('Failed to load borrowed books:', err)
      error.value = (err as Error).message || 'Failed to load borrowed books'
      // Non-critical — catalog will still render; nothing will be hidden.
    } finally {
      loading.value = false
    }
  }

  return {
    borrowedBookNames,
    loading,
    error,
    fetchBorrowedBooks,
  }
}
