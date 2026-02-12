import api from './api';

export const serviceService = {
    // Get all public services (search)
    searchServices: async (filters = {}) => {
        const params = new URLSearchParams(filters).toString();
        const response = await api.get(`/services/search?${params}`);
        return response.data;
    },

    // Get single service details
    getService: async (id) => {
        const response = await api.get(`/services/${id}`);
        return response.data;
    }
};
