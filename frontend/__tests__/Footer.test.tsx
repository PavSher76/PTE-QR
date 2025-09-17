import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Footer } from '../components/Footer'
import { LanguageSwitcher } from '../components/LanguageSwitcher'
import { LanguageProvider } from '../lib/i18n'

describe('Footer', () => {
  it('renders footer with logo and title', () => {
    render(
      <LanguageProvider>
        <Footer />
      </LanguageProvider>
    )
    
    expect(screen.getByAltText('PTE QR Logo')).toBeInTheDocument()
    expect(screen.getByText('PTE QR Система')).toBeInTheDocument()
  })

  it('renders description', () => {
    render(
      <LanguageProvider>
        <Footer />
      </LanguageProvider>
    )
    
    expect(screen.getByText(/Система проверки актуальности документов через QR-коды с интеграцией в ENOVIA PLM/)).toBeInTheDocument()
  })

  it('renders product section', () => {
    render(
      <LanguageProvider>
        <Footer />
      </LanguageProvider>
    )
    
    expect(screen.getByText('Продукт')).toBeInTheDocument()
    expect(screen.getByText('Возможности')).toBeInTheDocument()
    expect(screen.getByText('Интеграция')).toBeInTheDocument()
    expect(screen.getByText('API')).toBeInTheDocument()
  })

  it('renders support section', () => {
    render(
      <LanguageProvider>
        <Footer />
      </LanguageProvider>
    )
    
    expect(screen.getByText('Поддержка')).toBeInTheDocument()
    expect(screen.getByText('Документация')).toBeInTheDocument()
    expect(screen.getByText('Помощь')).toBeInTheDocument()
    expect(screen.getByText('Контакты')).toBeInTheDocument()
  })

  it('renders company section', () => {
    render(
      <LanguageProvider>
        <Footer />
      </LanguageProvider>
    )
    
    expect(screen.getByText('Компания')).toBeInTheDocument()
    expect(screen.getByText('О нас')).toBeInTheDocument()
    expect(screen.getByText('Политика конфиденциальности')).toBeInTheDocument()
    expect(screen.getByText('Условия использования')).toBeInTheDocument()
  })

  it('renders copyright notice', () => {
    render(
      <LanguageProvider>
        <Footer />
      </LanguageProvider>
    )
    
    expect(screen.getByText('© 2024 ПТИ. Все права защищены.')).toBeInTheDocument()
  })

  it('renders with English language', () => {
    render(
      <LanguageProvider>
        <div>
          <Footer />
          <LanguageSwitcher />
        </div>
      </LanguageProvider>
    )
    
    // Change language to English
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'en' } })
    
    expect(screen.getByText('PTE QR System')).toBeInTheDocument()
    expect(screen.getByText('Product')).toBeInTheDocument()
    expect(screen.getByText('Support')).toBeInTheDocument()
    expect(screen.getByText('Company')).toBeInTheDocument()
    expect(screen.getByText('© 2024 PTI. All rights reserved.')).toBeInTheDocument()
  })

  it('renders with Chinese language', () => {
    render(
      <LanguageProvider>
        <div>
          <Footer />
          <LanguageSwitcher />
        </div>
      </LanguageProvider>
    )
    
    // Change language to Chinese
    const languageSelect = screen.getByRole('combobox')
    fireEvent.change(languageSelect, { target: { value: 'zh' } })
    
    expect(screen.getByText('PTE QR 系统')).toBeInTheDocument()
    expect(screen.getByText('产品')).toBeInTheDocument()
    expect(screen.getByText('支持')).toBeInTheDocument()
    expect(screen.getByText('公司')).toBeInTheDocument()
    expect(screen.getByText('© 2024 PTI. 版权所有。')).toBeInTheDocument()
  })

  it('applies correct CSS classes', () => {
    render(
      <LanguageProvider>
        <Footer />
      </LanguageProvider>
    )
    
    const footer = screen.getByRole('contentinfo')
    expect(footer).toHaveClass('bg-gray-900', 'text-white')
  })

  it('renders all links as clickable elements', () => {
    render(
      <LanguageProvider>
        <Footer />
      </LanguageProvider>
    )
    
    const links = screen.getAllByRole('link')
    expect(links.length).toBeGreaterThan(0)
    
    links.forEach(link => {
      expect(link).toHaveAttribute('href', '#')
    })
  })
})
