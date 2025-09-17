/**
 * API functions
 */

import { DocumentStatusData } from '@/types/document'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Helper function to get auth headers
function getAuthHeaders() {
  const token = localStorage.getItem('pte-qr-token')
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  }
}

// Auth API functions
export async function loginUser(username: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      username,
      password,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || 'Login failed')
  }

  return response.json()
}

export async function logoutUser() {
  const token = localStorage.getItem('pte-qr-token')
  if (token) {
    try {
      await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
    } catch (error) {
      console.warn('Logout request failed:', error)
    }
  }
  localStorage.removeItem('pte-qr-token')
}

// Document API functions
export async function fetchDocumentStatus(
  docUid: string,
  revision: string,
  page: string | number
): Promise<DocumentStatusData> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/documents/${docUid}/revisions/${revision}/status?page=${page}`,
    {
      headers: getAuthHeaders(),
    }
  )

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || 'Failed to fetch document status')
  }

  return response.json()
}

export async function verifyQRSignature(
  docUid: string,
  revision: string,
  page: number,
  timestamp: number,
  signature: string
) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/documents/qr/verify?doc_uid=${docUid}&rev=${revision}&page=${page}&ts=${timestamp}&sig=${signature}`,
    {
      headers: getAuthHeaders(),
    }
  )

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || 'Failed to verify QR signature')
  }

  return response.json()
}

export async function generateQRCodes(request: {
  doc_uid: string
  revision: string
  pages: number[]
  style?: string
  dpi?: number
}) {
  const response = await fetch(`${API_BASE_URL}/api/v1/qrcodes/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || 'Failed to generate QR codes')
  }

  return response.json()
}
