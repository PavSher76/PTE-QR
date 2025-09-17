import React from 'react'
import { render, screen, fireEvent, act } from '@testing-library/react'
import '@testing-library/jest-dom'
import {
  ThemeProvider,
  NotificationsProvider,
  UserProvider,
  AppProvider,
  useTheme,
  useNotifications,
  useUser,
} from '../lib/context'

// Test component that uses all contexts
function TestComponent() {
  const { theme, toggleTheme } = useTheme()
  const {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
  } = useNotifications()
  const { user, isAuthenticated, login, logout } = useUser()

  return (
    <div>
      <div data-testid="theme">{theme}</div>
      <button data-testid="toggle-theme" onClick={toggleTheme}>
        Toggle Theme
      </button>

      <div data-testid="notifications-count">{notifications.length}</div>
      <button
        data-testid="add-notification"
        onClick={() =>
          addNotification({
            type: 'info',
            title: 'Test',
            message: 'Test message',
          })
        }
      >
        Add Notification
      </button>
      <button data-testid="clear-notifications" onClick={clearNotifications}>
        Clear Notifications
      </button>

      <div data-testid="user-status">
        {isAuthenticated ? 'authenticated' : 'not authenticated'}
      </div>
      <div data-testid="username">{user?.username || 'no user'}</div>
      <button
        data-testid="login"
        onClick={() =>
          login({ username: 'testuser', email: 'test@example.com' })
        }
      >
        Login
      </button>
      <button data-testid="logout" onClick={logout}>
        Logout
      </button>
    </div>
  )
}

// Helper function to render with providers
const renderWithProviders = (
  component: React.ReactElement,
  providers: React.ComponentType<{ children: React.ReactNode }>[] = [
    AppProvider,
  ]
) => {
  let result = component
  providers.reverse().forEach((Provider) => {
    result = <Provider>{result}</Provider>
  })
  return render(result)
}

describe('Context Providers', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('ThemeProvider', () => {
    it('provides default light theme', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      expect(screen.getByTestId('theme')).toHaveTextContent('light')
    })

    it('toggles theme between light and dark', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      const toggleButton = screen.getByTestId('toggle-theme')

      expect(screen.getByTestId('theme')).toHaveTextContent('light')

      fireEvent.click(toggleButton)
      expect(screen.getByTestId('theme')).toHaveTextContent('dark')

      fireEvent.click(toggleButton)
      expect(screen.getByTestId('theme')).toHaveTextContent('light')
    })

    it('persists theme in localStorage', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      const toggleButton = screen.getByTestId('toggle-theme')
      fireEvent.click(toggleButton)

      expect(localStorage.getItem('pte-qr-theme')).toBe('dark')
    })

    it('loads theme from localStorage on mount', () => {
      localStorage.setItem('pte-qr-theme', 'dark')

      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      expect(screen.getByTestId('theme')).toHaveTextContent('dark')
    })
  })

  describe('NotificationsProvider', () => {
    it('provides empty notifications array initially', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      expect(screen.getByTestId('notifications-count')).toHaveTextContent('0')
    })

    it('adds notifications', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      const addButton = screen.getByTestId('add-notification')
      fireEvent.click(addButton)

      expect(screen.getByTestId('notifications-count')).toHaveTextContent('1')
    })

    it('clears all notifications', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      const addButton = screen.getByTestId('add-notification')
      const clearButton = screen.getByTestId('clear-notifications')

      fireEvent.click(addButton)
      fireEvent.click(addButton)
      expect(screen.getByTestId('notifications-count')).toHaveTextContent('2')

      fireEvent.click(clearButton)
      expect(screen.getByTestId('notifications-count')).toHaveTextContent('0')
    })

    it('adds notification with correct properties', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      const addButton = screen.getByTestId('add-notification')
      fireEvent.click(addButton)

      // Check that notification was added with correct properties
      expect(screen.getByTestId('notifications-count')).toHaveTextContent('1')
    })
  })

  describe('UserProvider', () => {
    it('provides unauthenticated state initially', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      expect(screen.getByTestId('user-status')).toHaveTextContent(
        'not authenticated'
      )
      expect(screen.getByTestId('username')).toHaveTextContent('no user')
    })

    it('logs in user', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      const loginButton = screen.getByTestId('login')
      fireEvent.click(loginButton)

      expect(screen.getByTestId('user-status')).toHaveTextContent(
        'authenticated'
      )
      expect(screen.getByTestId('username')).toHaveTextContent('testuser')
    })

    it('logs out user', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      const loginButton = screen.getByTestId('login')
      const logoutButton = screen.getByTestId('logout')

      fireEvent.click(loginButton)
      expect(screen.getByTestId('user-status')).toHaveTextContent(
        'authenticated'
      )

      fireEvent.click(logoutButton)
      expect(screen.getByTestId('user-status')).toHaveTextContent(
        'not authenticated'
      )
      expect(screen.getByTestId('username')).toHaveTextContent('no user')
    })

    it('persists user in localStorage', () => {
      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      const loginButton = screen.getByTestId('login')
      fireEvent.click(loginButton)

      expect(localStorage.getItem('pte-qr-user')).toBeTruthy()
    })

    it('loads user from localStorage on mount', () => {
      const userData = { username: 'saveduser', email: 'saved@example.com' }
      localStorage.setItem('pte-qr-user', JSON.stringify(userData))

      renderWithProviders(<TestComponent />, [ThemeProvider, NotificationsProvider, UserProvider])

      expect(screen.getByTestId('user-status')).toHaveTextContent(
        'authenticated'
      )
      expect(screen.getByTestId('username')).toHaveTextContent('saveduser')
    })
  })

  describe('AppProvider', () => {
    it('provides all contexts together', () => {
      renderWithProviders(<TestComponent />)

      // Check that all contexts are available
      expect(screen.getByTestId('theme')).toBeInTheDocument()
      expect(screen.getByTestId('notifications-count')).toBeInTheDocument()
      expect(screen.getByTestId('user-status')).toBeInTheDocument()
    })

    it('allows interaction between contexts', () => {
      renderWithProviders(<TestComponent />)

      // Login user
      fireEvent.click(screen.getByTestId('login'))
      expect(screen.getByTestId('user-status')).toHaveTextContent(
        'authenticated'
      )

      // Add notification
      fireEvent.click(screen.getByTestId('add-notification'))
      expect(screen.getByTestId('notifications-count')).toHaveTextContent('1')

      // Toggle theme
      fireEvent.click(screen.getByTestId('toggle-theme'))
      expect(screen.getByTestId('theme')).toHaveTextContent('dark')
    })
  })

  describe('Context Hooks Error Handling', () => {
    it('throws error when useTheme is used outside ThemeProvider', () => {
      const consoleSpy = jest
        .spyOn(console, 'error')
        .mockImplementation(() => {})

      function ThemeTestComponent() {
        const { theme } = useTheme()
        return <div data-testid="theme">{theme}</div>
      }

      expect(() => {
        render(<ThemeTestComponent />)
      }).toThrow('useTheme must be used within ThemeProvider')

      consoleSpy.mockRestore()
    })

    it('throws error when useNotifications is used outside NotificationsProvider', () => {
      const consoleSpy = jest
        .spyOn(console, 'error')
        .mockImplementation(() => {})

      function NotificationsTestComponent() {
        const { notifications } = useNotifications()
        return <div data-testid="notifications-count">{notifications.length}</div>
      }

      expect(() => {
        render(<NotificationsTestComponent />)
      }).toThrow('useNotifications must be used within NotificationsProvider')

      consoleSpy.mockRestore()
    })

    it('throws error when useUser is used outside UserProvider', () => {
      const consoleSpy = jest
        .spyOn(console, 'error')
        .mockImplementation(() => {})

      function UserTestComponent() {
        const { user } = useUser()
        return <div data-testid="user-status">{user ? 'authenticated' : 'not authenticated'}</div>
      }

      expect(() => {
        render(<UserTestComponent />)
      }).toThrow('useUser must be used within UserProvider')

      consoleSpy.mockRestore()
    })
  })
})
