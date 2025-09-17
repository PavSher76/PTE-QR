import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import RootLayout from '../app/layout'

// Mock Next.js components
jest.mock('next/font/google', () => ({
  Inter: () => ({
    className: 'inter-font'
  })
}))

// Mock NotificationContainer component
jest.mock('../components/NotificationContainer', () => {
  return function MockNotificationContainer() {
    return <div data-testid="notification-container">Notification Container</div>
  }
})

// Mock AppProvider and LanguageProvider
jest.mock('../lib/context', () => ({
  AppProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-provider">{children}</div>
  )
}))

jest.mock('../lib/i18n', () => ({
  LanguageProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="language-provider">{children}</div>
  )
}))

describe('RootLayout', () => {
  it('renders with correct HTML structure', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('applies Inter font class to body', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    
    const body = document.body
    expect(body).toHaveClass('inter-font')
  })

  it('sets correct HTML lang attribute', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    
    const html = document.documentElement
    expect(html).toHaveAttribute('lang', 'en')
  })

  it('renders all provider components', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    
    expect(screen.getByTestId('language-provider')).toBeInTheDocument()
    expect(screen.getByTestId('app-provider')).toBeInTheDocument()
    expect(screen.getByTestId('notification-container')).toBeInTheDocument()
  })

  it('applies correct CSS classes to main container', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    
    const container = screen.getByText('Test Content').closest('div')
    expect(container).toHaveClass('min-h-screen', 'bg-gradient-to-br', 'from-blue-50', 'to-indigo-100', 'dark:from-gray-900', 'dark:to-gray-800')
  })

  it('renders children correctly', () => {
    const TestChild = () => <div data-testid="test-child">Child Component</div>
    
    render(
      <RootLayout>
        <TestChild />
      </RootLayout>
    )
    
    expect(screen.getByTestId('test-child')).toBeInTheDocument()
    expect(screen.getByText('Child Component')).toBeInTheDocument()
  })

  it('renders multiple children', () => {
    render(
      <RootLayout>
        <div data-testid="child-1">Child 1</div>
        <div data-testid="child-2">Child 2</div>
        <div data-testid="child-3">Child 3</div>
      </RootLayout>
    )
    
    expect(screen.getByTestId('child-1')).toBeInTheDocument()
    expect(screen.getByTestId('child-2')).toBeInTheDocument()
    expect(screen.getByTestId('child-3')).toBeInTheDocument()
  })

  it('maintains provider hierarchy', () => {
    render(
      <RootLayout>
        <div data-testid="content">Content</div>
      </RootLayout>
    )
    
    const content = screen.getByTestId('content')
    const languageProvider = screen.getByTestId('language-provider')
    const appProvider = screen.getByTestId('app-provider')
    
    // Check that content is inside both providers
    expect(languageProvider).toContainElement(content)
    expect(appProvider).toContainElement(content)
  })

  it('renders notification container at the end', () => {
    render(
      <RootLayout>
        <div>Main Content</div>
      </RootLayout>
    )
    
    const notificationContainer = screen.getByTestId('notification-container')
    expect(notificationContainer).toBeInTheDocument()
  })

  it('handles empty children', () => {
    render(<RootLayout>{null}</RootLayout>)
    
    expect(screen.getByTestId('language-provider')).toBeInTheDocument()
    expect(screen.getByTestId('app-provider')).toBeInTheDocument()
  })

  it('handles undefined children', () => {
    render(<RootLayout>{undefined}</RootLayout>)
    
    expect(screen.getByTestId('language-provider')).toBeInTheDocument()
    expect(screen.getByTestId('app-provider')).toBeInTheDocument()
  })
})
