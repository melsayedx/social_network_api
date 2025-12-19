import { Link } from 'react-router-dom'
import type { Post as PostType } from '../types'
import { useLikePost } from '../hooks/usePosts'
import { useAuthStore } from '../stores/authStore'
import './PostCard.css'

interface PostCardProps {
    post: PostType
}

export function PostCard({ post }: PostCardProps) {
    const { isAuthenticated } = useAuthStore()
    const likeMutation = useLikePost()

    const handleLike = () => {
        if (!isAuthenticated) return
        likeMutation.mutate(post.id)
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        const now = new Date()
        const diff = now.getTime() - date.getTime()

        const minutes = Math.floor(diff / 60000)
        const hours = Math.floor(diff / 3600000)
        const days = Math.floor(diff / 86400000)

        if (minutes < 1) return 'Just now'
        if (minutes < 60) return `${minutes}m ago`
        if (hours < 24) return `${hours}h ago`
        if (days < 7) return `${days}d ago`
        return date.toLocaleDateString()
    }

    return (
        <article className="post-card card fade-in">
            <header className="post-header">
                <Link to={`/profile/${post.user.username}`} className="post-author">
                    <img
                        src={post.user.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${post.user.username}`}
                        alt={post.user.username}
                        className="avatar"
                    />
                    <div className="author-info">
                        <span className="author-name">{post.user.username}</span>
                        <span className="post-time">{formatDate(post.created_at)}</span>
                    </div>
                </Link>

                {post.metadata?.edited && (
                    <span className="edited-badge">edited</span>
                )}
            </header>

            <div className="post-content">
                <p>{post.content}</p>

                {post.metadata?.hashtags && post.metadata.hashtags.length > 0 && (
                    <div className="hashtags">
                        {post.metadata.hashtags.map((tag) => (
                            <span key={tag} className="hashtag">#{tag}</span>
                        ))}
                    </div>
                )}
            </div>

            <footer className="post-footer">
                <button
                    className={`action-btn like-btn ${post.is_liked ? 'liked' : ''}`}
                    onClick={handleLike}
                    disabled={!isAuthenticated || likeMutation.isPending}
                >
                    <span className="icon">{post.is_liked ? '❤️' : '🤍'}</span>
                    <span>{post.likes_count}</span>
                </button>

                <Link to={`/post/${post.id}`} className="action-btn">
                    <span className="icon">💬</span>
                    <span>{post.comments_count}</span>
                </Link>

                <button className="action-btn">
                    <span className="icon">🔗</span>
                    <span>Share</span>
                </button>
            </footer>
        </article>
    )
}
