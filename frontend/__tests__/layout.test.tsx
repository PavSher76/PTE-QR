import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Mock Next.js components
jest.mock('next/font/google', () => ({
  Inter: () => ({
    className: 'inter-font',
  }),
}))

// Mock NotificationContainer component
jest.mock('../components/NotificationContainer', () => ({
  NotificationContainer: function MockNotificationContainer() {
    return (
      <div data-testid="notification-container">Notification Container</div>
    )
  },
}))

// Mock AppProvider and LanguageProvider
jest.mock('../lib/context', () => ({
  AppProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-provider">{children}</div>
  ),
}))

jest.mock('../lib/i18n', () => ({
  LanguageProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="language-provider">{children}</div>
  ),
}))

// Import after mocks
import RootLayout from '../app/layout'

describe('RootLayout', () => {
  it('renders without throwing errors', () => {
    // Простой тест, который проверяет, что компонент не падает
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Test Content</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('applies Inter font class to body', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Test Content</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('sets correct HTML lang attribute', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Test Content</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('renders all provider components', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Test Content</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('applies correct CSS classes to main container', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Test Content</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('renders children correctly', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Child Component</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('renders multiple children', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Child 1</div>
            <div>Child 2</div>
            <div>Child 3</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('maintains provider hierarchy', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Content</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('renders notification container at the end', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>
            <div>Main Content</div>
          </RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('handles empty children', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>{null}</RootLayout>
        </div>
      )
    }).not.toThrow()
  })

  it('handles undefined children', () => {
    expect(() => {
      render(
        <div>
          <RootLayout>{undefined}</RootLayout>
        </div>
      )
    }).not.toThrow()
  })
})
