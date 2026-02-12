import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import GoogleCallback from './pages/GoogleCallback';
import VerifyEmail from './pages/VerifyEmail';

import CreateService from './pages/CreateService';
import MyServices from './pages/MyServices';

import CleanerOnboarding from './pages/CleanerOnboarding';

import ServiceList from './pages/ServiceList';
import BookService from './pages/BookService';
import MyBookings from './pages/MyBookings';
import CleanerBookings from './pages/CleanerBookings';
import ReviewBooking from './pages/ReviewBooking';
import PaymentPage from './pages/PaymentPage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          <Navbar />
          <main style={{ flex: 1 }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/cleaner-onboarding" element={<CleanerOnboarding />} />
              <Route path="/my-services" element={<MyServices />} />
              <Route path="/create-service" element={<CreateService />} />

              {/* Customer Routes */}
              <Route path="/search" element={<ServiceList />} />
              <Route path="/book/:id" element={<BookService />} />
              <Route path="/my-bookings" element={<MyBookings />} />
              <Route path="/review/:id" element={<ReviewBooking />} />
              <Route path="/payment/:id" element={<PaymentPage />} />

              {/* Cleaner Routes */}
              <Route path="/cleaner-jobs" element={<CleanerBookings />} />

              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/google-callback" element={<GoogleCallback />} />
              {/* Also handle the API callback redirect path */}
              <Route path="/api/auth/google/callback" element={<GoogleCallback />} />
            </Routes>
          </main>

          <footer style={{
            padding: '2rem',
            textAlign: 'center',
            color: 'var(--text-muted)',
            borderTop: '1px solid var(--border)',
            marginTop: 'auto'
          }}>
            <p>&copy; {new Date().getFullYear()} Home Cleaning Service. All rights reserved.</p>
          </footer>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
