import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, RefreshCw } from 'lucide-react';
import type { ProgressEvent } from '../types/research';

interface LiveResearchTrailProps {
  topic: string;
  depth: string;
  startedAt: string;
  events: ProgressEvent[];
  isComplete: boolean;
  error?: string | null;
}

const STAGES = [
  { key: 'UNDERSTAND', label: 'Understand', match: ['INIT', 'PLANNER', 'UNDERSTAND'] },
  { key: 'EXPLORE', label: 'Explore', match: ['QUERY', 'EXPLORE'] },
  { key: 'SEARCH', label: 'Search', match: ['TAVILY', 'SEARCH', 'SCRAPE'] },
  { key: 'EVIDENCE', label: 'Evidence', match: ['EMBED', 'CHROMA', 'EVAL', 'CHUNK'] },
  { key: 'DEBATE', label: 'Debate', match: ['GAP', 'CONTRADICTION', 'DEBATE'] },
  { key: 'VERIFY', label: 'Verify', match: ['CLAIM', 'VERIF', 'CONFIDENCE'] },
  { key: 'DOSSIER', label: 'Dossier', match: ['SYNTHESIS', 'REPORT', 'COMPLETE'] },
];

export const LiveResearchTrail: React.FC<LiveResearchTrailProps> = ({
  topic,
  depth,
  startedAt,
  events,
  isComplete,
  error,
}) => {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Live wall-clock elapsed timer
  useEffect(() => {
    if (isComplete || error || !startedAt) {
      if (!startedAt) setElapsedSeconds(0);
      return;
    }
    const startTime = new Date(startedAt).getTime();
    if (isNaN(startTime)) {
      setElapsedSeconds(0);
      return;
    }
    
    const update = () => {
      const now = Date.now();
      const diff = Math.max(0, Math.floor((now - startTime) / 1000));
      setElapsedSeconds(diff);
    };

    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [startedAt, isComplete, error]);

  // Auto-scroll to latest event as new nodes arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  const formatElapsed = (sec: number) => {
    if (isNaN(sec) || sec <= 0) return '00:00 elapsed';
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')} elapsed`;
  };

  const latestEvent = events.length > 0 ? events[events.length - 1] : null;

  // Determine current active stage
  const getCurrentStageIndex = () => {
    if (isComplete) return STAGES.length - 1;
    if (!latestEvent) return 0;
    const step = latestEvent.step_name.toUpperCase();
    for (let i = STAGES.length - 1; i >= 0; i--) {
      if (STAGES[i].match.some((m) => step.includes(m))) {
        return i;
      }
    }
    return 0;
  };

  const activeStageIndex = getCurrentStageIndex();

  // Metrics from latest event
  const metrics = latestEvent?.metrics || {
    sources: 0,
    perspectives: depth === 'DEEP' ? 5 : 3,
    evidence: 0,
    iterations: 1,
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4 sm:space-y-6 min-w-0">
      {/* Investigation Header */}
      <div className="p-4 sm:p-6 rounded-2xl bg-research-paper border border-research-border shadow-subtle min-w-0">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className="font-mono text-[11px] font-bold uppercase tracking-wider text-research-blue">
                Investigating Topic
              </span>
              <span className="text-research-border">•</span>
              <span className="font-mono text-[11px] text-research-muted uppercase font-semibold">
                {depth} MODE
              </span>
            </div>
            <h2 className="font-serif text-xl sm:text-2xl md:text-3xl text-research-ink italic font-normal break-words">
              "{topic}"
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2 sm:gap-3 shrink-0">
            <div className="flex items-center gap-1.5 sm:gap-2 px-3 py-1.5 rounded-full bg-research-surface border border-research-border text-xs font-mono">
              <span
                className={`w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full shrink-0 ${
                  isComplete
                    ? 'bg-research-green'
                    : error
                    ? 'bg-research-coral'
                    : 'bg-research-blue animate-ping'
                }`}
              />
              <span className="font-semibold text-research-primary uppercase tracking-wide text-[10px] sm:text-xs">
                {isComplete ? 'RESEARCH COMPLETE' : error ? 'ERROR' : 'RESEARCHING'}
              </span>
            </div>

            <div className="font-mono text-[11px] sm:text-xs font-semibold text-research-secondary px-2.5 sm:px-3 py-1.5 rounded-full bg-research-paper border border-research-borderLight whitespace-nowrap">
              {formatElapsed(elapsedSeconds)}
            </div>
          </div>
        </div>

        {/* 7-Stage Progression Bar */}
        <div className="mt-5 sm:mt-6 pt-4 sm:pt-5 border-t border-research-borderLight min-w-0">
          <div className="grid grid-cols-7 gap-1 sm:gap-2 min-w-0">
            {STAGES.map((stage, idx) => {
              const isPassed = idx < activeStageIndex || isComplete;
              const isCurrent = idx === activeStageIndex && !isComplete;

              return (
                <div key={stage.key} className="text-center group min-w-0">
                  <div
                    className={`h-1.5 rounded-full transition-all duration-300 ${
                      isPassed
                        ? 'bg-research-blue'
                        : isCurrent
                        ? 'bg-research-blue/60 animate-pulse'
                        : 'bg-research-border/60'
                    }`}
                  />
                  <div
                    className={`font-mono text-[8px] xs:text-[9px] sm:text-[10px] mt-1.5 uppercase font-medium truncate block ${
                      isPassed
                        ? 'text-research-blue font-semibold'
                        : isCurrent
                        ? 'text-research-primary font-bold'
                        : 'text-research-muted'
                    }`}
                  >
                    {stage.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Live Compact Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 min-w-0">
        <div className="p-3 sm:p-3.5 rounded-xl bg-research-paper border border-research-borderLight shadow-subtle min-w-0">
          <div className="font-mono text-[9px] sm:text-[10px] text-research-muted uppercase font-semibold truncate">
            Sources Found
          </div>
          <div className="font-sans text-xl sm:text-2xl font-bold text-research-ink mt-0.5">
            {metrics.sources.toString().padStart(2, '0')}
          </div>
        </div>

        <div className="p-3 sm:p-3.5 rounded-xl bg-research-paper border border-research-borderLight shadow-subtle min-w-0">
          <div className="font-mono text-[9px] sm:text-[10px] text-research-muted uppercase font-semibold truncate">
            Perspectives
          </div>
          <div className="font-sans text-xl sm:text-2xl font-bold text-research-blue mt-0.5">
            {metrics.perspectives.toString().padStart(2, '0')}
          </div>
        </div>

        <div className="p-3 sm:p-3.5 rounded-xl bg-research-paper border border-research-borderLight shadow-subtle min-w-0">
          <div className="font-mono text-[9px] sm:text-[10px] text-research-muted uppercase font-semibold truncate">
            Evidence Chunks
          </div>
          <div className="font-sans text-xl sm:text-2xl font-bold text-research-green mt-0.5">
            {metrics.evidence.toString().padStart(2, '0')}
          </div>
        </div>

        <div className="p-3 sm:p-3.5 rounded-xl bg-research-paper border border-research-borderLight shadow-subtle min-w-0">
          <div className="font-mono text-[9px] sm:text-[10px] text-research-muted uppercase font-semibold truncate">
            Iterations
          </div>
          <div className="font-sans text-xl sm:text-2xl font-bold text-research-warning mt-0.5">
            {metrics.iterations.toString().padStart(2, '0')}
          </div>
        </div>
      </div>

      {/* Vertical Animated Research Trail */}
      <div className="p-4 sm:p-6 md:p-8 rounded-2xl bg-research-paper border border-research-border shadow-subtle min-w-0">
        <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 pb-4 mb-4 sm:mb-6 border-b border-research-borderLight">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-research-blue animate-pulse shrink-0" />
            <span className="font-mono text-xs font-bold uppercase tracking-wider text-research-primary">
              Live Investigation Trail
            </span>
          </div>
          <span className="font-mono text-[11px] text-research-muted">
            {events.length} pipeline events captured
          </span>
        </div>

        {events.length === 0 ? (
          <div className="py-12 text-center text-research-muted font-mono text-xs flex flex-col items-center gap-2">
            <RefreshCw className="w-5 h-5 text-research-blue animate-spin" />
            <span>Establishing pipeline connection and formulating initial hypotheses...</span>
          </div>
        ) : (
          <div ref={scrollRef} className="max-h-[380px] sm:max-h-[460px] overflow-y-auto pr-1 sm:pr-2 space-y-3 sm:space-y-4">
            <AnimatePresence initial={false}>
              {events.map((event, idx) => {
                const isLatest = idx === events.length - 1 && !isComplete;
                const isGap = event.step_name.includes('GAP');
                const isContradiction = event.step_name.includes('CONTRADICTION');
                const isVerify = event.step_name.includes('CLAIM') || event.step_name.includes('CONFIDENCE');
                const isSynthesis = event.step_name.includes('SYNTHESIS') || event.step_name === 'COMPLETE';

                return (
                  <motion.div
                    key={`${event.clock_time}-${idx}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, ease: 'easeOut' }}
                    className="flex items-start gap-2.5 sm:gap-4 relative group min-w-0"
                  >
                    {/* Compact responsive timestamp column */}
                    <div className="font-mono text-[10px] sm:text-xs font-medium text-research-muted w-16 sm:w-24 shrink-0 pt-0.5 truncate">
                      {event.clock_time}
                    </div>

                    {/* Node indicator */}
                    <div className="relative flex flex-col items-center shrink-0 mt-1">
                      <div
                        className={`w-3.5 h-3.5 rounded-full flex items-center justify-center transition-all ${
                          isLatest
                            ? 'bg-research-blue ring-4 ring-research-blue/20 animate-pulse'
                            : isGap
                            ? 'bg-research-warning'
                            : isContradiction
                            ? 'bg-research-coral'
                            : isVerify
                            ? 'bg-research-green'
                            : isSynthesis
                            ? 'bg-research-deepBlue'
                            : 'bg-research-primary'
                        }`}
                      >
                        {isLatest && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
                      </div>

                      {/* Connecting vertical line to next event */}
                      {idx < events.length - 1 && (
                        <div className="w-[1.5px] h-6 bg-research-borderLight group-hover:bg-research-border mt-1" />
                      )}
                    </div>

                    {/* Event Message */}
                    <div className="flex-1 min-w-0 pb-1">
                      <div
                        className={`font-sans text-xs sm:text-sm leading-relaxed break-words ${
                          isLatest
                            ? 'font-bold text-research-blue'
                            : 'font-normal text-research-primary'
                        }`}
                      >
                        {event.friendly_message}
                        {isLatest && (
                          <span className="inline-block w-1.5 h-3.5 bg-research-blue ml-1.5 animate-pulse" />
                        )}
                      </div>

                      {event.details && event.details !== event.friendly_message && (
                        <div className="font-body text-[11px] sm:text-xs text-research-muted mt-0.5 break-words line-clamp-3 sm:line-clamp-none">
                          {event.details}
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}

        {/* Error notification if pipeline encountered issues */}
        {error && (
          <div className="mt-6 p-4 rounded-xl bg-research-coralLight border border-research-coral/40 flex items-start gap-3 text-research-coral min-w-0">
            <AlertCircle className="w-5 h-5 text-research-coral shrink-0 mt-0.5" />
            <div className="min-w-0">
              <div className="font-sans text-xs font-bold uppercase tracking-wider">
                Research Pipeline Error
              </div>
              <div className="font-body text-xs mt-0.5 break-words text-research-primary">{error}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
