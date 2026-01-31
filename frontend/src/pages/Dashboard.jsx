import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (!user) {
            navigate('/login');
        }
    }, [user, navigate]);

    if (!user) return null;

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <div style={{ marginBottom: '3rem' }}>
                <h1>Hello, <span style={{ color: 'var(--primary)' }}>{user.full_name}</span></h1>
                <p style={{ color: 'var(--text-muted)' }}>Welcome to your dashboard.</p>
            </div>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '2rem'
            }}>
                {/* Profile Card */}
                <div className="glass-panel" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
                    <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
                        Profile Details
                    </h3>
                    <div style={{ marginBottom: '1rem' }}>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.875rem' }}>Email</span>
                        <span>{user.email}</span>
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.875rem' }}>Phone</span>
                        <span>{user.phone || 'Not provided'}</span>
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.875rem' }}>Role</span>
                        <span style={{ textTransform: 'capitalize' }}>{user.role}</span>
                    </div>
                    <div style={{ marginTop: '2rem' }}>
                        <button className="btn btn-secondary" style={{ width: '100%' }}>Edit Profile</button>
                    </div>
                </div>

                {/* Activity Card (Placeholder) */}
                <div className="glass-panel" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
                    <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
                        Recent Activity
                    </h3>
                    <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
                        No recent bookings or activity.
                    </p>
                    <div style={{ textAlign: 'center' }}>
                        {user.role === 'customer' ? (
                            <button className="btn btn-primary">Book a Cleaner</button>
                        ) : (
                            <button className="btn btn-primary">Create Service</button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
