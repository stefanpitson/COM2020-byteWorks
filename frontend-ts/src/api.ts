import axios from 'axios';

const api = axios.create({
  // This is the URL of your Python (FastAPI/Flask/Django) server
  baseURL: 'http://localhost:8000', 
  timeout: 5000, // 5 seconds before giving up
  headers: {
    'Content-Type': 'application/json',
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    // Attach the token to the headers
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;