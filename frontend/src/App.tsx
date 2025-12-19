import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
import { Navbar } from './components/Navbar'
import { HomePage } from './pages/Home'
import { LoginPage } from './pages/Login'
import { RegisterPage } from './pages/Register'
import { ProfilePage } from './pages/Profile'
import { useAuthStore } from './stores/authStore'
import { getToken } from './lib/api'
import './index.css'

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      retry: 1,
    },
  },
})

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Auth initializer
function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { fetchCurrentUser, isLoading } = useAuthStore()

  useEffect(() => {
    const token = getToken()
    if (token) {
      fetchCurrentUser()
    }
  }, [fetchCurrentUser])

  if (isLoading) {
    return (
      <div className="loading-container" style={{ minHeight: '100vh' }}>
        <div className="spinner" />
      </div>
    )
  }

  return <>{children}</>
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthInitializer>
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/profile/:username" element={<ProfilePage />} />
              <Route
                path="/feed"
                element={
                  <ProtectedRoute>
                    <HomePage />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </AuthInitializer>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
