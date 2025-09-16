/**
 * ENOVIA PLM integration utilities
 */

export interface ENOVIADocument {
  id: string;
  title: string;
  number: string;
  currentRevision: string;
  maturityState: string;
  lastModified: string;
}

export interface ENOVIARevision {
  id: string;
  revision: string;
  maturityState: string;
  releasedDate?: string;
  supersededBy?: string;
  lastModified: string;
}

export interface ENOVIAClientConfig {
  baseUrl: string;
  clientId: string;
  clientSecret: string;
  scope: string;
}

/**
 * ENOVIA API client
 */
export class ENOVIAClient {
  private config: ENOVIAClientConfig;
  private accessToken: string | null = null;
  private tokenExpiresAt: number | null = null;

  constructor(config: ENOVIAClientConfig) {
    this.config = config;
  }

  /**
   * Get OAuth2 access token
   */
  private async getAccessToken(): Promise<string> {
    if (this.accessToken && this.tokenExpiresAt && Date.now() < this.tokenExpiresAt) {
      return this.accessToken;
    }

    try {
      const response = await fetch(`${this.config.baseUrl}/oauth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'client_credentials',
          client_id: this.config.clientId,
          client_secret: this.config.clientSecret,
          scope: this.config.scope,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get access token');
      }

      const data = await response.json();
      this.accessToken = data.access_token;
      this.tokenExpiresAt = Date.now() + (data.expires_in * 1000) - 60000; // 1 minute buffer

      return this.accessToken!;
    } catch (error) {
      console.error('Error getting ENOVIA access token:', error);
      throw new Error('Failed to authenticate with ENOVIA');
    }
  }

  /**
   * Make authenticated request to ENOVIA API
   */
  private async makeRequest(endpoint: string): Promise<any> {
    const token = await this.getAccessToken();
    
    const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`ENOVIA API error: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get document metadata
   */
  async getDocumentMeta(docUid: string): Promise<ENOVIADocument | null> {
    try {
      return await this.makeRequest(`/api/documents/${docUid}`);
    } catch (error) {
      console.error('Error getting document metadata:', error);
      return null;
    }
  }

  /**
   * Get revision metadata
   */
  async getRevisionMeta(docUid: string, revision: string): Promise<ENOVIARevision | null> {
    try {
      return await this.makeRequest(`/api/documents/${docUid}/revisions/${revision}`);
    } catch (error) {
      console.error('Error getting revision metadata:', error);
      return null;
    }
  }

  /**
   * Get latest released revision
   */
  async getLatestReleased(docUid: string): Promise<ENOVIARevision | null> {
    try {
      return await this.makeRequest(`/api/documents/${docUid}/latest-released`);
    } catch (error) {
      console.error('Error getting latest released revision:', error);
      return null;
    }
  }

  /**
   * Check ENOVIA API health
   */
  async healthCheck(): Promise<boolean> {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.config.baseUrl}/api/health`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      return response.ok;
    } catch (error) {
      console.error('ENOVIA health check failed:', error);
      return false;
    }
  }
}

/**
 * Map ENOVIA state to business status
 */
export function mapENOVIAStateToBusinessStatus(enoviaState: string): string {
  const mapping: { [key: string]: string } = {
    'Released': 'APPROVED_FOR_CONSTRUCTION',
    'AFC': 'APPROVED_FOR_CONSTRUCTION',
    'Accepted': 'ACCEPTED_BY_CUSTOMER',
    'Approved': 'ACCEPTED_BY_CUSTOMER',
    'Obsolete': 'CHANGES_INTRODUCED_GET_NEW',
    'Superseded': 'CHANGES_INTRODUCED_GET_NEW',
    'In Work': 'IN_WORK',
    'Frozen': 'IN_WORK',
  };

  return mapping[enoviaState] || 'IN_WORK';
}

/**
 * Check if revision is actual
 */
export function isRevisionActual(revision: ENOVIARevision): boolean {
  return !revision.supersededBy && 
         !['Obsolete', 'Superseded'].includes(revision.maturityState);
}
