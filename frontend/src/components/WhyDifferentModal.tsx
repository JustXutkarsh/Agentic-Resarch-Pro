import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { Sparkles, X, ArrowDown, ShieldCheck, Search, BrainCircuit, RefreshCw } from 'lucide-react';

interface WhyDifferentModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const WhyDifferentModal: React.FC<WhyDifferentModalProps> = ({
  open,
  onOpenChange,
}) => {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-research-ink/40 backdrop-blur-sm z-50 transition-opacity animate-in fade-in" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92vw] max-w-2xl max-h-[85vh] overflow-y-auto bg-research-paper rounded-2xl border border-research-border shadow-2xl p-6 sm:p-8 z-50 focus:outline-none animate-in zoom-in-95">
          <div className="flex items-center justify-between pb-4 border-b border-research-borderLight">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-research-blue/10 flex items-center justify-center text-research-blue">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <Dialog.Title className="font-sans text-lg font-bold text-research-primary">
                  Why Agentic Research is Fundamentally Different
                </Dialog.Title>
                <Dialog.Description className="font-sans text-xs text-research-secondary">
                  Architectural comparison: One-pass retrieval vs Iterative evidence synthesis
                </Dialog.Description>
              </div>
            </div>
            <Dialog.Close asChild>
              <button
                className="w-8 h-8 rounded-full flex items-center justify-center text-research-muted hover:text-research-primary hover:bg-research-surface transition-colors"
                aria-label="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </Dialog.Close>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-6">
            {/* Traditional Search */}
            <div className="p-5 rounded-xl border border-research-borderLight bg-research-surface/40">
              <div className="flex items-center gap-2 mb-3">
                <Search className="w-4 h-4 text-research-muted" />
                <h4 className="font-mono text-xs font-semibold text-research-secondary uppercase tracking-wider">
                  Traditional Search
                </h4>
              </div>
              <p className="font-sans text-xs text-research-muted mb-4">
                Single query pass, accepting top ranking results without verification or gap analysis.
              </p>
              <div className="space-y-2 font-mono text-xs text-research-secondary">
                <div className="p-2 rounded bg-white border border-research-borderLight text-center">
                  Search Query
                </div>
                <div className="flex justify-center text-research-muted">
                  <ArrowDown className="w-3.5 h-3.5" />
                </div>
                <div className="p-2 rounded bg-white border border-research-borderLight text-center">
                  Read First Few Links
                </div>
                <div className="flex justify-center text-research-muted">
                  <ArrowDown className="w-3.5 h-3.5" />
                </div>
                <div className="p-2 rounded bg-white border border-research-borderLight text-center">
                  Select Convenient Information
                </div>
                <div className="flex justify-center text-research-muted">
                  <ArrowDown className="w-3.5 h-3.5" />
                </div>
                <div className="p-2 rounded bg-white border border-research-borderLight text-center">
                  Output Static Summary
                </div>
              </div>
            </div>

            {/* Agentic Research */}
            <div className="p-5 rounded-xl border-2 border-research-blue/30 bg-research-blue/[0.02]">
              <div className="flex items-center gap-2 mb-3">
                <BrainCircuit className="w-4 h-4 text-research-blue" />
                <h4 className="font-mono text-xs font-semibold text-research-blue uppercase tracking-wider">
                  Autonomous Agentic Research
                </h4>
              </div>
              <p className="font-sans text-xs text-research-secondary mb-4">
                Iterative hypothesis testing, multi-angle vector retrieval, contradiction detection, and claim grounding.
              </p>
              <div className="space-y-1.5 font-mono text-[11px] text-research-primary">
                <div className="p-1.5 rounded bg-white border border-research-blue/20 text-center font-medium">
                  1. Formulate Multi-Perspective Plan
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-white border border-research-blue/20 text-center font-medium">
                  2. Targeted Multi-Query Retrieval
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-white border border-research-blue/20 text-center font-medium">
                  3. Vector Index & Sliding-Window Extract
                </div>
                <div className="flex justify-center text-research-blue">
                  <RefreshCw className="w-3 h-3 animate-spin" style={{ animationDuration: '4s' }} />
                </div>
                <div className="p-1.5 rounded bg-amber-50 border border-research-warning/30 text-center text-amber-900 font-medium">
                  4. Autonomous Evidence Gap Detection & Follow-up
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-rose-50 border border-research-coral/30 text-center text-rose-900 font-medium">
                  5. Contradiction & Perspective Debate
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-emerald-50 border border-research-green/30 text-center text-emerald-900 font-medium">
                  6. Factual Claim Verification (NLI)
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-research-blue text-white text-center font-medium shadow-sm">
                  7. Synthesize Verified Editorial Dossier
                </div>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-research-surface/80 border border-research-border flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-research-green mt-0.5 shrink-0" />
            <div>
              <div className="font-sans text-xs font-bold uppercase tracking-wider text-research-ink">
                Defensible Architectural Principle
              </div>
              <div className="font-body text-xs text-research-secondary mt-0.5 leading-relaxed">
                The key difference is <strong>iterative, evidence-driven research</strong> rather than one-pass information retrieval. The system autonomously discovers gaps, retrieves counter-evidence, and validates claims against indexed vector chunks.
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <Dialog.Close asChild>
              <button className="px-4 py-2 rounded-lg bg-research-primary text-white font-sans text-xs font-semibold hover:bg-black transition-colors">
                Understood
              </button>
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
