import axios from "axios";
import { useAuthStore } from "../store/authStore";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().access_token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = useAuthStore.getState().refresh_token;
      if (refresh) {
        try {
          const res = await axios.post("/api/auth/refresh", { refresh_token: refresh });
          useAuthStore.getState().setTokens(res.data.access_token, res.data.refresh_token);
          error.config.headers.Authorization = `Bearer ${res.data.access_token}`;
          return api.request(error.config);
        } catch {
          useAuthStore.getState().logout();
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  logout: () => api.post("/auth/logout"),
};

export const callsApi = {
  start: (phone_number?: string) => api.post("/calls/start", { phone_number }),
  end: (call_id: string) => api.post("/calls/end", { call_id }),
  history: (limit = 50) => api.get(`/calls/history?limit=${limit}`),
  get: (call_id: string) => api.get(`/calls/${call_id}`),
};

export const analysisApi = {
  emotions: (call_id: string) => api.get(`/analysis/emotions/${call_id}`),
  personality: (customer_id: string) => api.get(`/analysis/personality/${customer_id}`),
};

export const reportsApi = {
  daily: (date?: string) => api.get(`/reports/daily${date ? `?report_date=${date}` : ""}`),
  operator: (operator_id: string) => api.get(`/reports/operator/${operator_id}`),
};
