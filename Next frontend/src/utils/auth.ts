// utils/auth.ts

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

export const login = async (username: string, password: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/token/`, {
      username,
      password,
    });

    const { access, refresh } = response.data;

    // Save tokens to localStorage
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);

    // Decode token (JWT is base64 encoded)
    const tokenPayload = JSON.parse(atob(access.split('.')[1]));

    // Custom fields from backend token
    const isSuperUser = tokenPayload?.is_superuser === true;
    const isStaff = tokenPayload?.is_staff === true;

    localStorage.setItem('isSuperUser', JSON.stringify(isSuperUser));
    localStorage.setItem('isStaff', JSON.stringify(isStaff));

    return access;
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Login failed');
  }
};

export const refreshToken = async () => {
  try {
    const refresh = localStorage.getItem('refreshToken');
    const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
      refresh,
    });

    const { access } = response.data;
    localStorage.setItem('accessToken', access);

    // Re-extract roles
    const tokenPayload = JSON.parse(atob(access.split('.')[1]));
    localStorage.setItem('isSuperUser', JSON.stringify(tokenPayload?.is_superuser || false));
    localStorage.setItem('isStaff', JSON.stringify(tokenPayload?.is_staff || false));

    return access;
  } catch {
    throw new Error('Token refresh failed');
  }
};

export const logout = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('isSuperUser');
  localStorage.removeItem('isStaff');
};

export const getAccessToken = () => localStorage.getItem('accessToken');

export const isAuthenticated = () => !!getAccessToken();

export const isSuperUser = () => localStorage.getItem('isSuperUser') === 'true';

export const isAdmin = () => localStorage.getItem('isStaff') === 'true';
