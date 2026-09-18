import { create } from "zustand"
import { persist } from "zustand/middleware"

export type AuthProvider = "password" | "google"

export type AuthSession = {
  token: string
  username: string
  displayName: string
  provider: AuthProvider
}

type AuthState = {
  session: AuthSession | null
  login: (session: AuthSession) => void
  logout: () => void
}

const STORAGE_KEY = "straight-classroom:session"

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      session: null,
      login: (session) => set({ session }),
      logout: () => set({ session: null }),
    }),
    {
      name: STORAGE_KEY,
      partialize: (state) => ({ session: state.session }),
    }
  )
)
