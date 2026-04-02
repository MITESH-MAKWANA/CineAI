import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ProtectedRoute from './components/ProtectedRoute'

// Pages
import Home        from './pages/Home'
import Login       from './pages/Login'
import Register    from './pages/Register'
import Onboarding  from './pages/Onboarding'
import Profile     from './pages/Profile'
import Explore     from './pages/Explore'
import MovieDetail from './pages/MovieDetail'
import Favorites   from './pages/Favorites'
import Watchlist   from './pages/Watchlist'
import About       from './pages/About'
import Contact     from './pages/Contact'
import ForgotPassword  from './pages/ForgotPassword'
import ChangePassword  from './pages/ChangePassword'
import MoodMatch   from './pages/MoodMatch'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3500,
            style: {
              background: '#1e1e2a',
              color: '#f0f0f5',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '10px',
              fontSize: '0.875rem',
              padding: '12px 16px',
              boxShadow: '0 8px 30px rgba(0,0,0,0.5)',
            },
            success: { iconTheme: { primary: '#10b981', secondary: '#1e1e2a' } },
            error:   { iconTheme: { primary: '#e50914', secondary: '#1e1e2a' } },
          }}
        />

        <Navbar />

        <Routes>
          {/* Public only */}
          <Route path="/"                element={<Home />} />
          <Route path="/login"           element={<Login />} />
          <Route path="/register"        element={<Register />} />
          <Route path="/about"           element={<About />} />
          <Route path="/contact"         element={<Contact />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/movie/:id"       element={<MovieDetail />} />

          {/* Protected — require login */}
          <Route path="/explore"         element={<ProtectedRoute><Explore /></ProtectedRoute>} />
          <Route path="/mood"            element={<ProtectedRoute><MoodMatch /></ProtectedRoute>} />
          <Route path="/onboarding"      element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
          <Route path="/profile"         element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/favorites"       element={<ProtectedRoute><Favorites /></ProtectedRoute>} />
          <Route path="/watchlist"       element={<ProtectedRoute><Watchlist /></ProtectedRoute>} />
          <Route path="/change-password" element={<ProtectedRoute><ChangePassword /></ProtectedRoute>} />

          {/* Legacy redirects */}
          <Route path="/genre-select"    element={<Navigate to="/" replace />} />
          <Route path="/genre-skip"      element={<Navigate to="/" replace />} />
          <Route path="/welcome"         element={<Navigate to="/explore" replace />} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        <Footer />
      </BrowserRouter>
    </AuthProvider>
  )
}
