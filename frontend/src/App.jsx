import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import GoogleCallback from './pages/GoogleCallback';
import VerifyEmail from './pages/VerifyEmail';

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
