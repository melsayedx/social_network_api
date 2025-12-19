/**
 * API client configuration with Axios
 * Handles authentication, error handling, and request/response interceptors
 */
import axios from 'axios'
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

// Token storage
const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY)
export const getRefreshToken = (): string | null => localStorage.getItem(REFRESH_TOKEN_KEY)
export const setTokens = (access: string, refresh: string): void => {
    localStorage.setItem(TOKEN_KEY, access)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
}
export const clearTokens = (): void => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
}

// Create API instance
const api: AxiosInstance = axios.create({
    baseURL: '/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor - add auth token
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = getToken()
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error: AxiosError) => Promise.reject(error)
)

// Response interceptor - handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

        // If 401 and not already retrying, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = getRefreshToken()
                if (refreshToken) {
                    const response = await axios.post('/api/v1/auth/token/refresh/', {
                        refresh: refreshToken,
                    })

                    const { access } = response.data
                    setTokens(access, refreshToken)

                    if (originalRequest.headers) {
                        originalRequest.headers.Authorization = `Bearer ${access}`
                    }
                    return api(originalRequest)
                }
            } catch {
                clearTokens()
                window.location.href = '/login'
            }
        }

        return Promise.reject(error)
    }
)

// Generate idempotency key for POST requests
export const generateIdempotencyKey = (): string => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// API methods with idempotency support
export const apiWithIdempotency = {
    post: <T>(url: string, data?: unknown): Promise<T> => {
        return api.post(url, data, {
            headers: {
                'X-Idempotency-Key': generateIdempotencyKey(),
            },
        }).then(res => res.data)
    },
}

export default api
