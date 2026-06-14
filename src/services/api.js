import axios from 'axios';
import { API_BASE_URL, ENDPOINTS } from '../config/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const schoolCode = localStorage.getItem('school_code');
  if (schoolCode) config.headers['X-School-Code'] = schoolCode;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status === 401 &&
      !original._retry &&
      !original.url.includes(ENDPOINTS.auth.refreshToken) &&
      !original.url.includes(ENDPOINTS.auth.login)
    ) {
      original._retry = true;
      try {
        await api.post(ENDPOINTS.auth.refreshToken);
        return api(original);
      } catch {
        window.location.href = '/admin/login';
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
