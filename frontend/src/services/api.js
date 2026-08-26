import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Only redirect if not already on login/register page
      const isAuthPage = window.location.pathname.includes('/login') || window.location.pathname.includes('/register');
      if (!isAuthPage) {
        localStorage.removeItem('token');
        localStorage.removeItem('userName');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
