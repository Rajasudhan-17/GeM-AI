export type VerificationStatus = 'PASS' | 'FAIL' | 'REVIEW' | 'NOT_APPLICABLE';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type DecisionEnum = 'ACCEPTED' | 'REJECTED';
export type DocumentStatus = 'UPLOADED' | 'PROCESSING' | 'PROCESSED' | 'VERIFIED' | 'FLAGGED' | 'FAILED';
export type VerificationRunStatus =
  | 'PENDING'
  | 'RUNNING'
  | 'OCR'
  | 'EXTRACTING'
  | 'VERIFYING'
  | 'RULE_EVALUATION'
  | 'SCORING'
  | 'AI_ANALYSIS'
  | 'COMPLETED'
  | 'FAILED';

export type DocumentType =
  | 'GST'
  | 'UDYAM'
  | 'PAN'
  | 'EPFO'
  | 'ESIC'
  | 'OEM'
  | 'DIGILOCKER'
  | 'BLACKLIST'
  | 'UNKNOWN';

export interface HealthResponse {
  status: string;
  service: string;
  database: string;
  repository: string;
  version: string;
}

export interface TenderRequirement {
  id: string;
  tender_id: string;
  code: string;
  name: string;
  document_type: DocumentType;
  rule_code: string;
  is_mandatory: boolean;
  weight: number;
  description: string;
}

export interface Tender {
  id: string;
  tender_number: string;
  title: string;
  category: string;
  description: string;
  organization: string;
  estimated_value_inr: number;
  closing_date?: string;
  requirements: TenderRequirement[];
  created_at: string;
}

export interface Bidder {
  id: string;
  name: string;
  legal_entity_type: string;
  primary_email: string;
  primary_phone: string;
  registered_address: string;
  pan: string;
  gstin: string;
  udyam_number: string;
  created_at: string;
}

export interface Bid {
  id: string;
  tender_id: string;
  bidder_id: string;
  bidder_name?: string;
  bid_number: string;
  submitted_at: string;
  status: string;
  latest_verification_run_id?: string;
  latest_score?: number;
  latest_risk_level?: RiskLevel;
}

export interface BidSummary {
  bid_id: string;
  bidder_id: string;
  bidder_name: string;
  tender_number: string;
  tender_title: string;
  submitted_at: string;
  status: string;
  verification_run_id?: string;
  score?: number;
  risk_level?: RiskLevel;
  passed_checks: number;
  failed_checks: number;
  review_checks: number;
  na_checks: number;
  total_checks: number;
  documents_count: number;
  latest_decision?: string;
}

export interface FactComparison {
  matched: boolean;
  discrepancies: string[];
  field_comparisons: Record<string, Record<string, any>>;
}

export interface VerificationCheck {
  id: string;
  run_id: string;
  requirement_code: string;
  rule_code: string;
  check_name: string;
  document_type: DocumentType;
  document_id?: string;
  status: VerificationStatus;
  extracted_facts?: Record<string, any>;
  source_facts?: Record<string, any>;
  fact_comparison?: FactComparison;
  reason: string;
  evidence: Record<string, any>;
  evaluated_at: string;
}

export interface ScoreComponent {
  requirement_code: string;
  rule_code: string;
  weight: number;
  status: string;
  points_awarded: number;
  max_possible_points: number;
  notes: string;
}

export interface ComplianceScore {
  total_score: number;
  passed_count: number;
  failed_count: number;
  review_count: number;
  na_count: number;
  components: ScoreComponent[];
}

export interface RiskFactor {
  category: string;
  severity: string;
  description: string;
  impact: string;
}

export interface RiskAssessment {
  risk_level: RiskLevel;
  risk_score: number;
  primary_risk_drivers: string[];
  risk_factors: RiskFactor[];
}

export interface AIRecommendation {
  summary: string;
  risk_explanation: string;
  key_findings: string[];
  suggested_action: string;
  drafted_reason: string;
}

export interface VerificationRun {
  id: string;
  bid_id: string;
  bidder_id: string;
  correlation_id: string;
  status: VerificationRunStatus;
  current_stage: string;
  progress_pct: number;
  checks: VerificationCheck[];
  score?: ComplianceScore;
  risk_assessment?: RiskAssessment;
  ai_recommendation?: AIRecommendation;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface VerificationStartResponse {
  run_id: string;
  status: VerificationRunStatus;
  correlation_id: string;
  message: string;
}

export interface DocumentItem {
  id: string;
  bid_id: string;
  bidder_id: string;
  file_name: string;
  original_file_name: string;
  file_size_bytes: number;
  mime_type: string;
  document_type: DocumentType;
  status: DocumentStatus;
  ocr_text_preview?: string;
  extracted_facts: Record<string, any>;
  created_at: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  file_name: string;
  document_type: DocumentType;
  status: DocumentStatus;
  message: string;
}

export interface AIChatResponse {
  answer: string;
  related_checks: string[];
  generated_at: string;
}

export interface AIDecisionReasonResponse {
  reason: string;
  suggested_decision: string;
  confidence: number;
  generated_at: string;
}

export interface DecisionRecord {
  id: string;
  bid_id: string;
  bidder_id: string;
  decision: DecisionEnum;
  reason: string;
  officer_id: string;
  officer_name: string;
  score_at_decision: number;
  risk_at_decision: RiskLevel;
  verification_run_id: string;
  created_at: string;
}

export interface DecisionHistoryResponse {
  bid_id: string;
  current_decision?: DecisionRecord;
  history: DecisionRecord[];
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  action: string;
  actor: string;
  entity_type: string;
  entity_id: string;
  correlation_id: string;
  metadata: Record<string, any>;
  previous_hash: string;
  event_hash: string;
}
