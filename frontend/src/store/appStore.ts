import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';

interface AppState {
  connectionStatus: ConnectionStatus;
  lastMessage: any;
  user: {
    id: string;
    email: string;
    name: string;
  } | null;
  theme: 'light' | 'dark' | 'system';
  notifications: {
    enabled: boolean;
    sound: boolean;
    desktop: boolean;
  };
  trading: {
    autoTrading: boolean;
    riskLevel: 'low' | 'medium' | 'high';
    maxPositionSize: number;
  };
}

interface AppActions {
  setConnectionStatus: (status: ConnectionStatus) => void;
  setLastMessage: (message: any) => void;
  setUser: (user: AppState['user']) => void;
  setTheme: (theme: AppState['theme']) => void;
  updateNotifications: (notifications: Partial<AppState['notifications']>) => void;
  updateTrading: (trading: Partial<AppState['trading']>) => void;
  logout: () => void;
}

export const useAppStore = create<AppState & AppActions>()(
  persist(
    (set) => ({
      // Initial state
      connectionStatus: 'disconnected',
      lastMessage: null,
      user: null,
      theme: 'system',
      notifications: {
        enabled: true,
        sound: true,
        desktop: true,
      },
      trading: {
        autoTrading: false,
        riskLevel: 'medium',
        maxPositionSize: 1000,
      },

      // Actions
      setConnectionStatus: (status) => set({ connectionStatus: status }),
      setLastMessage: (message) => set({ lastMessage: message }),
      setUser: (user) => set({ user }),
      setTheme: (theme) => set({ theme }),
      updateNotifications: (notifications) =>
        set((state) => ({
          notifications: { ...state.notifications, ...notifications },
        })),
      updateTrading: (trading) =>
        set((state) => ({
          trading: { ...state.trading, ...trading },
        })),
      logout: () =>
        set({
          user: null,
          connectionStatus: 'disconnected',
          lastMessage: null,
        }),
    }),
    {
      name: 'app-storage',
      partialize: (state) => ({
        user: state.user,
        theme: state.theme,
        notifications: state.notifications,
        trading: state.trading,
      }),
    }
  )
);