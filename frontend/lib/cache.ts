/**
 * Client-side caching utilities
 */

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

/**
 * Simple in-memory cache
 */
class MemoryCache {
  private cache = new Map<string, CacheItem<any>>();

  set<T>(key: string, data: T, ttl: number = 5 * 60 * 1000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    // Check if item has expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  has(key: string): boolean {
    const item = this.cache.get(key);
    
    if (!item) {
      return false;
    }

    // Check if item has expired
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

// Global cache instance
const cache = new MemoryCache();

/**
 * Cache key generators
 */
export const cacheKeys = {
  documentStatus: (docUid: string, revision: string, page: number) => 
    `status:${docUid}:${revision}:${page}`,
  
  documentMeta: (docUid: string) => 
    `meta:${docUid}`,
  
  revisionMeta: (docUid: string, revision: string) => 
    `revision:${docUid}:${revision}`,
  
  qrCode: (docUid: string, revision: string, page: number) => 
    `qr:${docUid}:${revision}:${page}`,
};

/**
 * Cache TTL constants (in milliseconds)
 */
export const CACHE_TTL = {
  DOCUMENT_STATUS: 15 * 60 * 1000, // 15 minutes
  DOCUMENT_META: 60 * 60 * 1000,   // 1 hour
  REVISION_META: 30 * 60 * 1000,   // 30 minutes
  QR_CODE: 24 * 60 * 60 * 1000,    // 24 hours
} as const;

/**
 * Cache wrapper for async functions
 */
export async function withCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = CACHE_TTL.DOCUMENT_STATUS
): Promise<T> {
  // Try to get from cache first
  const cached = cache.get<T>(key);
  if (cached !== null) {
    return cached;
  }

  // Fetch data if not in cache
  const data = await fetcher();
  
  // Store in cache
  cache.set(key, data, ttl);
  
  return data;
}

/**
 * Invalidate cache entries by pattern
 */
export function invalidateCache(pattern: string): void {
  const keys = Array.from(cache['cache'].keys());
  const regex = new RegExp(pattern);
  
  keys.forEach(key => {
    if (regex.test(key)) {
      cache.delete(key);
    }
  });
}

/**
 * Clear all cache
 */
export function clearCache(): void {
  cache.clear();
}

/**
 * Get cache statistics
 */
export function getCacheStats(): {
  size: number;
  keys: string[];
} {
  return {
    size: cache.size(),
    keys: Array.from(cache['cache'].keys())
  };
}

export default cache;
