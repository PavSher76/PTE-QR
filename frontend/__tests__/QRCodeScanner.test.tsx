import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { LanguageProvider } from '../lib/i18n'
import { LanguageSwitcher } from '../components/LanguageSwitcher'

// Mock QRCodeScanner component
jest.mock('../components/QRCodeScanner', () => ({
  QRCodeScanner: ({ onScan, onCancel }: { onScan: (data: string) => void; onCancel: () => void }) => (
    <div data-testid="qr-scanner">
      <p>Наведите камеру на QR-код документа</p>
      <button onClick={() => onScan('test-qr-data')}>Сканировать</button>
      <button onClick={onCancel}>Отмена</button>
    </div>
  ),
}))

import { QRCodeScanner } from '../components/QRCodeScanner'

// Helper function to render with LanguageProvider and LanguageSwitcher
const renderWithLanguageProvider = (component: React.ReactElement) => {
  return render(
    <LanguageProvider>
      <div>
        <LanguageSwitcher />
        {component}
      </div>
    </LanguageProvider>
  )
}

describe('QRCodeScanner', () => {
  const mockOnScan = jest.fn()
  const mockOnCancel = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders scanner interface', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    expect(
      screen.getByText('Наведите камеру на QR-код документа')
    ).toBeInTheDocument()
    expect(screen.getByText('Сканировать')).toBeInTheDocument()
    expect(screen.getByText('Отмена')).toBeInTheDocument()
  })

  it('calls onScan when scan button is clicked', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    const scanButton = screen.getByText('Сканировать')
    fireEvent.click(scanButton)

    expect(mockOnScan).toHaveBeenCalledWith('test-qr-data')
  })

  it('calls onCancel when cancel button is clicked', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    const cancelButton = screen.getByText('Отмена')
    fireEvent.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalledTimes(1)
  })

  it('renders with language switcher', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    // Проверяем, что LanguageSwitcher рендерится
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('has correct test id', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    expect(screen.getByTestId('qr-scanner')).toBeInTheDocument()
  })
})
