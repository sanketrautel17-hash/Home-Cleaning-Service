import { useState, useEffect } from 'react';
import { bookingService } from '../services/booking';

const CleanerBookings = () => {
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        bookingService.getCleanerBookings()
            .then(data => setBookings(data.bookings || []))
            .catch(err => console.error("Failed to fetch jobs", err))
            .finally(() => setLoading(false));
    }, []);

    const handleStatusUpdate = async (bookingId, newStatus) => {
        try {
            await bookingService.updateStatus(bookingId, newStatus);
            // Refresh list or update local state
            setBookings(prev => prev.map(booking =>
                booking.id === bookingId ? { ...booking, status: newStatus } : booking
            ));
        } catch (err) {
            alert("Failed to update status");
        }
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <h1 style={{ marginBottom: '2rem' }}>Job Requests</h1>

            {bookings.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
                    <p>No jobs assigned yet.</p>
                </div>
            ) : (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                    {bookings.map(booking => (
                        <div key={booking.id} className="glass-panel" style={{ padding: '1.5rem', borderRadius: 'var(--radius-lg)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                <div>
                                    <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>
                                        {booking.customer_snapshot?.full_name || "Customer"}
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
                                    background: 'rgba(59, 130, 246, 0.1)',
                                    color: '#3b82f6',
                                    textTransform: 'uppercase'
                                }}>
                                    {booking.status}
                                </span>
                            </div>

                            <div style={{ padding: '1rem 0', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)', marginBottom: '1rem' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                    <div>
                                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Service</span>
                                        <span style={{ fontWeight: 600 }}>{booking.service_snapshot?.name}</span>
                                    </div>
                                    <div>
                                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Price</span>
                                        <span style={{ fontWeight: 600 }}>₹{booking.total_price}</span>
                                    </div>
                                    <div style={{ gridColumn: 'span 2' }}>
                                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Address</span>
                                        <span>{booking.address.street}, {booking.address.city}, {booking.address.pincode}</span>
                                    </div>
                                    {booking.special_instructions && (
                                        <div style={{ gridColumn: 'span 2' }}>
                                            <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Note</span>
                                            <span>{booking.special_instructions}</span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                                {booking.status === 'pending' && (
                                    <>
                                        <button className="btn btn-primary" onClick={() => handleStatusUpdate(booking.id, 'confirmed')} style={{ fontSize: '0.875rem' }}>
                                            Accept Job
                                        </button>
                                        <button className="btn btn-secondary" onClick={() => handleStatusUpdate(booking.id, 'cancelled')} style={{ fontSize: '0.875rem', color: '#ef4444' }}>
                                            Reject
                                        </button>
                                    </>
                                )}
                                {booking.status === 'confirmed' && (
                                    <button className="btn btn-primary" onClick={() => handleStatusUpdate(booking.id, 'in_progress')} style={{ fontSize: '0.875rem' }}>
                                        Start Job
                                    </button>
                                )}
                                {booking.status === 'in_progress' && (
                                    <button className="btn btn-primary" onClick={() => handleStatusUpdate(booking.id, 'completed')} style={{ fontSize: '0.875rem', background: '#22c55e', borderColor: '#22c55e' }}>
                                        Complete Job
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

export default CleanerBookings;
