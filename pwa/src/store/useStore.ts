import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { AppState } from '../types'

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      settings: {
        apiUrl: 'http://localhost:8000',
        darkMode: false,
      },
      currentCase: null,
      currentDiagnosis: null,
      caseHistory: [],
      isLoading: false,
      error: null,
      sidebarOpen: true,

      setSettings: (s) =>
        set((state) => ({ settings: { ...state.settings, ...s } })),

      setCurrentCase: (c) => set({ currentCase: c }),
      setCurrentDiagnosis: (d) => set({ currentDiagnosis: d }),

      addToHistory: (c, d) =>
        set((state) => ({
          caseHistory: [{ case: c, diagnosis: d }, ...state.caseHistory].slice(0, 100),
        })),

      setLoading: (l) => set({ isLoading: l }),
      setError: (e) => set({ error: e }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      toggleDarkMode: () =>
        set((state) => {
          const next = !state.settings.darkMode
          if (next) document.documentElement.classList.add('dark')
          else document.documentElement.classList.remove('dark')
          return { settings: { ...state.settings, darkMode: next } }
        }),
    }),
    {
      name: 'vetriage-storage',
      partialize: (state) => ({
        settings: state.settings,
        caseHistory: state.caseHistory,
      }),
    }
  )
)
