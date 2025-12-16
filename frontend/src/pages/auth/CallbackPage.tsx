import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function CallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      // Check for tokens in URL params (new flow: backend redirects with tokens)
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');
      const isNewUser = searchParams.get('is_new_user') === 'true';
      
      if (accessToken && refreshToken) {
        // New flow: tokens provided directly in URL
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        
        // Fetch user profile with Authorization header
        try {
          const userResponse = await axios.get(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });
          const user = userResponse.data;
          
          // Redirect based on user role
          if (isNewUser) {
            navigate('/welcome');
          } else if (user.role === 'agency_admin') {
            navigate('/admin/dashboard');
          } else {
            navigate('/dashboard');
          }
        } catch (err) {
          console.error('Failed to fetch user profile:', err);
          navigate('/dashboard');  // Fallback
        }
        
        return;
      }
      
      // Old flow: handle OAuth code exchange (fallback)
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const errorParam = searchParams.get('error');

      if (errorParam) {
        setError(`Authentication failed: ${errorParam}`);
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      if (!code || !state) {
        setError('Missing authorization parameters');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      try {
        // Exchange code for tokens (backend should now redirect instead)
        const response = await axios.get(
          `${API_BASE_URL}/api/v1/auth/google/callback?code=${code}&state=${state}`
        );

        const { access_token, refresh_token, user, is_new_user } = response.data;

        // Store tokens
        localStorage.setItem('access_token', access_token);
        if (refresh_token) {
          localStorage.setItem('refresh_token', refresh_token);
        }

        // Set default axios header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        // Redirect based on user role
        if (is_new_user) {
          navigate('/welcome');
        } else if (user.role === 'agency_admin') {
          navigate('/admin/dashboard');
        } else {
          navigate('/dashboard');
        }
      } catch (err: any) {
        console.error('OAuth callback error:', err);
        setError(err.response?.data?.detail || 'Authentication failed. Please try again.');
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <div style={{
        background: 'white',
        padding: '3rem',
        borderRadius: '16px',
        textAlign: 'center',
        maxWidth: '400px'
      }}>
        {error ? (
          <>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>
            <h2 style={{ color: '#e53e3e', marginBottom: '1rem' }}>Authentication Failed</h2>
            <p style={{ color: '#666' }}>{error}</p>
            <p style={{ color: '#999', fontSize: '0.9rem', marginTop: '1rem' }}>
              Redirecting to login...
            </p>
          </>
        ) : (
          <>
            <div className="spinner" style={{
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #667eea',
              borderRadius: '50%',
              width: '50px',
              height: '50px',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 1.5rem'
            }}></div>
            <h2 style={{ color: '#333', marginBottom: '0.5rem' }}>Completing Sign In...</h2>
            <p style={{ color: '#666', fontSize: '0.9rem' }}>Please wait while we verify your credentials</p>
          </>
        )}
      </div>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
