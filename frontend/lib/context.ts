/**
 * Simple context providers
 */

'use client';

import React from 'react';

// Empty context for now - can be implemented later
export function AppProviders({ children }: { children: React.ReactNode }) {
  return React.createElement('div', null, children);
}

// Alias for compatibility
export const AppProvider = AppProviders;

// Placeholder hooks
export function useTheme() {
  return {
    theme: 'light' as const,
    toggleTheme: () => {}
  };
}

export function useLanguage() {
  return {
    language: 'ru' as const,
    setLanguage: (lang: string) => {}
  };
}

export function useNotifications() {
  return {
    notifications: [] as Array<{
      id: string;
      type: 'success' | 'error' | 'warning' | 'info';
      title: string;
      message: string;
      timestamp: number;
    }>,
    addNotification: (notification: any) => {},
    removeNotification: (id: string) => {},
    clearNotifications: () => {}
  };
}

export function useUser() {
  return {
    user: {
      username: 'demo_user',
      email: 'demo@example.com'
    },
    isAuthenticated: true,
    login: (credentials: any) => {},
    logout: () => {}
  };
}