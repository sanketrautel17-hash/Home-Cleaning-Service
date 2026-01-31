import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div style={{ position: 'relative', overflow: 'hidden' }}>

            {/* Hero Section */}
            <div className="container" style={{ padding: '8rem 1rem', textAlign: 'center' }}>
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                    <h1 style={{
                        fontSize: '3.5rem',
                        fontWeight: 800,
                        lineHeight: 1.2,
                        marginBottom: '2rem',
                        background: 'linear-gradient(to right, #fff, #94a3b8)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent'
                    }}>
                        Premium Home Cleaning needed for modern lifestyles
                    </h1>
                    <p style={{
                        fontSize: '1.25rem',
                        color: 'var(--text-muted)',
                        marginBottom: '3rem',
                        lineHeight: 1.8
                    }}>
                        Connect with top-rated cleaning professionals for a spotless home.
                        Trusted by thousands of homeowners for reliable, high-quality service.
                    </p>
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                        <Link to="/register" className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1.125rem' }}>
                            Find a Cleaner
                        </Link>
                        <Link to="/register" className="btn btn-secondary" style={{ padding: '1rem 2rem', fontSize: '1.125rem' }}>
                            Become a Cleaner
                        </Link>
                    </div>
                </div>
            </div>

            {/* Features Grid */}
            <div className="container" style={{ paddingBottom: '8rem' }}>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '2rem'
                }}>
                    {[
                        { title: "Verified Professionals", desc: "All cleaners undergo strict background checks and vetting processes." },
                        { title: "Secure Payments", desc: "Pay safely online only after the service is completed to your satisfaction." },
                        { title: "Satisfaction Guarantee", desc: "Not happy? We'll re-clean for free until you're satisfied." }
                    ].map((feature, i) => (
                        <div key={i} className="glass-panel" style={{ padding: '2rem', borderRadius: 'var(--radius-lg)' }}>
                            <h3 style={{ color: 'var(--primary)', marginBottom: '1rem' }}>{feature.title}</h3>
                            <p style={{ color: 'var(--text-muted)' }}>{feature.desc}</p>
                        </div>
                    ))}
                </div>
            </div>

        </div>
    );
};

export default Home;
