import { useParams } from 'react-router-dom'
import { useUser, useFollowUser } from '../hooks/useUsers'
import { usePosts } from '../hooks/usePosts'
import { useAuthStore } from '../stores/authStore'
import { PostCard } from '../components/PostCard'
import './Profile.css'

export function ProfilePage() {
    const { username } = useParams<{ username: string }>()
    const { user: currentUser, isAuthenticated } = useAuthStore()
    const { data: user, isLoading } = useUser(username || '')
    const { data: postsData } = usePosts()
    const followMutation = useFollowUser()

    const isOwnProfile = currentUser?.username === username

    // Filter posts by this user (simplified - should use useUserPosts)
    const userPosts = postsData?.results.filter(p => p.user.username === username) || []

    const handleFollow = () => {
        if (username) {
            followMutation.mutate(username)
        }
    }

    if (isLoading) {
        return (
            <div className="loading-container">
                <div className="spinner" />
            </div>
        )
    }

    if (!user) {
        return (
            <div className="error-message">User not found</div>
        )
    }

    return (
        <div className="profile-page">
            <header className="profile-header card">
                <img
                    src={user.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${user.username}`}
                    alt={user.username}
                    className="avatar avatar-lg profile-avatar"
                />

                <div className="profile-info">
                    <h1 className="profile-name">{user.username}</h1>
                    {user.bio && <p className="profile-bio">{user.bio}</p>}

                    <div className="profile-stats">
                        <div className="stat">
                            <span className="stat-value">{user.posts_count}</span>
                            <span className="stat-label">Posts</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">{user.followers_count}</span>
                            <span className="stat-label">Followers</span>
                        </div>
                        <div className="stat">
                            <span className="stat-value">{user.following_count}</span>
                            <span className="stat-label">Following</span>
                        </div>
                    </div>
                </div>

                {isAuthenticated && !isOwnProfile && (
                    <button
                        className="btn btn-primary"
                        onClick={handleFollow}
                        disabled={followMutation.isPending}
                    >
                        {followMutation.isPending ? 'Loading...' : 'Follow'}
                    </button>
                )}
            </header>

            <section className="profile-posts">
                <h2 className="section-title">Posts</h2>
                {userPosts.map((post) => (
                    <PostCard key={post.id} post={post} />
                ))}
                {userPosts.length === 0 && (
                    <div className="empty-state">
                        <p>No posts yet</p>
                    </div>
                )}
            </section>
        </div>
    )
}
