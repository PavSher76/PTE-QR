/**
 * Performance monitoring and optimization utilities
 */

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
  metadata?: Record<string, any>;
}

export interface PerformanceEntry {
  name: string;
  entryType: string;
  startTime: number;
  duration: number;
  timestamp: number;
}

export class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private observers: PerformanceObserver[] = [];

  constructor() {
    this.initializeObservers();
  }

  private initializeObservers(): void {
    if (typeof window === 'undefined' || !('PerformanceObserver' in window)) {
      return;
    }

    // Observe navigation timing
    try {
      const navObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric({
            name: `navigation.${entry.name}`,
            value: entry.duration,
            unit: 'ms',
            timestamp: entry.startTime,
            metadata: {
              entryType: entry.entryType,
            },
          });
        }
      });
      navObserver.observe({ entryTypes: ['navigation'] });
      this.observers.push(navObserver);
    } catch (error) {
      console.warn('Failed to initialize navigation observer:', error);
    }

    // Observe resource timing
    try {
      const resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric({
            name: `resource.${entry.name}`,
            value: entry.duration,
            unit: 'ms',
            timestamp: entry.startTime,
            metadata: {
              entryType: entry.entryType,
              initiatorType: (entry as any).initiatorType,
            },
          });
        }
      });
      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.push(resourceObserver);
    } catch (error) {
      console.warn('Failed to initialize resource observer:', error);
    }

    // Observe paint timing
    try {
      const paintObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.recordMetric({
            name: `paint.${entry.name}`,
            value: entry.startTime,
            unit: 'ms',
            timestamp: entry.startTime,
            metadata: {
              entryType: entry.entryType,
            },
          });
        }
      });
      paintObserver.observe({ entryTypes: ['paint'] });
      this.observers.push(paintObserver);
    } catch (error) {
      console.warn('Failed to initialize paint observer:', error);
    }
  }

  recordMetric(metric: PerformanceMetric): void {
    this.metrics.push(metric);
    
    // Keep only last 1000 metrics to prevent memory leaks
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
  }

  getMetrics(name?: string): PerformanceMetric[] {
    if (name) {
      return this.metrics.filter(metric => metric.name === name);
    }
    return [...this.metrics];
  }

  getAverageMetric(name: string, timeWindow?: number): number | null {
    const metrics = this.getMetrics(name);
    
    if (metrics.length === 0) {
      return null;
    }

    let filteredMetrics = metrics;
    if (timeWindow) {
      const cutoff = Date.now() - timeWindow;
      filteredMetrics = metrics.filter(metric => metric.timestamp >= cutoff);
    }

    if (filteredMetrics.length === 0) {
      return null;
    }

    const sum = filteredMetrics.reduce((acc, metric) => acc + metric.value, 0);
    return sum / filteredMetrics.length;
  }

  getSlowestMetrics(count: number = 10): PerformanceMetric[] {
    return [...this.metrics]
      .sort((a, b) => b.value - a.value)
      .slice(0, count);
  }

  clearMetrics(): void {
    this.metrics = [];
  }

  disconnect(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

export const performanceMonitor = new PerformanceMonitor();

export function measureAsync<T>(
  name: string,
  operation: () => Promise<T>
): Promise<T> {
  const startTime = performance.now();
  
  return operation().then(
    (result) => {
      const endTime = performance.now();
      performanceMonitor.recordMetric({
        name,
        value: endTime - startTime,
        unit: 'ms',
        timestamp: startTime,
        metadata: { success: true },
      });
      return result;
    },
    (error) => {
      const endTime = performance.now();
      performanceMonitor.recordMetric({
        name,
        value: endTime - startTime,
        unit: 'ms',
        timestamp: startTime,
        metadata: { success: false, error: error.message },
      });
      throw error;
    }
  );
}

export function measureSync<T>(
  name: string,
  operation: () => T
): T {
  const startTime = performance.now();
  
  try {
    const result = operation();
    const endTime = performance.now();
    performanceMonitor.recordMetric({
      name,
      value: endTime - startTime,
      unit: 'ms',
      timestamp: startTime,
      metadata: { success: true },
    });
    return result;
  } catch (error) {
    const endTime = performance.now();
    performanceMonitor.recordMetric({
      name,
      value: endTime - startTime,
      unit: 'ms',
      timestamp: startTime,
      metadata: { success: false, error: (error as Error).message },
    });
    throw error;
  }
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout);
    }
    
    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

export function createImageOptimizer(
  maxWidth: number = 800,
  maxHeight: number = 600,
  quality: number = 0.8
): (file: File) => Promise<File> {
  return (file: File): Promise<File> => {
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        const { width, height } = calculateDimensions(
          img.width,
          img.height,
          maxWidth,
          maxHeight
        );
        
        canvas.width = width;
        canvas.height = height;
        
        ctx?.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob(
          (blob) => {
            if (blob) {
              const optimizedFile = new File([blob], file.name, {
                type: file.type,
                lastModified: Date.now(),
              });
              resolve(optimizedFile);
            } else {
              reject(new Error('Failed to optimize image'));
            }
          },
          file.type,
          quality
        );
      };
      
      img.onerror = () => {
        reject(new Error('Failed to load image'));
      };
      
      img.src = URL.createObjectURL(file);
    });
  };
}

function calculateDimensions(
  originalWidth: number,
  originalHeight: number,
  maxWidth: number,
  maxHeight: number
): { width: number; height: number } {
  let { width, height } = { width: originalWidth, height: originalHeight };
  
  if (width > maxWidth) {
    height = (height * maxWidth) / width;
    width = maxWidth;
  }
  
  if (height > maxHeight) {
    width = (width * maxHeight) / height;
    height = maxHeight;
  }
  
  return { width: Math.round(width), height: Math.round(height) };
}

export function preloadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load image: ${src}`));
    img.src = src;
  });
}

export function preloadImages(srcs: string[]): Promise<HTMLImageElement[]> {
  return Promise.all(srcs.map(preloadImage));
}

export function createLazyLoader(
  rootMargin: string = '50px',
  threshold: number = 0.1
): (element: Element, callback: () => void) => void {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
    return (element: Element, callback: () => void) => {
      // Fallback: load immediately
      callback();
    };
  }
  
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          callback();
          observer.unobserve(entry.target);
        }
      });
    },
    { rootMargin, threshold }
  );
  
  return (element: Element, callback: () => void) => {
    observer.observe(element);
  };
}

export function getPerformanceReport(): {
  metrics: PerformanceMetric[];
  summary: {
    totalMetrics: number;
    averageLoadTime: number | null;
    slowestOperations: PerformanceMetric[];
  };
} {
  const metrics = performanceMonitor.getMetrics();
  const averageLoadTime = performanceMonitor.getAverageMetric('navigation.loadEventEnd');
  const slowestOperations = performanceMonitor.getSlowestMetrics(5);
  
  return {
    metrics,
    summary: {
      totalMetrics: metrics.length,
      averageLoadTime,
      slowestOperations,
    },
  };
}