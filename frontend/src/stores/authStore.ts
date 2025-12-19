/**
 * Zustand store for authentication state
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '../types'
import api, { setTokens, clearTokens } from '../lib/api'

interface AuthState {
    user: User | null
    isAuthenticated: boolean
    isLoading: boolean

    // Actions
    login: (username: string, password: string) => Promise<void>
    register: (data: RegisterData) => Promise<void>
    logout: () => void
    fetchCurrentUser: () => Promise<void>
    updateProfile: (data: Partial<User>) => Promise<void>
}

interface RegisterData {
    username: string
    email: string
    password: string
    password_confirm: string
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            isAuthenticated: false,
            isLoading: false,

            login: async (username: string, password: string) => {
                set({ isLoading: true })
                try {
                    const response = await api.post('/auth/token/', { username, password })
                    const { access, refresh } = response.data
                    setTokens(access, refresh)

                    // Fetch user data
                    const userResponse = await api.get('/users/me/')
                    set({
                        user: userResponse.data,
                        isAuthenticated: true,
                        isLoading: false
                    })
                } catch (error) {
                    set({ isLoading: false })
                    throw error
                }
            },

            register: async (data: RegisterData) => {
                set({ isLoading: true })
                try {
                    await api.post('/auth/register/', data)
                    set({ isLoading: false })
                } catch (error) {
                    set({ isLoading: false })
                    throw error
                }
            },

            logout: () => {
                clearTokens()
                set({ user: null, isAuthenticated: false })
            },

            fetchCurrentUser: async () => {
                set({ isLoading: true })
                try {
                    const response = await api.get('/users/me/')
                    set({
                        user: response.data,
                        isAuthenticated: true,
                        isLoading: false
                    })
                } catch {
                    clearTokens()
                    set({ user: null, isAuthenticated: false, isLoading: false })
                }
            },

            updateProfile: async (data: Partial<User>) => {
                const response = await api.patch('/users/me/', data)
                set({ user: response.data })
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                user: state.user,
                isAuthenticated: state.isAuthenticated
            }),
        }
    )
)
