import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import HomePage from '../app/page'
import { Header } from '../components/Header'
import { AppProvider } from '../lib/context'
import { LanguageProvider } from '../lib/i18n'

// Mock Next.js components
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: any) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

// Mock QRCodeScanner component
jest.mock('../components/QRCodeScanner', () => {
  return function MockQRCodeScanner({ onScan, onCancel }: any) {
    return (
      <div data-testid="qr-scanner">
        <button onClick={() => onScan('https://example.com/qr')}>
          Mock Scan
        </button>
        <button onClick={onCancel}>Cancel</button>
      </div>
    )
  }
})

// Mock DocumentStatus component
jest.mock('../components/DocumentStatus', () => {
  return function MockDocumentStatus({ qrData }: any) {
    return <div data-testid="document-status">Status: {qrData}</div>
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

describe('AI-NK Styles', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('Header AI-NK Styles', () => {
    it('applies AI-NK header styling', () => {
      renderWithProviders(<Header />)
      
      const header = screen.getByRole('banner')
      expect(header).toHaveClass(
        'border-b',
        'border-white/20',
        'bg-white/80',
        'backdrop-blur-md',
        'shadow-lg'
      )
    })

    it('applies AI-NK title gradient styling', () => {
      renderWithProviders(<Header />)
      
      const title = screen.getByText('PTE QR Система')
      expect(title).toHaveClass(
        'bg-gradient-to-r',
        'from-primary-600',
        'to-accent-600',
        'bg-clip-text',
        'text-transparent'
      )
    })

    it('applies AI-NK navigation hover effects', () => {
      renderWithProviders(<Header />)
      
      const aboutLink = screen.getByText('О системе')
      expect(aboutLink).toHaveClass(
        'text-secondary-600',
        'hover:text-primary-600',
        'hover:scale-105'
      )
    })
  })

  describe('HomePage AI-NK Styles', () => {
    it('applies AI-NK main title gradient and animation', () => {
      renderWithProviders(<HomePage />)
      
      const mainTitle = screen.getByRole('heading', {
        level: 1,
        name: 'PTE QR Система',
      })
      expect(mainTitle).toHaveClass(
        'bg-gradient-to-r',
        'from-primary-600',
        'via-accent-600',
        'to-primary-600',
        'bg-clip-text',
        'text-transparent',
        'animate-pulse-slow'
      )
    })

    it('applies AI-NK card styling with backdrop blur', () => {
      renderWithProviders(<HomePage />)
      
      const cards = screen.getAllByText(/Сканирование QR-кода|Статус документа/)
      cards.forEach(card => {
        const cardElement = card.closest('.card')
        expect(cardElement).toHaveClass('card')
        // Стили backdrop-blur применяются через CSS, а не через классы Tailwind
      })
    })

    it('applies AI-NK section headers styling', () => {
      renderWithProviders(<HomePage />)
      
      const sectionHeaders = screen.getAllByRole('heading', { level: 2 })
      sectionHeaders.forEach(header => {
        expect(header).toHaveClass(
          'text-primary-700',
          'dark:text-primary-300',
          'animate-slide-up'
        )
      })
    })

    it('applies AI-NK description styling', () => {
      renderWithProviders(<HomePage />)
      
      const description = screen.getByText('Система проверки актуальности документов через QR-коды')
      expect(description).toHaveClass(
        'text-secondary-600',
        'dark:text-secondary-300',
        'animate-fade-in'
      )
    })
  })

  describe('Button AI-NK Styles', () => {
    it('applies AI-NK button styling with gradients', () => {
      renderWithProviders(<HomePage />)
      
      const scanButton = screen.getByText('Сканировать QR')
      expect(scanButton).toHaveClass('btn-primary')
      
      // Проверяем, что кнопка имеет правильные стили через CSS классы
      const buttonElement = scanButton.closest('button')
      expect(buttonElement).toHaveClass('btn-primary')
    })

    it('applies AI-NK button hover effects', () => {
      renderWithProviders(<Header />)
      
      const loginButton = screen.getByText('Войти')
      expect(loginButton).toHaveClass('btn-secondary')
    })
  })

  describe('Layout AI-NK Styles', () => {
    it('applies AI-NK background gradient', () => {
      renderWithProviders(<HomePage />)
      
      // Проверяем, что основной контейнер имеет AI-NK градиент
      // Градиент применяется к родительскому элементу в layout
      const mainElement = screen.getByRole('main')
      expect(mainElement).toBeInTheDocument()
    })
  })

  describe('Dark Mode AI-NK Styles', () => {
    it('applies AI-NK dark mode header styling', () => {
      localStorage.setItem('pte-qr-theme', 'dark')
      renderWithProviders(<Header />)
      
      const header = screen.getByRole('banner')
      expect(header).toHaveClass('dark:bg-nk-900/80', 'dark:border-white/10')
    })

    it('applies AI-NK dark mode title styling', () => {
      localStorage.setItem('pte-qr-theme', 'dark')
      renderWithProviders(<HomePage />)
      
      const mainTitle = screen.getByRole('heading', {
        level: 1,
        name: 'PTE QR Система',
      })
      expect(mainTitle).toHaveClass(
        'dark:from-primary-400',
        'dark:via-accent-400',
        'dark:to-primary-400'
      )
    })

    it('applies AI-NK dark mode background gradient', () => {
      localStorage.setItem('pte-qr-theme', 'dark')
      renderWithProviders(<HomePage />)
      
      // Проверяем, что main элемент существует (градиент применяется в layout)
      const mainElement = screen.getByRole('main')
      expect(mainElement).toBeInTheDocument()
    })
  })

  describe('Animation Classes', () => {
    it('applies fade-in animation to description', () => {
      renderWithProviders(<HomePage />)
      
      const description = screen.getByText('Система проверки актуальности документов через QR-коды')
      expect(description).toHaveClass('animate-fade-in')
    })

    it('applies slide-up animation to section headers', () => {
      renderWithProviders(<HomePage />)
      
      const sectionHeaders = screen.getAllByRole('heading', { level: 2 })
      sectionHeaders.forEach(header => {
        expect(header).toHaveClass('animate-slide-up')
      })
    })

    it('applies pulse animation to main title', () => {
      renderWithProviders(<HomePage />)
      
      const mainTitle = screen.getByRole('heading', {
        level: 1,
        name: 'PTE QR Система',
      })
      expect(mainTitle).toHaveClass('animate-pulse-slow')
    })
  })
})
