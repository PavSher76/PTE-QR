/**
 * API functions
 */

import { DocumentStatusData } from '@/types/document'

// Placeholder API functions
export async function fetchDocumentStatus(
  docUid: string,
  revision: string,
  page: string | number
): Promise<DocumentStatusData> {
  // Placeholder implementation
  return {
    doc_uid: docUid,
    revision,
    page: typeof page === 'string' ? parseInt(page) : page,
    business_status: 'APPROVED_FOR_CONSTRUCTION',
    enovia_state: 'Released',
    is_actual: true,
    released_at: new Date().toISOString(),
    links: {
      openDocument: '#',
      openLatest: '#',
    },
  }
}
