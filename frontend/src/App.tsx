import React, { useState } from 'react';
import { AgenticHeroGraph } from './components/AgenticHeroGraph';
import { ResearchComposer } from './components/ResearchComposer';
import { WhyDifferentModal } from './components/WhyDifferentModal';
import { LiveResearchTrail } from './components/LiveResearchTrail';
import { ContinuousDossierView } from './components/ContinuousDossierView';
import type { ResearchDepth, ProgressEvent, ResearchResultData } from './types/research';
import { getApiUrl } from './config/api';

export const App: React.FC = () => {
  const [screen, setScreen] = useState<'home' | 'live' | 'dossier'>('home');
  const [topic, setTopic] = useState('');
  const [depth, setDepth] = useState<ResearchDepth>('STANDARD');
  const [startedAt, setStartedAt] = useState<string>('');
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResearchResultData | null>(null);
  const [isWhyDifferentOpen, setIsWhyDifferentOpen] = useState(false);

  // Trigger Research Execution
  const handleStartResearch = async (selectedTopic: string, selectedDepth: ResearchDepth) => {
    setTopic(selectedTopic);
    setDepth(selectedDepth);
    setEvents([]);
    setIsComplete(false);
    setError(null);
    setResult(null);
    setScreen('live');

    try {
      const response = await fetch(getApiUrl('/api/research'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: selectedTopic, depth: selectedDepth }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to initialize research session.');
      }

      const initData = await response.json();
      setStartedAt(initData.started_at);

      // Connect to Server-Sent Events (SSE) Stream
      const eventSource = new EventSource(getApiUrl(initData.stream_url));

      eventSource.addEventListener('progress', (e: MessageEvent) => {
        try {
          const eventData: ProgressEvent = JSON.parse(e.data);
          setEvents((prev) => {
            // Deduplicate if needed
            if (prev.length > 0 && prev[prev.length - 1].friendly_message === eventData.friendly_message) {
              const copy = [...prev];
              copy[copy.length - 1] = eventData;
              return copy;
            }
            return [...prev, eventData];
          });
        } catch (err) {
          console.error('Error parsing progress event:', err);
        }
      });

      eventSource.addEventListener('complete', (e: MessageEvent) => {
        try {
          const eventData: ProgressEvent = JSON.parse(e.data);
          setIsComplete(true);
          if (eventData.result) {
            setResult(eventData.result);
          }
          eventSource.close();
          // Seamless transition into the continuous publication dossier
          setTimeout(() => {
            setScreen('dossier');
          }, 1400);
        } catch (err) {
          console.error('Error parsing complete event:', err);
        }
      });

      eventSource.addEventListener('error', (e: any) => {
        console.error('EventSource error:', e);
        // If already completed, ignore disconnects
        if (!isComplete) {
          setError('Live event stream disconnected or encountered a network interruption.');
        }
        eventSource.close();
      });
    } catch (err: any) {
      console.error('Failed to start research:', err);
      setError(err.message || 'An unexpected error occurred during research launch.');
    }
  };

  const handleNewInvestigation = () => {
    setScreen('home');
    setTopic('');
    setEvents([]);
    setIsComplete(false);
    setError(null);
    setResult(null);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-research-bg text-research-primary font-sans">
      {/* Top Compact Navigation Bar */}
      <header className="sticky top-0 z-40 w-full bg-research-bg/90 backdrop-blur-md border-b border-research-border">
        <div className="max-w-instrument mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div
            onClick={handleNewInvestigation}
            className="flex items-center gap-2 cursor-pointer select-none group"
          >
            <span className="font-sans text-sm sm:text-base font-bold tracking-tight text-research-ink group-hover:text-research-blue transition-colors">
              ✦ AGENTIC RESEARCH
            </span>
            <span className="font-mono text-[10px] uppercase font-bold text-research-blue bg-research-blue/10 px-1.5 py-0.5 rounded">
              v2.0 PRO
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white border border-research-borderLight text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-research-green" />
              <span className="text-[11px] text-research-secondary font-medium">READY</span>
            </div>
            <div className="w-7 h-7 rounded-full bg-research-primary text-white font-mono text-xs font-bold flex items-center justify-center shadow-sm">
              U
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-instrument w-full mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {screen === 'home' && (
          <div className="space-y-10 sm:space-y-12">
            {/* Hero Typography */}
            <div className="text-center max-w-2xl mx-auto space-y-3">
              <div className="font-mono text-[11px] font-bold tracking-[0.2em] text-research-muted uppercase">
                Autonomous Research Instrument
              </div>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-sans font-bold tracking-tight text-research-ink leading-[1.08]">
                Research beyond{' '}
                <span className="font-serif italic font-normal text-research-blue text-[1.12em] tracking-normal">
                  the obvious.
                </span>
              </h1>
              <p className="font-body text-sm sm:text-base text-research-secondary leading-relaxed pt-1">
                Semi-autonomous evidence retrieval, multi-angle dialectic debate, and continuous publication-grade dossiers.
              </p>
            </div>

            {/* Atmospheric Research Network Graphic */}
            <div className="max-w-3xl mx-auto">
              <AgenticHeroGraph isResearching={false} />
            </div>

            {/* Research Command Surface (Composer) */}
            <ResearchComposer
              onStartResearch={handleStartResearch}
              onOpenWhyDifferent={() => setIsWhyDifferentOpen(true)}
            />
          </div>
        )}

        {screen === 'live' && (
          <div className="py-4">
            <LiveResearchTrail
              topic={topic}
              depth={depth}
              startedAt={startedAt}
              events={events}
              isComplete={isComplete}
              error={error}
            />

            {/* If complete, offer immediate jump to dossier */}
            {isComplete && result && (
              <div className="text-center mt-6">
                <button
                  onClick={() => setScreen('dossier')}
                  className="px-6 py-2.5 rounded-xl bg-research-blue text-white font-sans text-xs font-bold hover:bg-research-deepBlue transition-colors shadow-md animate-bounce"
                >
                  View Final Research Dossier →
                </button>
              </div>
            )}
          </div>
        )}

        {screen === 'dossier' && result && (
          <ContinuousDossierView
            result={result}
            onNewInvestigation={handleNewInvestigation}
          />
        )}
      </main>

      {/* Permanent Examiner Attribution Footer on Every Screen */}
      <footer className="w-full border-t border-research-border bg-research-bg py-5">
        <div className="max-w-instrument mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs">
          <div className="font-mono font-semibold text-research-primary">
            Built by - <span className="font-bold">Utkarsh Pandey</span>
          </div>
          <div className="font-sans text-research-muted text-[11px]">
            Agentic Research PRO • Autonomous Intelligence Laboratory
          </div>
          <div className="font-mono text-research-muted text-[10px]">
            Academic & Defense Benchmark Standard
          </div>
        </div>
      </footer>

      {/* Radix UI "✦ Why this is different" Modal */}
      <WhyDifferentModal
        open={isWhyDifferentOpen}
        onOpenChange={setIsWhyDifferentOpen}
      />
    </div>
  );
};

export default App;
