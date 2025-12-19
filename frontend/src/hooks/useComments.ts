/**
 * React Query hooks for Comments
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, { apiWithIdempotency } from '../lib/api'
import type { Comment, PaginatedResponse, CreateCommentData } from '../types'

// Query keys
export const commentKeys = {
    all: ['comments'] as const,
    list: (postId: string) => [...commentKeys.all, 'list', postId] as const,
}

// Fetch comments for a post
export function useComments(postId: string) {
    return useQuery({
        queryKey: commentKeys.list(postId),
        queryFn: async () => {
            const { data } = await api.get<PaginatedResponse<Comment>>(
                `/posts/${postId}/comments/`
            )
            return data
        },
        enabled: !!postId,
    })
}

// Create comment mutation (with idempotency)
export function useCreateComment(postId: string) {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: CreateCommentData) =>
            apiWithIdempotency.post<Comment>(`/posts/${postId}/comments/`, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: commentKeys.list(postId) })
        },
    })
}

// Delete comment mutation
export function useDeleteComment(postId: string) {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (commentId: string) => {
            await api.delete(`/comments/${commentId}/`)
            return commentId
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: commentKeys.list(postId) })
        },
    })
}
