import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import './Navbar.css'

export function Navbar() {
    const { user, isAuthenticated, logout } = useAuthStore()
    const location = useLocation()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-logo">
                    <span className="logo-icon">🌐</span>
                    <span className="logo-text">SocialNet</span>
                </Link>

                <div className="navbar-links">
                    <Link
                        to="/"
                        className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
                    >
                        Home
                    </Link>

                    {isAuthenticated && (
                        <Link
                            to="/feed"
                            className={`nav-link ${location.pathname === '/feed' ? 'active' : ''}`}
                        >
                            Feed
                        </Link>
                    )}
                </div>

                <div className="navbar-actions">
                    {isAuthenticated ? (
                        <>
                            <Link to={`/profile/${user?.username}`} className="user-menu">
                                <img
                                    src={user?.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${user?.username}`}
                                    alt={user?.username}
                                    className="avatar avatar-sm"
                                />
                                <span className="username">{user?.username}</span>
                            </Link>
                            <button onClick={handleLogout} className="btn btn-ghost">
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="btn btn-ghost">Login</Link>
                            <Link to="/register" className="btn btn-primary">Sign Up</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    )
}
