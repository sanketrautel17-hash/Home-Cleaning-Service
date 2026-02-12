import api from './api';

export const bookingService = {
    // Create Booking
    createBooking: async (data) => {
        const response = await api.post('/bookings', data);
        return response.data;
    },

    // Get Booking Details
    getBooking: async (id) => {
        const response = await api.get(`/bookings/${id}`);
        return response.data;
    },

    // Customer: Get My Bookings
    getMyBookings: async () => {
        const response = await api.get('/bookings/my-bookings');
        return response.data;
    },

    // Cleaner: Get Incoming Requests
    getCleanerBookings: async () => {
        const response = await api.get('/bookings/cleaner');
        return response.data;
    },

    // Update Status (Accept/Reject/Complete/Start)
    updateStatus: async (id, status) => {
        const response = await api.patch(`/bookings/${id}/status`, null, {
            params: { status }
        });
        return response.data;
    }
};
