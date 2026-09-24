import React, { useState } from 'react';
import { AgenticHeroGraph } from './components/AgenticHeroGraph';
import { ResearchComposer } from './components/ResearchComposer';
import { WhyDifferentModal } from './components/WhyDifferentModal';
import { LiveResearchTrail } from './components/LiveResearchTrail';
import { ContinuousDossierView } from './components/ContinuousDossierView';
import { ThemeToggle } from './components/ThemeToggle';
import type { ResearchDepth, ProgressEvent, ResearchResultData } from './types/research';
import { getApiUrl, API_BASE_URL, isLocalEnvironment } from './config/api';

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

    // Category A: Check if API_BASE_URL is missing in a remote deployment (e.g. Vercel)
    if (!API_BASE_URL && !isLocalEnvironment) {
      const errMessage =
        'Backend API URL is not configured (VITE_API_BASE_URL is missing). In your Vercel Project Settings > Environment Variables, add VITE_API_BASE_URL pointing to your Render backend service, then trigger a redeployment.';
      console.error('[API Config Error]', {
        apiBaseUrl: API_BASE_URL || '(empty)',
        hostname: window.location.hostname,
        cause: 'VITE_API_BASE_URL was not injected during Vite build',
      });
      setError(errMessage);
      return;
    }

    const researchEndpoint = getApiUrl('/api/research');
    console.info('[Research Pipeline Launch]', {
      endpoint: researchEndpoint,
      apiBaseUrl: API_BASE_URL || '(same-origin / dev proxy)',
      depth: selectedDepth,
    });

    try {
      let response: Response;
      try {
        response = await fetch(researchEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic: selectedTopic, depth: selectedDepth }),
        });
      } catch (fetchErr: any) {
        console.error('[Fetch Network Error]', {
          endpoint: researchEndpoint,
          apiBaseUrl: API_BASE_URL || '(same-origin)',
          errorName: fetchErr.name,
          errorMessage: fetchErr.message,
        });

        if (isLocalEnvironment) {
          throw new Error('Failed to connect to local backend server. Please verify that the FastAPI backend is running (python server.py on port 8000).');
        }

        // Diagnostic probe: Differentiate Category B (Backend unreachable) vs Category C (CORS failure)
        let isCorsFailure = false;
        try {
          const probeUrl = getApiUrl('/health');
          // 'no-cors' mode succeeds if the server is alive and reachable over HTTP even if CORS headers were blocked
          await fetch(probeUrl, { method: 'GET', mode: 'no-cors', signal: AbortSignal.timeout(3500) });
          isCorsFailure = true;
        } catch {
          isCorsFailure = false;
        }

        if (isCorsFailure) {
          // Category C: CORS failure
          throw new Error(
            `CORS connection error: The Render backend at ${API_BASE_URL} is online, but did not permit requests from origin "${window.location.origin}". Ensure CORS_ALLOW_ORIGINS on Render includes "${window.location.origin}".`
          );
        } else {
          // Category B: Backend unreachable
          throw new Error(
            `Backend unreachable at ${API_BASE_URL}. The Render service may be sleeping (Render free-tier cold starts take ~45s) or offline. Please wait a moment and try again.`
          );
        }
      }

      // Category D: /api/research returned non-2xx
      if (!response.ok) {
        let errMessage = `Server error (${response.status} ${response.statusText || 'Error'})`;
        try {
          const errData = await response.json();
          if (errData.detail) errMessage = errData.detail;
        } catch {
          // Response body was not JSON
        }

        console.error('[API Response Error]', {
          endpoint: researchEndpoint,
          status: response.status,
          statusText: response.statusText,
          message: errMessage,
        });

        if (response.status === 405) {
          throw new Error('API endpoint returned 405 Method Not Allowed. The request was routed to a static host rather than the Render FastAPI backend.');
        } else if (response.status === 502 || response.status === 503) {
          throw new Error(`Backend service is temporarily unavailable (HTTP ${response.status}). Render may still be booting the container.`);
        } else if (response.status === 504) {
          throw new Error('Backend request timed out (HTTP 504). Please try again.');
        }
        throw new Error(errMessage);
      }

      const initData = await response.json();
      setStartedAt(initData.started_at);

      // Connect to Server-Sent Events (SSE) Stream
      const sseUrl = getApiUrl(initData.stream_url);
      console.info('[Connecting SSE Stream]', { sseUrl });

      let receivedEventCount = 0;
      const eventSource = new EventSource(sseUrl);

      eventSource.addEventListener('progress', (e: MessageEvent) => {
        receivedEventCount++;
        try {
          const eventData: ProgressEvent = JSON.parse(e.data);
          setEvents((prev) => {
            // Deduplicate consecutive identical messages
            if (prev.length > 0 && prev[prev.length - 1].friendly_message === eventData.friendly_message) {
              const copy = [...prev];
              copy[copy.length - 1] = eventData;
              return copy;
            }
            return [...prev, eventData];
          });
        } catch (err) {
          console.error('[SSE Progress Parse Error]', err);
        }
      });

      eventSource.addEventListener('complete', (e: MessageEvent) => {
        receivedEventCount++;
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
          console.error('[SSE Complete Parse Error]', err);
        }
      });

      // Handle stream errors (Category E: transport disconnect vs Category F: backend application error)
      eventSource.addEventListener('error', (e: any) => {
        // Category F: Check if backend delivered an explicit application error payload
        if (e.data) {
          try {
            const errPayload = JSON.parse(e.data);
            const appError = errPayload.friendly_message || errPayload.error || 'Research interrupted by backend.';
            console.error('[Backend Application Error]', { sseUrl, error: appError });
            setError(appError);
            eventSource.close();
            return;
          } catch {
            // Not a JSON payload
          }
        }

        // Category E: SSE connection or transport failure
        console.error('[SSE Connection Error]', {
          sseUrl,
          readyState: eventSource.readyState,
          receivedEvents: receivedEventCount,
          eventType: e.type,
        });

        if (!isComplete) {
          if (receivedEventCount === 0) {
            setError('Real-time SSE research stream failed to connect. Check backend stream availability and CORS.');
          } else {
            setError('Live research stream disconnected during execution.');
          }
        }
        eventSource.close();
      });
    } catch (err: any) {
      console.error('[Pipeline Launch Exception]', err);
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
    <div className="min-h-screen min-h-dvh flex flex-col justify-between bg-research-bg text-research-primary font-sans overflow-x-hidden">
      {/* Top Compact Navigation Bar */}
      <header className="sticky top-0 z-40 w-full bg-research-bg/90 backdrop-blur-md border-b border-research-border">
        <div className="max-w-instrument mx-auto px-3 sm:px-6 h-14 flex items-center justify-between">
          <div
            onClick={handleNewInvestigation}
            className="flex items-center gap-1.5 sm:gap-2 cursor-pointer select-none group min-h-[44px]"
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && handleNewInvestigation()}
            aria-label="Agentic Research Home"
          >
            <span className="font-sans text-xs xs:text-sm sm:text-base font-bold tracking-tight text-research-ink group-hover:text-research-blue transition-colors whitespace-nowrap">
              ✦ AGENTIC RESEARCH
            </span>
            <span className="font-mono text-[9px] sm:text-[10px] uppercase font-bold text-research-blue bg-research-blue/10 px-1 sm:px-1.5 py-0.5 rounded whitespace-nowrap">
              v2.0 PRO
            </span>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle />
            <div
              className="flex items-center gap-1.5 px-2 sm:px-2.5 py-1 rounded-full bg-research-paper border border-research-borderLight text-xs font-mono"
              title="Autonomous Research Engine Ready"
            >
              <span className="w-2 h-2 rounded-full bg-research-green shrink-0 animate-pulse" />
              <span className="hidden sm:inline text-[11px] text-research-secondary font-medium">READY</span>
            </div>
            <div
              className="w-7 h-7 rounded-full bg-research-primary text-white dark:bg-research-paper dark:text-research-primary dark:border dark:border-research-border font-mono text-xs font-bold flex items-center justify-center shadow-sm shrink-0"
              aria-label="Examiner session: Utkarsh Pandey"
            >
              U
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-instrument w-full mx-auto px-3 sm:px-6 py-6 sm:py-12 min-w-0">
        {screen === 'home' && (
          <div className="space-y-8 sm:space-y-12 min-w-0">
            {/* Hero Typography */}
            <div className="text-center max-w-2xl mx-auto space-y-3 min-w-0 px-1">
              <div className="font-mono text-[10px] sm:text-[11px] font-bold tracking-[0.2em] text-research-muted uppercase">
                Autonomous Research Instrument
              </div>
              <h1 className="text-3xl sm:text-5xl md:text-6xl font-sans font-bold tracking-tight text-research-ink leading-[1.12] sm:leading-[1.08] break-words">
                Research beyond{' '}
                <span className="font-serif italic font-normal text-research-blue text-[1.12em] tracking-normal">
                  the obvious.
                </span>
              </h1>
              <p className="font-body text-xs sm:text-base text-research-secondary leading-relaxed pt-1 max-w-xl mx-auto break-words">
                Semi-autonomous evidence retrieval, multi-angle dialectic debate, and continuous publication-grade dossiers.
              </p>
            </div>

            {/* Atmospheric Research Network Graphic */}
            <div className="max-w-3xl mx-auto w-full min-w-0">
              <AgenticHeroGraph isResearching={false} />
            </div>

            {/* Research Command Surface (Composer) */}
            <div className="w-full min-w-0">
              <ResearchComposer
                onStartResearch={handleStartResearch}
                onOpenWhyDifferent={() => setIsWhyDifferentOpen(true)}
              />
            </div>
          </div>
        )}

        {screen === 'live' && (
          <div className="py-2 sm:py-4 min-w-0 w-full">
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
                  className="w-full sm:w-auto px-6 py-3 rounded-xl bg-research-blue text-white font-sans text-xs font-bold hover:bg-research-deepBlue transition-colors shadow-md animate-bounce min-h-[44px]"
                >
                  View Final Research Dossier →
                </button>
              </div>
            )}

            {/* If error occurred, offer return to composer */}
            {error && (
              <div className="text-center mt-6">
                <button
                  onClick={handleNewInvestigation}
                  className="w-full sm:w-auto px-6 py-3 rounded-xl bg-research-paper border border-research-border hover:bg-research-surface text-research-primary font-sans text-xs font-bold transition-colors shadow-subtle min-h-[44px]"
                >
                  ← Return to Investigation Composer
                </button>
              </div>
            )}
          </div>
        )}

        {screen === 'dossier' && result && (
          <div className="min-w-0 w-full">
            <ContinuousDossierView
              result={result}
              onNewInvestigation={handleNewInvestigation}
            />
          </div>
        )}
      </main>

      {/* Permanent Examiner Attribution Footer on Every Screen */}
      <footer className="w-full border-t border-research-border bg-research-bg py-5 safe-pb">
        <div className="max-w-instrument mx-auto px-3 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2.5 text-center sm:text-left text-xs min-w-0">
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
