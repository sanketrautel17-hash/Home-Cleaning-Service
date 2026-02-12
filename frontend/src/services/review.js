import api from './api';

export const reviewService = {
    // Create Review
    createReview: async (data) => {
        const response = await api.post('/reviews', data);
        return response.data;
    },

    // Get Reviews for Cleaner (Public)
    getCleanerReviews: async (cleanerId) => {
        const response = await api.get(`/reviews/cleaner/${cleanerId}`);
        return response.data;
    }
};
