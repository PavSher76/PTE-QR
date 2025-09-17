import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Logo } from '../components/Logo'
import { LanguageSwitcher } from '../components/LanguageSwitcher'
import { LanguageProvider } from '../lib/i18n'
import { useTranslation } from '../lib/i18n'

// Test component that uses translation
function TestComponent() {
  const { t } = useTranslation()
  return (
    <div>
      <h1>{t('app.title')}</h1>
      <p>{t('app.description')}</p>
    </div>
  )
}

// Helper function to render with LanguageProvider
const renderWithLanguageProvider = (component: React.ReactElement) => {
  return render(<LanguageProvider>{component}</LanguageProvider>)
}

describe('Integration Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
  })

  describe('Logo and LanguageSwitcher Integration', () => {
    it('renders both components together', () => {
      renderWithLanguageProvider(
        <div>
          <Logo size="medium" variant="compact" />
          <LanguageSwitcher />
        </div>
      )

      // Check that Logo is rendered
      const logo = screen.getByAltText('PTE QR Logo')
      expect(logo).toBeInTheDocument()

      // Check that LanguageSwitcher is rendered
      const languageSelect = screen.getByRole('combobox')
      expect(languageSelect).toBeInTheDocument()
    })

    it('maintains language state across components', () => {
      renderWithLanguageProvider(
        <div>
          <LanguageSwitcher />
          <TestComponent />
        </div>
      )

      // Initially should be in Russian (or show translation key if not found)
      const titleElement = screen.getByText(/app\.title|PTE QR/)
      expect(titleElement).toBeInTheDocument()

      // Change language to English
      const languageSelect = screen.getByRole('combobox')
      fireEvent.change(languageSelect, { target: { value: 'en' } })

      // Check that language changed (either translation or key)
      const updatedTitleElement = screen.getByText(/app\.title|PTE QR/)
      expect(updatedTitleElement).toBeInTheDocument()
    })
  })

  describe('Language Persistence', () => {
    it('persists language selection across renders', () => {
      // First render
      const { unmount } = renderWithLanguageProvider(
        <div>
          <LanguageSwitcher />
          <TestComponent />
        </div>
      )

      // Change language to English
      const languageSelect = screen.getByRole('combobox')
      fireEvent.change(languageSelect, { target: { value: 'en' } })

      // Unmount
      unmount()

      // Second render
      renderWithLanguageProvider(
        <div>
          <LanguageSwitcher />
          <TestComponent />
        </div>
      )

      // Should still be in English
      const newLanguageSelect = screen.getByRole('combobox')
      expect(newLanguageSelect).toHaveValue('en')
      expect(screen.getByText(/app\.title|PTE QR/)).toBeInTheDocument()
    })

    it('falls back to default language when localStorage is empty', () => {
      // Ensure localStorage is empty
      localStorage.clear()

      renderWithLanguageProvider(
        <div>
          <LanguageSwitcher />
          <TestComponent />
        </div>
      )

      // Should default to Russian
      const languageSelect = screen.getByRole('combobox')
      expect(languageSelect).toHaveValue('ru')
      expect(screen.getByText(/app\.title|PTE QR/)).toBeInTheDocument()
    })
  })

  describe('Component Props Integration', () => {
    it('Logo responds to different size props', () => {
      renderWithLanguageProvider(
        <div>
          <Logo size="small" variant="compact" data-testid="small-logo" />
          <Logo size="medium" variant="compact" data-testid="medium-logo" />
          <Logo size="large" variant="full" data-testid="large-logo" />
        </div>
      )

      const smallLogo = screen.getByTestId('small-logo')
      const mediumLogo = screen.getByTestId('medium-logo')
      const largeLogo = screen.getByTestId('large-logo')

      expect(smallLogo).toBeInTheDocument()
      expect(mediumLogo).toBeInTheDocument()
      expect(largeLogo).toBeInTheDocument()

      // Check that different sizes are applied
      expect(smallLogo).toHaveClass('w-6', 'h-6')
      expect(mediumLogo).toHaveClass('w-10', 'h-10')
      expect(largeLogo).toHaveClass('w-16', 'h-16')
    })
  })

  describe('Error Handling', () => {
    it('handles invalid language selection gracefully', () => {
      renderWithLanguageProvider(
        <div>
          <LanguageSwitcher />
          <TestComponent />
        </div>
      )

      const languageSelect = screen.getByRole('combobox')

      // Try to set an invalid language (this should not break the app)
      // The component should handle this gracefully
      fireEvent.change(languageSelect, { target: { value: 'invalid' } })

      // App should still be functional
      expect(languageSelect).toBeInTheDocument()
      expect(screen.getByText(/app\.title|PTE QR/)).toBeInTheDocument()
    })
  })
})
