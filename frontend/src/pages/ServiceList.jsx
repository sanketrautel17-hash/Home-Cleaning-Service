import { useState, useEffect } from 'react';
import { serviceService } from '../services/service';
import ServiceCard from '../components/ServiceCard';

const ServiceList = () => {
    const [services, setServices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        category: '',
        min_price: '',
        max_price: ''
    });

    const fetchServices = async () => {
        setLoading(true);
        try {
            const data = await serviceService.searchServices(filters);
            setServices(data.services || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchServices();
    }, []);

    const handleFilterChange = (e) => {
        setFilters({ ...filters, [e.target.name]: e.target.value });
    };

    const handleSearch = (e) => {
        e.preventDefault();
        fetchServices();
    };

    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>
            <h1 style={{ marginBottom: '2rem' }}>Browse Services</h1>

            {/* Filter Bar */}
            <form onSubmit={handleSearch} className="glass-panel" style={{ padding: '1.5rem', borderRadius: 'var(--radius-md)', marginBottom: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'end' }}>
                <div style={{ flex: 1, minWidth: '200px' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Category</label>
                    <select name="category" value={filters.category} onChange={handleFilterChange} style={{ width: '100%', padding: '0.5rem' }}>
                        <option value="">All Categories</option>
                        <option value="regular">Regular Cleaning</option>
                        <option value="deep">Deep Cleaning</option>
                        <option value="move_in_out">Move In/Out</option>
                    </select>
                </div>
                <div style={{ width: '120px' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Min Price</label>
                    <input type="number" name="min_price" value={filters.min_price} onChange={handleFilterChange} style={{ width: '100%', padding: '0.5rem' }} placeholder="₹0" />
                </div>
                <div style={{ width: '120px' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Max Price</label>
                    <input type="number" name="max_price" value={filters.max_price} onChange={handleFilterChange} style={{ width: '100%', padding: '0.5rem' }} placeholder="₹5000" />
                </div>
                <button type="submit" className="btn btn-primary" style={{ height: '38px', padding: '0 1.5rem' }}>
                    Search
                </button>
            </form>

            {loading ? (
                <div>Loading services...</div>
            ) : services.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '4rem' }}>
                    <p>No services found matching your criteria.</p>
                </div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                    gap: '2rem'
                }}>
                    {services.map(service => (
                        <ServiceCard key={service.id} service={service} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default ServiceList;
