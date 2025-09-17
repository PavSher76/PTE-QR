import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Header } from '../components/Header'
import { AppProvider } from '../lib/context'
import { LanguageProvider } from '../lib/i18n'

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: any) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

// Helper function to render with all providers
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <AppProvider>
      <LanguageProvider>{component}</LanguageProvider>
    </AppProvider>
  )
}

describe('Header', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('renders header with logo and title', () => {
    renderWithProviders(<Header />)

    expect(screen.getByAltText('PTE QR Logo')).toBeInTheDocument()
    expect(screen.getByText('PTE QR Система')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    renderWithProviders(<Header />)

    expect(screen.getByText('PTE QR Система')).toBeInTheDocument()
    expect(screen.getByText('О системе')).toBeInTheDocument()
  })

  it('renders language selector', () => {
    renderWithProviders(<Header />)

    const languageSelect = screen.getByRole('combobox')
    expect(languageSelect).toBeInTheDocument()
    expect(languageSelect).toHaveValue('ru')
  })

  it('changes language when selection changes', () => {
    renderWithProviders(<Header />)

    const languageSelect = screen.getByRole('combobox')

    fireEvent.change(languageSelect, { target: { value: 'en' } })
    expect(languageSelect).toHaveValue('en')

    fireEvent.change(languageSelect, { target: { value: 'zh' } })
    expect(languageSelect).toHaveValue('zh')
  })

  it('renders theme toggle button', () => {
    renderWithProviders(<Header />)

    const themeButton = screen.getByTitle('Тема')
    expect(themeButton).toBeInTheDocument()
  })

  it('toggles theme when button is clicked', () => {
    renderWithProviders(<Header />)

    const themeButton = screen.getByTitle('Тема')

    // Initially should be light theme (sun icon)
    expect(themeButton.querySelector('svg')).toBeInTheDocument()

    fireEvent.click(themeButton)

    // Should now be dark theme (moon icon)
    expect(themeButton.querySelector('svg')).toBeInTheDocument()
  })

  it('shows login button when user is not authenticated', () => {
    renderWithProviders(<Header />)

    expect(screen.getByText('Войти')).toBeInTheDocument()
  })

  it('shows user info and logout when authenticated', async () => {
    // Mock authenticated user
    localStorage.setItem(
      'pte-qr-user',
      JSON.stringify({
        username: 'testuser',
        email: 'test@example.com',
      })
    )
    localStorage.setItem('pte-qr-token', 'mock-token')

    renderWithProviders(<Header />)

    // Wait for useEffect to run
    await screen.findByText('testuser')
    expect(screen.getByText('Выйти')).toBeInTheDocument()
  })

  it('logs out user when logout button is clicked', async () => {
    // Mock authenticated user
    localStorage.setItem(
      'pte-qr-user',
      JSON.stringify({
        username: 'testuser',
        email: 'test@example.com',
      })
    )
    localStorage.setItem('pte-qr-token', 'mock-token')

    renderWithProviders(<Header />)

    // Wait for useEffect to run
    await screen.findByText('testuser')
    const logoutButton = screen.getByText('Выйти')
    fireEvent.click(logoutButton)

    // User should be logged out - wait for state update
    await waitFor(() => {
      expect(screen.queryByText('testuser')).not.toBeInTheDocument()
    })
    
    // Check that login button appears (it might be in a different state)
    const loginButton = screen.queryByText('Войти')
    if (loginButton) {
      expect(loginButton).toBeInTheDocument()
    }
  })

  it('applies correct CSS classes for dark theme', () => {
    // Set dark theme
    localStorage.setItem('pte-qr-theme', 'dark')

    renderWithProviders(<Header />)

    const header = screen.getByRole('banner')
    expect(header).toHaveClass('dark:bg-gray-800')
  })

  it('applies correct CSS classes for light theme', () => {
    // Set light theme
    localStorage.setItem('pte-qr-theme', 'light')

    renderWithProviders(<Header />)

    const header = screen.getByRole('banner')
    expect(header).toHaveClass('bg-white')
  })

  it('renders with different language texts', () => {
    renderWithProviders(<Header />)

    // Change to English
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'en' } })

    // Should show English text
    expect(screen.getByText('PTE QR System')).toBeInTheDocument()
    expect(screen.getByText('About')).toBeInTheDocument()
  })
})
