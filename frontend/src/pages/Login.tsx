import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import './Auth.css'

export function LoginPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const { login, isLoading } = useAuthStore()
    const navigate = useNavigate()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        try {
            await login(username, password)
            navigate('/')
        } catch {
            setError('Invalid username or password')
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card card">
                <h1 className="auth-title">Welcome Back</h1>
                <p className="auth-subtitle">Sign in to your account</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            type="text"
                            className="input"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            className="input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
                        {isLoading ? <span className="spinner" /> : 'Sign In'}
                    </button>
                </form>

                <p className="auth-footer">
                    Don't have an account? <Link to="/register">Sign up</Link>
                </p>
            </div>
        </div>
    )
}
