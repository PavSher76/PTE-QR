import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import HomePage from '../app/page'

// Mock the components
jest.mock('../components/Header', () => {
  return function MockHeader() {
    return <div data-testid="header">Header</div>
  }
})

jest.mock('../components/Footer', () => {
  return function MockFooter() {
    return <div data-testid="footer">Footer</div>
  }
})

jest.mock('../components/QRCodeScanner', () => {
  return function MockQRCodeScanner() {
    return <div data-testid="qr-scanner">QR Scanner</div>
  }
})

jest.mock('../components/DocumentStatus', () => {
  return function MockDocumentStatus() {
    return <div data-testid="document-status">Document Status</div>
  }
})

jest.mock('../components/LanguageSwitcher', () => {
  return function MockLanguageSwitcher() {
    return <div data-testid="language-switcher">Language Switcher</div>
  }
})

jest.mock('../components/NotificationContainer', () => {
  return function MockNotificationContainer() {
    return <div data-testid="notification-container">Notifications</div>
  }
})

describe('HomePage', () => {
  it('renders the main page components', () => {
    render(<HomePage />)
    
    expect(screen.getByTestId('header')).toBeInTheDocument()
    expect(screen.getByTestId('footer')).toBeInTheDocument()
    expect(screen.getByTestId('language-switcher')).toBeInTheDocument()
  })

  it('displays the main heading', () => {
    render(<HomePage />)
    
    // The heading should be present (it will show the translation key if translations don't work)
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toBeInTheDocument()
  })

  it('shows QR scanning section', () => {
    render(<HomePage />)
    
    // Look for the scan button
    const scanButton = screen.getByRole('button', { name: /сканировать/i })
    expect(scanButton).toBeInTheDocument()
  })
})
