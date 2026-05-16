import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "../types";

interface AuthStore {
  user: User | null;
  access_token: string | null;
  refresh_token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, access_token: string, refresh_token: string) => void;
  setTokens: (access_token: string, refresh_token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      access_token: null,
      refresh_token: null,
      isAuthenticated: false,
      setAuth: (user, access_token, refresh_token) =>
        set({ user, access_token, refresh_token, isAuthenticated: true }),
      setTokens: (access_token, refresh_token) => set({ access_token, refresh_token }),
      logout: () => set({ user: null, access_token: null, refresh_token: null, isAuthenticated: false }),
    }),
    { name: "callmate-auth", partialize: (s) => ({ access_token: s.access_token, refresh_token: s.refresh_token, user: s.user, isAuthenticated: s.isAuthenticated }) }
  )
);
