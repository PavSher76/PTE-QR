import { 
  createNotification, 
  showNotification, 
  hideNotification, 
  clearNotifications,
  NotificationType,
  Notification
} from '../lib/notifications'

// Mock the context
const mockAddNotification = jest.fn()
const mockRemoveNotification = jest.fn()
const mockClearNotifications = jest.fn()

jest.mock('../lib/context', () => ({
  useNotifications: () => ({
    addNotification: mockAddNotification,
    removeNotification: mockRemoveNotification,
    clearNotifications: mockClearNotifications,
  }),
}))

describe('Notification Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should export all functions', () => {
    expect(createNotification).toBeDefined()
    expect(showNotification).toBeDefined()
    expect(hideNotification).toBeDefined()
    expect(clearNotifications).toBeDefined()
  })

  it('should be functions', () => {
    expect(typeof createNotification).toBe('function')
    expect(typeof showNotification).toBe('function')
    expect(typeof hideNotification).toBe('function')
    expect(typeof clearNotifications).toBe('function')
  })

  it('should create notification', () => {
    const notification = createNotification('Test message', 'success')
    expect(notification).toBeDefined()
    expect(notification.message).toBe('Test message')
    expect(notification.type).toBe('success')
    expect(notification.id).toBeDefined()
  })

  it('should create notification with custom id', () => {
    const notification = createNotification('Test message', 'error', 'custom-id')
    expect(notification.id).toBe('custom-id')
  })

  it('should handle showNotification', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation()
    showNotification('Test message', 'info')
    expect(consoleSpy).toHaveBeenCalledWith('Notification [info]: Test message')
    consoleSpy.mockRestore()
  })

  it('should handle hideNotification', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation()
    hideNotification('test-id')
    expect(consoleSpy).toHaveBeenCalledWith('Hide notification: test-id')
    consoleSpy.mockRestore()
  })

  it('should handle clearNotifications', () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation()
    clearNotifications()
    expect(consoleSpy).toHaveBeenCalledWith('Clear all notifications')
    consoleSpy.mockRestore()
  })

  it('should create different notification types', () => {
    const success = createNotification('Success', 'success')
    const error = createNotification('Error', 'error')
    const warning = createNotification('Warning', 'warning')
    const info = createNotification('Info', 'info')

    expect(success.type).toBe('success')
    expect(error.type).toBe('error')
    expect(warning.type).toBe('warning')
    expect(info.type).toBe('info')
  })

  it('should generate unique ids', () => {
    const notification1 = createNotification('Test 1', 'success')
    const notification2 = createNotification('Test 2', 'success')
    
    expect(notification1.id).not.toBe(notification2.id)
  })
})
