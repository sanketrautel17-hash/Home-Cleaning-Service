import api from './api';

export const cleanerService = {
    // Profile Management
    createProfile: async (data) => {
        const response = await api.post('/cleaners/profile', data);
        return response.data;
    },

    getProfile: async () => {
        const response = await api.get('/cleaners/profile/me');
        return response.data;
    },

    updateProfile: async (data) => {
        const response = await api.put('/cleaners/profile', data);
        return response.data;
    },

    // Service Management
    createService: async (data) => {
        const response = await api.post('/services/', data);
        return response.data;
    },

    getMyServices: async () => {
        const response = await api.get('/services/me');
        return response.data;
    },

    // For customers to find services
    searchCleaners: async (filters) => {
        const params = new URLSearchParams(filters).toString();
        const response = await api.get(`/cleaners?${params}`);
        return response.data;
    }
};
