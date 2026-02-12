import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { bookingService } from '../services/booking';
import { paymentService } from '../services/payment';

const PaymentPage = () => {
    const { id: bookingId } = useParams();
    const navigate = useNavigate();
    const [booking, setBooking] = useState(null);
    const [loading, setLoading] = useState(true);
    const [processing, setProcessing] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        bookingService.getBooking(bookingId)
            .then(data => setBooking(data))
            .catch(err => setError("Booking not found"))
            .finally(() => setLoading(false));
    }, [bookingId]);

    const handlePayment = async () => {
        setProcessing(true);
        try {
            const response = await paymentService.initiatePayment({
                booking_id: bookingId,
                method: 'card'
            });

            // In a real app, we would redirect to response.payment_url
            // Here we simulate the gateway success
            // const paymentUrl = response.payment_url;
            // window.location.href = paymentUrl; 

            // Simulating...
            const paymentId = response.payment_id;
            await paymentService.verifyPayment(paymentId);

            alert("Payment Successful!");
            navigate('/my-bookings');

        } catch (err) {
            setError(err.response?.data?.detail || "Payment failed");
        } finally {
            setProcessing(false);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="error-message">{error}</div>;

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <div className="glass-panel" style={{ maxWidth: '500px', margin: '0 auto', padding: '2rem', textAlign: 'center' }}>
                <h2 style={{ marginBottom: '2rem' }}>Complete Payment</h2>

                <div style={{ marginBottom: '2rem', padding: '1rem', background: 'var(--surface-light)', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--primary)', marginBottom: '0.5rem' }}>
                        ₹{booking.total_price}
                    </div>
                    <p style={{ color: 'var(--text-muted)' }}>Total Amount Due</p>
                </div>

                <div style={{ textAlign: 'left', marginBottom: '2rem' }}>
                    <p><strong>Service:</strong> {booking.service_snapshot?.name}</p>
                    <p><strong>Date:</strong> {new Date(booking.scheduled_date).toLocaleDateString()}</p>
                    <p><strong>Address:</strong> {booking.address.street}, {booking.address.city}</p>
                </div>

                <button
                    onClick={handlePayment}
                    className="btn btn-primary"
                    style={{ width: '100%', padding: '1rem', fontSize: '1.25rem' }}
                    disabled={processing}
                >
                    {processing ? "Processing..." : `Pay ₹${booking.total_price}`}
                </button>

                <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    Secure payment via MockGateway
                </p>
            </div>
        </div>
    );
};

export default PaymentPage;
