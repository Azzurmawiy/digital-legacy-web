import axios from 'axios';

const API_URL = (import.meta.env.VITE_API_URL as string) || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT
apiClient.interceptors.request.use(
  (config) => {
    // DO NOT add token for login or register requests
    const isAuthRequest = config.url?.includes('/auth/login/') || config.url?.includes('/auth/register/');
    
    if (!isAuthRequest) {
      const token = localStorage.getItem('access_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors for expired tokens
    if (error.response?.status === 401 && !originalRequest._retry) {
      // If the error is specifically "token not valid", just log out immediately to clear the state
      const errorDetail = error.response?.data?.detail || "";
      if (errorDetail.includes("token not valid") || errorDetail.includes("invalid_token")) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Retry the original request
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // If refresh fails, log out
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
