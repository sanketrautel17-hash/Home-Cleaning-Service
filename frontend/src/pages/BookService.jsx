import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { serviceService } from '../services/service';
import { bookingService } from '../services/booking';

const BookService = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [service, setService] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const [bookingData, setBookingData] = useState({
        date: '',
        time: '',
        address: {
            street: '',
            city: '',
            state: '',
            pincode: ''
        },
        instructions: ''
    });

    useEffect(() => {
        serviceService.getService(id)
            .then(data => setService(data))
            .catch(err => setError("Service not found"))
            .finally(() => setLoading(false));
    }, [id]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name.includes('.')) {
            const [parent, child] = name.split('.');
            setBookingData(prev => ({
                ...prev,
                [parent]: { ...prev[parent], [child]: value }
            }));
        } else {
            setBookingData(prev => ({ ...prev, [name]: value }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await bookingService.createBooking({
                service_id: id,
                cleaner_id: service.cleaner_id,
                scheduled_date: bookingData.date,
                start_time: bookingData.time,
                duration_hours: service.duration_hours,
                address: bookingData.address,
                special_instructions: bookingData.instructions
            });
            navigate('/my-bookings');
        } catch (err) {
            setError(err.response?.data?.detail || "Booking failed");
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="error-message">{error}</div>;
    if (!service) return null;

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <div className="glass-panel" style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
                <h2 style={{ marginBottom: '2rem' }}>Book Service: {service.name}</h2>

                <div style={{ marginBottom: '2rem', padding: '1rem', background: 'var(--surface-light)', borderRadius: 'var(--radius-md)' }}>
                    <p><strong>Category:</strong> {service.category}</p>
                    <p><strong>Price:</strong> ₹{service.price}</p>
                    <p><strong>Duration:</strong> {service.duration_hours} hours</p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.5rem' }}>

                    {/* Date & Time */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label>Date</label>
                            <input
                                type="date"
                                name="date"
                                value={bookingData.date}
                                onChange={handleChange}
                                required
                                min={new Date().toISOString().split('T')[0]}
                            />
                        </div>
                        <div className="form-group">
                            <label>Start Time</label>
                            <input
                                type="time"
                                name="time"
                                value={bookingData.time}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    {/* Address Section */}
                    <h3 style={{ fontSize: '1.1rem', marginTop: '1rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>Service Location</h3>

                    <div className="form-group">
                        <label>Street Address</label>
                        <input
                            type="text"
                            name="address.street"
                            value={bookingData.address.street}
                            onChange={handleChange}
                            required
                            placeholder="Flat No, Building, Street"
                        />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label>City</label>
                            <input
                                type="text"
                                name="address.city"
                                value={bookingData.address.city}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>State</label>
                            <input
                                type="text"
                                name="address.state"
                                value={bookingData.address.state}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Pincode</label>
                            <input
                                type="text"
                                name="address.pincode"
                                value={bookingData.address.pincode}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Special Instructions (Optional)</label>
                        <textarea
                            name="instructions"
                            value={bookingData.instructions}
                            onChange={handleChange}
                            rows="3"
                            placeholder="Gate code, pets, specific areas to focus on..."
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ padding: '1rem' }}>
                        Confirm Booking
                    </button>
                </form>
            </div>
        </div>
    );
};

export default BookService;
