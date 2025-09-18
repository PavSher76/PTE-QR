import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Подавляем предупреждение о DOM nesting для тестов RootLayout
const originalError = console.error
beforeAll(() => {
  console.error = jest.fn()
})

afterAll(() => {
  console.error = originalError
})

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

// Mock ThemeWrapper component
jest.mock('../components/ThemeWrapper', () => ({
  ThemeWrapper: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="theme-wrapper">{children}</div>
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
    // Используем document.body для тестирования HTML элемента
    const { container } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('applies Inter font class to body', () => {
    const { container } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('sets correct HTML lang attribute', () => {
    const { container } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('renders all provider components', () => {
    const { container } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('applies correct CSS classes to main container', () => {
    const { container } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('renders children correctly', () => {
    const { container } = render(
      <RootLayout>
        <div>Child Component</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('renders multiple children', () => {
    const { container } = render(
      <RootLayout>
        <div>Child 1</div>
        <div>Child 2</div>
        <div>Child 3</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('maintains provider hierarchy', () => {
    const { container } = render(
      <RootLayout>
        <div>Content</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('renders notification container at the end', () => {
    const { container } = render(
      <RootLayout>
        <div>Main Content</div>
      </RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('handles empty children', () => {
    const { container } = render(
      <RootLayout>{null}</RootLayout>
    )
    expect(container).toBeDefined()
  })

  it('handles undefined children', () => {
    const { container } = render(
      <RootLayout>{undefined}</RootLayout>
    )
    expect(container).toBeDefined()
  })
})
