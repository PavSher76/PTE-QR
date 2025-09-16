export interface DocumentStatusData {
  doc_uid: string;
  revision: string;
  page: number;
  business_status: 'APPROVED_FOR_CONSTRUCTION' | 'ACCEPTED_BY_CUSTOMER' | 'CHANGES_INTRODUCED_GET_NEW' | 'IN_WORK';
  enovia_state: string;
  is_actual: boolean;
  released_at?: string;
  superseded_by?: string;
  links: {
    openDocument?: string;
    openLatest?: string;
  };
}

// Alias for compatibility
export type DocumentStatus = DocumentStatusData;

export interface QRCodeRequest {
  doc_uid: string;
  revision: string;
  pages: number[];
  style?: 'black' | 'inverted' | 'with_label';
  dpi?: number;
  mode?: 'images' | 'pdf-stamp';
}

export interface QRCodeItem {
  page: number;
  format: 'png' | 'svg' | 'pdf';
  data_base64: string;
  url: string;
}

export interface QRCodeResponse {
  doc_uid: string;
  revision: string;
  items: QRCodeItem[];
}

export interface StatusMappingItem {
  business_status: DocumentStatusData['business_status'];
  color: string;
  action_label: string;
}

export interface StatusMapping {
  [enoviaState: string]: StatusMappingItem;
}
