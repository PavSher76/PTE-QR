import {
  formatDate,
  formatFileSize,
  debounce,
  generateId,
  formatRelativeTime,
  isValidEmail,
  isValidUrl,
  truncateText,
  capitalizeFirst,
  throttle,
  deepClone,
  isEmpty,
  capitalize,
  camelCase,
  kebabCase,
  truncate,
  escapeHtml,
  unescapeHtml,
  parseQueryString,
  buildQueryString,
  getFileExtension,
  downloadFile,
  copyToClipboard,
  isMobile,
  isTouchDevice,
  getDeviceType,
  sleep,
  retry,
  groupBy,
  sortBy,
  unique,
  chunk,
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

  describe('throttle', () => {
    beforeEach(() => {
      jest.useFakeTimers()
    })

    afterEach(() => {
      jest.useRealTimers()
    })

    it('throttles function execution', () => {
      const mockFn = jest.fn()
      const throttledFn = throttle(mockFn, 100)

      throttledFn()
      throttledFn()
      throttledFn()

      expect(mockFn).toHaveBeenCalledTimes(1)

      jest.advanceTimersByTime(100)
      throttledFn()
      expect(mockFn).toHaveBeenCalledTimes(2)
    })
  })

  describe('deepClone', () => {
    it('clones primitive values', () => {
      expect(deepClone(42)).toBe(42)
      expect(deepClone('hello')).toBe('hello')
      expect(deepClone(true)).toBe(true)
      expect(deepClone(null)).toBe(null)
    })

    it('clones arrays', () => {
      const original = [1, 2, { a: 3 }]
      const cloned = deepClone(original)

      expect(cloned).toEqual(original)
      expect(cloned).not.toBe(original)
      expect(cloned[2]).not.toBe(original[2])
    })

    it('clones objects', () => {
      const original = { a: 1, b: { c: 2 } }
      const cloned = deepClone(original)

      expect(cloned).toEqual(original)
      expect(cloned).not.toBe(original)
      expect(cloned.b).not.toBe(original.b)
    })

    it('clones dates', () => {
      const original = new Date('2024-01-15')
      const cloned = deepClone(original)

      expect(cloned).toEqual(original)
      expect(cloned).not.toBe(original)
    })
  })

  describe('isEmpty', () => {
    it('returns true for empty values', () => {
      expect(isEmpty(null)).toBe(true)
      expect(isEmpty(undefined)).toBe(true)
      expect(isEmpty('')).toBe(true)
      expect(isEmpty('   ')).toBe(true)
      expect(isEmpty([])).toBe(true)
      expect(isEmpty({})).toBe(true)
    })

    it('returns false for non-empty values', () => {
      expect(isEmpty(0)).toBe(false)
      expect(isEmpty(false)).toBe(false)
      expect(isEmpty('hello')).toBe(false)
      expect(isEmpty([1, 2, 3])).toBe(false)
      expect(isEmpty({ a: 1 })).toBe(false)
    })
  })

  describe('capitalize', () => {
    it('capitalizes first letter and lowercases rest', () => {
      expect(capitalize('hello')).toBe('Hello')
      expect(capitalize('WORLD')).toBe('World')
      expect(capitalize('hELLo')).toBe('Hello')
    })
  })

  describe('camelCase', () => {
    it('converts kebab-case to camelCase', () => {
      expect(camelCase('hello-world')).toBe('helloWorld')
      expect(camelCase('my-component-name')).toBe('myComponentName')
    })
  })

  describe('kebabCase', () => {
    it('converts camelCase to kebab-case', () => {
      expect(kebabCase('helloWorld')).toBe('hello-world')
      expect(kebabCase('myComponentName')).toBe('my-component-name')
    })
  })

  describe('truncate', () => {
    it('truncates long strings', () => {
      expect(truncate('hello world', 5)).toBe('he...')
      expect(truncate('hello world', 5, '...')).toBe('he...')
    })

    it('does not truncate short strings', () => {
      expect(truncate('hello', 10)).toBe('hello')
    })
  })

  describe('escapeHtml', () => {
    it('escapes HTML characters', () => {
      expect(escapeHtml('<div>hello</div>')).toBe(
        '&lt;div&gt;hello&lt;/div&gt;'
      )
      expect(escapeHtml('& "quoted"')).toBe('&amp; "quoted"')
    })
  })

  describe('unescapeHtml', () => {
    it('unescapes HTML characters', () => {
      expect(unescapeHtml('&lt;div&gt;hello&lt;/div&gt;')).toBe(
        '<div>hello</div>'
      )
      expect(unescapeHtml('&amp; &quot;quoted&quot;')).toBe('& "quoted"')
    })
  })

  describe('parseQueryString', () => {
    it('parses query string', () => {
      const result = parseQueryString('a=1&b=2&c=hello')
      expect(result).toEqual({ a: '1', b: '2', c: 'hello' })
    })

    it('handles empty query string', () => {
      expect(parseQueryString('')).toEqual({})
    })
  })

  describe('buildQueryString', () => {
    it('builds query string from object', () => {
      const result = buildQueryString({ a: 1, b: 'hello', c: null })
      expect(result).toBe('a=1&b=hello')
    })

    it('handles empty object', () => {
      expect(buildQueryString({})).toBe('')
    })
  })

  describe('getFileExtension', () => {
    it('extracts file extension', () => {
      expect(getFileExtension('file.txt')).toBe('txt')
      expect(getFileExtension('image.jpg')).toBe('jpg')
      expect(getFileExtension('noextension')).toBe('noextension')
    })
  })

  describe('downloadFile', () => {
    beforeEach(() => {
      // Mock DOM methods
      global.URL.createObjectURL = jest.fn(() => 'mock-url')
      global.URL.revokeObjectURL = jest.fn()
      document.createElement = jest.fn(() => ({
        href: '',
        download: '',
        click: jest.fn(),
      })) as any
      document.body.appendChild = jest.fn()
      document.body.removeChild = jest.fn()
    })

    it('downloads blob data', () => {
      const blob = new Blob(['test data'])
      downloadFile(blob, 'test.txt')

      expect(global.URL.createObjectURL).toHaveBeenCalledWith(blob)
    })

    it('downloads string data', () => {
      downloadFile('test data', 'test.txt', 'text/plain')

      expect(global.URL.createObjectURL).toHaveBeenCalled()
    })
  })

  describe('copyToClipboard', () => {
    beforeEach(() => {
      // Mock clipboard API
      Object.assign(navigator, {
        clipboard: {
          writeText: jest.fn().mockResolvedValue(undefined),
        },
      })
      global.window.isSecureContext = true
    })

    it('copies text to clipboard', async () => {
      await copyToClipboard('test text')
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('test text')
    })
  })

  describe('isMobile', () => {
    it('detects mobile user agents', () => {
      Object.defineProperty(navigator, 'userAgent', {
        value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
        writable: true,
      })
      expect(isMobile()).toBe(true)
    })

    it('detects non-mobile user agents', () => {
      Object.defineProperty(navigator, 'userAgent', {
        value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        writable: true,
      })
      expect(isMobile()).toBe(false)
    })
  })

  describe('isTouchDevice', () => {
    it('detects touch devices', () => {
      Object.defineProperty(window, 'ontouchstart', {
        value: {},
        writable: true,
      })
      expect(isTouchDevice()).toBe(true)
    })

    it('detects non-touch devices', () => {
      Object.defineProperty(window, 'ontouchstart', {
        value: undefined,
        writable: true,
      })
      Object.defineProperty(navigator, 'maxTouchPoints', {
        value: 0,
        writable: true,
      })
      // Reset the property to ensure it's undefined
      delete (window as any).ontouchstart
      expect(isTouchDevice()).toBe(false)
    })
  })

  describe('getDeviceType', () => {
    it('detects mobile devices', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 500,
        writable: true,
      })
      expect(getDeviceType()).toBe('mobile')
    })

    it('detects tablet devices', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 900,
        writable: true,
      })
      expect(getDeviceType()).toBe('tablet')
    })

    it('detects desktop devices', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 1200,
        writable: true,
      })
      expect(getDeviceType()).toBe('desktop')
    })
  })

  describe('sleep', () => {
    it('waits for specified time', async () => {
      const start = Date.now()
      await sleep(100)
      const end = Date.now()
      expect(end - start).toBeGreaterThanOrEqual(100)
    })
  })

  describe('retry', () => {
    it('retries failed function', async () => {
      let attempts = 0
      const fn = jest.fn().mockImplementation(() => {
        attempts++
        if (attempts < 3) {
          return Promise.reject(new Error('Failed'))
        }
        return Promise.resolve('Success')
      })

      const result = await retry(fn, 3, 10)
      expect(result).toBe('Success')
      expect(fn).toHaveBeenCalledTimes(3)
    })

    it('fails after max attempts', async () => {
      const fn = jest.fn().mockRejectedValue(new Error('Always fails'))

      await expect(retry(fn, 2, 10)).rejects.toThrow('Always fails')
      expect(fn).toHaveBeenCalledTimes(2)
    })
  })

  describe('groupBy', () => {
    it('groups array by key function', () => {
      const items = [
        { category: 'a', value: 1 },
        { category: 'b', value: 2 },
        { category: 'a', value: 3 },
      ]

      const result = groupBy(items, (item) => item.category)
      expect(result).toEqual({
        a: [
          { category: 'a', value: 1 },
          { category: 'a', value: 3 },
        ],
        b: [{ category: 'b', value: 2 }],
      })
    })
  })

  describe('sortBy', () => {
    it('sorts array by key function ascending', () => {
      const items = [{ value: 3 }, { value: 1 }, { value: 2 }]
      const result = sortBy(items, (item) => item.value)
      expect(result).toEqual([{ value: 1 }, { value: 2 }, { value: 3 }])
    })

    it('sorts array by key function descending', () => {
      const items = [{ value: 1 }, { value: 3 }, { value: 2 }]
      const result = sortBy(items, (item) => item.value, 'desc')
      expect(result).toEqual([{ value: 3 }, { value: 2 }, { value: 1 }])
    })
  })

  describe('unique', () => {
    it('removes duplicates from array', () => {
      expect(unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3])
      expect(unique(['a', 'b', 'a', 'c'])).toEqual(['a', 'b', 'c'])
    })
  })

  describe('chunk', () => {
    it('splits array into chunks', () => {
      expect(chunk([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]])
      expect(chunk([1, 2, 3, 4], 2)).toEqual([
        [1, 2],
        [3, 4],
      ])
    })
  })
})
