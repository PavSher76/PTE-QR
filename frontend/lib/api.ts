import axios from 'axios';
import { DocumentStatusData, QRCodeRequest, QRCodeResponse } from '@/types/document';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const documentApi = {
  /**
   * Get document status by QR parameters
   */
  async getDocumentStatus(
    docUid: string,
    revision: string,
    page: number
  ): Promise<DocumentStatusData> {
    const response = await api.get(
      `/api/v1/documents/${docUid}/revisions/${revision}/status`,
      {
        params: { page }
      }
    );
    return response.data;
  },

  /**
   * Verify QR signature
   */
  async verifyQRSignature(
    docUid: string,
    revision: string,
    page: number,
    timestamp: number,
    signature: string
  ): Promise<{ valid: boolean; message: string }> {
    const response = await api.get('/api/v1/qr/verify', {
      params: {
        doc_uid: docUid,
        rev: revision,
        page,
        ts: timestamp,
        sig: signature
      }
    });
    return response.data;
  }
};

export const qrCodeApi = {
  /**
   * Generate QR codes for document pages
   */
  async generateQRCodes(request: QRCodeRequest): Promise<QRCodeResponse> {
    const response = await api.post('/api/v1/qrcodes', request);
    return response.data;
  }
};

export const adminApi = {
  /**
   * Get status mapping configuration
   */
  async getStatusMapping() {
    const response = await api.get('/api/v1/admin/status-mapping');
    return response.data;
  },

  /**
   * Update status mapping configuration
   */
  async updateStatusMapping(mapping: any) {
    const response = await api.put('/api/v1/admin/status-mapping', mapping);
    return response.data;
  }
};

export const healthApi = {
  /**
   * Check API health
   */
  async checkHealth() {
    const response = await api.get('/api/v1/health');
    return response.data;
  },

  /**
   * Get metrics
   */
  async getMetrics() {
    const response = await api.get('/api/v1/metrics');
    return response.data;
  }
};

export default api;
