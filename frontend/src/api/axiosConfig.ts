import axios from "axios";
import { clearAuthSession } from "../utils/authSession";

const api = axios.create({
  baseURL: "/api",
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (
      token &&
      config.url !== "/login" &&
      config.url !== "/customer/signup" &&
      config.url !== "/vendor/signup"
    ) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Session expired. Redirecting to login...");

      clearAuthSession()

      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
