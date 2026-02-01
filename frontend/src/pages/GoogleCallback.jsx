import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const GoogleCallback = () => {
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const { handleGoogleCallback } = useAuth();

    useEffect(() => {
        const processCallback = async () => {
            const code = searchParams.get('code');
            const state = searchParams.get('state');
            const errorParam = searchParams.get('error');

            if (errorParam) {
                setError('Google login was cancelled or failed');
                setLoading(false);
                return;
            }

            if (!code) {
                setError('No authorization code received from Google');
                setLoading(false);
                return;
            }

            try {
                await handleGoogleCallback(code, state);
                navigate('/dashboard');
            } catch (err) {
                console.error('Google callback error:', err);
                setError(err.response?.data?.detail || 'Failed to complete Google login');
                setLoading(false);
            }
        };

        processCallback();
    }, [searchParams, handleGoogleCallback, navigate]);

    if (loading) {
        return (
            <div className="container" style={{
                minHeight: '80vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                <div className="glass-panel" style={{
                    padding: '3rem',
                    borderRadius: 'var(--radius-xl)',
                    textAlign: 'center'
                }}>
                    {/* Loading Spinner */}
                    <div style={{
                        width: '48px',
                        height: '48px',
                        border: '3px solid var(--border)',
                        borderTopColor: 'var(--primary)',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                        margin: '0 auto 1.5rem'
                    }} />
                    <h3 style={{ marginBottom: '0.5rem' }}>Completing Sign In</h3>
                    <p style={{ color: 'var(--text-muted)' }}>
                        Please wait while we verify your Google account...
                    </p>

                    <style>{`
                        @keyframes spin {
                            to { transform: rotate(360deg); }
                        }
                    `}</style>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container" style={{
                minHeight: '80vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                <div className="glass-panel" style={{
                    padding: '2.5rem',
                    borderRadius: 'var(--radius-xl)',
                    textAlign: 'center',
                    maxWidth: '400px'
                }}>
                    {/* Error Icon */}
                    <div style={{
                        width: '64px',
                        height: '64px',
                        borderRadius: '50%',
                        background: 'rgba(239, 68, 68, 0.1)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 1.5rem'
                    }}>
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--error)" strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="15" y1="9" x2="9" y2="15" />
                            <line x1="9" y1="9" x2="15" y2="15" />
                        </svg>
                    </div>

                    <h3 style={{ marginBottom: '0.75rem' }}>Login Failed</h3>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>{error}</p>

                    <button
                        onClick={() => navigate('/login')}
                        className="btn btn-primary"
                        style={{ width: '100%' }}
                    >
                        Back to Login
                    </button>
                </div>
            </div>
        );
    }

    return null;
};

export default GoogleCallback;
