/**
 * Context providers for the application
 */

'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'

// Theme context
const ThemeContext = createContext<{
  theme: 'light' | 'dark'
  toggleTheme: () => void
} | null>(null)

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
} | null>(null)

// User context
const UserContext = createContext<{
  user: {
    username: string
    email: string
    role: string
    isAdmin: boolean
  } | null
  isAuthenticated: boolean
  login: (credentials: { username: string; password: string }) => Promise<{ success: boolean; error?: string }>
  logout: () => void
} | null>(null)

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
    role: string
    isAdmin: boolean
  } | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const savedUser = localStorage.getItem('pte-qr-user')
    const savedToken = localStorage.getItem('pte-qr-token')
    if (savedUser && savedToken) {
      setUser(JSON.parse(savedUser))
      setIsAuthenticated(true)
    }
  }, [])

  const login = async (credentials: { username: string; password: string }) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (response.ok) {
        const data = await response.json()

        // Store token in localStorage
        localStorage.setItem('pte-qr-token', data.access_token)

        // Create user object
        const userData = {
          username: credentials.username,
          email: `${credentials.username}@example.com`,
          role: credentials.username === 'admin' ? 'admin' : 'user',
          isAdmin: credentials.username === 'admin',
        }

        setUser(userData)
        setIsAuthenticated(true)
        localStorage.setItem('pte-qr-user', JSON.stringify(userData))

        return { success: true }
      } else {
        const errorData = await response.json()
        return { success: false, error: errorData.detail || 'Login failed' }
      }
    } catch (error) {
      return { success: false, error: 'Network error' }
    }
  }

  const logout = async () => {
    try {
      const token = localStorage.getItem('pte-qr-token')
      if (token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      }
    } catch (error) {
      console.warn('Logout request failed:', error)
    } finally {
      setUser(null)
      setIsAuthenticated(false)
      localStorage.removeItem('pte-qr-user')
      localStorage.removeItem('pte-qr-token')
    }
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
