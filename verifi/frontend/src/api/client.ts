import {
  HealthResponse,
  Tender,
  Bidder,
  Bid,
  BidSummary,
  VerificationCheck,
  DocumentItem,
  DocumentUploadResponse,
  VerificationStartResponse,
  VerificationRun,
  AIChatResponse,
  AIDecisionReasonResponse,
  DecisionRecord,
  DecisionHistoryResponse,
  AuditEvent,
  DecisionEnum,
  DocumentType,
} from './types';

// Environment variable with fallback
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const BASE_URL = `${API_URL}/api/v1`;

class ApiError extends Error {
  code: string;
  details: Record<string, any>;
  statusCode: number;

  constructor(message: string, code = 'API_ERROR', details = {}, statusCode = 500) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
    this.statusCode = statusCode;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Accept': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, { ...options, headers });
    
    if (!response.ok) {
      let errorData: any = {};
      try {
        errorData = await response.json();
      } catch {
        errorData = { error: { message: response.statusText } };
      }
      
      const code = errorData?.error?.code || `HTTP_${response.status}`;
      const message = errorData?.error?.message || `Request failed with status ${response.status}`;
      const details = errorData?.error?.details || {};
      
      throw new ApiError(message, code, details, response.status);
    }

    return await response.json();
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      err.message || 'Unable to connect to VERIFI backend. Please check server status.',
      'NETWORK_ERROR',
      {},
      0
    );
  }
}

// 1. Health
export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}

// 2. Tenders
export async function getTenders(): Promise<Tender[]> {
  return request<Tender[]>('/tenders');
}

export async function getTender(tenderId: string): Promise<Tender> {
  return request<Tender>(`/tenders/${tenderId}`);
}

// 3. Bidders
export async function getBidders(): Promise<Bidder[]> {
  return request<Bidder[]>('/bidders');
}

export async function getBidder(bidderId: string): Promise<Bidder> {
  return request<Bidder>(`/bidders/${bidderId}`);
}

// 4. Bids
export async function getBids(): Promise<Bid[]> {
  return request<Bid[]>('/bids');
}

export async function getBid(bidId: string): Promise<Bid> {
  return request<Bid>(`/bids/${bidId}`);
}

export async function getBidSummary(bidId: string): Promise<BidSummary> {
  return request<BidSummary>(`/bids/${bidId}/summary`);
}

export async function getBidChecks(bidId: string): Promise<VerificationCheck[]> {
  return request<VerificationCheck[]>(`/bids/${bidId}/checks`);
}

// 5. Documents
export async function getBidDocuments(bidId: string): Promise<DocumentItem[]> {
  return request<DocumentItem[]>(`/bids/${bidId}/documents`);
}

export async function uploadDocument(
  bidId: string,
  file: File,
  documentType?: DocumentType
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (documentType) {
    formData.append('document_type', documentType);
  }

  const url = `${BASE_URL}/bids/${bidId}/documents/upload`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData?.error?.message || 'Failed to upload document.',
      errorData?.error?.code || 'UPLOAD_FAILED',
      {},
      response.status
    );
  }

  return await response.json();
}

// 6. Verification Pipeline
export async function startVerification(bidId: string): Promise<VerificationStartResponse> {
  return request<VerificationStartResponse>(`/bids/${bidId}/verify`, {
    method: 'POST',
  });
}

export async function getVerificationRun(runId: string): Promise<VerificationRun> {
  return request<VerificationRun>(`/verification-runs/${runId}`);
}

export async function getVerificationCheck(checkId: string): Promise<VerificationCheck> {
  return request<VerificationCheck>(`/verification-checks/${checkId}`);
}

export async function retryVerificationCheck(checkId: string): Promise<VerificationCheck> {
  return request<VerificationCheck>(`/verification-checks/${checkId}/retry`, {
    method: 'POST',
  });
}

// 7. AI Assistant
export async function chatWithAI(
  bidId: string,
  message: string,
  focusCheckId?: string
): Promise<AIChatResponse> {
  return request<AIChatResponse>(`/bids/${bidId}/ai/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, focus_check_id: focusCheckId }),
  });
}

export async function generateDecisionReason(bidId: string): Promise<AIDecisionReasonResponse> {
  return request<AIDecisionReasonResponse>(`/bids/${bidId}/ai/generate-reason`, {
    method: 'POST',
  });
}

// 8. Decisions
export async function submitDecision(
  bidId: string,
  decision: DecisionEnum,
  reason: string,
  officerName = 'Senior Evaluation Officer'
): Promise<DecisionRecord> {
  return request<DecisionRecord>(`/bids/${bidId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      decision,
      reason,
      officer_id: 'OFFICER-001',
      officer_name: officerName,
    }),
  });
}

export async function getDecision(bidId: string): Promise<DecisionHistoryResponse> {
  return request<DecisionHistoryResponse>(`/bids/${bidId}/decision`);
}

// 9. Audit Trail
export async function getAuditTrail(bidId: string): Promise<AuditEvent[]> {
  return request<AuditEvent[]>(`/bids/${bidId}/audit`);
}
