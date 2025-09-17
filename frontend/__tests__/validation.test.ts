import {
  validateEmail,
  validateURL,
  validatePhone,
  validateDocumentId,
  validateQRCode,
  validateForm,
  sanitizeInput,
  escapeHTML,
  unescapeHTML,
} from '../lib/validation'

describe('Validation Functions', () => {
  it('should export all functions', () => {
    expect(validateEmail).toBeDefined()
    expect(validateURL).toBeDefined()
    expect(validatePhone).toBeDefined()
    expect(validateDocumentId).toBeDefined()
    expect(validateQRCode).toBeDefined()
    expect(validateForm).toBeDefined()
    expect(sanitizeInput).toBeDefined()
    expect(escapeHTML).toBeDefined()
    expect(unescapeHTML).toBeDefined()
  })

  it('should be functions', () => {
    expect(typeof validateEmail).toBe('function')
    expect(typeof validateURL).toBe('function')
    expect(typeof validatePhone).toBe('function')
    expect(typeof validateDocumentId).toBe('function')
    expect(typeof validateQRCode).toBe('function')
    expect(typeof validateForm).toBe('function')
    expect(typeof sanitizeInput).toBe('function')
    expect(typeof escapeHTML).toBe('function')
    expect(typeof unescapeHTML).toBe('function')
  })

  it('should validate email', () => {
    expect(validateEmail('test@example.com')).toBe(true)
    expect(validateEmail('invalid-email')).toBe(false)
  })

  it('should validate URL', () => {
    expect(validateURL('https://example.com')).toBe(true)
    expect(validateURL('invalid-url')).toBe(false)
  })

  it('should validate phone', () => {
    expect(validatePhone('+1234567890')).toBe(true)
    expect(validatePhone('invalid-phone')).toBe(false)
  })

  it('should validate document ID', () => {
    expect(validateDocumentId('3D-00001234')).toBe(true)
    expect(validateDocumentId('invalid-id')).toBe(false)
  })

  it('should validate QR code', () => {
    expect(validateQRCode('https://qr.pti.ru/r/3D-00001234/B/3')).toBe(true)
    expect(validateQRCode('invalid-qr')).toBe(false)
  })

  it('should validate form', () => {
    const formData = { email: 'test@example.com', password: 'Password123!' }
    const rules = { email: 'required|email', password: 'required|min:8' }
    expect(validateForm(formData, rules)).toBe(true)
  })

  it('should sanitize input', () => {
    expect(sanitizeInput('<script>alert("xss")</script>')).toBe(
      'scriptalert(xss)/script'
    )
  })

  it('should escape HTML', () => {
    expect(escapeHTML('<div>test</div>')).toBe('&lt;div&gt;test&lt;/div&gt;')
  })

  it('should unescape HTML', () => {
    expect(unescapeHTML('&lt;div&gt;test&lt;/div&gt;')).toBe('<div>test</div>')
  })
})
