import cache, {
  cacheKeys,
  CACHE_TTL,
  withCache,
  invalidateCache,
  clearCache,
  getCacheStats,
} from '../lib/cache'

describe('Cache Service', () => {
  beforeEach(() => {
    cache.clear()
  })

  it('should be defined', () => {
    expect(cache).toBeDefined()
  })

  it('should have get method', () => {
    expect(typeof cache.get).toBe('function')
  })

  it('should have set method', () => {
    expect(typeof cache.set).toBe('function')
  })

  it('should have delete method', () => {
    expect(typeof cache.delete).toBe('function')
  })

  it('should have clear method', () => {
    expect(typeof cache.clear).toBe('function')
  })

  it('should handle set and get with key', () => {
    const testData = { data: 'test' }
    cache.set('test-key', testData, 3600)

    const result = cache.get('test-key')
    expect(result).toEqual(testData)
  })

  it('should handle get with non-existent key', () => {
    const result = cache.get('non-existent')
    expect(result).toBeNull()
  })

  it('should handle delete with key', () => {
    cache.set('test-key', { data: 'test' }, 3600)
    const deleted = cache.delete('test-key')

    expect(deleted).toBe(true)
    expect(cache.get('test-key')).toBeNull()
  })

  it('should handle clear', () => {
    cache.set('test-key1', { data: 'test1' }, 3600)
    cache.set('test-key2', { data: 'test2' }, 3600)

    cache.clear()

    expect(cache.get('test-key1')).toBeNull()
    expect(cache.get('test-key2')).toBeNull()
  })

  it('should handle cache expiration', () => {
    const testData = { data: 'test' }
    cache.set('test-key', testData, 1) // 1ms TTL

    // Wait for expiration
    setTimeout(() => {
      const result = cache.get('test-key')
      expect(result).toBeNull()
    }, 10)
  })

  it('should export cache keys generator', () => {
    expect(cacheKeys.documentStatus('doc1', 'A', 1)).toBe('status:doc1:A:1')
    expect(cacheKeys.documentMeta('doc1')).toBe('meta:doc1')
    expect(cacheKeys.revisionMeta('doc1', 'A')).toBe('revision:doc1:A')
    expect(cacheKeys.qrCode('doc1', 'A', 1)).toBe('qr:doc1:A:1')
  })

  it('should export cache TTL constants', () => {
    expect(CACHE_TTL.DOCUMENT_STATUS).toBe(15 * 60 * 1000)
    expect(CACHE_TTL.DOCUMENT_META).toBe(60 * 60 * 1000)
    expect(CACHE_TTL.REVISION_META).toBe(30 * 60 * 1000)
    expect(CACHE_TTL.QR_CODE).toBe(24 * 60 * 60 * 1000)
  })

  it('should work with withCache wrapper', async () => {
    const mockFetcher = jest.fn().mockResolvedValue({ data: 'fetched' })

    const result1 = await withCache('test-key', mockFetcher, 3600)
    const result2 = await withCache('test-key', mockFetcher, 3600)

    expect(result1).toEqual({ data: 'fetched' })
    expect(result2).toEqual({ data: 'fetched' })
    expect(mockFetcher).toHaveBeenCalledTimes(1) // Should only call once due to caching
  })

  it('should handle cache invalidation by pattern', () => {
    cache.set('status:doc1:A:1', { data: 'status1' }, 3600)
    cache.set('status:doc1:A:2', { data: 'status2' }, 3600)
    cache.set('meta:doc1', { data: 'meta1' }, 3600)

    invalidateCache('status:doc1:A:.*')

    expect(cache.get('status:doc1:A:1')).toBeNull()
    expect(cache.get('status:doc1:A:2')).toBeNull()
    expect(cache.get('meta:doc1')).toEqual({ data: 'meta1' }) // Should still exist
  })

  it('should provide cache statistics', () => {
    cache.set('key1', { data: 'test1' }, 3600)
    cache.set('key2', { data: 'test2' }, 3600)

    const stats = getCacheStats()

    expect(stats.size).toBe(2)
    expect(stats.keys).toContain('key1')
    expect(stats.keys).toContain('key2')
  })
})
