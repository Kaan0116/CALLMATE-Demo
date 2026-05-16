import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 5000,
});

export default api;

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  logout: () => Promise.resolve(),
};

export const callsApi = {
  start: (phone_number?: string) => api.post("/calls/start", { phone_number }),
  end: (call_id: string) => api.post("/calls/end", { call_id }),
  history: () => Promise.resolve({ data: [] }),
  get: (call_id: string) => api.get(`/calls/${call_id}`),
};

export const analysisApi = {
  emotions: (call_id: string) => api.get(`/analysis/emotions/${call_id}`),
  personality: (customer_id: string) => api.get(`/analysis/personality/${customer_id}`),
};

export const reportsApi = {
  daily: () => Promise.resolve({ data: null }),
  operator: (operator_id: string) => api.get(`/reports/operator/${operator_id}`),
};
