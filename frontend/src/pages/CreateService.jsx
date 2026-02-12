import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { cleanerService } from '../services/cleaner';

const CreateService = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        price: '',
        category: 'regular',
        price_type: 'flat',
        duration_hours: '',
        description: '',
        is_active: true
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await cleanerService.createService({
                ...formData,
                price: parseFloat(formData.price),
                duration_hours: parseFloat(formData.duration_hours)
            });
            navigate('/dashboard'); // Or my-services
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create service');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <div className="glass-panel" style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem' }}>
                <h2 style={{ marginBottom: '2rem', textAlign: 'center' }}>Create New Service</h2>

                {error && <div className="error-message" style={{ marginBottom: '1rem' }}>{error}</div>}

                <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem' }}>

                    {/* Name */}
                    <div className="form-group">
                        <label>Service Name</label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            placeholder="e.g. Deep Home Cleaning"
                        />
                    </div>

                    {/* Category */}
                    <div className="form-group">
                        <label>Category</label>
                        <select name="category" value={formData.category} onChange={handleChange}>
                            <option value="regular">Regular Cleaning</option>
                            <option value="deep">Deep Cleaning</option>
                            <option value="move_in_out">Move In/Out</option>
                            <option value="office">Office Cleaning</option>
                            <option value="specialized">Specialized</option>
                        </select>
                    </div>

                    {/* Pricing */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label>Price (₹)</label>
                            <input
                                type="number"
                                name="price"
                                value={formData.price}
                                onChange={handleChange}
                                required
                                min="0"
                                step="10"
                            />
                        </div>
                        <div className="form-group">
                            <label>Pricing Type</label>
                            <select name="price_type" value={formData.price_type} onChange={handleChange}>
                                <option value="flat">Flat Rate</option>
                                <option value="per_hour">Per Hour</option>
                                <option value="per_sqft">Per Sqft</option>
                            </select>
                        </div>
                    </div>

                    {/* Duration */}
                    <div className="form-group">
                        <label>Duration (Hours)</label>
                        <input
                            type="number"
                            name="duration_hours"
                            value={formData.duration_hours}
                            onChange={handleChange}
                            required
                            min="0.5"
                            step="0.5"
                        />
                    </div>

                    {/* Description */}
                    <div className="form-group">
                        <label>Description (Optional)</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows="4"
                            placeholder="Describe what's included..."
                        />
                    </div>

                    {/* Active Checkbox */}
                    <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input
                            type="checkbox"
                            name="is_active"
                            checked={formData.is_active}
                            onChange={handleChange}
                            id="is_active"
                        />
                        <label htmlFor="is_active" style={{ marginBottom: 0 }}>Active (Visible to customers)</label>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: '1rem' }}>
                        {loading ? 'Creating...' : 'Create Service Package'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CreateService;
