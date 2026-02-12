import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { bookingService } from '../services/booking';

const MyBookings = () => {
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        bookingService.getMyBookings()
            .then(data => setBookings(data.bookings || []))
            .catch(err => console.error("Failed to fetch bookings", err))
            .finally(() => setLoading(false));
    }, []);

    const getStatusColor = (status) => {
        switch (status) {
            case 'pending': return '#fbbf24';
            case 'confirmed': return '#3b82f6';
            case 'in_progress': return '#8b5cf6';
            case 'completed': return '#22c55e';
            case 'cancelled': return '#ef4444';
            default: return 'var(--text-muted)';
        }
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <h1 style={{ marginBottom: '2rem' }}>My Bookings</h1>

            {bookings.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
                    <p>No bookings found.</p>
                    <Link to="/search" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                        Browse Services
                    </Link>
                </div>
            ) : (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                    {bookings.map(booking => (
                        <div key={booking.id} className="glass-panel" style={{ padding: '1.5rem', borderRadius: 'var(--radius-lg)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                <div>
                                    <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>
                                        {booking.service_snapshot?.name || "Service Booking"}
                                    </h3>
                                    <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                        {new Date(booking.scheduled_date).toLocaleDateString()} at {booking.start_time}
                                    </span>
                                </div>
                                <span style={{
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: '1rem',
                                    fontSize: '0.75rem',
                                    fontWeight: 600,
                                    background: `${getStatusColor(booking.status)}20`,
                                    color: getStatusColor(booking.status)
                                }}>
                                    {booking.status.toUpperCase()}
                                </span>
                            </div>

                            <div style={{ padding: '1rem 0', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)', marginBottom: '1rem' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                    <div>
                                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Price</span>
                                        <span style={{ fontWeight: 600 }}>₹{booking.total_price}</span>
                                    </div>
                                    <div>
                                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Duration</span>
                                        <span>{booking.duration_hours} hrs</span>
                                    </div>
                                    <div style={{ gridColumn: 'span 2' }}>
                                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Address</span>
                                        <span>{booking.address.street}, {booking.address.city}, {booking.address.pincode}</span>
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                                {booking.status === 'completed' && (
                                    <Link to={`/review/${booking.id}`} className="btn btn-secondary" style={{ fontSize: '0.875rem' }}>
                                        Write Review
                                    </Link>
                                )}
                                {booking.payment_status === 'pending' && booking.status !== 'cancelled' && (
                                    <Link to={`/payment/${booking.id}`} className="btn btn-primary" style={{ fontSize: '0.875rem' }}>
                                        Pay Now
                                    </Link>
                                )}
                                {(booking.status === 'pending' || booking.status === 'confirmed') && (
                                    <button className="btn btn-outline-danger" style={{ fontSize: '0.875rem', color: '#ef4444', border: '1px solid #ef4444', padding: '0.5rem 1rem', borderRadius: 'var(--radius-md)', background: 'transparent' }}>
                                        Cancel
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default MyBookings;
