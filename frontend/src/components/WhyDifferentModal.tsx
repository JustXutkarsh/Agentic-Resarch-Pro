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
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[calc(100vw-24px)] max-w-2xl max-h-[calc(100dvh-24px)] overflow-y-auto bg-research-paper rounded-2xl border border-research-border shadow-2xl p-4 sm:p-8 z-50 focus:outline-none animate-in zoom-in-95 min-w-0">
          <div className="flex items-center justify-between gap-3 pb-3 sm:pb-4 border-b border-research-borderLight">
            <div className="flex items-center gap-2 sm:gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-lg bg-research-blue/10 flex items-center justify-center text-research-blue shrink-0">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <Dialog.Title className="font-sans text-sm sm:text-lg font-bold text-research-primary break-words">
                  Why Agentic Research is Fundamentally Different
                </Dialog.Title>
                <Dialog.Description className="font-sans text-[11px] sm:text-xs text-research-secondary truncate">
                  Architectural comparison: One-pass retrieval vs Iterative evidence synthesis
                </Dialog.Description>
              </div>
            </div>
            <Dialog.Close asChild>
              <button
                className="min-w-[40px] min-h-[40px] w-10 h-10 rounded-full flex items-center justify-center text-research-muted hover:text-research-primary hover:bg-research-surface transition-colors shrink-0"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </Dialog.Close>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 my-4 sm:my-6 min-w-0">
            {/* Traditional Search */}
            <div className="p-3.5 sm:p-5 rounded-xl border border-research-borderLight bg-research-surface/40 min-w-0">
              <div className="flex items-center gap-2 mb-2 sm:mb-3">
                <Search className="w-4 h-4 text-research-muted shrink-0" />
                <h4 className="font-mono text-xs font-semibold text-research-secondary uppercase tracking-wider">
                  Traditional Search
                </h4>
              </div>
              <p className="font-sans text-xs text-research-muted mb-3 sm:mb-4 break-words">
                Single query pass, accepting top ranking results without verification or gap analysis.
              </p>
              <div className="space-y-1.5 sm:space-y-2 font-mono text-xs text-research-secondary">
                <div className="p-2 rounded bg-research-paper border border-research-borderLight text-center break-words">
                  Search Query
                </div>
                <div className="flex justify-center text-research-muted">
                  <ArrowDown className="w-3.5 h-3.5" />
                </div>
                <div className="p-2 rounded bg-research-paper border border-research-borderLight text-center break-words">
                  Read First Few Links
                </div>
                <div className="flex justify-center text-research-muted">
                  <ArrowDown className="w-3.5 h-3.5" />
                </div>
                <div className="p-2 rounded bg-research-paper border border-research-borderLight text-center break-words">
                  Select Convenient Information
                </div>
                <div className="flex justify-center text-research-muted">
                  <ArrowDown className="w-3.5 h-3.5" />
                </div>
                <div className="p-2 rounded bg-research-paper border border-research-borderLight text-center break-words">
                  Output Static Summary
                </div>
              </div>
            </div>

            {/* Agentic Research */}
            <div className="p-3.5 sm:p-5 rounded-xl border-2 border-research-blue/30 bg-research-blue/[0.02] min-w-0">
              <div className="flex items-center gap-2 mb-2 sm:mb-3">
                <BrainCircuit className="w-4 h-4 text-research-blue shrink-0" />
                <h4 className="font-mono text-xs font-semibold text-research-blue uppercase tracking-wider">
                  Autonomous Agentic Research
                </h4>
              </div>
              <p className="font-sans text-xs text-research-secondary mb-3 sm:mb-4 break-words">
                Iterative hypothesis testing, multi-angle vector retrieval, contradiction detection, and claim grounding.
              </p>
              <div className="space-y-1.5 font-mono text-[10px] sm:text-[11px] text-research-primary">
                <div className="p-1.5 rounded bg-research-paper border border-research-blue/20 text-center font-medium break-words">
                  1. Formulate Multi-Perspective Plan
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-research-paper border border-research-blue/20 text-center font-medium break-words">
                  2. Targeted Multi-Query Retrieval
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-research-paper border border-research-blue/20 text-center font-medium break-words">
                  3. Vector Index & Sliding-Window Extract
                </div>
                <div className="flex justify-center text-research-blue">
                  <RefreshCw className="w-3 h-3 animate-spin" style={{ animationDuration: '4s' }} />
                </div>
                <div className="p-1.5 rounded bg-research-warningLight border border-research-warning/30 text-center text-research-warning font-medium break-words">
                  4. Autonomous Evidence Gap Detection
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-research-coralLight border border-research-coral/30 text-center text-research-coral font-medium break-words">
                  5. Contradiction & Perspective Debate
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-research-greenLight border border-research-green/30 text-center text-research-green font-medium break-words">
                  6. Factual Claim Verification (NLI)
                </div>
                <div className="flex justify-center text-research-blue">
                  <ArrowDown className="w-3 h-3" />
                </div>
                <div className="p-1.5 rounded bg-research-blue text-white text-center font-medium shadow-sm break-words">
                  7. Synthesize Verified Editorial Dossier
                </div>
              </div>
            </div>
          </div>

          <div className="p-3.5 sm:p-4 rounded-xl bg-research-surface/80 border border-research-border flex items-start gap-2.5 sm:gap-3 min-w-0">
            <ShieldCheck className="w-5 h-5 text-research-green mt-0.5 shrink-0" />
            <div className="min-w-0">
              <div className="font-sans text-xs font-bold uppercase tracking-wider text-research-ink">
                Defensible Architectural Principle
              </div>
              <div className="font-body text-xs text-research-secondary mt-0.5 leading-relaxed break-words">
                The key difference is <strong>iterative, evidence-driven research</strong> rather than one-pass information retrieval. The system autonomously discovers gaps, retrieves counter-evidence, and validates claims against indexed vector chunks.
              </div>
            </div>
          </div>

          <div className="mt-5 sm:mt-6 flex justify-end">
            <Dialog.Close asChild>
              <button className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-research-primary text-white dark:bg-white dark:text-[#101114] font-sans text-xs font-semibold hover:bg-black dark:hover:bg-gray-100 transition-colors min-h-[44px] flex items-center justify-center">
                Understood
              </button>
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
