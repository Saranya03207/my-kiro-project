/**
 * Authentication and Session Management
 */

import apiClient, { ApiError } from './api.js';
import { showToast } from './utils.js';

const STORAGE_KEYS = {
  TOKEN: 'canteen_session_token',
  USER_ID: 'canteen_user_id',
  ROLE: 'canteen_user_role'
};

export class AuthService {
  static getToken() {
    return sessionStorage.getItem(STORAGE_KEYS.TOKEN);
  }

  static getUser() {
    const id = sessionStorage.getItem(STORAGE_KEYS.USER_ID) || '';
    const role = sessionStorage.getItem(STORAGE_KEYS.ROLE) || '';
    return {
      userId: id,
      user_id: id,
      role: role
    };
  }

  static isAuthenticated() {
    return !!this.getToken();
  }

  static async login(userId, role) {
    const trimmedId = (userId || '').trim();
    if (!trimmedId) {
      showToast('Please enter your User ID', 'warning');
      return false;
    }
    if (!role || !['student', 'admin'].includes(role)) {
      showToast('Please select a valid role', 'warning');
      return false;
    }

    try {
      this.clearSession();
      const response = await apiClient.login(trimmedId, role);
      
      if (response && response.token) {
        sessionStorage.setItem(STORAGE_KEYS.TOKEN, response.token);
        sessionStorage.setItem(STORAGE_KEYS.USER_ID, response.user_id || trimmedId);
        sessionStorage.setItem(STORAGE_KEYS.ROLE, response.role || role);
        return true;
      }
      throw new Error('Authentication did not return a session token');
    } catch (error) {
      console.error('Login failed:', error);
      showToast(error.message || 'Login failed. Please check credentials.', 'error');
      return false;
    }
  }

  static async logout() {
    try {
      if (this.getToken()) {
        await apiClient.logout();
      }
    } catch (err) {
      console.warn('Backend logout call completed with note:', err);
    } finally {
      this.clearSession();
      window.location.href = 'index.html';
    }
  }

  static clearSession() {
    sessionStorage.removeItem(STORAGE_KEYS.TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.USER_ID);
    sessionStorage.removeItem(STORAGE_KEYS.ROLE);
  }

  static requireAuth(requiredRole = null) {
    const { userId, role } = this.getUser();
    const token = this.getToken();

    if (!token || !userId) {
      this.clearSession();
      window.location.href = 'index.html';
      return false;
    }

    if (requiredRole && role !== requiredRole) {
      if (role === 'student' && requiredRole === 'admin') {
        window.location.href = 'student.html';
        return false;
      }
    }

    // Populate user greeting if present
    const greetingEl = document.getElementById('userGreeting');
    if (greetingEl) {
      greetingEl.textContent = userId;
    }
    const avatarEl = document.getElementById('userAvatar');
    if (avatarEl) {
      avatarEl.textContent = userId.charAt(0).toUpperCase();
    }

    return true;
  }

  static checkGuest() {
    const { role } = this.getUser();
    const token = this.getToken();
    if (token && role) {
      if (role === 'admin') {
        window.location.href = 'admin.html';
      } else {
        window.location.href = 'student.html';
      }
    }
  }
}

export default AuthService;
