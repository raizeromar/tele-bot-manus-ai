import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for handling authentication cookies
});

// Auth API
export const authAPI = {
  login: (username, password) => 
    api.post('/users/login/', { username, password }),
  
  register: (username, email, password) => 
    api.post('/users/register/', { username, email, password }),
  
  logout: () => 
    api.post('/users/logout/'),
  
  getCurrentUser: () => 
    api.get('/users/me/'),
};

// Telegram Account API
export const accountAPI = {
  getAccounts: () => 
    api.get('/telegram/accounts/'),
  
  createAccount: (accountData) => 
    api.post('/telegram/accounts/', accountData),
  
  authenticate: (accountId) => 
    api.post(`/telegram/accounts/${accountId}/authenticate/`),
  
  verifyCode: (accountId, code, requestId) => 
    api.post(`/telegram/accounts/${accountId}/verify_code/`, { code, request_id: requestId }),
  
  toggleActive: (accountId) => 
    api.patch(`/telegram/accounts/${accountId}/`, { is_active: false }),
  
  deleteAccount: (accountId) => 
    api.delete(`/telegram/accounts/${accountId}/`),
};

// Telegram Group API
export const groupAPI = {
  getGroups: () => 
    api.get('/telegram/groups/'),
  
  joinGroup: (accountId, groupLink) => 
    api.post('/telegram/groups/join/', { account_id: accountId, group_link: groupLink }),
  
  collectMessages: (groupId, accountId, limit = 100) => 
    api.post(`/telegram/groups/${groupId}/collect_messages/`, { account_id: accountId, limit }),
  
  toggleActive: (groupId) => 
    api.patch(`/telegram/groups/${groupId}/`, { is_active: false }),
};

// Summary API
export const summaryAPI = {
  getSummaries: () => 
    api.get('/summaries/'),
  
  getSummaryById: (summaryId) => 
    api.get(`/summaries/${summaryId}/`),
  
  generateSummary: (groupId, days = 7) => 
    api.post('/summaries/generate/', { group_id: groupId, days }),
  
  provideFeedback: (summaryId, rating, comment = '') => 
    api.post('/feedback/', { summary: summaryId, rating, comment }),
};

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    // You could add auth token here if using token-based auth
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      // Redirect to login page or refresh token
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default api;
