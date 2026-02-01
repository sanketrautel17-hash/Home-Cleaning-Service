import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../services/api';

const VerifyEmail = () => {
    const [status, setStatus] = useState('verifying'); // verifying, success, error
    const [message, setMessage] = useState('Verifying your email...');
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    useEffect(() => {
        const verify = async () => {
            const token = searchParams.get('token');
            if (!token) {
                setStatus('error');
                setMessage('Invalid verification link. No token provided.');
                return;
            }

            try {
                // Call verification API
                const response = await api.post(`/auth/verify-email?token=${token}`);
                setStatus('success');
                setMessage(response.data.message || 'Email verified successfully!');

                // Optional: Redirect after delay
                // setTimeout(() => navigate('/login'), 5000);
            } catch (err) {
                console.error("Verification failed", err);
                setStatus('error');
                setMessage(err.response?.data?.detail || 'Verification failed. The link may be expired or invalid.');
            }
        };

        verify();
    }, [searchParams]);

    return (
        <div className="container" style={{
            minHeight: '80vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }}>
            <div className="glass-panel" style={{
                width: '100%',
                maxWidth: '500px',
                padding: '3rem',
                borderRadius: 'var(--radius-xl)',
                textAlign: 'center'
            }}>
                {status === 'verifying' && (
                    <>
                        <div style={{
                            width: '48px',
                            height: '48px',
                            border: '3px solid var(--border)',
                            borderTopColor: 'var(--primary)',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite',
                            margin: '0 auto 1.5rem'
                        }} />
                        <h2 style={{ marginBottom: '1rem' }}>Verifying...</h2>
                    </>
                )}

                {status === 'success' && (
                    <>
                        <div style={{
                            width: '64px',
                            height: '64px',
                            background: 'rgba(16, 185, 129, 0.1)',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 1.5rem',
                            color: 'var(--success)'
                        }}>
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                                <polyline points="22 4 12 14.01 9 11.01" />
                            </svg>
                        </div>
                        <h2 style={{ marginBottom: '1rem' }}>Verified!</h2>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                            {message}
                        </p>
                        <button
                            onClick={() => navigate('/login')}
                            className="btn btn-primary"
                            style={{ width: '100%' }}
                        >
                            Continue to Login
                        </button>
                    </>
                )}

                {status === 'error' && (
                    <>
                        <div style={{
                            width: '64px',
                            height: '64px',
                            background: 'rgba(239, 68, 68, 0.1)',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 1.5rem',
                            color: 'var(--error)'
                        }}>
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" y1="8" x2="12" y2="12" />
                                <line x1="12" y1="16" x2="12.01" y2="16" />
                            </svg>
                        </div>
                        <h2 style={{ marginBottom: '1rem' }}>Verification Failed</h2>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                            {message}
                        </p>
                        <button
                            onClick={() => navigate('/login')}
                            className="btn btn-secondary"
                            style={{ width: '100%' }}
                        >
                            Back to Login
                        </button>
                    </>
                )}

                <style>{`
                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                `}</style>
            </div>
        </div>
    );
};

export default VerifyEmail;
