import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { DocumentStatus } from '../components/DocumentStatus'
import { LanguageProvider } from '../lib/i18n'
import { DocumentStatusData } from '../types/document'

// Mock document data
const mockDocumentData: DocumentStatusData = {
  doc_uid: '3D-00001234',
  revision: 'B',
  page: 3,
  business_status: 'APPROVED_FOR_CONSTRUCTION',
  enovia_state: 'Released',
  is_actual: true,
  released_at: '2024-01-15T10:30:00Z',
  links: {
    openDocument: 'https://example.com/document',
    openLatest: 'https://example.com/latest'
  }
}

const mockOutdatedDocumentData: DocumentStatusData = {
  doc_uid: '3D-00001234',
  revision: 'A',
  page: 1,
  business_status: 'SUPERSEDED',
  enovia_state: 'Obsolete',
  is_actual: false,
  released_at: '2023-12-01T10:30:00Z',
  links: {
    openDocument: 'https://example.com/document',
    openLatest: 'https://example.com/latest'
  }
}

// Helper function to render with LanguageProvider
const renderWithLanguageProvider = (component: React.ReactElement) => {
  return render(
    <LanguageProvider>
      {component}
    </LanguageProvider>
  )
}

describe('DocumentStatus', () => {
  it('renders no data message when no data provided', () => {
    renderWithLanguageProvider(<DocumentStatus />)
    
    expect(screen.getByText('Нет данных для отображения')).toBeInTheDocument()
  })

  it('renders document information when data is provided', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockDocumentData} />)
    
    expect(screen.getByText('Статус документа')).toBeInTheDocument()
    expect(screen.getByText('3D-00001234')).toBeInTheDocument()
    expect(screen.getByText('B')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('renders actual status for current document', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockDocumentData} />)
    
    const statusElement = screen.getByText('АКТУАЛЬНЫЙ')
    expect(statusElement).toBeInTheDocument()
    expect(statusElement).toHaveClass('text-green-600')
  })

  it('renders outdated status for superseded document', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockOutdatedDocumentData} />)
    
    const statusElement = screen.getByText('УСТАРЕЛ')
    expect(statusElement).toBeInTheDocument()
    expect(statusElement).toHaveClass('text-red-600')
  })

  it('renders ENOVIA state', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockDocumentData} />)
    
    expect(screen.getByText('Состояние в ENOVIA')).toBeInTheDocument()
    expect(screen.getByText('Released')).toBeInTheDocument()
  })

  it('renders release date when available', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockDocumentData} />)
    
    expect(screen.getByText('Дата выпуска')).toBeInTheDocument()
    expect(screen.getByText('15.01.2024')).toBeInTheDocument()
  })

  it('renders action links when available', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockDocumentData} />)
    
    const openDocumentLink = screen.getByText('Открыть документ')
    const openLatestLink = screen.getByText('Открыть последнюю версию')
    
    expect(openDocumentLink).toBeInTheDocument()
    expect(openLatestLink).toBeInTheDocument()
    
    expect(openDocumentLink).toHaveAttribute('href', 'https://example.com/document')
    expect(openLatestLink).toHaveAttribute('href', 'https://example.com/latest')
  })

  it('creates mock data when qrData is provided', () => {
    renderWithLanguageProvider(<DocumentStatus qrData="https://example.com/qr" />)
    
    expect(screen.getByText('Статус документа')).toBeInTheDocument()
    expect(screen.getByText('Sample-Document')).toBeInTheDocument()
    expect(screen.getByText('A')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('renders with English language', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockDocumentData} />)
    
    // Change language to English
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'en' } })
    
    expect(screen.getByText('Document Status')).toBeInTheDocument()
    expect(screen.getByText('Document')).toBeInTheDocument()
    expect(screen.getByText('Revision')).toBeInTheDocument()
    expect(screen.getByText('Page')).toBeInTheDocument()
    expect(screen.getByText('ACTUAL')).toBeInTheDocument()
    expect(screen.getByText('ENOVIA State')).toBeInTheDocument()
    expect(screen.getByText('Released At')).toBeInTheDocument()
    expect(screen.getByText('Open Document')).toBeInTheDocument()
    expect(screen.getByText('Open Latest')).toBeInTheDocument()
  })

  it('renders with Chinese language', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockDocumentData} />)
    
    // Change language to Chinese
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'zh' } })
    
    expect(screen.getByText('文档状态')).toBeInTheDocument()
    expect(screen.getByText('文档')).toBeInTheDocument()
    expect(screen.getByText('修订版')).toBeInTheDocument()
    expect(screen.getByText('页面')).toBeInTheDocument()
    expect(screen.getByText('当前')).toBeInTheDocument()
    expect(screen.getByText('ENOVIA状态')).toBeInTheDocument()
    expect(screen.getByText('发布日期')).toBeInTheDocument()
    expect(screen.getByText('打开文档')).toBeInTheDocument()
    expect(screen.getByText('打开最新版本')).toBeInTheDocument()
  })

  it('applies correct CSS classes for dark theme', () => {
    renderWithLanguageProvider(<DocumentStatus data={mockDocumentData} />)
    
    const container = screen.getByText('Статус документа').closest('div')
    expect(container).toHaveClass('bg-white', 'dark:bg-gray-800')
  })

  it('handles missing links gracefully', () => {
    const dataWithoutLinks = { ...mockDocumentData, links: undefined }
    renderWithLanguageProvider(<DocumentStatus data={dataWithoutLinks} />)
    
    expect(screen.queryByText('Открыть документ')).not.toBeInTheDocument()
    expect(screen.queryByText('Открыть последнюю версию')).not.toBeInTheDocument()
  })

  it('handles missing release date gracefully', () => {
    const dataWithoutDate = { ...mockDocumentData, released_at: undefined }
    renderWithLanguageProvider(<DocumentStatus data={dataWithoutDate} />)
    
    expect(screen.queryByText('Дата выпуска')).not.toBeInTheDocument()
  })
})
