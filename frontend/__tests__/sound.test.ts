import { playSuccessSound, playErrorSound, playScanningSound } from '../lib/sound'

// Mock Web Audio API
const mockAudioContext = {
  createOscillator: jest.fn(() => ({
    connect: jest.fn(),
    start: jest.fn(),
    stop: jest.fn(),
    frequency: { setValueAtTime: jest.fn() },
    type: 'sine'
  })),
  createGain: jest.fn(() => ({
    connect: jest.fn(),
    gain: {
      setValueAtTime: jest.fn(),
      linearRampToValueAtTime: jest.fn(),
      exponentialRampToValueAtTime: jest.fn()
    }
  })),
  currentTime: 0,
  destination: {}
}

// Mock window.AudioContext
Object.defineProperty(window, 'AudioContext', {
  value: jest.fn(() => mockAudioContext),
  writable: true
})

Object.defineProperty(window, 'webkitAudioContext', {
  value: jest.fn(() => mockAudioContext),
  writable: true
})

describe('Sound utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should play success sound without errors', () => {
    expect(() => playSuccessSound()).not.toThrow()
  })

  it('should play error sound without errors', () => {
    expect(() => playErrorSound()).not.toThrow()
  })

  it('should play scanning sound without errors', () => {
    expect(() => playScanningSound()).not.toThrow()
  })

  it('should handle audio context creation errors gracefully', () => {
    // Mock AudioContext to throw an error
    Object.defineProperty(window, 'AudioContext', {
      value: jest.fn(() => {
        throw new Error('AudioContext not supported')
      }),
      writable: true
    })

    // Should not throw errors
    expect(() => playSuccessSound()).not.toThrow()
    expect(() => playErrorSound()).not.toThrow()
    expect(() => playScanningSound()).not.toThrow()
  })
})
