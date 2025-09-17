import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import HomePage from '../app/page'
import { AppProvider } from '../lib/context'
import { LanguageProvider } from '../lib/i18n'

// Mock Next.js components
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: any) {
    return <a href={href} {...props}>{children}</a>
  }
})

// Mock QRCodeScanner component
jest.mock('../components/QRCodeScanner', () => {
  return function MockQRCodeScanner({ onScan, onCancel }: any) {
    return (
      <div data-testid="qr-scanner">
        <button onClick={() => onScan('https://example.com/qr')}>Mock Scan</button>
        <button onClick={onCancel}>Cancel</button>
      </div>
    )
  }
})

// Mock DocumentStatus component
jest.mock('../components/DocumentStatus', () => {
  return function MockDocumentStatus({ qrData }: any) {
    return <div data-testid="document-status">Document Status: {qrData}</div>
  }
})

// Helper function to render with all providers
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <AppProvider>
      <LanguageProvider>
        {component}
      </LanguageProvider>
    </AppProvider>
  )
}

describe('HomePage', () => {
  beforeEach(() => {
    localStorage.clear()
    // Mock document.title
    Object.defineProperty(document, 'title', {
      value: '',
      writable: true
    })
  })

  it('renders main page elements', () => {
    renderWithProviders(<HomePage />)
    
    expect(screen.getByText('PTE QR Система')).toBeInTheDocument()
    expect(screen.getByText('Система проверки актуальности документов через QR-коды')).toBeInTheDocument()
    expect(screen.getByText('Сканирование QR-кода')).toBeInTheDocument()
    expect(screen.getByText('Статус документа')).toBeInTheDocument()
  })

  it('renders scan button initially', () => {
    renderWithProviders(<HomePage />)
    
    expect(screen.getByText('Сканировать QR')).toBeInTheDocument()
    expect(screen.getByText('Отсканируйте QR-код для проверки статуса документа')).toBeInTheDocument()
  })

  it('shows QR scanner when scan button is clicked', () => {
    renderWithProviders(<HomePage />)
    
    const scanButton = screen.getByText('Сканировать QR')
    fireEvent.click(scanButton)
    
    expect(screen.getByTestId('qr-scanner')).toBeInTheDocument()
  })

  it('handles QR code scan', async () => {
    renderWithProviders(<HomePage />)
    
    const scanButton = screen.getByText('Сканировать QR')
    fireEvent.click(scanButton)
    
    const mockScanButton = screen.getByText('Mock Scan')
    fireEvent.click(mockScanButton)
    
    await waitFor(() => {
      expect(screen.getByText('Успешно')).toBeInTheDocument()
      expect(screen.getByText('https://example.com/qr')).toBeInTheDocument()
    })
  })

  it('shows document status after scan', async () => {
    renderWithProviders(<HomePage />)
    
    const scanButton = screen.getByText('Сканировать QR')
    fireEvent.click(scanButton)
    
    const mockScanButton = screen.getByText('Mock Scan')
    fireEvent.click(mockScanButton)
    
    await waitFor(() => {
      expect(screen.getByTestId('document-status')).toBeInTheDocument()
      expect(screen.getByText('Document Status: https://example.com/qr')).toBeInTheDocument()
    })
  })

  it('allows rescanning after successful scan', async () => {
    renderWithProviders(<HomePage />)
    
    // First scan
    const scanButton = screen.getByText('Сканировать QR')
    fireEvent.click(scanButton)
    
    const mockScanButton = screen.getByText('Mock Scan')
    fireEvent.click(mockScanButton)
    
    await waitFor(() => {
      expect(screen.getByText('Успешно')).toBeInTheDocument()
    })
    
    // Click rescan button
    const rescanButton = screen.getByText('Сканировать QR')
    fireEvent.click(rescanButton)
    
    expect(screen.getByTestId('qr-scanner')).toBeInTheDocument()
  })

  it('handles scan cancellation', () => {
    renderWithProviders(<HomePage />)
    
    const scanButton = screen.getByText('Сканировать QR')
    fireEvent.click(scanButton)
    
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)
    
    expect(screen.queryByTestId('qr-scanner')).not.toBeInTheDocument()
    expect(screen.getByText('Сканировать QR')).toBeInTheDocument()
  })

  it('renders features section', () => {
    renderWithProviders(<HomePage />)
    
    expect(screen.getByText('Проверка актуальности')).toBeInTheDocument()
    expect(screen.getByText('Мгновенная проверка актуальности документа и его ревизии')).toBeInTheDocument()
    
    expect(screen.getByText('Мобильная версия')).toBeInTheDocument()
    expect(screen.getByText('Оптимизировано для использования на мобильных устройствах')).toBeInTheDocument()
    
    expect(screen.getByText('Безопасность')).toBeInTheDocument()
    expect(screen.getByText('HMAC подпись обеспечивает защиту от подделки QR-кодов')).toBeInTheDocument()
  })

  it('updates document title when language changes', () => {
    renderWithProviders(<HomePage />)
    
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'en' } })
    
    expect(document.title).toBe('PTE QR System')
  })

  it('renders with English language', () => {
    renderWithProviders(<HomePage />)
    
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'en' } })
    
    expect(screen.getByText('PTE QR System')).toBeInTheDocument()
    expect(screen.getByText('Document status verification system via QR codes')).toBeInTheDocument()
    expect(screen.getByText('QR Code Scanning')).toBeInTheDocument()
    expect(screen.getByText('Document Status')).toBeInTheDocument()
    expect(screen.getByText('Status Verification')).toBeInTheDocument()
    expect(screen.getByText('Mobile Version')).toBeInTheDocument()
    expect(screen.getByText('Security')).toBeInTheDocument()
  })

  it('renders with Chinese language', () => {
    renderWithProviders(<HomePage />)
    
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'zh' } })
    
    expect(screen.getByText('PTE QR 系统')).toBeInTheDocument()
    expect(screen.getByText('通过二维码验证文档状态的系统')).toBeInTheDocument()
    expect(screen.getByText('二维码扫描')).toBeInTheDocument()
    expect(screen.getByText('文档状态')).toBeInTheDocument()
    expect(screen.getByText('状态验证')).toBeInTheDocument()
    expect(screen.getByText('移动版本')).toBeInTheDocument()
    expect(screen.getByText('安全性')).toBeInTheDocument()
  })

  it('shows instruction when no data is scanned', () => {
    renderWithProviders(<HomePage />)
    
    const documentStatusSection = screen.getByText('Статус документа').closest('.card')
    expect(documentStatusSection).toHaveTextContent('Отсканируйте QR-код для проверки статуса документа')
  })

  it('applies correct CSS classes for dark theme', () => {
    localStorage.setItem('pte-qr-theme', 'dark')
    
    renderWithProviders(<HomePage />)
    
    const mainTitle = screen.getByText('PTE QR Система')
    expect(mainTitle).toHaveClass('dark:text-white')
  })

  it('renders logo and language switcher', () => {
    renderWithProviders(<HomePage />)
    
    expect(screen.getByAltText('PTE QR Logo')).toBeInTheDocument()
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('handles multiple scans correctly', async () => {
    renderWithProviders(<HomePage />)
    
    // First scan
    const scanButton = screen.getByText('Сканировать QR')
    fireEvent.click(scanButton)
    
    const mockScanButton = screen.getByText('Mock Scan')
    fireEvent.click(mockScanButton)
    
    await waitFor(() => {
      expect(screen.getByText('Успешно')).toBeInTheDocument()
    })
    
    // Second scan
    const rescanButton = screen.getByText('Сканировать QR')
    fireEvent.click(rescanButton)
    
    const secondMockScanButton = screen.getByText('Mock Scan')
    fireEvent.click(secondMockScanButton)
    
    await waitFor(() => {
      expect(screen.getByText('Успешно')).toBeInTheDocument()
    })
  })
})
