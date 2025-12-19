/**
 * React Query hooks for Users and Follows
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import type { User, PaginatedResponse } from '../types'

// Query keys
export const userKeys = {
    all: ['users'] as const,
    lists: () => [...userKeys.all, 'list'] as const,
    details: () => [...userKeys.all, 'detail'] as const,
    detail: (username: string) => [...userKeys.details(), username] as const,
    followers: (username: string) => [...userKeys.detail(username), 'followers'] as const,
    following: (username: string) => [...userKeys.detail(username), 'following'] as const,
}

// Fetch user by username
export function useUser(username: string) {
    return useQuery({
        queryKey: userKeys.detail(username),
        queryFn: async () => {
            const { data } = await api.get<User>(`/users/${username}/`)
            return data
        },
        enabled: !!username,
    })
}

// Fetch user's posts
export function useUserPosts(username: string, page = 1) {
    return useQuery({
        queryKey: [...userKeys.detail(username), 'posts', page],
        queryFn: async () => {
            const { data } = await api.get<PaginatedResponse<Post>>(`/users/${username}/posts/`, {
                params: { page },
            })
            return data
        },
        enabled: !!username,
    })
}

// Fetch followers
export function useFollowers(username: string) {
    return useQuery({
        queryKey: userKeys.followers(username),
        queryFn: async () => {
            const { data } = await api.get<PaginatedResponse<{ user: User; created_at: string }>>(
                `/users/${username}/followers/`
            )
            return data
        },
        enabled: !!username,
    })
}

// Fetch following
export function useFollowing(username: string) {
    return useQuery({
        queryKey: userKeys.following(username),
        queryFn: async () => {
            const { data } = await api.get<PaginatedResponse<{ user: User; created_at: string }>>(
                `/users/${username}/following/`
            )
            return data
        },
        enabled: !!username,
    })
}

// Follow/unfollow mutation
export function useFollowUser() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (username: string) => {
            const { data } = await api.post<{ following: boolean; followers_count: number }>(
                `/users/${username}/follow/`
            )
            return { username, ...data }
        },
        onSuccess: (data) => {
            // Update user in cache
            queryClient.setQueryData(userKeys.detail(data.username), (old: User | undefined) => {
                if (!old) return old
                return {
                    ...old,
                    followers_count: data.followers_count,
                }
            })
            // Invalidate followers/following lists
            queryClient.invalidateQueries({ queryKey: userKeys.followers(data.username) })
        },
    })
}

// Type import for usePosts reference
import type { Post } from '../types'
