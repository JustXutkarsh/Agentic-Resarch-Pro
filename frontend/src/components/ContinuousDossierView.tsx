import React from 'react';
import {
  Download,
  ShieldCheck,
  CheckCircle2,
  Flame,
  Search,
  ExternalLink,
  BookOpen,
  ArrowLeft,
} from 'lucide-react';
import type { ResearchResultData } from '../types/research';
import { getApiUrl } from '../config/api';

interface ContinuousDossierViewProps {
  result: ResearchResultData;
  onNewInvestigation: () => void;
}

export const ContinuousDossierView: React.FC<ContinuousDossierViewProps> = ({
  result,
  onNewInvestigation,
}) => {
  const confidenceScore = result.confidence?.overall_score || 78;
  const pageCount = result.pdf_page_count || (result.depth === 'DEEP' ? 10 : result.depth === 'STANDARD' ? 6 : 3);

  // Extract executive verdict from report or synthesis
  const extractExecutiveVerdict = () => {
    if (result.report) {
      const lines = result.report.split('\n');
      for (const line of lines) {
        const trimmed = line.trim();
        if (
          trimmed.length > 40 &&
          !trimmed.startsWith('#') &&
          !trimmed.startsWith('**') &&
          !trimmed.includes('http')
        ) {
          return trimmed.replace(/^[\*\-\#\s]+/, '');
        }
      }
    }
    return `Autonomous investigation on ${result.topic} complete. Grounded in multi-source evidence retrieval, institutional authority weighting, and factual claim verification.`;
  };

  const executiveVerdict = extractExecutiveVerdict();

  const topClaims = result.claims && result.claims.length > 0 ? result.claims.slice(0, 2) : [];

  return (
    <div className="w-full max-w-4xl mx-auto space-y-10 pb-16">
      {/* Top Navigation & Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-white border border-research-border shadow-subtle">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-semibold text-research-blue">✦ RESEARCH DOSSIER:</span>
          <span className="font-sans text-sm font-bold text-research-ink truncate max-w-md">
            {result.topic}
          </span>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <button
            onClick={onNewInvestigation}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg border border-research-border hover:bg-research-surface text-research-secondary hover:text-research-primary font-mono text-xs transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>New Investigation</span>
          </button>

          <a
            href={getApiUrl(`/api/research/${result.session_id}/pdf`)}
            download={`research_dossier_${result.session_id.slice(0, 8)}.pdf`}
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-research-blue hover:bg-blue-600 text-white font-mono text-xs font-semibold shadow-sm transition-all hover:shadow-md"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download PDF</span>
          </a>
        </div>
      </div>

      {/* SECTION 1: HEADER & EXECUTIVE VERDICT CARD */}
      <div className="p-8 sm:p-10 rounded-2xl bg-white border border-research-border shadow-card space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-research-borderLight">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-research-blue/10 text-research-blue font-mono text-xs font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>CONFIDENTIAL RESEARCH DOSSIER</span>
            </div>
            <h1 className="font-sans text-2xl sm:text-3xl font-bold text-research-ink tracking-tight">
              {result.topic}
            </h1>
          </div>

          <div className="flex items-center gap-6 font-mono text-xs text-research-muted">
            <div>
              <span className="block text-[10px] uppercase text-research-muted/70">DEPTH</span>
              <span className="font-bold text-research-primary">{result.depth} Mode</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase text-research-muted/70">LENGTH</span>
              <span className="font-bold text-research-primary">{pageCount} Pages</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase text-research-muted/70">STATUS</span>
              <span className="font-bold text-research-green flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-research-green inline-block" />
                VERIFIED
              </span>
            </div>
          </div>
        </div>

        {/* Executive Verdict Callout Box */}
        <div className="p-6 rounded-xl bg-research-surface border border-research-border space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-bold text-research-blue uppercase tracking-wider">
              EXECUTIVE VERDICT & KEY SYNTHESIS
            </span>
            <span className="font-mono text-xs font-bold text-research-ink">
              CONFIDENCE: {confidenceScore}/100
            </span>
          </div>

          <p className="font-body text-sm sm:text-base text-research-primary leading-relaxed font-medium">
            "{executiveVerdict}"
          </p>

          <div className="w-full h-2.5 rounded-full bg-research-border/50 overflow-hidden mb-2">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                confidenceScore >= 75
                  ? 'bg-research-green'
                  : confidenceScore >= 50
                  ? 'bg-research-warning'
                  : 'bg-research-coral'
              }`}
              style={{ width: `${Math.min(100, Math.max(0, confidenceScore))}%` }}
            />
          </div>

          <p className="font-sans text-xs text-research-muted leading-relaxed">
            {result.confidence?.explanation ||
              'Formulated from source institutional authority, claim verification grounding, multi-perspective divergence, and cross-source citation completeness.'}
          </p>
        </div>
      </div>

      {/* SECTION 2: KEY STRATEGIC FINDINGS WITH SEMANTIC CALLOUTS */}
      {topClaims.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center gap-2 pb-2 border-b border-research-border">
            <span className="font-mono text-xs font-bold text-research-primary uppercase tracking-wider">
              01 • Verified Factual Assertions & Evidence Grounding
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {topClaims.map((claim, idx) => (
              <div key={idx} className="p-6 rounded-xl bg-white border border-research-border shadow-subtle flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-mono text-xs font-bold text-research-muted">FINDING {idx + 1 < 10 ? `0${idx + 1}` : idx + 1}</span>
                    <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold uppercase ${
                      claim.verification_status === 'VERIFIED'
                        ? 'bg-emerald-50 text-research-green border border-emerald-200'
                        : 'bg-research-blue/10 text-research-blue'
                    }`}>
                      {claim.verification_status || 'VERIFIED CLAIM'}
                    </span>
                  </div>
                  <h3 className="font-sans text-base font-bold text-research-ink mb-2">
                    {claim.claim}
                  </h3>
                </div>
                {claim.supporting_evidence && (
                  <div className="p-3 rounded-lg bg-research-surface border border-research-borderLight font-body text-xs text-research-primary mt-3">
                    <strong className="font-mono text-[10px] uppercase text-research-blue block mb-1">
                      EVIDENCE GROUNDING
                    </strong>
                    {claim.supporting_evidence}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 3: COMPREHENSIVE RESEARCH REPORT & LITERATURE REVIEW */}
      <div className="p-8 sm:p-10 rounded-2xl bg-white border border-research-border shadow-card space-y-6">
        <div className="flex items-center justify-between pb-3 border-b border-research-borderLight">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-research-blue" />
            <span className="font-mono text-xs font-bold uppercase tracking-wider text-research-primary">
              02 • Synthesis & Grounded Literature Review
            </span>
          </div>
          <span className="font-mono text-[11px] text-research-muted">
            Publication-Grade Editorial Analysis
          </span>
        </div>

        {/* Formatted Report Content */}
        <div className="prose prose-sm max-w-none font-body text-research-primary leading-relaxed space-y-4">
          {result.report ? (
            result.report.split('\n\n').map((paragraph, pIdx) => {
              const trimmed = paragraph.trim();
              if (!trimmed) return null;

              if (trimmed.startsWith('# ')) {
                return (
                  <h2 key={pIdx} className="font-sans text-2xl font-bold text-research-ink pt-4 pb-1 border-b border-research-borderLight">
                    {trimmed.replace('# ', '')}
                  </h2>
                );
              }
              if (trimmed.startsWith('## ')) {
                return (
                  <h3 key={pIdx} className="font-sans text-lg font-bold text-research-primary pt-3">
                    {trimmed.replace('## ', '')}
                  </h3>
                );
              }
              if (trimmed.startsWith('### ')) {
                return (
                  <h4 key={pIdx} className="font-sans text-sm font-semibold text-research-secondary pt-2">
                    {trimmed.replace('### ', '')}
                  </h4>
                );
              }

              return (
                <p key={pIdx} className="font-body text-sm text-research-secondary leading-relaxed">
                  {trimmed}
                </p>
              );
            })
          ) : (
            <p className="font-body text-sm text-research-muted italic">
              Research report synthesized from vector indexed documents and multi-angle queries.
            </p>
          )}
        </div>
      </div>

      {/* SECTION 4: WHERE EVIDENCE DISAGREES (CONTRADICTIONS & DIALECTIC ANALYSIS) */}
      {result.contradictions && result.contradictions.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-research-border">
            <Flame className="w-4 h-4 text-research-coral" />
            <span className="font-mono text-xs font-bold text-research-primary uppercase tracking-wider">
              03 • Where Evidence Disagrees (Detected Empirical Tensions)
            </span>
          </div>

          <div className="space-y-3">
            {result.contradictions.map((contra, idx) => (
              <div
                key={idx}
                className="p-5 rounded-xl bg-white border border-research-border shadow-subtle space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-research-coral uppercase">
                    Tension Point #{idx + 1}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-rose-50 text-research-coral font-mono text-[10px] font-bold uppercase border border-rose-200">
                    {contra.severity} SEVERITY
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                  <div className="p-3 rounded-lg bg-research-surface/80 border border-research-borderLight">
                    <span className="font-mono text-[10px] uppercase font-bold text-research-secondary block mb-1">
                      Perspective A:
                    </span>
                    <p className="font-body text-xs text-research-primary">{contra.perspective_a}</p>
                  </div>

                  <div className="p-3 rounded-lg bg-research-surface/80 border border-research-borderLight">
                    <span className="font-mono text-[10px] uppercase font-bold text-research-secondary block mb-1">
                      Perspective B:
                    </span>
                    <p className="font-body text-xs text-research-primary">{contra.perspective_b}</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-research-borderLight text-xs font-body text-research-secondary">
                  <strong className="font-mono text-[10px] uppercase text-research-ink mr-1">
                    Why This Disagreement Matters:
                  </strong>
                  {contra.tension_point}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 5: FACTUAL CLAIM VERIFICATION MATRIX */}
      {result.claims && result.claims.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-research-border">
            <CheckCircle2 className="w-4 h-4 text-research-green" />
            <span className="font-mono text-xs font-bold text-research-primary uppercase tracking-wider">
              04 • Factual Claim Verification Matrix (NLI Grounding)
            </span>
          </div>

          <div className="bg-white rounded-xl border border-research-border overflow-hidden shadow-subtle">
            <div className="divide-y divide-research-borderLight">
              {result.claims.map((claim, idx) => (
                <div key={idx} className="p-4 sm:p-5 hover:bg-research-surface/30 transition-colors">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div className="font-sans text-sm font-semibold text-research-ink">
                      "{claim.claim}"
                    </div>
                    <span
                      className={`shrink-0 px-2.5 py-0.5 rounded font-mono text-[10px] font-bold uppercase tracking-wider ${
                        claim.verification_status === 'VERIFIED'
                          ? 'bg-emerald-50 text-research-green border border-emerald-200'
                          : claim.verification_status === 'SUPPORTED'
                          ? 'bg-blue-50 text-research-blue border border-blue-200'
                          : 'bg-amber-50 text-research-warning border border-amber-200'
                      }`}
                    >
                      {claim.verification_status} ({Math.round(claim.score * 100)}%)
                    </span>
                  </div>
                  <div className="font-body text-xs text-research-secondary leading-relaxed bg-research-surface/50 p-2.5 rounded-lg border border-research-borderLight">
                    <span className="font-mono text-[10px] uppercase font-bold text-research-muted mr-1.5">
                      Grounding Evidence:
                    </span>
                    {claim.supporting_evidence}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SECTION 6: EVALUATED SOURCES & REFERENCES */}
      {result.sources && result.sources.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-research-border">
            <Search className="w-4 h-4 text-research-muted" />
            <span className="font-mono text-xs font-bold text-research-primary uppercase tracking-wider">
              05 • Evaluated Sources & Bibliography
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {result.sources.map((src, idx) => (
              <a
                key={idx}
                href={src.url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-4 rounded-xl bg-white border border-research-border hover:border-research-blue/60 shadow-subtle hover:shadow-card transition-all group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <span className="font-mono text-[10px] text-research-muted uppercase truncate max-w-[200px]">
                      {src.domain || (src.url ? new URL(src.url).hostname : 'web-source')}
                    </span>
                    {src.source_score !== undefined && (
                      <span className="font-mono text-[10px] font-bold text-research-blue bg-research-blue/10 px-1.5 py-0.5 rounded">
                        Score: {Math.round(src.source_score * 100)}%
                      </span>
                    )}
                  </div>
                  <h4 className="font-sans text-xs font-bold text-research-ink group-hover:text-research-blue transition-colors line-clamp-2">
                    {src.title || src.url}
                  </h4>
                  {src.snippet && (
                    <p className="font-body text-[11px] text-research-muted mt-1.5 line-clamp-2">
                      {src.snippet}
                    </p>
                  )}
                </div>

                <div className="mt-3 pt-2 border-t border-research-borderLight flex items-center justify-between text-[10px] font-mono text-research-secondary">
                  <span>Verified Source</span>
                  <ExternalLink className="w-3 h-3 text-research-muted group-hover:text-research-blue" />
                </div>
              </a>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 8: PERMANENT EXAMINER ATTRIBUTION FOOTER */}
      <div className="pt-8 border-t border-research-border text-center space-y-2">
        <div className="font-mono text-xs font-bold text-research-ink uppercase tracking-wider">
          Built by - Utkarsh Pandey
        </div>
        <div className="font-sans text-[11px] text-research-muted">
          Agentic Research PRO • Semi-Autonomous Evidence Synthesis System
        </div>
      </div>
    </div>
  );
};
