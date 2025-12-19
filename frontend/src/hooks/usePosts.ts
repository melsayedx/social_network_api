/**
 * React Query hooks for Posts
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, { apiWithIdempotency } from '../lib/api'
import type { Post, PaginatedResponse, CreatePostData } from '../types'

// Query keys
export const postKeys = {
    all: ['posts'] as const,
    lists: () => [...postKeys.all, 'list'] as const,
    list: (filters: Record<string, unknown>) => [...postKeys.lists(), filters] as const,
    details: () => [...postKeys.all, 'detail'] as const,
    detail: (id: string) => [...postKeys.details(), id] as const,
    following: () => [...postKeys.all, 'following'] as const,
}

// Fetch all posts
export function usePosts(page = 1) {
    return useQuery({
        queryKey: postKeys.list({ page }),
        queryFn: async () => {
            const { data } = await api.get<PaginatedResponse<Post>>('/posts/', {
                params: { page },
            })
            return data
        },
    })
}

// Fetch following feed
export function useFollowingFeed(page = 1) {
    return useQuery({
        queryKey: [...postKeys.following(), page],
        queryFn: async () => {
            const { data } = await api.get<PaginatedResponse<Post>>('/posts/following/', {
                params: { page },
            })
            return data
        },
    })
}

// Fetch single post
export function usePost(postId: string) {
    return useQuery({
        queryKey: postKeys.detail(postId),
        queryFn: async () => {
            const { data } = await api.get<Post>(`/posts/${postId}/`)
            return data
        },
        enabled: !!postId,
    })
}

// Create post mutation
export function useCreatePost() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreatePostData) =>
            apiWithIdempotency.post<Post>('/posts/', data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: postKeys.lists() })
        },
    })
}

// Like/unlike post mutation
export function useLikePost() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (postId: string) => {
            const { data } = await api.post<{ liked: boolean; likes_count: number }>(
                `/posts/${postId}/like/`
            )
            return { postId, ...data }
        },
        onSuccess: (data) => {
            // Update the specific post in cache
            queryClient.setQueryData(postKeys.detail(data.postId), (old: Post | undefined) => {
                if (!old) return old
                return {
                    ...old,
                    is_liked: data.liked,
                    likes_count: data.likes_count,
                }
            })
            // Invalidate lists to refresh
            queryClient.invalidateQueries({ queryKey: postKeys.lists() })
        },
    })
}

// Delete post mutation
export function useDeletePost() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (postId: string) => {
            await api.delete(`/posts/${postId}/`)
            return postId
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: postKeys.lists() })
        },
    })
}
