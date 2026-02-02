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

    // NOTE: Google OAuth callback is handled by GoogleCallback.jsx component
    // Do NOT handle it here to avoid duplicate code exchange attempts

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
        // URL encode the code to handle special characters
        const encodedCode = encodeURIComponent(code);
        const response = await api.get(`/auth/google/callback?code=${encodedCode}${state ? `&state=${encodeURIComponent(state)}` : ''}`);
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
