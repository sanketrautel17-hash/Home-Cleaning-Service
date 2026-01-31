import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        phone: '',
        role: 'customer'
    });
    const [error, setError] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Basic password validation
        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            return;
        }

        try {
            await register(formData);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
        }
    };

    return (
        <div className="container" style={{
            minHeight: '80vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem 0'
        }}>
            <div className="glass-panel" style={{
                width: '100%',
                maxWidth: '500px',
                padding: '2.5rem',
                borderRadius: 'var(--radius-xl)'
            }}>
                <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Create Account</h2>

                {error && (
                    <div style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        color: 'var(--error)',
                        padding: '0.75rem',
                        borderRadius: 'var(--radius-md)',
                        marginBottom: '1.5rem',
                        textAlign: 'center'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="label">Full Name</label>
                        <input
                            type="text"
                            name="full_name"
                            className="input"
                            value={formData.full_name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="label">Email Address</label>
                        <input
                            type="email"
                            name="email"
                            className="input"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="label">Phone Number</label>
                        <input
                            type="tel"
                            name="phone"
                            className="input"
                            value={formData.phone}
                            onChange={handleChange}
                        />
                    </div>

                    <div className="form-group">
                        <label className="label">I want to...</label>
                        <select
                            name="role"
                            className="input"
                            value={formData.role}
                            onChange={handleChange}
                            style={{ cursor: 'pointer' }}
                        >
                            <option value="customer">Hire Cleaners</option>
                            <option value="cleaner">Become a Cleaner</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="label">Password</label>
                        <input
                            type="password"
                            name="password"
                            className="input"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            placeholder="Min 8 chars, 1 uppercase, 1 symbol"
                        />
                        <small style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                            Must contain at least 8 characters, one uppercase, one lowercase, one number and one special character.
                        </small>
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
                        Create Account
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: '2rem', color: 'var(--text-muted)' }}>
                    Already have an account? <Link to="/login">Sign in</Link>
                </p>
            </div>
        </div>
    );
};

export default Register;
