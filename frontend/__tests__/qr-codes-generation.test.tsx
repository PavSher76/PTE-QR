import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { LanguageProvider } from '../lib/i18n'

// Mock API functions for QR code generation and retrieval
const mockApi = {
  generateQRCode: jest.fn(),
  getDocumentStatus: jest.fn(),
  getQRCodeData: jest.fn(),
}

// Mock document data
const mockDocument = {
  id: '3D-00001234',
  title: 'Test Document',
  revision: 'B',
  totalPages: 10,
  status: 'АКТУАЛЬНЫЙ',
  enoviaMaturityState: 'Released',
  releaseDate: '2024-01-15T10:30:00Z',
}

// Mock QR code data for each page
const mockQRCodeData = Array.from({ length: 10 }, (_, index) => ({
  id: `qr-${index + 1}`,
  documentId: mockDocument.id,
  page: index + 1,
  qrData: `https://pte-qr.local/r/${mockDocument.id}/${mockDocument.revision}/${index + 1}`,
  generatedAt: new Date().toISOString(),
  expiresAt: null, // Бессрочно
  isActive: true,
}))

// Test component for QR code generation and display
function QRCodeTestComponent() {
  const [qrCodes, setQrCodes] = React.useState<any[]>([])
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const generateAllQRCodes = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const generatedCodes = []
      
      // Generate QR codes for all 10 pages
      for (let page = 1; page <= 10; page++) {
        const qrData = {
          documentId: mockDocument.id,
          revision: mockDocument.revision,
          page: page,
        }
        
        const response = await mockApi.generateQRCode(qrData)
        generatedCodes.push(response)
      }
      
      setQrCodes(generatedCodes)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const getDocumentStatus = async (documentId: string, revision: string, page: number) => {
    try {
      const response = await mockApi.getDocumentStatus(documentId, revision, page)
      return response
    } catch (err) {
      throw new Error(`Failed to get document status: ${err}`)
    }
  }

  return (
    <div>
      <h1>QR Code Generation Test</h1>
      <p>Document: {mockDocument.id} Rev. {mockDocument.revision} ({mockDocument.totalPages} pages)</p>
      
      <button 
        onClick={generateAllQRCodes}
        disabled={loading}
        data-testid="generate-qr-codes"
      >
        {loading ? 'Generating...' : 'Generate 10 QR Codes'}
      </button>
      
      {error && (
        <div data-testid="error-message" style={{ color: 'red' }}>
          Error: {error}
        </div>
      )}
      
      {qrCodes.length > 0 && (
        <div data-testid="qr-codes-list">
          <h2>Generated QR Codes ({qrCodes.length})</h2>
          {qrCodes.map((qr, index) => (
            <div key={qr.id || index} data-testid={`qr-code-${index + 1}`}>
              <p>Page {qr.page}: {qr.qrData}</p>
              <p>Generated: {new Date(qr.generatedAt).toLocaleString()}</p>
              <p>Expires: {qr.expiresAt ? new Date(qr.expiresAt).toLocaleString() : 'Бессрочно'}</p>
              <p>Active: {qr.isActive ? 'Yes' : 'No'}</p>
            </div>
          ))}
        </div>
      )}
      
      <div data-testid="test-results">
        <h2>Test Results</h2>
        <p>Total QR Codes Generated: {qrCodes.length}</p>
        <p>Expected: 10</p>
        <p>Success Rate: {qrCodes.length === 10 ? '100%' : `${(qrCodes.length / 10) * 100}%`}</p>
        <p>All QR Codes Valid: {qrCodes.every(qr => qr.isActive && qr.qrData) ? 'Yes' : 'No'}</p>
      </div>
    </div>
  )
}

describe('QR Code Generation Test - 10 QR Codes for 10 Pages', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks()
    
    // Setup successful API responses
    mockApi.generateQRCode.mockImplementation((data) => {
      const page = data.page
      return Promise.resolve({
        id: `qr-${page}`,
        documentId: data.documentId,
        revision: data.revision,
        page: page,
        qrData: `https://pte-qr.local/r/${data.documentId}/${data.revision}/${page}`,
        generatedAt: new Date().toISOString(),
        expiresAt: null, // Бессрочно
        isActive: true,
      })
    })
    
    mockApi.getDocumentStatus.mockImplementation((documentId, revision, page) => {
      return Promise.resolve({
        document: {
          ...mockDocument,
          currentPage: page,
        },
        status: 'АКТУАЛЬНЫЙ',
        lastChecked: new Date().toISOString(),
      })
    })
  })

  it('should generate 10 QR codes for document with 10 pages', async () => {
    render(
      <LanguageProvider>
        <QRCodeTestComponent />
      </LanguageProvider>
    )

    // Verify initial state
    expect(screen.getByText('Document: 3D-00001234 Rev. B (10 pages)')).toBeInTheDocument()
    expect(screen.getByTestId('generate-qr-codes')).toBeInTheDocument()

    // Click generate button
    const generateButton = screen.getByTestId('generate-qr-codes')
    fireEvent.click(generateButton)

    // Wait for generation to complete
    await waitFor(() => {
      expect(screen.getByText('Generating...')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByTestId('qr-codes-list')).toBeInTheDocument()
    }, { timeout: 5000 })

    // Verify all 10 QR codes were generated
    expect(screen.getByText('Generated QR Codes (10)')).toBeInTheDocument()
    
    // Check each QR code
    for (let i = 1; i <= 10; i++) {
      const qrCodeElement = screen.getByTestId(`qr-code-${i}`)
      expect(qrCodeElement).toBeInTheDocument()
      expect(qrCodeElement).toHaveTextContent(`Page ${i}:`)
      expect(qrCodeElement).toHaveTextContent(`https://pte-qr.local/r/3D-00001234/B/${i}`)
      expect(qrCodeElement).toHaveTextContent('Active: Yes')
    }

    // Verify test results
    expect(screen.getByText('Total QR Codes Generated: 10')).toBeInTheDocument()
    expect(screen.getByText('Expected: 10')).toBeInTheDocument()
    expect(screen.getByText('Success Rate: 100%')).toBeInTheDocument()
    expect(screen.getByText('All QR Codes Valid: Yes')).toBeInTheDocument()

    // Verify API was called 10 times
    expect(mockApi.generateQRCode).toHaveBeenCalledTimes(10)
  })

  it('should handle QR code generation errors gracefully', async () => {
    // Mock API to fail on 5th call
    mockApi.generateQRCode.mockImplementation((data) => {
      if (data.page === 5) {
        return Promise.reject(new Error('QR generation failed for page 5'))
      }
      return Promise.resolve({
        id: `qr-${data.page}`,
        documentId: data.documentId,
        revision: data.revision,
        page: data.page,
        qrData: `https://pte-qr.local/r/${data.documentId}/${data.revision}/${data.page}`,
        generatedAt: new Date().toISOString(),
        expiresAt: null, // Бессрочно
        isActive: true,
      })
    })

    render(
      <LanguageProvider>
        <QRCodeTestComponent />
      </LanguageProvider>
    )

    const generateButton = screen.getByTestId('generate-qr-codes')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument()
    })

    expect(screen.getByText(/Error: QR generation failed for page 5/)).toBeInTheDocument()
  })

  it('should validate QR code data format', async () => {
    render(
      <LanguageProvider>
        <QRCodeTestComponent />
      </LanguageProvider>
    )

    const generateButton = screen.getByTestId('generate-qr-codes')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(screen.getByTestId('qr-codes-list')).toBeInTheDocument()
    })

    // Validate QR code data format for each page
    for (let i = 1; i <= 10; i++) {
      const qrCodeElement = screen.getByTestId(`qr-code-${i}`)
      const expectedUrl = `https://pte-qr.local/r/3D-00001234/B/${i}`
      expect(qrCodeElement).toHaveTextContent(expectedUrl)
    }
  })

  it('should verify QR codes are set to never expire', async () => {
    render(
      <LanguageProvider>
        <QRCodeTestComponent />
      </LanguageProvider>
    )

    const generateButton = screen.getByTestId('generate-qr-codes')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(screen.getByTestId('qr-codes-list')).toBeInTheDocument()
    })

    // Check that all QR codes are set to never expire
    for (let i = 1; i <= 10; i++) {
      const qrCodeElement = screen.getByTestId(`qr-code-${i}`)
      expect(qrCodeElement).toHaveTextContent('Expires: Бессрочно')
    }
  })
})
