import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Logo } from '../components/Logo'

describe('Logo', () => {
  it('renders with default props', () => {
    render(<Logo />)

    const logo = screen.getByAltText('PTE QR Logo')
    expect(logo).toBeInTheDocument()
    expect(logo).toHaveAttribute('src', '/images/logo-compact.svg')
  })

  it('renders with large size and full variant', () => {
    render(<Logo size="large" variant="full" />)

    const logo = screen.getByAltText('PTE QR Logo')
    expect(logo).toBeInTheDocument()
    expect(logo).toHaveAttribute('src', '/images/logo.svg')
    expect(logo).toHaveAttribute('width', '64')
    expect(logo).toHaveAttribute('height', '64')
  })

  it('renders with small size and compact variant', () => {
    render(<Logo size="small" variant="compact" />)

    const logo = screen.getByAltText('PTE QR Logo')
    expect(logo).toBeInTheDocument()
    expect(logo).toHaveAttribute('src', '/images/logo-compact.svg')
    expect(logo).toHaveAttribute('width', '24')
    expect(logo).toHaveAttribute('height', '24')
  })

  it('applies custom className', () => {
    render(<Logo className="custom-class" />)

    const logoContainer = screen.getByAltText('PTE QR Logo').parentElement
    expect(logoContainer).toHaveClass('custom-class')
  })
})
