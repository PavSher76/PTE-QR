/**
 * General utility functions
 */

export function formatDate(
  date: Date | string,
  locale: string = 'ru-RU'
): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRelativeTime(
  date: Date | string,
  locale: string = 'ru-RU'
): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diff = now.getTime() - d.getTime()

  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) {
    return `${days} ${locale === 'ru-RU' ? 'дн.' : 'days'} назад`
  } else if (hours > 0) {
    return `${hours} ${locale === 'ru-RU' ? 'ч.' : 'hrs'} назад`
  } else if (minutes > 0) {
    return `${minutes} ${locale === 'ru-RU' ? 'мин.' : 'min'} назад`
  } else {
    return locale === 'ru-RU' ? 'только что' : 'just now'
  }
}

export function generateId(length: number = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  if (typeof func !== 'function') {
    throw new Error('First argument must be a function')
  }

  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }

    timeout = setTimeout(() => {
      try {
        func(...args)
      } catch (error) {
        console.error('Error in debounced function:', error)
      }
    }, wait)
  }
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  if (typeof func !== 'function') {
    throw new Error('First argument must be a function')
  }

  let inThrottle: boolean = false

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      try {
        func(...args)
      } catch (error) {
        console.error('Error in throttled function:', error)
      }
      inThrottle = true
      setTimeout(
        () => {
          inThrottle = false
        },
        Math.max(0, limit)
      )
    }
  }
}

export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T
  }

  if (obj instanceof Array) {
    return obj.map((item) => deepClone(item)) as T
  }

  if (typeof obj === 'object') {
    const cloned = {} as T
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key])
      }
    }
    return cloned
  }

  return obj
}

export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) {
    return true
  }

  if (typeof value === 'string') {
    return value.trim().length === 0
  }

  if (Array.isArray(value)) {
    return value.length === 0
  }

  // Handle Date objects
  if (value instanceof Date) {
    return false
  }

  if (typeof value === 'object') {
    return Object.keys(value).length === 0
  }

  return false
}

export function capitalize(str: string): string {
  if (!str || typeof str !== 'string') {
    return ''
  }
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

export function camelCase(str: string): string {
  if (!str || typeof str !== 'string') {
    return ''
  }
  return str.replace(/[-_]([a-z])/g, (g) => g[1].toUpperCase())
}

export function kebabCase(str: string): string {
  if (!str || typeof str !== 'string') {
    return ''
  }
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/_/g, '-')
    .toLowerCase()
}

export function truncate(
  str: string,
  length: number,
  suffix: string = '...'
): string {
  if (!str || typeof str !== 'string') {
    return ''
  }

  if (str.length <= length) {
    return str
  }
  return str.substring(0, length - suffix.length) + suffix
}

export function escapeHtml(str: string): string {
  if (!str || typeof str !== 'string') {
    return ''
  }

  const div = document.createElement('div')
  div.textContent = str
  return div.innerHTML
}

export function unescapeHtml(str: string): string {
  if (!str || typeof str !== 'string') {
    return ''
  }

  const div = document.createElement('div')
  div.innerHTML = str
  return div.textContent || div.innerText || ''
}

export function parseQueryString(query: string): Record<string, string> {
  if (!query || typeof query !== 'string') {
    return {}
  }

  const params: Record<string, string> = {}
  const pairs = query.split('&')

  for (const pair of pairs) {
    const [key, value] = pair.split('=')
    if (key) {
      params[decodeURIComponent(key)] = decodeURIComponent(value || '')
    }
  }

  return params
}

export function buildQueryString(params: Record<string, any>): string {
  if (!params || typeof params !== 'object') {
    return ''
  }

  const pairs: string[] = []

  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined) {
      if (Array.isArray(value)) {
        pairs.push(
          `${encodeURIComponent(key)}=${encodeURIComponent(value.join(','))}`
        )
      } else {
        pairs.push(
          `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`
        )
      }
    }
  }

  return pairs.join('&')
}

export function getFileExtension(filename: string): string {
  if (!filename || typeof filename !== 'string') {
    return ''
  }
  return filename.split('.').pop()?.toLowerCase() || ''
}

export function formatFileSize(bytes: number): string {
  if (bytes === null || bytes === undefined || isNaN(bytes)) {
    return '0 B'
  }

  if (bytes === Infinity) {
    return 'Infinity B'
  }

  if (bytes < 0) {
    return formatFileSize(Math.abs(bytes)).replace(/^/, '-')
  }

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`
}

export function downloadFile(
  data: Blob | string,
  filename: string,
  mimeType?: string
): void {
  const blob =
    typeof data === 'string'
      ? new Blob([data], { type: mimeType || 'text/plain' })
      : data
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  URL.revokeObjectURL(url)
}

export function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text || '')
  } else {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text || ''
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()

    return new Promise((resolve, reject) => {
      if (document.execCommand('copy')) {
        resolve()
      } else {
        reject(new Error('Failed to copy to clipboard'))
      }
      document.body.removeChild(textArea)
    })
  }
}

export function isMobile(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
}

export function isTouchDevice(): boolean {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

export function getDeviceType(): 'mobile' | 'tablet' | 'desktop' {
  const width = window.innerWidth
  if (width < 768) return 'mobile'
  if (width < 1024) return 'tablet'
  return 'desktop'
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function retry<T>(
  fn: () => Promise<T>,
  maxAttempts: number = 3,
  delay: number = 1000
): Promise<T> {
  if (typeof fn !== 'function') {
    return Promise.reject(new Error('First argument must be a function'))
  }

  if (maxAttempts <= 0) {
    return Promise.reject(new Error('maxAttempts must be greater than 0'))
  }

  return new Promise((resolve, reject) => {
    let attempts = 0

    const attempt = () => {
      attempts++
      const result = fn()

      if (!result || typeof result.then !== 'function') {
        reject(new Error('Function must return a Promise'))
        return
      }

      result.then(resolve).catch((error) => {
        if (attempts >= maxAttempts) {
          reject(error)
        } else {
          setTimeout(attempt, Math.max(0, delay))
        }
      })
    }

    attempt()
  })
}

export function groupBy<T, K extends string | number>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, T[]> {
  if (!array || !Array.isArray(array)) {
    return {} as Record<K, T[]>
  }

  return array.reduce(
    (groups, item) => {
      const key = keyFn(item)
      if (!groups[key]) {
        groups[key] = []
      }
      groups[key].push(item)
      return groups
    },
    {} as Record<K, T[]>
  )
}

export function sortBy<T>(
  array: T[],
  keyFn: (item: T) => string | number,
  direction: 'asc' | 'desc' = 'asc'
): T[] {
  if (!array || !Array.isArray(array)) {
    return []
  }

  // Normalize direction to valid values
  const normalizedDirection = direction === 'desc' ? 'desc' : 'asc'

  return [...array].sort((a, b) => {
    const aVal = keyFn(a)
    const bVal = keyFn(b)

    // Handle null/undefined values
    if (aVal == null && bVal == null) return 0
    if (aVal == null) return normalizedDirection === 'asc' ? -1 : 1
    if (bVal == null) return normalizedDirection === 'asc' ? 1 : -1

    // Handle mixed types
    if (typeof aVal !== typeof bVal) {
      const aType = typeof aVal
      const bType = typeof bVal
      if (aType < bType) return normalizedDirection === 'asc' ? -1 : 1
      if (aType > bType) return normalizedDirection === 'asc' ? 1 : -1
    }

    if (aVal < bVal) return normalizedDirection === 'asc' ? -1 : 1
    if (aVal > bVal) return normalizedDirection === 'asc' ? 1 : -1
    return 0
  })
}

export function unique<T>(array: T[]): T[] {
  return Array.from(new Set(array))
}

export function chunk<T>(array: T[], size: number): T[][] {
  if (!array || !Array.isArray(array) || size <= 0) {
    return []
  }

  const chunks: T[][] = []
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size))
  }
  return chunks
}

// Validation functions
export function isValidEmail(email: string): boolean {
  if (!email || typeof email !== 'string') {
    return false
  }

  // Check length limit (RFC 5321)
  if (email.length > 254) {
    return false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function isValidUrl(url: string): boolean {
  try {
    const urlObj = new URL(url)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
  } catch {
    return false
  }
}

// Text utility functions
export function truncateText(
  text: string,
  maxLength: number,
  suffix: string = '...'
): string {
  if (!text || typeof text !== 'string') {
    return ''
  }

  if (text.length <= maxLength) {
    return text
  }
  return text.substring(0, maxLength) + suffix
}

export function capitalizeFirst(text: string): string {
  if (!text || typeof text !== 'string') return ''
  return text.charAt(0).toUpperCase() + text.slice(1)
}
