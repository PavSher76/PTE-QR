import { 
  formatDate, 
  formatFileSize, 
  debounce, 
  generateId, 
  formatRelativeTime,
  isValidEmail,
  isValidUrl,
  truncateText,
  capitalizeFirst
} from '../lib/utils'

describe('Utils', () => {
  describe('formatDate', () => {
    it('formats date correctly with Russian locale', () => {
      const date = new Date('2024-01-15T10:30:00Z')
      const formatted = formatDate(date)
      // Check that it's a valid date string (Russian locale format)
      expect(formatted).toContain('2024')
      expect(formatted).toContain('г.')
    })

    it('formats date with English locale', () => {
      const date = new Date('2024-01-15T10:30:00Z')
      const formatted = formatDate(date, 'en-US')
      expect(formatted).toContain('2024')
      expect(formatted).toContain('January')
    })

    it('handles string date input', () => {
      const formatted = formatDate('2024-01-15T10:30:00Z')
      expect(formatted).toContain('2024')
    })

    it('handles invalid date', () => {
      const formatted = formatDate(new Date('invalid'))
      expect(formatted).toBe('Invalid Date')
    })
  })

  describe('formatRelativeTime', () => {
    it('formats recent time correctly', () => {
      const now = new Date()
      const oneMinuteAgo = new Date(now.getTime() - 60000)
      const formatted = formatRelativeTime(oneMinuteAgo)
      expect(formatted).toContain('мин.')
    })

    it('formats time with English locale', () => {
      const now = new Date()
      const oneHourAgo = new Date(now.getTime() - 3600000)
      const formatted = formatRelativeTime(oneHourAgo, 'en-US')
      expect(formatted).toContain('hrs')
    })
  })

  describe('generateId', () => {
    it('generates id with default length', () => {
      const id = generateId()
      expect(id).toHaveLength(8)
      expect(id).toMatch(/^[A-Za-z0-9]+$/)
    })

    it('generates id with custom length', () => {
      const id = generateId(12)
      expect(id).toHaveLength(12)
    })

    it('generates unique ids', () => {
      const id1 = generateId()
      const id2 = generateId()
      expect(id1).not.toBe(id2)
    })
  })

  describe('formatFileSize', () => {
    it('formats bytes correctly', () => {
      expect(formatFileSize(1024)).toBe('1.0 KB')
      expect(formatFileSize(1048576)).toBe('1.0 MB')
      expect(formatFileSize(1073741824)).toBe('1.0 GB')
    })

    it('handles zero size', () => {
      expect(formatFileSize(0)).toBe('0.0 B')
    })

    it('handles small sizes', () => {
      expect(formatFileSize(500)).toBe('500.0 B')
    })
  })

  describe('isValidEmail', () => {
    it('validates correct emails', () => {
      expect(isValidEmail('test@example.com')).toBe(true)
      expect(isValidEmail('user.name@domain.co.uk')).toBe(true)
    })

    it('rejects invalid emails', () => {
      expect(isValidEmail('invalid-email')).toBe(false)
      expect(isValidEmail('@domain.com')).toBe(false)
      expect(isValidEmail('user@')).toBe(false)
    })
  })

  describe('isValidUrl', () => {
    it('validates correct URLs', () => {
      expect(isValidUrl('https://example.com')).toBe(true)
      expect(isValidUrl('http://localhost:3000')).toBe(true)
    })

    it('rejects invalid URLs', () => {
      expect(isValidUrl('not-a-url')).toBe(false)
      expect(isValidUrl('ftp://example.com')).toBe(false)
    })
  })

  describe('truncateText', () => {
    it('truncates long text', () => {
      const longText = 'This is a very long text that should be truncated'
      const truncated = truncateText(longText, 20)
      expect(truncated).toHaveLength(23) // 20 + '...'
      expect(truncated.endsWith('...')).toBe(true)
    })

    it('does not truncate short text', () => {
      const shortText = 'Short text'
      const result = truncateText(shortText, 20)
      expect(result).toBe(shortText)
    })
  })

  describe('capitalizeFirst', () => {
    it('capitalizes first letter', () => {
      expect(capitalizeFirst('hello')).toBe('Hello')
      expect(capitalizeFirst('world')).toBe('World')
    })

    it('handles empty string', () => {
      expect(capitalizeFirst('')).toBe('')
    })
  })

  describe('debounce', () => {
    beforeEach(() => {
      jest.useFakeTimers()
    })

    afterEach(() => {
      jest.useRealTimers()
    })

    it('delays function execution', () => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn()
      expect(mockFn).not.toHaveBeenCalled()

      jest.advanceTimersByTime(100)
      expect(mockFn).toHaveBeenCalledTimes(1)
    })

    it('cancels previous calls', () => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn()
      debouncedFn()
      debouncedFn()

      jest.advanceTimersByTime(100)
      expect(mockFn).toHaveBeenCalledTimes(1)
    })
  })
})
