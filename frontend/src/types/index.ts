/**
 * Type definitions for API responses
 */

export interface User {
    id: string
    username: string
    email?: string
    bio: string
    avatar: string
    phone_number?: string
    preferences?: Record<string, unknown>
    followers_count: number
    following_count: number
    posts_count: number
    created_at: string
}

export interface Post {
    id: string
    user: User
    content: string
    likes_count: number
    comments_count: number
    is_liked: boolean
    metadata?: {
        hashtags?: string[]
        edited?: boolean
    }
    created_at: string
    updated_at?: string
}

export interface Comment {
    id: string
    user: User
    content: string
    created_at: string
}

export interface PaginatedResponse<T> {
    count: number
    next: string | null
    previous: string | null
    results: T[]
}

export interface AuthTokens {
    access: string
    refresh: string
}

export interface LoginCredentials {
    username: string
    password: string
}

export interface RegisterData {
    username: string
    email: string
    password: string
    password_confirm: string
    phone_number?: string
}

export interface CreatePostData {
    content: string
    hashtags?: string[]
}

export interface CreateCommentData {
    content: string
}

export interface UpdateProfileData {
    bio?: string
    avatar?: string
    phone_number?: string
    preferences?: Record<string, unknown>
}
