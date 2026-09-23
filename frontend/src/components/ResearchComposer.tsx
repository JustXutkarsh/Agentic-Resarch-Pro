import React, { useState } from 'react';
import { Search, Zap, Compass, Brain, ArrowRight, Sparkles } from 'lucide-react';
import type { ResearchDepth } from '../types/research';

interface ResearchComposerProps {
  onStartResearch: (topic: string, depth: ResearchDepth) => void;
  onOpenWhyDifferent: () => void;
  disabled?: boolean;
}

export const ResearchComposer: React.FC<ResearchComposerProps> = ({
  onStartResearch,
  onOpenWhyDifferent,
  disabled = false,
}) => {
  const [topic, setTopic] = useState('');
  const [depth, setDepth] = useState<ResearchDepth>('STANDARD');

  const exampleTopics = [
    'Will the AI bubble burst?',
    'Is quantum computing commercially viable?',
    'How autonomous AI agents transform software engineering',
    'Global nuclear fusion commercialization roadmap',
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim() || disabled) return;
    onStartResearch(topic.trim(), depth);
  };

  return (
    <div className="w-full max-w-3xl mx-auto min-w-0">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Command Surface Input Box */}
        <div className="relative group min-w-0">
          <label
            htmlFor="research-topic-input"
            className="block font-mono text-[11px] font-semibold text-research-secondary tracking-wider uppercase mb-2"
          >
            What would you like to investigate?
          </label>
          <div className="relative flex items-center bg-research-paper rounded-2xl border border-research-border shadow-composer transition-all duration-300 focus-within:border-research-blue focus-within:shadow-composerFocus focus-within:-translate-y-0.5 min-h-[56px]">
            <div className="pl-4 pr-2 text-research-muted group-focus-within:text-research-blue transition-colors shrink-0">
              <Search className="w-5 h-5" />
            </div>
            <input
              id="research-topic-input"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Will the AI bubble burst?"
              disabled={disabled}
              className="w-full py-3.5 sm:py-4 pr-4 bg-transparent font-sans text-base sm:text-lg text-research-ink placeholder:text-research-muted/70 focus:outline-none min-w-0"
              autoFocus
            />
          </div>

          {/* Prompt pills for quick exploration */}
          <div className="-mx-1 px-1 flex items-center gap-2 mt-2.5 overflow-x-auto pb-1 text-xs no-scrollbar touch-pan-x">
            <span className="font-mono text-[10px] text-research-muted shrink-0 uppercase pl-1">
              Examples:
            </span>
            {exampleTopics.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setTopic(example)}
                className="shrink-0 px-3 py-1.5 min-h-[34px] sm:min-h-0 rounded-full bg-research-surface/80 border border-research-borderLight text-research-secondary hover:text-research-primary hover:border-research-blue/40 transition-colors text-[11px] font-sans flex items-center"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Depth Cards (Clicking card selects it directly) */}
        <div className="min-w-0">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-2.5 gap-1">
            <span className="font-mono text-[11px] font-semibold text-research-secondary tracking-wider uppercase">
              Investigation Depth
            </span>
            <span className="font-sans text-xs text-research-muted">
              Select desired evidence density & page count
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-3.5">
            {/* Quick Card */}
            <div
              onClick={() => setDepth('QUICK')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setDepth('QUICK')}
              className={`relative p-3.5 sm:p-4 rounded-xl border transition-all duration-200 cursor-pointer text-left select-none min-h-[84px] ${
                depth === 'QUICK'
                  ? 'bg-research-paper border-research-blue shadow-card ring-1 ring-research-blue'
                  : 'bg-research-paper/70 border-research-border hover:border-research-border hover:bg-research-paper shadow-subtle'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                      depth === 'QUICK'
                        ? 'bg-research-blue text-white'
                        : 'bg-research-surface text-research-secondary'
                    }`}
                  >
                    <Zap className="w-3.5 h-3.5" />
                  </div>
                  <span className="font-sans font-bold text-sm text-research-ink">
                    ⚡ QUICK
                  </span>
                </div>
                {depth === 'QUICK' && (
                  <span className="w-2 h-2 rounded-full bg-research-blue animate-pulse" />
                )}
              </div>
              <div className="font-mono text-[10px] text-research-muted uppercase font-semibold mb-1">
                Fast Orientation • ~3 Pages
              </div>
              <div className="font-body text-xs text-research-secondary leading-snug">
                Rapid multi-source scan with high-level consensus synthesis and key takeaways.
              </div>
            </div>

            {/* Standard Card (Recommended) */}
            <div
              onClick={() => setDepth('STANDARD')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setDepth('STANDARD')}
              className={`relative p-3.5 sm:p-4 rounded-xl border transition-all duration-200 cursor-pointer text-left select-none min-h-[84px] ${
                depth === 'STANDARD'
                  ? 'bg-research-paper border-research-blue shadow-card ring-1 ring-research-blue'
                  : 'bg-research-paper/70 border-research-border hover:border-research-border hover:bg-research-paper shadow-subtle'
              }`}
            >
              {/* Floating Recommended Badge */}
              <div className="absolute -top-2.5 right-3 px-2 py-0.5 rounded-full bg-research-blue text-white font-mono text-[9px] font-bold uppercase tracking-wider shadow-sm">
                RECOMMENDED
              </div>

              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                      depth === 'STANDARD'
                        ? 'bg-research-blue text-white'
                        : 'bg-research-surface text-research-secondary'
                    }`}
                  >
                    <Compass className="w-3.5 h-3.5" />
                  </div>
                  <span className="font-sans font-bold text-sm text-research-ink">
                    ◉ STANDARD
                  </span>
                </div>
                {depth === 'STANDARD' && (
                  <span className="w-2 h-2 rounded-full bg-research-blue animate-pulse" />
                )}
              </div>
              <div className="font-mono text-[10px] text-research-muted uppercase font-semibold mb-1">
                Balanced Investigation • ~5-6 Pages
              </div>
              <div className="font-body text-xs text-research-secondary leading-snug">
                Iterative gap detection, claim verification matrix, and dialectical debate.
              </div>
            </div>

            {/* Deep Card */}
            <div
              onClick={() => setDepth('DEEP')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setDepth('DEEP')}
              className={`relative p-3.5 sm:p-4 rounded-xl border transition-all duration-200 cursor-pointer text-left select-none min-h-[84px] ${
                depth === 'DEEP'
                  ? 'bg-research-paper border-research-blue shadow-card ring-1 ring-research-blue'
                  : 'bg-research-paper/70 border-research-border hover:border-research-border hover:bg-research-paper shadow-subtle'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                      depth === 'DEEP'
                        ? 'bg-research-blue text-white'
                        : 'bg-research-surface text-research-secondary'
                    }`}
                  >
                    <Brain className="w-3.5 h-3.5" />
                  </div>
                  <span className="font-sans font-bold text-sm text-research-ink">
                    🧠 DEEP
                  </span>
                </div>
                {depth === 'DEEP' && (
                  <span className="w-2 h-2 rounded-full bg-research-blue animate-pulse" />
                )}
              </div>
              <div className="font-mono text-[10px] text-research-muted uppercase font-semibold mb-1">
                Extended Analysis • ~9-10+ Pages
              </div>
              <div className="font-body text-xs text-research-secondary leading-snug">
                Comprehensive literature review, rigorous contradiction analysis, and deep citations.
              </div>
            </div>
          </div>
        </div>

        {/* Primary CTA & Secondary Action */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <button
            type="button"
            onClick={onOpenWhyDifferent}
            className="group flex items-center gap-1.5 text-xs font-sans font-semibold text-research-secondary hover:text-research-primary transition-colors min-h-[44px] py-2 px-1"
          >
            <Sparkles className="w-3.5 h-3.5 text-research-blue group-hover:rotate-12 transition-transform" />
            <span>✦ Why this is different</span>
          </button>

          <button
            type="submit"
            disabled={!topic.trim() || disabled}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-research-primary text-white dark:bg-white dark:text-[#101114] font-sans text-sm font-bold tracking-wide flex items-center justify-center gap-2 shadow-md hover:bg-black dark:hover:bg-gray-100 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 transition-all duration-200 min-h-[48px]"
          >
            <span>BEGIN RESEARCH</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>
      </form>
    </div>
  );
};
