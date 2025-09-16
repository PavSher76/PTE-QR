import QRCode from 'qrcode';

export interface QRCodeOptions {
  width?: number;
  height?: number;
  margin?: number;
  color?: {
    dark?: string;
    light?: string;
  };
  errorCorrectionLevel?: 'L' | 'M' | 'Q' | 'H';
}

/**
 * Generate QR code as data URL
 */
export async function generateQRCodeDataURL(
  text: string,
  options: QRCodeOptions = {}
): Promise<string> {
  const defaultOptions = {
    width: 256,
    height: 256,
    margin: 2,
    color: {
      dark: '#000000',
      light: '#FFFFFF'
    },
    errorCorrectionLevel: 'M' as const,
    ...options
  };

  try {
    return await QRCode.toDataURL(text, defaultOptions);
  } catch (error) {
    console.error('Error generating QR code:', error);
    throw new Error('Failed to generate QR code');
  }
}

/**
 * Generate QR code as SVG string
 */
export async function generateQRCodeSVG(
  text: string,
  options: QRCodeOptions = {}
): Promise<string> {
  const defaultOptions = {
    width: 256,
    height: 256,
    margin: 2,
    color: {
      dark: '#000000',
      light: '#FFFFFF'
    },
    errorCorrectionLevel: 'M' as const,
    ...options
  };

  try {
    return await QRCode.toString(text, { type: 'svg', ...defaultOptions });
  } catch (error) {
    console.error('Error generating QR code SVG:', error);
    throw new Error('Failed to generate QR code SVG');
  }
}

/**
 * Parse QR URL to extract parameters
 */
export function parseQRUrl(url: string): {
  docUid: string;
  revision: string;
  page: number;
  timestamp: number;
  signature: string;
} | null {
  try {
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split('/');
    
    if (pathParts.length < 5 || pathParts[1] !== 'r') {
      return null;
    }

    const docUid = pathParts[2];
    const revision = pathParts[3];
    const page = parseInt(pathParts[4]);
    const timestamp = parseInt(urlObj.searchParams.get('ts') || '0');
    const signature = urlObj.searchParams.get('t') || '';

    if (!docUid || !revision || isNaN(page) || !timestamp || !signature) {
      return null;
    }

    return {
      docUid,
      revision,
      page,
      timestamp,
      signature
    };
  } catch (error) {
    console.error('Error parsing QR URL:', error);
    return null;
  }
}

/**
 * Validate QR URL format
 */
export function isValidQRUrl(url: string): boolean {
  return parseQRUrl(url) !== null;
}

/**
 * Generate QR URL for testing
 */
export function generateTestQRUrl(
  docUid: string,
  revision: string,
  page: number,
  baseUrl: string = 'https://qr.pti.ru'
): string {
  const timestamp = Math.floor(Date.now() / 1000);
  // This is a mock signature for testing
  const signature = 'test_signature_' + timestamp;
  
  return `${baseUrl}/r/${docUid}/${revision}/${page}?ts=${timestamp}&t=${signature}`;
}
