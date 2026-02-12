import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { cleanerService } from '../services/cleaner';

const CleanerOnboarding = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        bio: '',
        experience_years: 0,
        city: '',
        specializations: []
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await cleanerService.createProfile({
                ...formData,
                experience_years: parseInt(formData.experience_years),
                specializations: formData.specializations
            });
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create profile');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <div className="glass-panel" style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem' }}>
                <h2 style={{ marginBottom: '2rem', textAlign: 'center' }}>Complete Your Cleaner Profile</h2>
                <p style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--text-muted)' }}>
                    Tell customers about yourself to get started.
                </p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem' }}>
                    <div className="form-group">
                        <label>City</label>
                        <input
                            type="text"
                            name="city"
                            value={formData.city}
                            onChange={handleChange}
                            required
                            placeholder="e.g. Mumbai"
                        />
                    </div>

                    <div className="form-group">
                        <label>Experience (Years)</label>
                        <input
                            type="number"
                            name="experience_years"
                            value={formData.experience_years}
                            onChange={handleChange}
                            required
                            min="0"
                        />
                    </div>

                    <div className="form-group">
                        <label>Bio</label>
                        <textarea
                            name="bio"
                            value={formData.bio}
                            onChange={handleChange}
                            required
                            rows="4"
                            placeholder="Describe your experience and skills..."
                        />
                    </div>

                    <div className="form-group">
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Specializations</label>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '0.5rem' }}>
                            {[
                                { id: 'regular', label: 'Regular Cleaning' },
                                { id: 'deep', label: 'Deep Cleaning' },
                                { id: 'move_in_out', label: 'Move In/Out Cleaning' },
                                { id: 'office', label: 'Office Cleaning' },
                                { id: 'specialized', label: 'Specialized Cleaning' }
                            ].map(spec => (
                                <label key={spec.id} style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    padding: '0.5rem',
                                    background: 'rgba(255,255,255,0.05)',
                                    borderRadius: 'var(--radius-sm)',
                                    cursor: 'pointer'
                                }}>
                                    <input
                                        type="checkbox"
                                        checked={Array.isArray(formData.specializations) && formData.specializations.includes(spec.id)}
                                        onChange={(e) => {
                                            const newSpecs = e.target.checked
                                                ? [...(Array.isArray(formData.specializations) ? formData.specializations : []), spec.id]
                                                : (Array.isArray(formData.specializations) ? formData.specializations : []).filter(s => s !== spec.id);
                                            setFormData({ ...formData, specializations: newSpecs });
                                        }}
                                        style={{ marginRight: '0.75rem', width: '1.25rem', height: '1.25rem' }}
                                    />
                                    {spec.label}
                                </label>
                            ))}
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Creating Profile...' : 'Save Profile'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CleanerOnboarding;
