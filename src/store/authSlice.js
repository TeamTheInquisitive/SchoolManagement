import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../services/api';
import { ENDPOINTS } from '../config/api';

export const login = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    localStorage.removeItem('school_code');
    const { data } = await api.post(ENDPOINTS.auth.login, { ...credentials, portal: 'admin' });
    // Secondary frontend check: ensure role matches this portal
    if (data.user?.role !== 'admin') {
      return rejectWithValue({ error: "This account doesn't have access to this portal. Please use the correct portal." });
    }
    localStorage.setItem('user', JSON.stringify(data.user));
    if (data.user?.school_code) localStorage.setItem('school_code', data.user.school_code);
    return data.user;
  } catch (err) {
    return rejectWithValue(err.response?.data || { error: 'Login failed' });
  }
});

export const fetchMe = createAsyncThunk('auth/fetchMe', async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get(ENDPOINTS.auth.me);
    localStorage.setItem('user', JSON.stringify(data));
    return data;
  } catch (err) {
    localStorage.removeItem('user');
    return rejectWithValue(err.response?.data);
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    loading: false,
    error: null,
  },
  reducers: {
    logout(state) {
      state.user = null;
      localStorage.removeItem('user');
      localStorage.removeItem('school_code');
      localStorage.removeItem('admin-sidebar-collapsed');
      document.cookie.split(';').forEach(c => { document.cookie = c.trim().split('=')[0] + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'; });
      api.post(ENDPOINTS.auth.logout).catch(() => {});
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(login.fulfilled, (state, action) => { state.loading = false; state.user = action.payload; })
      .addCase(login.rejected, (state, action) => { state.loading = false; state.error = action.payload?.error || 'Login failed'; })
      .addCase(fetchMe.fulfilled, (state, action) => { state.user = action.payload; })
      .addCase(fetchMe.rejected, (state) => { state.user = null; });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
