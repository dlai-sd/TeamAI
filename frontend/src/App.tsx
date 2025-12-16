import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import LoginPage from './pages/auth/LoginPage'
import CallbackPage from './pages/auth/CallbackPage'
import DashboardPage from './pages/DashboardPage'
import InvitesPage from './pages/admin/InvitesPage'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<CallbackPage />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />
          
          {/* Admin routes */}
          <Route path="/admin/invites" element={
            <ProtectedRoute requireAdmin>
              <InvitesPage />
            </ProtectedRoute>
          } />
          
          <Route path="/admin/dashboard" element={
            <ProtectedRoute requireAdmin>
              <DashboardPage />
            </ProtectedRoute>
          } />
          
          {/* Redirect root to dashboard or login */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* 404 */}
          <Route path="*" element={
            <div style={{ textAlign: 'center', padding: '3rem' }}>
              <h1>404 - Page Not Found</h1>
              <p><a href="/dashboard">Go to Dashboard</a></p>
            </div>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
