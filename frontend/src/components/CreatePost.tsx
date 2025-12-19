import { useState } from 'react'
import { useCreatePost } from '../hooks/usePosts'
import './CreatePost.css'

export function CreatePost() {
    const [content, setContent] = useState('')
    const createPost = useCreatePost()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!content.trim()) return

        // Extract hashtags from content
        const hashtags = content.match(/#\w+/g)?.map(t => t.slice(1)) || []

        try {
            await createPost.mutateAsync({ content, hashtags })
            setContent('')
        } catch (error) {
            console.error('Failed to create post:', error)
        }
    }

    return (
        <form className="create-post card" onSubmit={handleSubmit}>
            <textarea
                className="input textarea"
                placeholder="What's on your mind?"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                maxLength={500}
            />

            <div className="create-post-footer">
                <span className="char-count">{content.length}/500</span>
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={!content.trim() || createPost.isPending}
                >
                    {createPost.isPending ? (
                        <span className="spinner" />
                    ) : (
                        'Post'
                    )}
                </button>
            </div>
        </form>
    )
}
