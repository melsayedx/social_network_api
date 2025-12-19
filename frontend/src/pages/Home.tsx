import { usePosts } from '../hooks/usePosts'
import { PostCard } from '../components/PostCard'
import { CreatePost } from '../components/CreatePost'
import { useAuthStore } from '../stores/authStore'
import './Home.css'

export function HomePage() {
    const { isAuthenticated } = useAuthStore()
    const { data, isLoading, error } = usePosts()

    if (isLoading) {
        return (
            <div className="loading-container">
                <div className="spinner" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="error-message">
                Failed to load posts. Please try again.
            </div>
        )
    }

    return (
        <div className="home-page">
            <h1 className="page-title">Explore</h1>

            {isAuthenticated && <CreatePost />}

            <div className="posts-list">
                {data?.results.map((post) => (
                    <PostCard key={post.id} post={post} />
                ))}

                {data?.results.length === 0 && (
                    <div className="empty-state">
                        <p>No posts yet. Be the first to post!</p>
                    </div>
                )}
            </div>
        </div>
    )
}
