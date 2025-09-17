/**
 * Error handling utilities
 */

export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: number
  stack?: string
}

export class AppError extends Error {
  public code: string
  public statusCode: number
  public details?: any
  public timestamp: number

  constructor(message: string, code: string, statusCode: number = 500, details?: any) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.statusCode = statusCode
    this.details = details
    this.timestamp = Date.now()
  }
}

export class ValidationError extends AppError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 400)
    this.name = 'ValidationError'
  }
}

export class NetworkError extends AppError {
  constructor(message: string) {
    super(message, 'NETWORK_ERROR', 0)
    this.name = 'NetworkError'
  }
}

export class AuthError extends AppError {
  constructor(message: string) {
    super(message, 'AUTH_ERROR', 401)
    this.name = 'AuthError'
  }
}

export class NotFoundError extends AppError {
  constructor(message: string) {
    super(message, 'NOT_FOUND_ERROR', 404)
    this.name = 'NotFoundError'
  }
}

export class ServerError extends AppError {
  constructor(message: string) {
    super(message, 'SERVER_ERROR', 500)
    this.name = 'ServerError'
  }
}

export class PTEQRError extends Error {
  public code: string
  public details?: any
  public timestamp: number

  constructor(code: string, message: string, details?: any) {
    super(message)
    this.name = 'PTEQRError'
    this.code = code
    this.details = details
    this.timestamp = Date.now()
  }
}

export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  CONNECTION_ERROR: 'CONNECTION_ERROR',
  API_ERROR: 'API_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  QR_INVALID_FORMAT: 'QR_INVALID_FORMAT',
  QR_INVALID_SIGNATURE: 'QR_INVALID_SIGNATURE',
  QR_EXPIRED: 'QR_EXPIRED',
  QR_SCAN_FAILED: 'QR_SCAN_FAILED',
  DOCUMENT_NOT_FOUND: 'DOCUMENT_NOT_FOUND',
  REVISION_NOT_FOUND: 'REVISION_NOT_FOUND',
  DOCUMENT_ACCESS_DENIED: 'DOCUMENT_ACCESS_DENIED',
  CAMERA_ACCESS_DENIED: 'CAMERA_ACCESS_DENIED',
  CAMERA_NOT_AVAILABLE: 'CAMERA_NOT_AVAILABLE',
  CAMERA_ERROR: 'CAMERA_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
  VALIDATION_FAILED: 'VALIDATION_FAILED',
  OPERATION_FAILED: 'OPERATION_FAILED',
} as const

export const ERROR_MESSAGES = {
  ru: {
    [ERROR_CODES.NETWORK_ERROR]:
      'Ошибка сети. Проверьте подключение к интернету.',
    [ERROR_CODES.TIMEOUT_ERROR]: 'Превышено время ожидания ответа от сервера.',
    [ERROR_CODES.CONNECTION_ERROR]: 'Ошибка подключения к серверу.',
    [ERROR_CODES.API_ERROR]: 'Ошибка API сервера.',
    [ERROR_CODES.UNAUTHORIZED]:
      'Необходима авторизация для выполнения операции.',
    [ERROR_CODES.FORBIDDEN]: 'Доступ запрещен.',
    [ERROR_CODES.NOT_FOUND]: 'Запрашиваемый ресурс не найден.',
    [ERROR_CODES.VALIDATION_ERROR]: 'Ошибка валидации данных.',
    [ERROR_CODES.SERVER_ERROR]: 'Внутренняя ошибка сервера.',
    [ERROR_CODES.QR_INVALID_FORMAT]: 'Неверный формат QR-кода.',
    [ERROR_CODES.QR_INVALID_SIGNATURE]: 'Неверная подпись QR-кода.',
    [ERROR_CODES.QR_EXPIRED]: 'QR-код устарел.',
    [ERROR_CODES.QR_SCAN_FAILED]: 'Ошибка при сканировании QR-кода.',
    [ERROR_CODES.DOCUMENT_NOT_FOUND]: 'Документ не найден.',
    [ERROR_CODES.REVISION_NOT_FOUND]: 'Ревизия документа не найдена.',
    [ERROR_CODES.DOCUMENT_ACCESS_DENIED]: 'Доступ к документу запрещен.',
    [ERROR_CODES.CAMERA_ACCESS_DENIED]: 'Доступ к камере запрещен.',
    [ERROR_CODES.CAMERA_NOT_AVAILABLE]: 'Камера недоступна.',
    [ERROR_CODES.CAMERA_ERROR]: 'Ошибка камеры.',
    [ERROR_CODES.UNKNOWN_ERROR]: 'Неизвестная ошибка.',
    [ERROR_CODES.VALIDATION_FAILED]: 'Ошибка валидации.',
    [ERROR_CODES.OPERATION_FAILED]: 'Операция не выполнена.',
  },
  en: {
    [ERROR_CODES.NETWORK_ERROR]:
      'Network error. Check your internet connection.',
    [ERROR_CODES.TIMEOUT_ERROR]: 'Server response timeout exceeded.',
    [ERROR_CODES.CONNECTION_ERROR]: 'Server connection error.',
    [ERROR_CODES.API_ERROR]: 'API server error.',
    [ERROR_CODES.UNAUTHORIZED]: 'Authorization required for this operation.',
    [ERROR_CODES.FORBIDDEN]: 'Access denied.',
    [ERROR_CODES.NOT_FOUND]: 'Requested resource not found.',
    [ERROR_CODES.VALIDATION_ERROR]: 'Data validation error.',
    [ERROR_CODES.SERVER_ERROR]: 'Internal server error.',
    [ERROR_CODES.QR_INVALID_FORMAT]: 'Invalid QR code format.',
    [ERROR_CODES.QR_INVALID_SIGNATURE]: 'Invalid QR code signature.',
    [ERROR_CODES.QR_EXPIRED]: 'QR code expired.',
    [ERROR_CODES.QR_SCAN_FAILED]: 'QR code scan failed.',
    [ERROR_CODES.DOCUMENT_NOT_FOUND]: 'Document not found.',
    [ERROR_CODES.REVISION_NOT_FOUND]: 'Document revision not found.',
    [ERROR_CODES.DOCUMENT_ACCESS_DENIED]: 'Document access denied.',
    [ERROR_CODES.CAMERA_ACCESS_DENIED]: 'Camera access denied.',
    [ERROR_CODES.CAMERA_NOT_AVAILABLE]: 'Camera not available.',
    [ERROR_CODES.CAMERA_ERROR]: 'Camera error.',
    [ERROR_CODES.UNKNOWN_ERROR]: 'Unknown error.',
    [ERROR_CODES.VALIDATION_FAILED]: 'Validation failed.',
    [ERROR_CODES.OPERATION_FAILED]: 'Operation failed.',
  },
}

export function getErrorMessage(
  code: string,
  language: 'ru' | 'en' = 'ru'
): string {
  return (
    ERROR_MESSAGES[language][
      code as keyof (typeof ERROR_MESSAGES)[typeof language]
    ] || ERROR_MESSAGES[language][ERROR_CODES.UNKNOWN_ERROR]
  )
}

export function createErrorFromResponse(
  response: Response,
  language: 'ru' | 'en' = 'ru'
): PTEQRError {
  let code: any = ERROR_CODES.API_ERROR
  let message = getErrorMessage(code, language)

  switch (response.status) {
    case 400:
      code = ERROR_CODES.VALIDATION_ERROR
      break
    case 401:
      code = ERROR_CODES.UNAUTHORIZED
      break
    case 403:
      code = ERROR_CODES.FORBIDDEN
      break
    case 404:
      code = ERROR_CODES.NOT_FOUND
      break
    case 500:
      code = ERROR_CODES.SERVER_ERROR
      break
    default:
      code = ERROR_CODES.API_ERROR
  }

  message = getErrorMessage(code, language)

  return new PTEQRError(code, message, {
    status: response.status,
    statusText: response.statusText,
  })
}

export function createErrorFromException(
  error: any,
  language: 'ru' | 'en' = 'ru'
): PTEQRError {
  if (error instanceof PTEQRError) {
    return error
  }

  let code: any = ERROR_CODES.UNKNOWN_ERROR
  let message = getErrorMessage(code, language)

  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    code = ERROR_CODES.NETWORK_ERROR
  } else if (error.name === 'AbortError') {
    code = ERROR_CODES.TIMEOUT_ERROR
  } else if (error.message.includes('camera')) {
    code = ERROR_CODES.CAMERA_ERROR
  } else if (error.message.includes('QR')) {
    code = ERROR_CODES.QR_SCAN_FAILED
  }

  message = getErrorMessage(code, language)

  return new PTEQRError(code, message, {
    originalError: error,
    stack: error.stack,
  })
}

export function createError(message: string, code: string, statusCode: number = 500): AppError {
  return new AppError(message, code, statusCode)
}

export function isAppError(error: any): error is AppError {
  return error instanceof AppError
}


export async function handleAsyncError<T>(
  operation: () => Promise<T>,
  language: 'ru' | 'en' = 'ru'
): Promise<T> {
  try {
    return await operation()
  } catch (error) {
    throw createErrorFromException(error, language)
  }
}

export function handleSyncError<T>(
  operation: () => T,
  language: 'ru' | 'en' = 'ru'
): T {
  try {
    return operation()
  } catch (error) {
    throw createErrorFromException(error, language)
  }
}
