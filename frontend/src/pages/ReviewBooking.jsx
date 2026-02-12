import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { bookingService } from '../services/booking';
import { reviewService } from '../services/review';

const ReviewBooking = () => {
    const { id: bookingId } = useParams();
    const navigate = useNavigate();
    const [booking, setBooking] = useState(null);
    const [loading, setLoading] = useState(true);
    const [formData, setFormData] = useState({
        rating: 5,
        comment: ''
    });
    const [error, setError] = useState('');

    useEffect(() => {
        bookingService.getBooking(bookingId)
            .then(data => setBooking(data))
            .catch(err => setError("Booking not found"))
            .finally(() => setLoading(false));
    }, [bookingId]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await reviewService.createReview({
                booking_id: bookingId,
                cleaner_id: booking.cleaner_id,
                rating: parseInt(formData.rating),
                comment: formData.comment
            });
            navigate('/my-bookings');
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to submit review");
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="error-message">{error}</div>;

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <div className="glass-panel" style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem' }}>
                <h2 style={{ marginBottom: '2rem', textAlign: 'center' }}>Rate Your Experience</h2>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <p>How was your service with <strong>{booking.cleaner_snapshot?.full_name}</strong>?</p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem' }}>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '1rem', cursor: 'pointer' }}>
                            {[1, 2, 3, 4, 5].map(star => (
                                <span
                                    key={star}
                                    style={{ color: star <= formData.rating ? '#fbbf24' : '#e5e7eb', margin: '0 0.25rem' }}
                                    onClick={() => setFormData({ ...formData, rating: star })}
                                >
                                    ★
                                </span>
                            ))}
                        </div>
                        <input type="hidden" name="rating" value={formData.rating} />
                    </div>

                    <div className="form-group">
                        <label>Comment (Optional)</label>
                        <textarea
                            value={formData.comment}
                            onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
                            rows="4"
                            placeholder="Share your feedback..."
                        />
                    </div>

                    <button type="submit" className="btn btn-primary">
                        Submit Review
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ReviewBooking;
