import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { cleanerService } from '../services/cleaner';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [loadingProfile, setLoadingProfile] = useState(false);

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }

        if (user.role === 'cleaner') {
            setLoadingProfile(true);
            cleanerService.getProfile()
                .then(data => setProfile(data))
                .catch(err => {
                    // Profile not found is expected for new cleaners
                    console.log("No profile found");
                })
                .finally(() => setLoadingProfile(false));
        }
    }, [user, navigate]);

    if (!user) return null;

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <div style={{ marginBottom: '3rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1>Hello, <span style={{ color: 'var(--primary)' }}>{user.full_name}</span></h1>
                    <p style={{ color: 'var(--text-muted)' }}>Welcome to your dashboard.</p>
                </div>
                <button onClick={logout} className="btn btn-secondary">Logout</button>
            </div>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '2rem'
            }}>
                {/* Profile Card */}
                <div className="glass-panel" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
                    <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
                        Account Details
                    </h3>
                    <div style={{ marginBottom: '1rem' }}>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.875rem' }}>Email</span>
                        <span>{user.email}</span>
                    </div>
                    <div style={{ marginBottom: '1rem' }}>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.875rem' }}>Role</span>
                        <span style={{ textTransform: 'capitalize' }}>{user.role}</span>
                    </div>
                </div>

                {/* Actions Card */}
                <div className="glass-panel" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
                    <h3 style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
                        Quick Actions
                    </h3>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {user.role === 'customer' ? (
                            <>
                                <Link to="/search" className="btn btn-primary" style={{ textAlign: 'center' }}>
                                    Find a Cleaner
                                </Link>
                                <Link to="/my-bookings" className="btn btn-secondary" style={{ textAlign: 'center' }}>
                                    My Bookings
                                </Link>
                            </>
                        ) : (
                            <>
                                {loadingProfile ? (
                                    <p>Loading profile...</p>
                                ) : profile ? (
                                    <>
                                        <div style={{ background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
                                            Profile Active • {profile.city}
                                        </div>
                                        <Link to="/cleaner-jobs" className="btn btn-primary" style={{ textAlign: 'center' }}>
                                            View Job Requests
                                        </Link>
                                        <Link to="/my-services" className="btn btn-secondary" style={{ textAlign: 'center' }}>
                                            Manage My Services
                                        </Link>
                                    </>
                                ) : (
                                    <Link to="/cleaner-onboarding" className="btn btn-primary" style={{ textAlign: 'center' }}>
                                        Complete Profile Setup
                                    </Link>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
