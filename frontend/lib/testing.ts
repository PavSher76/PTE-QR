/**
 * Testing utilities and helpers
 */

export interface TestConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  headless: boolean;
}

export interface TestResult {
  name: string;
  passed: boolean;
  duration: number;
  error?: string;
  metadata?: Record<string, any>;
}

export interface TestSuite {
  name: string;
  tests: TestResult[];
  passed: number;
  failed: number;
  duration: number;
}

export class TestRunner {
  private config: TestConfig;
  private results: TestSuite[] = [];

  constructor(config: Partial<TestConfig> = {}) {
    this.config = {
      baseUrl: 'http://localhost:3000',
      timeout: 5000,
      retries: 3,
      headless: true,
      ...config,
    };
  }

  async runTest(name: string, testFn: () => Promise<void>): Promise<TestResult> {
    const startTime = Date.now();
    let error: string | undefined;
    let passed = false;

    for (let attempt = 1; attempt <= this.config.retries; attempt++) {
      try {
        await Promise.race([
          testFn(),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Test timeout')), this.config.timeout)
          ),
        ]);
        passed = true;
        break;
      } catch (err) {
        error = err instanceof Error ? err.message : String(err);
        if (attempt === this.config.retries) {
          break;
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    return {
      name,
      passed,
      duration: Date.now() - startTime,
      error,
    };
  }

  async runSuite(name: string, tests: Array<{ name: string; fn: () => Promise<void> }>): Promise<TestSuite> {
    const startTime = Date.now();
    const results: TestResult[] = [];

    for (const test of tests) {
      const result = await this.runTest(test.name, test.fn);
      results.push(result);
    }

    const passed = results.filter(r => r.passed).length;
    const failed = results.length - passed;

    const suite: TestSuite = {
      name,
      tests: results,
      passed,
      failed,
      duration: Date.now() - startTime,
    };

    this.results.push(suite);
    return suite;
  }

  getResults(): TestSuite[] {
    return [...this.results];
  }

  getSummary(): { total: number; passed: number; failed: number; duration: number } {
    const total = this.results.reduce((sum, suite) => sum + suite.tests.length, 0);
    const passed = this.results.reduce((sum, suite) => sum + suite.passed, 0);
    const failed = this.results.reduce((sum, suite) => sum + suite.failed, 0);
    const duration = this.results.reduce((sum, suite) => sum + suite.duration, 0);

    return { total, passed, failed, duration };
  }
}

export function createMockFetch(responses: Record<string, any>): typeof fetch {
  return async (input: any, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input.toString();
    const response = responses[url];

    if (!response) {
      throw new Error(`No mock response for URL: ${url}`);
    }

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  };
}

export function createMockLocalStorage(): Storage {
  const store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { Object.keys(store).forEach(key => delete store[key]); },
    get length() { return Object.keys(store).length; },
    key: (index: number) => Object.keys(store)[index] || null,
  };
}

export function createMockSessionStorage(): Storage {
  return createMockLocalStorage();
}

export function createMockGeolocation(): Geolocation {
  return {
    getCurrentPosition: (success, error) => {
      setTimeout(() => {
        success({
          coords: {
            latitude: 55.7558,
            longitude: 37.6176,
            accuracy: 10,
            altitude: null,
            altitudeAccuracy: null,
            heading: null,
            speed: null,
          },
          timestamp: Date.now(),
        });
      }, 100);
    },
    watchPosition: () => 1,
    clearWatch: () => {},
  };
}

export function createMockCamera(): MediaDevices {
  return {
    getUserMedia: async () => {
      const canvas = document.createElement('canvas');
      canvas.width = 640;
      canvas.height = 480;
      const ctx = canvas.getContext('2d');
      ctx?.fillRect(0, 0, 640, 480);
      
      return new MediaStream([canvas.captureStream().getVideoTracks()[0]]);
    },
    enumerateDevices: async () => [
      { deviceId: '1', kind: 'videoinput', label: 'Mock Camera', groupId: '1' },
    ],
  } as any;
}

export function waitFor(condition: () => boolean, timeout: number = 5000): Promise<void> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const check = () => {
      if (condition()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('Timeout waiting for condition'));
      } else {
        setTimeout(check, 100);
      }
    };
    
    check();
  });
}

export function waitForElement(selector: string, timeout: number = 5000): Promise<Element> {
  return new Promise((resolve, reject) => {
    const element = document.querySelector(selector);
    if (element) {
      resolve(element);
      return;
    }

    const observer = new MutationObserver(() => {
      const element = document.querySelector(selector);
      if (element) {
        observer.disconnect();
        resolve(element);
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });

    setTimeout(() => {
      observer.disconnect();
      reject(new Error(`Element not found: ${selector}`));
    }, timeout);
  });
}

export function simulateUserEvent(element: Element, eventType: string): void {
  const event = new Event(eventType, { bubbles: true, cancelable: true });
  element.dispatchEvent(event);
}

export function simulateKeyboardEvent(element: Element, key: string): void {
  const event = new KeyboardEvent('keydown', { key, bubbles: true, cancelable: true });
  element.dispatchEvent(event);
}

export function simulateMouseEvent(element: Element, eventType: string, x: number = 0, y: number = 0): void {
  const event = new MouseEvent(eventType, {
    bubbles: true,
    cancelable: true,
    clientX: x,
    clientY: y,
  });
  element.dispatchEvent(event);
}

export function createTestData(): {
  document: any;
  qrCode: any;
  user: any;
} {
  return {
    document: {
      docUid: 'TEST-DOC-001',
      revision: 'A',
      page: 1,
      businessStatus: 'Актуальный',
      enoviaState: 'Released',
      isActual: true,
      releasedAt: new Date().toISOString(),
    },
    qrCode: {
      docUid: 'TEST-DOC-001',
      revision: 'A',
      page: 1,
      timestamp: Math.floor(Date.now() / 1000),
      signature: 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
    },
    user: {
      id: 'test-user-1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'employee',
    },
  };
}

export function createTestEnvironment(): {
  fetch: typeof fetch;
  localStorage: Storage;
  sessionStorage: Storage;
  geolocation: Geolocation;
  camera: MediaDevices;
} {
  return {
    fetch: createMockFetch({
      '/api/v1/documents/TEST-DOC-001/revisions/A/status': {
        docUid: 'TEST-DOC-001',
        revision: 'A',
        page: 1,
        businessStatus: 'Актуальный',
        isActual: true,
      },
    }),
    localStorage: createMockLocalStorage(),
    sessionStorage: createMockSessionStorage(),
    geolocation: createMockGeolocation(),
    camera: createMockCamera(),
  };
}