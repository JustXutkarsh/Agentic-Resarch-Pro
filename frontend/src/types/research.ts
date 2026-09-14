/**
 * Type definitions for Agentic Research.
 */

export type ResearchDepth = 'QUICK' | 'STANDARD' | 'DEEP';

export interface ResearchPlan {
  research_dimensions: string[];
  search_queries: string[];
  target_perspectives: string[];
  methodology_summary: string;
}

export interface ResearchGap {
  dimension: string;
  reason: string;
  follow_up_query: string;
  status: string;
}

export interface ClaimVerification {
  claim: string;
  score: number;
  verification_status: string;
  supporting_evidence: string;
  confidence_label: string;
}

export interface Contradiction {
  perspective_a: string;
  perspective_b: string;
  tension_point: string;
  severity: string;
}

export interface ResearchConfidence {
  overall_score: number;
  category_scores: Record<string, number>;
  explanation: string;
}

export interface ResearchMetrics {
  session_id: string;
  topic: string;
  depth: string;
  generated_queries: number;
  sources_evaluated: number;
  sources_accepted: number;
  sources_rejected: number;
  scraped_pages: number;
  extracted_chunks: number;
  research_iterations: number;
  identified_gaps: number;
  verified_claims: number;
  detected_contradictions: number;
  execution_time_seconds: number;
}

export interface SourceEvaluation {
  authority_score: number;
  relevance_score: number;
  recency_score: number;
  evidence_quality_score: number;
  reputation_score: number;
  overall_score: number;
  recency_unknown?: boolean;
  explanation?: string;
}

export interface AcceptedSource {
  title?: string;
  url?: string;
  snippet?: string;
  domain?: string;
  source_score?: number;
  evaluation?: SourceEvaluation;
}

export interface ResearchResultData {
  session_id: string;
  topic: string;
  depth: ResearchDepth;
  plan?: ResearchPlan;
  report: string;
  sources_accepted: number;
  sources_rejected: number;
  sources?: AcceptedSource[];
  gaps?: ResearchGap[];
  claims?: ClaimVerification[];
  contradictions?: Contradiction[];
  confidence?: ResearchConfidence;
  metrics?: ResearchMetrics;
  pdf_path?: string;
  pdf_page_count?: number;
  pdf_size_bytes?: number;
}

export interface ProgressEvent {
  type: 'progress' | 'complete' | 'error';
  step_name: string;
  pct: number;
  clock_time: string;
  elapsed_sec: number;
  elapsed_str: string;
  friendly_message: string;
  details?: string;
  metrics?: {
    sources: number;
    perspectives: number;
    evidence: number;
    iterations: number;
  };
  result?: ResearchResultData;
  pdf_url?: string;
  error?: string;
  status: 'running' | 'complete' | 'error';
}
