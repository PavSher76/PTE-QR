import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { QRCodeScanner } from '../components/QRCodeScanner'
import { LanguageProvider } from '../lib/i18n'

// Mock navigator.mediaDevices
const mockGetUserMedia = jest.fn()
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: mockGetUserMedia,
  },
  writable: true,
})

// Mock HTMLVideoElement
const mockVideo = {
  srcObject: null,
  play: jest.fn(),
  videoWidth: 640,
  videoHeight: 480,
}

// Mock HTMLCanvasElement
const mockCanvas = {
  width: 0,
  height: 0,
  getContext: jest.fn(() => ({
    drawImage: jest.fn(),
  })),
}

// Helper function to render with LanguageProvider
const renderWithLanguageProvider = (component: React.ReactElement) => {
  return render(<LanguageProvider>{component}</LanguageProvider>)
}

describe('QRCodeScanner', () => {
  const mockOnScan = jest.fn()
  const mockOnCancel = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    mockGetUserMedia.mockResolvedValue({
      getTracks: () => [{ stop: jest.fn() }],
    })
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

  it('shows error when camera access fails', async () => {
    mockGetUserMedia.mockRejectedValue(new Error('Camera access denied'))

    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    await waitFor(() => {
      expect(
        screen.getByText('Не удалось получить доступ к камере')
      ).toBeInTheDocument()
    })
  })

  it('calls onCancel when cancel button is clicked', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    const cancelButton = screen.getByText('Отмена')
    fireEvent.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalledTimes(1)
  })

  it('calls onCancel when close button is clicked in error state', async () => {
    mockGetUserMedia.mockRejectedValue(new Error('Camera access denied'))

    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    await waitFor(() => {
      expect(
        screen.getByText('Не удалось получить доступ к камере')
      ).toBeInTheDocument()
    })

    const closeButton = screen.getByText('Закрыть')
    fireEvent.click(closeButton)

    expect(mockOnCancel).toHaveBeenCalledTimes(1)
  })

  it('simulates QR code scan after delay', async () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    const scanButton = screen.getByText('Сканировать')
    fireEvent.click(scanButton)

    // Wait for the simulated scan to complete
    await waitFor(
      () => {
        expect(mockOnScan).toHaveBeenCalledWith(
          'https://qr.pti.ru/r/3D-00001234/B/3?ts=1703123456&t=abc123def456'
        )
      },
      { timeout: 3000 }
    )
  })

  it('renders with English language', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    // Change language to English
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'en' } })

    expect(
      screen.getByText('Point camera at document QR code')
    ).toBeInTheDocument()
    expect(screen.getByText('Scan')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
  })

  it('renders with Chinese language', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    // Change language to Chinese
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'zh' } })

    expect(screen.getByText('将摄像头对准文档二维码')).toBeInTheDocument()
    expect(screen.getByText('扫描')).toBeInTheDocument()
    expect(screen.getByText('取消')).toBeInTheDocument()
  })

  it('shows scanning animation when scanning', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    // The component should show scanning state initially
    const scanningDots = screen
      .getAllByRole('generic')
      .filter((el) => el.className.includes('animate-pulse'))
    expect(scanningDots.length).toBeGreaterThan(0)
  })

  it('disables scan button when not scanning', () => {
    mockGetUserMedia.mockRejectedValue(new Error('Camera access denied'))

    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    // In error state, scan button should be disabled
    const scanButton = screen.queryByText('Сканировать')
    if (scanButton) {
      expect(scanButton).toBeDisabled()
    }
  })

  it('renders QR code overlay', () => {
    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    // Check for QR code overlay elements
    const overlay = screen
      .getByRole('generic')
      .querySelector('.border-primary-500')
    expect(overlay).toBeInTheDocument()
  })

  it('handles video element setup', async () => {
    const mockVideoElement = { ...mockVideo }
    const mockCanvasElement = { ...mockCanvas }

    // Mock createRef to return our mock elements
    jest
      .spyOn(React, 'useRef')
      .mockReturnValueOnce({ current: mockVideoElement })
      .mockReturnValueOnce({ current: mockCanvasElement })

    renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        video: { facingMode: 'environment' },
      })
    })
  })

  it('stops camera on unmount', () => {
    const mockStream = {
      getTracks: () => [{ stop: jest.fn() }],
    }
    mockGetUserMedia.mockResolvedValue(mockStream)

    const { unmount } = renderWithLanguageProvider(
      <QRCodeScanner onScan={mockOnScan} onCancel={mockOnCancel} />
    )

    unmount()

    // Camera should be stopped on unmount
    expect(mockStream.getTracks()[0].stop).toHaveBeenCalled()
  })
})
