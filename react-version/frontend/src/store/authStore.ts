import { create } from 'zustand'

interface User {
    email: string
    name: string
    picture?: string
    subscription: 'active' | 'inactive'
}

interface AuthState {
    user: User | null
    token: string | null
    setAuth: (user: User, token: string) => void
    logout: () => void
}

const getInitialUser = () => {
    try {
        const user = localStorage.getItem('user')
        return user ? JSON.parse(user) : null
    } catch (e) {
        console.error('Error parsing user from localStorage', e)
        return null
    }
}

export const useAuthStore = create<AuthState>((set) => {
    const initialUser = getInitialUser();
    const initialToken = localStorage.getItem('token');
    console.log('AuthStore Initial State:', { user: !!initialUser, token: !!initialToken });
    return {
        user: initialUser,
        token: initialToken,
        setAuth: (user, token) => {
        console.log('Setting auth state:', { user, token })
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))
        set({ user, token })
    },
    logout: () => {
        console.log('Logging out...')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        set({ user: null, token: null })
    },
    };
})
