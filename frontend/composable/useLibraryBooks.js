import { ref, onMounted } from "vue"
import { createResource } from "./useFrappeFetch"
import { useBookRequest } from "./useBookRequest"

export const useBooks = () => {
    const data = ref([])
    const requestedBook = ref([])
    const allBooks = ref([])
    const recommendations = ref([])
    const loading = ref(false)
    const error = ref(null)
    
    // Integrate book request composable
    const bookRequest = useBookRequest()

    const fetchAllBooks = async()=>{
        loading.value = true,
        error.value = null
        try {
            const resource = createResource({
                url: 'vidyaan.library.api.get_catalog',
            })
            const res = await resource.fetch()
            console.log(res);

            allBooks.value = res
        } catch (err) {
            console.error("Failed to load books:", err)
            error.value = err.message || "Unknown error"
        } finally {
            loading.value = false
        }
    }

    const fetchData = async () => {
        loading.value = true
        error.value = null
        try {
            const resource = createResource({
                url: 'vidyaan.library.api.get_my_issues',
            })
            const res = await resource.fetch()
            console.log(res);
            
            data.value = res
        } catch (err) {
            console.error("Failed to load books:", err)
            error.value = err.message || "Unknown error"
        } finally {
            loading.value = false
        }
    }

    const fetchRequestedBook= async()=>{
        loading.value = true
        error.value= null
        try {
            const resource = createResource({
                url: 'vidyaan.library.api.get_my_requests',
            })
            const res = await resource.fetch()
            console.log(res);

            requestedBook.value = res
        } catch (err) {
            console.error("Failed to load books:", err)
            error.value = err.message || "Unknown error"
        } finally {
            loading.value = false
        }
    }

    const fetchRecommendations = async () => {
        loading.value = true
        error.value = null
        try {
            const resource = createResource({
                url: 'vidyaan.library.api.get_book_recommendations',
            })
            const res = await resource.fetch()
            console.log("Recommendations:", res);
            
            recommendations.value = res.sections || []
        } catch (err) {
            console.error("Failed to load recommendations:", err)
            error.value = err.message || "Unknown error"
        } finally {
            loading.value = false
        }
    }

    return { 
        data, 
        loading, 
        error, 
        fetchData, 
        requestedBook, 
        fetchRequestedBook, 
        allBooks, 
        fetchAllBooks, 
        recommendations, 
        fetchRecommendations,
        // Book request composable functions
        bookRequest,
        isBookRequested: bookRequest.isBookRequested,
        getButtonText: bookRequest.getButtonText,
        toggleBookRequest: bookRequest.toggleBookRequest,
        requestBook: bookRequest.requestBook,
        cancelRequest: bookRequest.cancelRequest,
    }
}