import { ref } from "vue"
import { createResource, call } from "./useFrappeFetch"
import { useToast } from "./useToast"

export const useBookRequest = () => {
    const { addToast } = useToast();
    const requestedBooks = ref(new Set())   // Only books with PENDING requests
    const bookRequestMap = ref({})          // book ID → request doc name
    const requeststatus = ref({})           // book ID → real request status locally tracked for UI
    const loading = ref(false)
    const error = ref(null)
    const successMessage = ref(null)

    // ─── Request a book ────────────────────────────────────────────────────────
    const requestBook = async (bookData) => {
        loading.value = true
        error.value = null
        successMessage.value = null

        try {
            const resource = createResource({
                url: 'vidyaan.library.api.request_book',
            })

            const res = await resource.submit({
                book: bookData.name || bookData.id,
                library: bookData.library
            })

            if (resource.error.value) {
                throw resource.error.value;
            }

            const bookId = bookData.name || bookData.id

            // Mark as pending locally so the button flips immediately
            requestedBooks.value.add(bookId)
            if (res && (res.request_id || res.name)) {
                bookRequestMap.value[bookId] = res.request_id || res.name
            }
            requeststatus.value[bookId] = "Pending"

            successMessage.value = `Book "${bookData.title}" requested successfully!`
            addToast(`Book "${bookData.title}" requested successfully!`, "success");
            console.log("Book request created:", res)

            return res
        } catch (err) {
            console.error("Failed to request book:", err)

            let errMsg = "Failed to request book.";
            if (err.data && err.data._server_messages) {
                try {
                    const messages = JSON.parse(err.data._server_messages);
                    errMsg = JSON.parse(messages[0]).message;
                } catch (e) { }
            } else if (err.data && err.data.exc_type) {
                errMsg = err.data.exc_type;
            } else if (err.message) {
                errMsg = err.message;
            }

            error.value = errMsg;
            addToast(errMsg, "error");
        } finally {
            loading.value = false
        }
    }

    // ─── Cancel a book request ─────────────────────────────────────────────────
    const cancelRequest = async (bookId, explicitRequestName = null) => {
        loading.value = true
        error.value = null
        successMessage.value = null

        try {
            const request_name = explicitRequestName || bookRequestMap.value[bookId];
            if (!request_name) {
                throw new Error("Could not find the original request ID to cancel.");
            }

            const resource = createResource({
                url: 'vidyaan.library.api.cancel_request',
            })

            const res = await resource.submit({
                request_name: request_name
            })

            if (resource.error.value) {
                throw resource.error.value;
            }

            // Remove from pending set immediately so button flips back
            requestedBooks.value.delete(bookId)
            delete bookRequestMap.value[bookId]
            delete requeststatus.value[bookId]

            successMessage.value = "Book request cancelled successfully!"
            addToast("Book request cancelled successfully!", "success");
            console.log("Book request cancelled:", res)

            return res
        } catch (err) {
            console.error("Failed to cancel request:", err)

            let errMsg = "Failed to cancel request.";
            if (err.data && err.data._server_messages) {
                try {
                    const messages = JSON.parse(err.data._server_messages);
                    errMsg = JSON.parse(messages[0]).message;
                } catch (e) { }
            } else if (err.message) {
                errMsg = err.message;
            }

            error.value = errMsg;
            addToast(errMsg, "error");
        } finally {
            loading.value = false
        }
    }

    // ─── Core check: only returns true for PENDING requests ───────────────────
    // `requestedBooks` is populated exclusively from get_all_pending_requests,
    // so this naturally returns false for Approved / Issued / Cancelled books.
    const isBookRequested = (bookId) => {
        return requestedBooks.value.has(bookId)
    }

    const getButtonText = (bookId) => isBookRequested(bookId) ? "Cancel Request" : "Request Book"
    const getButtonStatus = (bookId) => isBookRequested(bookId) ? 'cancel' : 'request'

    const toggleBookRequest = async (bookData) => {
        const bookId = bookData.name || bookData.id
        if (isBookRequested(bookId)) {
            await cancelRequest(bookId, bookData.requestId)
        } else {
            await requestBook(bookData)
        }
    }

    // ─── Load PENDING requests from the dedicated API ─────────────────────────
    // Uses get_all_pending_requests which already filters status == "Pending",
    // so requestedBooks will never contain Approved/Issued/Cancelled entries.
    const loadUserRequests = async () => {
        loading.value = true
        error.value = null

        try {
            const resource = createResource({
                url: 'vidyaan.library.api.get_my_requests',
            })

            const res = await resource.fetch()

            if (res && Array.isArray(res)) {
                // Deduplicate to only keep the latest request per book ID
                const latestRequests = [];
                const seenBooks = new Set();
                res.forEach(req => {
                    if (!seenBooks.has(req.book)) {
                        seenBooks.add(req.book);
                        latestRequests.push(req);
                    }
                });

                // Keep track of pending requests for responsive UI buttons
                const pendingRequests = latestRequests.filter(r => r.status === "Pending" || r.status === "Approved");
                requestedBooks.value = new Set(pendingRequests.map(r => r.book))

                bookRequestMap.value = {}
                requeststatus.value = {}
                latestRequests.forEach(req => {
                    bookRequestMap.value[req.book] = req.name
                    requeststatus.value[req.book] = req.status
                })
            }

            console.log("Pending requests loaded:", [...requestedBooks.value])
            return res
        } catch (err) {
            console.error("Failed to load pending requests:", err)
            console.warn("Could not load existing requests - continuing anyway")
        } finally {
            loading.value = false
        }
    }

    const init = async () => {
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
export const getPendingRequest = async () => {
    const requestResource = createResource({
        url: 'vidyaan.library.api.get_my_requests',
    })
    const request = await requestResource.fetch()   // fetch, not submit — no body needed
    return request
}