import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn().mockResolvedValue(undefined),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
    }
  },
}))

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return '/'
  },
}))

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
global.localStorage = localStorageMock

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock HTMLMediaElement.play() method
Object.defineProperty(HTMLMediaElement.prototype, 'play', {
  writable: true,
  value: jest.fn().mockImplementation(() => {
    return Promise.resolve()
  }),
})

// Mock HTMLVideoElement specific properties
Object.defineProperty(HTMLVideoElement.prototype, 'videoWidth', {
  writable: true,
  value: 640,
})

Object.defineProperty(HTMLVideoElement.prototype, 'videoHeight', {
  writable: true,
  value: 480,
})

// Mock MediaStream
global.MediaStream = class MediaStream {
  constructor() {
    this.getTracks = jest.fn(() => [])
  }
}

// Mock MediaStreamTrack
global.MediaStreamTrack = class MediaStreamTrack {
  constructor() {
    this.stop = jest.fn()
  }
}

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
  })
)

// Mock Headers
global.Headers = class Headers {
  constructor(init) {
    this.headers = new Map(init)
  }
  
  get(name) {
    return this.headers.get(name)
  }
  
  set(name, value) {
    this.headers.set(name, value)
  }
  
  has(name) {
    return this.headers.has(name)
  }
  
  delete(name) {
    this.headers.delete(name)
  }
}

// Mock Request
global.Request = class Request {
  constructor(url, options = {}) {
    this.url = url
    this.method = options.method || 'GET'
    this.headers = new Headers(options.headers)
    this.body = options.body
  }
}

// Mock Response
global.Response = class Response {
  constructor(body, options = {}) {
    this.body = body
    this.status = options.status || 200
    this.statusText = options.statusText || 'OK'
    this.ok = this.status >= 200 && this.status < 300
    this.headers = new Headers(options.headers)
  }
  
  json() {
    return Promise.resolve(JSON.parse(this.body))
  }
  
  text() {
    return Promise.resolve(this.body)
  }
}

// Mock AudioContext
global.AudioContext = class AudioContext {
  constructor() {
    this.currentTime = 0
    this.destination = {}
  }
  
  createOscillator() {
    return {
      connect: jest.fn(),
      disconnect: jest.fn(),
      start: jest.fn(),
      stop: jest.fn(),
      frequency: { value: 440 },
      type: 'sine'
    }
  }
  
  createGain() {
    return {
      connect: jest.fn(),
      disconnect: jest.fn(),
      gain: { value: 1 }
    }
  }
}

// Mock webkitAudioContext
global.webkitAudioContext = global.AudioContext
