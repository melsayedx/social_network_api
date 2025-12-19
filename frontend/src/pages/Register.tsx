import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import './Auth.css'

export function RegisterPage() {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password_confirm: '',
    })
    const [error, setError] = useState('')
    const { register, isLoading } = useAuthStore()
    const navigate = useNavigate()

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (formData.password !== formData.password_confirm) {
            setError('Passwords do not match')
            return
        }

        try {
            await register(formData)
            navigate('/login')
        } catch (err: unknown) {
            const error = err as { response?: { data?: { username?: string[]; email?: string[] } } }
            if (error.response?.data?.username) {
                setError(error.response.data.username[0])
            } else if (error.response?.data?.email) {
                setError(error.response.data.email[0])
            } else {
                setError('Registration failed. Please try again.')
            }
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-card card">
                <h1 className="auth-title">Create Account</h1>
                <p className="auth-subtitle">Join the community today</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            className="input"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            className="input"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            className="input"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            minLength={8}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password_confirm">Confirm Password</label>
                        <input
                            id="password_confirm"
                            name="password_confirm"
                            type="password"
                            className="input"
                            value={formData.password_confirm}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary btn-full" disabled={isLoading}>
                        {isLoading ? <span className="spinner" /> : 'Create Account'}
                    </button>
                </form>

                <p className="auth-footer">
                    Already have an account? <Link to="/login">Sign in</Link>
                </p>
            </div>
        </div>
    )
}
