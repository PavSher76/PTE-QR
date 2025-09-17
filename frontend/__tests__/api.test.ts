import { fetchDocumentStatus } from '../lib/api'

// Mock fetch
global.fetch = jest.fn()

describe('API Functions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should export fetchDocumentStatus function', () => {
    expect(fetchDocumentStatus).toBeDefined()
    expect(typeof fetchDocumentStatus).toBe('function')
  })

  it('should fetch document status with correct parameters', async () => {
    const mockResponse = {
      doc_uid: 'test-doc',
      revision: 'A',
      page: 1,
      business_status: 'APPROVED_FOR_CONSTRUCTION',
      enovia_state: 'Released',
      is_actual: true,
      released_at: '2024-01-01T00:00:00Z',
      links: {
        openDocument: '#',
        openLatest: '#',
      },
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const result = await fetchDocumentStatus('test-doc', 'A', 1)

    expect(result).toEqual(
      expect.objectContaining({
        doc_uid: 'test-doc',
        revision: 'A',
        page: 1,
        business_status: 'APPROVED_FOR_CONSTRUCTION',
        enovia_state: 'Released',
        is_actual: true,
      })
    )
  })

  it('should handle string page parameter', async () => {
    const mockResponse = {
      doc_uid: 'test-doc',
      revision: 'A',
      page: 1,
      business_status: 'APPROVED_FOR_CONSTRUCTION',
      enovia_state: 'Released',
      is_actual: true,
      released_at: '2024-01-01T00:00:00Z',
      links: {
        openDocument: '#',
        openLatest: '#',
      },
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const result = await fetchDocumentStatus('test-doc', 'A', '1')

    expect(result.page).toBe(1)
  })

  it('should handle number page parameter', async () => {
    const mockResponse = {
      doc_uid: 'test-doc',
      revision: 'A',
      page: 2,
      business_status: 'APPROVED_FOR_CONSTRUCTION',
      enovia_state: 'Released',
      is_actual: true,
      released_at: '2024-01-01T00:00:00Z',
      links: {
        openDocument: '#',
        openLatest: '#',
      },
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const result = await fetchDocumentStatus('test-doc', 'A', 2)

    expect(result.page).toBe(2)
  })
})
