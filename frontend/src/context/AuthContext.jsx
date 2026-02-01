import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is logged in
        const checkAuth = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    const response = await api.get('/auth/me');
                    setUser(response.data.user);
                } catch (error) {
                    console.error("Auth check failed", error);
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            }
            setLoading(false);
        };

        checkAuth();
    }, []);

    // Handle Google OAuth callback
    useEffect(() => {
        const handleGoogleCallback = async () => {
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            const state = urlParams.get('state');

            // Check if this is a Google OAuth callback
            if (code && window.location.pathname.includes('google-callback')) {
                try {
                    const response = await api.get(`/auth/google/callback?code=${code}${state ? `&state=${state}` : ''}`);
                    const { user, tokens } = response.data;

                    localStorage.setItem('access_token', tokens.access_token);
                    localStorage.setItem('refresh_token', tokens.refresh_token);
                    setUser(user);

                    // Redirect to dashboard
                    window.location.href = '/dashboard';
                } catch (error) {
                    console.error("Google login failed", error);
                    window.location.href = '/login?error=google_login_failed';
                }
            }
        };

        handleGoogleCallback();
    }, []);

    const login = async (email, password) => {
        const response = await api.post('/auth/login', { email, password });
        const { user, tokens } = response.data;

        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        setUser(user);
        return user;
    };

    const register = async (userData) => {
        const response = await api.post('/auth/register', userData);

        // Check if registration returned tokens (auto-login enabled)
        if (response.data.tokens) {
            const { user, tokens } = response.data;
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);
            setUser(user);
            return user;
        }

        // Otherwise return the response (message)
        return response.data;
    };

    // Google OAuth login - redirect to Google
    const loginWithGoogle = async () => {
        try {
            const response = await api.get('/auth/google/login');
            const { url } = response.data;

            // Redirect to Google OAuth page
            window.location.href = url;
        } catch (error) {
            console.error("Failed to get Google login URL", error);
            throw error;
        }
    };

    // Handle Google OAuth callback (for direct API call if needed)
    const handleGoogleCallback = async (code, state) => {
        const response = await api.get(`/auth/google/callback?code=${code}${state ? `&state=${state}` : ''}`);
        const { user, tokens } = response.data;

        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        setUser(user);
        return user;
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{
            user,
            login,
            register,
            logout,
            loading,
            loginWithGoogle,
            handleGoogleCallback
        }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
