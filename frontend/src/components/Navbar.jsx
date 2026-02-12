import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout } = useAuth();

    return (
        <nav style={{
            borderBottom: '1px solid var(--border)',
            backgroundColor: 'rgba(15, 23, 42, 0.8)',
            backdropFilter: 'blur(10px)',
            position: 'sticky',
            top: 0,
            zIndex: 50
        }}>
            <div className="container" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                height: '4rem'
            }}>
                <Link to="/" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text)' }}>
                    Clean<span style={{ color: 'var(--primary)' }}>Pro</span>
                </Link>

                <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                    {user ? (
                        <>
                            <Link to="/search" style={{ color: 'var(--text-muted)' }}>Find Services</Link>

                            {user.role === 'customer' && (
                                <Link to="/my-bookings" style={{ color: 'var(--text-muted)' }}>My Bookings</Link>
                            )}

                            {user.role === 'cleaner' && (
                                <>
                                    <Link to="/cleaner-jobs" style={{ color: 'var(--text-muted)' }}>Incoming Jobs</Link>
                                    <Link to="/my-services" style={{ color: 'var(--text-muted)' }}>My Services</Link>
                                </>
                            )}

                            <Link to="/dashboard" style={{ color: 'var(--text-muted)' }}>Dashboard</Link>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{user.full_name}</span>
                                <button onClick={logout} className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}>
                                    Logout
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <Link to="/login" style={{ color: 'var(--text-muted)' }}>Login</Link>
                            <Link to="/register" className="btn btn-primary">
                                Get Started
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
