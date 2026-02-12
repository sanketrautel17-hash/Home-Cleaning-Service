import api from './api';

export const paymentService = {
    // Initiate Booking Payment
    initiatePayment: async (data) => {
        const response = await api.post('/payments/initiate', data);
        return response.data;
    },

    // Verify Payment (Mock, happens on success page)
    verifyPayment: async (paymentId) => {
        const response = await api.post(`/payments/verify/${paymentId}`);
        return response.data;
    },

    // Check Payment Status
    getPaymentStatus: async (bookingId) => {
        const response = await api.get(`/payments/status/${bookingId}`);
        return response.data;
    }
};
