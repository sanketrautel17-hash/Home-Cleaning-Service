import { Link } from 'react-router-dom';

const ServiceCard = ({ service, showActions = false, onDelete }) => {
    const {
        id,
        name,
        price,
        category,
        duration_hours,
        description,
        is_active,
        cleaner_name,
        cleaner_rating
    } = service;

    return (
        <div className="glass-panel" style={{
            borderRadius: 'var(--radius-lg)',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            position: 'relative',
            opacity: is_active ? 1 : 0.7
        }}>
            {/* Status Badge (if cleaner view) */}
            {showActions && (
                <div style={{
                    position: 'absolute',
                    top: '1rem',
                    right: '1rem',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '2rem',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    background: is_active ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: is_active ? '#22c55e' : '#ef4444',
                    border: '1px solid currentColor'
                }}>
                    {is_active ? 'Active' : 'Inactive'}
                </div>
            )}

            {/* Category Tag */}
            <div style={{ marginBottom: '1rem' }}>
                <span style={{
                    textTransform: 'uppercase',
                    fontSize: '0.75rem',
                    letterSpacing: '0.05em',
                    color: 'var(--primary)',
                    fontWeight: 600
                }}>
                    {category.replace('_', ' ')}
                </span>
            </div>

            <h3 style={{ marginBottom: '0.5rem', fontSize: '1.25rem' }}>{name}</h3>

            <p style={{
                color: 'var(--text-muted)',
                fontSize: '0.875rem',
                marginBottom: '1.5rem',
                flex: 1,
                lineHeight: 1.6
            }}>
                {description || "Professional cleaning service tailored to your needs."}
            </p>

            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '1rem',
                borderTop: '1px solid var(--border)',
                marginBottom: '1rem'
            }}>
                <div>
                    <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>₹{price}</span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}> / service</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    <span style={{ fontSize: '0.875rem' }}>{duration_hours}h</span>
                </div>
            </div>

            {/* Cleaner Info (Public View) */}
            {!showActions && cleaner_name && (
                <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'var(--surface-light)' }} />
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                        {cleaner_name}
                        {cleaner_rating && <span style={{ color: '#fbbf24', marginLeft: '0.25rem' }}>★ {cleaner_rating}</span>}
                    </span>
                </div>
            )}

            <div style={{ marginTop: 'auto' }}>
                {showActions ? (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                        <Link to={`/edit-service/${id}`} className="btn btn-secondary" style={{ textAlign: 'center', padding: '0.5rem' }}>
                            Edit
                        </Link>
                        {/* Delete/Deactivate button could go here */}
                    </div>
                ) : (
                    <Link to={`/book/${id}`} className="btn btn-primary" style={{ display: 'block', textAlign: 'center' }}>
                        Book Now
                    </Link>
                )}
            </div>
        </div>
    );
};

export default ServiceCard;
