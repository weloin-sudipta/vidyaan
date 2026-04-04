import { ref } from 'vue'
import { createResource } from './useFrappeFetch'

/**
 * useBorrowedBooks
 * ----------------
 * Fetches Book Issue records where status = "Issued" for the logged-in user.
 * Exposes `borrowedBookNames` — a Set of book IDs — so the catalog can
 * simply do  `borrowedBookNames.has(book.name)`  to hide already-issued books.
 */
export const useBorrowedBooks = () => {
    const borrowedBookNames = ref(new Set())
    const loading = ref(false)
    const error = ref(null)

    const fetchBorrowedBooks = async () => {
        loading.value = true
        error.value = null

        try {
            const resource = createResource({
                url: 'vidyaan.library.api.get_my_issues',
            })

            const res = await resource.fetch()

            if (res && Array.isArray(res)) {
                // `all_borrowed_books` returns Book Issue rows (Book.star selected).
                // The book identifier field is `book` on the Book Issue doctype.
                borrowedBookNames.value = new Set(
                    res.map(issue => issue.book).filter(Boolean)
                )
            }

            console.log('Borrowed books loaded:', [...borrowedBookNames.value])
            return res
        } catch (err) {
            console.error('Failed to load borrowed books:', err)
            error.value = err.message || 'Failed to load borrowed books'
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