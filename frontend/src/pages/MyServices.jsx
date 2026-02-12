import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { cleanerService } from '../services/cleaner';

const MyServices = () => {
    const [services, setServices] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchServices = async () => {
            try {
                const data = await cleanerService.getMyServices();
                setServices(data.services || []);
            } catch (err) {
                console.error("Failed to fetch services", err);
            } finally {
                setLoading(false);
            }
        };
        fetchServices();
    }, []);

    if (loading) return <div>Loading...</div>;

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '2rem' }}>My Service Packages</h1>
                <Link to="/create-service" className="btn btn-primary">
                    + Create New Service
                </Link>
            </div>

            {services.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
                    <p>No services created yet.</p>
                    <Link to="/create-service" className="btn btn-secondary" style={{ marginTop: '1rem' }}>
                        Start Offering Services
                    </Link>
                </div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '2rem'
                }}>
                    {services.map(service => (
                        <div key={service.id} className="glass-panel" style={{ padding: '1.5rem', borderRadius: 'var(--radius-lg)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div>
                                    <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>{service.name}</h3>
                                    <span style={{
                                        color: 'var(--primary)',
                                        fontSize: '0.875rem',
                                        fontWeight: 600,
                                        textTransform: 'uppercase'
                                    }}>
                                        {service.category}
                                    </span>
                                </div>
                                <span style={{
                                    background: service.is_active ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                    color: service.is_active ? '#22c55e' : '#ef4444',
                                    padding: '0.25rem 0.5rem',
                                    borderRadius: '1rem',
                                    fontSize: '0.75rem',
                                    fontWeight: 600
                                }}>
                                    {service.is_active ? 'Active' : 'Hidden'}
                                </span>
                            </div>

                            <div style={{ margin: '1rem 0' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    <span>₹{service.price}</span>
                                    <span>•</span>
                                    <span>{service.duration_hours} hrs</span>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                                <button className="btn btn-secondary" style={{ flex: 1, padding: '0.5rem' }}>Edit</button>
                                {/* Add delete/toggle active functionality */}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default MyServices;
