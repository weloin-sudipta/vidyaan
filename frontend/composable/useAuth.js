import { useUserProfile } from './useUserProfile'

export const logout = async () => {
    const { clearProfile } = useUserProfile()
    const router = useRouter()
    
    try {
        const response = await fetch('/api/method/logout', {
            method: 'GET',
            credentials: 'same-origin',
        });

        if (response.ok) {
            clearProfile()
            // Use router for client-side navigation, fallback to window for total reset if needed
            if (process.client) {
                router.push('/auth/login')
            }
        } else {
            const data = await response.json();
            throw new Error(data.message || 'Logout failed');
        }
    } catch (error) {
        console.error('Error during logout:', error);
        // Even if API fails, we should clear local state and redirect
        clearProfile()
        if (process.client) {
            router.push('/auth/login')
        }
        throw error;
    }
};

export const login = async (usr, pwd) => {
    const { loadProfile, userRole } = useUserProfile()
    const router = useRouter()
    const route = useRoute()

    try {
        const response = await fetch('/api/method/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                usr: usr,
                pwd: pwd
            })
        });

        const data = await response.json();

        if (response.ok) {
            await loadProfile()
            
            if (process.client) {
                // Use redirect query param if present, otherwise always go to / (index.vue handles role-based dashboard)
                const redirectTo = route.query.redirect || '/'
                router.push(redirectTo)
            }
            console.log('Logged in successfully');
        } else {
            throw new Error(data.message || 'Login failed');
        }

    } catch (error) {
        console.error('Error during login:', error);
        throw error;
    }
};