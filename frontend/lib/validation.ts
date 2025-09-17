/**
 * Validation utilities
 */

export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => boolean | string
}

export interface ValidationResult {
  isValid: boolean
  errors: string[]
}

export interface ValidationSchema {
  [key: string]: ValidationRule
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function validateURL(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

export function validatePhone(phone: string): boolean {
  const phoneRegex = /^\+?[\d\s\-\(\)]+$/
  return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10
}

export function validatePassword(password: string): boolean {
  return (
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /\d/.test(password)
  )
}

export function validateDocumentId(docId: string): boolean {
  const docIdRegex = /^[A-Z0-9\-]+$/
  return docIdRegex.test(docId) && docId.length >= 5
}

export function validateQRCode(qrCode: string): boolean {
  return qrCode.includes('qr.pti.ru') || qrCode.includes('example.com')
}

export function validateForm(data: any, rules: any): boolean {
  for (const field in rules) {
    if (rules[field].required && !data[field]) {
      return false
    }
  }
  return true
}

export function escapeHTML(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

export function unescapeHTML(html: string): string {
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

export function validateField(
  value: any,
  rules: ValidationRule,
  language: 'ru' | 'en' = 'ru'
): string[] {
  const errors: string[] = []

  if (
    rules.required &&
    (value === undefined || value === null || value === '')
  ) {
    errors.push(
      language === 'ru'
        ? 'Поле обязательно для заполнения'
        : 'Field is required'
    )
  }

  if (value !== undefined && value !== null && value !== '') {
    if (rules.minLength && value.length < rules.minLength) {
      errors.push(
        language === 'ru'
          ? `Минимальная длина: ${rules.minLength} символов`
          : `Minimum length: ${rules.minLength} characters`
      )
    }

    if (rules.maxLength && value.length > rules.maxLength) {
      errors.push(
        language === 'ru'
          ? `Максимальная длина: ${rules.maxLength} символов`
          : `Maximum length: ${rules.maxLength} characters`
      )
    }

    if (rules.pattern && !rules.pattern.test(value)) {
      errors.push(
        language === 'ru' ? 'Неверный формат данных' : 'Invalid format'
      )
    }

    if (rules.custom) {
      const customResult = rules.custom(value)
      if (customResult !== true) {
        errors.push(
          typeof customResult === 'string' ? customResult : 'Invalid value'
        )
      }
    }
  }

  return errors
}

export function validateObject(
  data: any,
  schema: ValidationSchema,
  language: 'ru' | 'en' = 'ru'
): ValidationResult {
  const errors: string[] = []

  for (const [field, rules] of Object.entries(schema)) {
    const fieldErrors = validateField(data[field], rules, language)
    errors.push(...fieldErrors.map((error) => `${field}: ${error}`))
  }

  return {
    isValid: errors.length === 0,
    errors,
  }
}

export const VALIDATION_PATTERNS = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^\+?[1-9]\d{1,14}$/,
  url: /^https?:\/\/.+/,
  docUid: /^[A-Za-z0-9_-]+$/,
  revision: /^[A-Za-z0-9._-]+$/,
  page: /^\d+$/,
  timestamp: /^\d{10}$/,
  signature: /^[A-Fa-f0-9]+$/,
}

export const VALIDATION_RULES = {
  email: {
    required: true,
    pattern: VALIDATION_PATTERNS.email,
  },
  phone: {
    required: true,
    pattern: VALIDATION_PATTERNS.phone,
  },
  url: {
    required: true,
    pattern: VALIDATION_PATTERNS.url,
  },
  docUid: {
    required: true,
    minLength: 1,
    maxLength: 100,
    pattern: VALIDATION_PATTERNS.docUid,
  },
  revision: {
    required: true,
    minLength: 1,
    maxLength: 50,
    pattern: VALIDATION_PATTERNS.revision,
  },
  page: {
    required: true,
    pattern: VALIDATION_PATTERNS.page,
    custom: (value: string) => {
      const pageNum = parseInt(value, 10)
      return pageNum > 0 && pageNum <= 10000
    },
  },
  timestamp: {
    required: true,
    pattern: VALIDATION_PATTERNS.timestamp,
    custom: (value: string) => {
      const timestamp = parseInt(value, 10)
      const now = Math.floor(Date.now() / 1000)
      const oneYearAgo = now - 365 * 24 * 60 * 60
      return timestamp >= oneYearAgo && timestamp <= now
    },
  },
  signature: {
    required: true,
    pattern: VALIDATION_PATTERNS.signature,
    custom: (value: string) => value.length === 64, // SHA-256 hex length
  },
}

export function validateQRCodeParams(
  params: any,
  language: 'ru' | 'en' = 'ru'
): ValidationResult {
  const schema: ValidationSchema = {
    docUid: VALIDATION_RULES.docUid,
    revision: VALIDATION_RULES.revision,
    page: VALIDATION_RULES.page,
    timestamp: VALIDATION_RULES.timestamp,
    signature: VALIDATION_RULES.signature,
  }

  return validateObject(params, schema, language)
}

export function validateDocumentStatus(
  data: any,
  language: 'ru' | 'en' = 'ru'
): ValidationResult {
  const schema: ValidationSchema = {
    docUid: VALIDATION_RULES.docUid,
    revision: VALIDATION_RULES.revision,
    page: VALIDATION_RULES.page,
  }

  return validateObject(data, schema, language)
}

export function validateQRCodeRequest(
  data: any,
  language: 'ru' | 'en' = 'ru'
): ValidationResult {
  const schema: ValidationSchema = {
    docUid: VALIDATION_RULES.docUid,
    revision: VALIDATION_RULES.revision,
    page: VALIDATION_RULES.page,
  }

  return validateObject(data, schema, language)
}

export function validateStatusMapping(
  data: any,
  language: 'ru' | 'en' = 'ru'
): ValidationResult {
  const schema: ValidationSchema = {
    enoviaState: {
      required: true,
      minLength: 1,
      maxLength: 100,
    },
    businessStatus: {
      required: true,
      minLength: 1,
      maxLength: 100,
    },
    isActual: {
      required: true,
      custom: (value: any) => typeof value === 'boolean',
    },
  }

  return validateObject(data, schema, language)
}

export function sanitizeInput(input: string): string {
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/['"]/g, '') // Remove quotes
    .replace(/[;]/g, '') // Remove semicolons
    .substring(0, 1000) // Limit length
}

export function sanitizeObject(obj: any): any {
  if (typeof obj === 'string') {
    return sanitizeInput(obj)
  }

  if (Array.isArray(obj)) {
    return obj.map(sanitizeObject)
  }

  if (obj && typeof obj === 'object') {
    const sanitized: any = {}
    for (const [key, value] of Object.entries(obj)) {
      sanitized[key] = sanitizeObject(value)
    }
    return sanitized
  }

  return obj
}
