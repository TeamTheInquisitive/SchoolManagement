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

let refreshPromise = null;

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
        // Single-flight: share one refresh across all concurrent 401s so we
        // don't fire multiple /refresh-token calls that race on token rotation.
        if (!refreshPromise) {
          refreshPromise = api.post(ENDPOINTS.auth.refreshToken).finally(() => { refreshPromise = null; });
        }
        await refreshPromise;
        return api(original);
      } catch {
        // Refresh genuinely failed — clear stale auth so we don't loop on /login.
        localStorage.removeItem('user');
        localStorage.removeItem('school_code');
        window.location.href = '/admin/login';
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
