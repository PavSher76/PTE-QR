import {
  AppError,
  ValidationError, 
  NetworkError, 
  AuthError, 
  NotFoundError, 
  ServerError,
  createError,
  isAppError
} from '../lib/errors'

describe('Error Classes', () => {
  it('should create AppError', () => {
    const error = new AppError('Test error', 'TEST_ERROR', 400)
    expect(error.message).toBe('Test error')
    expect(error.code).toBe('TEST_ERROR')
    expect(error.statusCode).toBe(400)
    expect(error.name).toBe('AppError')
  })

  it('should create ValidationError', () => {
    const error = new ValidationError('Validation failed')
    expect(error.message).toBe('Validation failed')
    expect(error.code).toBe('VALIDATION_ERROR')
    expect(error.statusCode).toBe(400)
    expect(error.name).toBe('ValidationError')
  })

  it('should create NetworkError', () => {
    const error = new NetworkError('Network failed')
    expect(error.message).toBe('Network failed')
    expect(error.code).toBe('NETWORK_ERROR')
    expect(error.statusCode).toBe(0)
    expect(error.name).toBe('NetworkError')
  })

  it('should create AuthError', () => {
    const error = new AuthError('Auth failed')
    expect(error.message).toBe('Auth failed')
    expect(error.code).toBe('AUTH_ERROR')
    expect(error.statusCode).toBe(401)
    expect(error.name).toBe('AuthError')
  })

  it('should create NotFoundError', () => {
    const error = new NotFoundError('Not found')
    expect(error.message).toBe('Not found')
    expect(error.code).toBe('NOT_FOUND_ERROR')
    expect(error.statusCode).toBe(404)
    expect(error.name).toBe('NotFoundError')
  })

  it('should create ServerError', () => {
    const error = new ServerError('Server error')
    expect(error.message).toBe('Server error')
    expect(error.code).toBe('SERVER_ERROR')
    expect(error.statusCode).toBe(500)
    expect(error.name).toBe('ServerError')
  })
})

describe('Error Utilities', () => {
  it('should create error with createError', () => {
    const error = createError('Test error', 'TEST_ERROR', 400)
    expect(error).toBeInstanceOf(AppError)
    expect(error.message).toBe('Test error')
    expect(error.code).toBe('TEST_ERROR')
    expect(error.statusCode).toBe(400)
  })

  it('should check if error is AppError', () => {
    const appError = new AppError('Test', 'TEST', 400)
    const regularError = new Error('Test')
    
    expect(isAppError(appError)).toBe(true)
    expect(isAppError(regularError)).toBe(false)
  })

  it('should handle error types', () => {
    const appError = new AppError('Test error', 'TEST', 400)
    const regularError = new Error('Regular error')
    const stringError = 'String error'
    
    expect(appError.message).toBe('Test error')
    expect(regularError.message).toBe('Regular error')
    expect(stringError).toBe('String error')
  })
})
