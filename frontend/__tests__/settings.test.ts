import { 
  getSettings, 
  setSettings, 
  resetSettings, 
  updateSetting,
  getSetting,
  hasSetting,
  removeSetting,
  clearSettings,
  exportSettings,
  importSettings
} from '../lib/settings'

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('Settings Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should export all functions', () => {
    expect(getSettings).toBeDefined()
    expect(setSettings).toBeDefined()
    expect(resetSettings).toBeDefined()
    expect(updateSetting).toBeDefined()
    expect(getSetting).toBeDefined()
    expect(hasSetting).toBeDefined()
    expect(removeSetting).toBeDefined()
    expect(clearSettings).toBeDefined()
    expect(exportSettings).toBeDefined()
    expect(importSettings).toBeDefined()
  })

  it('should be functions', () => {
    expect(typeof getSettings).toBe('function')
    expect(typeof setSettings).toBe('function')
    expect(typeof resetSettings).toBe('function')
    expect(typeof updateSetting).toBe('function')
    expect(typeof getSetting).toBe('function')
    expect(typeof hasSetting).toBe('function')
    expect(typeof removeSetting).toBe('function')
    expect(typeof clearSettings).toBe('function')
    expect(typeof exportSettings).toBe('function')
    expect(typeof importSettings).toBe('function')
  })

  it('should handle getSettings', () => {
    localStorageMock.getItem.mockReturnValue('{"theme": "dark"}')
    const result = getSettings()
    expect(result).toBeDefined()
    expect(localStorageMock.getItem).toHaveBeenCalledWith('pte_qr_settings')
  })

  it('should handle setSettings', () => {
    const settings = { theme: 'dark', language: 'ru' }
    setSettings(settings)
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'pte_qr_settings',
      JSON.stringify(settings)
    )
  })

  it('should handle resetSettings', () => {
    resetSettings()
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('pte_qr_settings')
  })

  it('should handle updateSetting', () => {
    localStorageMock.getItem.mockReturnValue('{"theme": "light"}')
    updateSetting('theme', 'dark')
    expect(localStorageMock.setItem).toHaveBeenCalled()
  })

  it('should handle getSetting', () => {
    localStorageMock.getItem.mockReturnValue('{"theme": "dark"}')
    const result = getSetting('theme')
    expect(result).toBe('dark')
  })

  it('should handle hasSetting', () => {
    localStorageMock.getItem.mockReturnValue('{"theme": "dark"}')
    const result = hasSetting('theme')
    expect(result).toBe(true)
  })

  it('should handle removeSetting', () => {
    localStorageMock.getItem.mockReturnValue('{"theme": "dark", "language": "ru"}')
    removeSetting('theme')
    expect(localStorageMock.setItem).toHaveBeenCalled()
  })

  it('should handle clearSettings', () => {
    clearSettings()
    expect(localStorageMock.clear).toHaveBeenCalled()
  })

  it('should handle exportSettings', () => {
    localStorageMock.getItem.mockReturnValue('{"theme": "dark"}')
    const result = exportSettings()
    expect(result).toBeDefined()
    expect(typeof result).toBe('string')
  })

  it('should handle importSettings', () => {
    const settings = '{"theme": "dark", "language": "ru"}'
    importSettings(settings)
    expect(localStorageMock.setItem).toHaveBeenCalledWith('pte_qr_settings', '{"theme":"dark","language":"ru"}')
  })
})
