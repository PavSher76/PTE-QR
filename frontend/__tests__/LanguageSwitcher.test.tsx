import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { LanguageSwitcher } from '../components/LanguageSwitcher'
import { LanguageProvider } from '../lib/i18n'

// Helper function to render with LanguageProvider
const renderWithLanguageProvider = (component: React.ReactElement) => {
  return render(
    <LanguageProvider>
      {component}
    </LanguageProvider>
  )
}

describe('LanguageSwitcher', () => {
  it('renders language options', () => {
    renderWithLanguageProvider(<LanguageSwitcher />)
    
    const select = screen.getByRole('combobox')
    expect(select).toBeInTheDocument()
    
    // Check that all language options are present
    expect(screen.getByText('🇷🇺 Русский')).toBeInTheDocument()
    expect(screen.getByText('🇺🇸 English')).toBeInTheDocument()
    expect(screen.getByText('🇨🇳 中文')).toBeInTheDocument()
  })

  it('has Russian selected by default', () => {
    renderWithLanguageProvider(<LanguageSwitcher />)
    
    const select = screen.getByRole('combobox')
    expect(select).toHaveValue('ru')
  })

  it('changes language when selection changes', () => {
    renderWithLanguageProvider(<LanguageSwitcher />)
    
    const select = screen.getByRole('combobox')
    
    // Change to English
    fireEvent.change(select, { target: { value: 'en' } })
    expect(select).toHaveValue('en')
    
    // Change to Chinese
    fireEvent.change(select, { target: { value: 'zh' } })
    expect(select).toHaveValue('zh')
    
    // Change back to Russian
    fireEvent.change(select, { target: { value: 'ru' } })
    expect(select).toHaveValue('ru')
  })

  it('persists language selection in localStorage', () => {
    // Clear localStorage before test
    localStorage.clear()
    
    renderWithLanguageProvider(<LanguageSwitcher />)
    
    const select = screen.getByRole('combobox')
    
    // Change to English
    fireEvent.change(select, { target: { value: 'en' } })
    
    // Check that language is stored in localStorage
    expect(localStorage.getItem('pte-qr-language')).toBe('en')
  })
})
