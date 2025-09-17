/**
 * Context providers for the application
 */

'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'

// Theme context
const ThemeContext = createContext<{
  theme: 'light' | 'dark'
  toggleTheme: () => void
}>({
  theme: 'light',
  toggleTheme: () => {},
})

// Notifications context
const NotificationsContext = createContext<{
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    title: string
    message: string
    timestamp: number
  }>
  addNotification: (
    notification: Omit<
      {
        id: string
        type: 'success' | 'error' | 'warning' | 'info'
        title: string
        message: string
        timestamp: number
      },
      'id' | 'timestamp'
    >
  ) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void
}>({
  notifications: [],
  addNotification: () => {},
  removeNotification: () => {},
  clearNotifications: () => {},
})

// User context
const UserContext = createContext<{
  user: {
    username: string
    email: string
  } | null
  isAuthenticated: boolean
  login: (credentials: any) => void
  logout: () => void
}>({
  user: null,
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
})

// Theme provider
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const savedTheme = localStorage.getItem('pte-qr-theme') as 'light' | 'dark'
    if (savedTheme) {
      setTheme(savedTheme)
    }
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('pte-qr-theme', newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

// Notifications provider
export function NotificationsProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const [notifications, setNotifications] = useState<
    Array<{
      id: string
      type: 'success' | 'error' | 'warning' | 'info'
      title: string
      message: string
      timestamp: number
    }>
  >([])

  const addNotification = (
    notification: Omit<
      {
        id: string
        type: 'success' | 'error' | 'warning' | 'info'
        title: string
        message: string
        timestamp: number
      },
      'id' | 'timestamp'
    >
  ) => {
    const newNotification = {
      ...notification,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: Date.now(),
    }
    setNotifications((prev) => [...prev, newNotification])
  }

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }

  const clearNotifications = () => {
    setNotifications([])
  }

  return (
    <NotificationsContext.Provider
      value={{
        notifications,
        addNotification,
        removeNotification,
        clearNotifications,
      }}
    >
      {children}
    </NotificationsContext.Provider>
  )
}

// User provider
export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<{
    username: string
    email: string
  } | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const savedUser = localStorage.getItem('pte-qr-user')
    if (savedUser) {
      setUser(JSON.parse(savedUser))
      setIsAuthenticated(true)
    }
  }, [])

  const login = (credentials: any) => {
    // Mock login - in real app would call API
    const mockUser = {
      username: credentials.username || 'demo_user',
      email: credentials.email || 'demo@example.com',
    }
    setUser(mockUser)
    setIsAuthenticated(true)
    localStorage.setItem('pte-qr-user', JSON.stringify(mockUser))
  }

  const logout = () => {
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('pte-qr-user')
  }

  return (
    <UserContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </UserContext.Provider>
  )
}

// Main app provider that combines all providers
export function AppProvider({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <NotificationsProvider>
        <UserProvider>{children}</UserProvider>
      </NotificationsProvider>
    </ThemeProvider>
  )
}

// Hooks to use contexts
export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}

export function useNotifications() {
  const context = useContext(NotificationsContext)
  if (!context) {
    throw new Error(
      'useNotifications must be used within NotificationsProvider'
    )
  }
  return context
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within UserProvider')
  }
  return context
}
