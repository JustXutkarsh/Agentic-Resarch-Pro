import React, { useMemo, useState, useEffect, useRef } from 'react';
import {
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  type Node,
  type Edge,
  Position,
  Handle,
  Background,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface AgenticHeroGraphProps {
  isResearching?: boolean;
}

// Custom Node for the Atmospheric Research Graph
const NetworkNode = ({
  data,
}: {
  data: { label: string; tag: string; active?: boolean; pulse?: boolean; compact?: boolean };
}) => {
  const isInsight = data.tag === 'INSIGHT';
  const isQuestion = data.tag === 'QUESTION';
  const isPlaywright = data.tag === 'PLAYWRIGHT';

  return (
    <div
      className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-md border text-center transition-all duration-300 select-none ${
        data.active
          ? 'bg-research-blue/10 border-research-blue text-research-blue shadow-[0_0_16px_rgba(49,91,255,0.25)]'
          : isInsight
          ? 'bg-white/90 border-research-green text-research-green font-semibold shadow-sm'
          : isQuestion
          ? 'bg-white/95 border-research-primary text-research-primary font-semibold shadow-subtle'
          : isPlaywright
          ? 'bg-white/95 border-research-blue/70 text-research-blue font-semibold shadow-subtle hover:border-research-blue'
          : 'bg-white/80 border-research-border text-research-secondary shadow-subtle hover:border-research-blue/60'
      }`}
      style={{
        minWidth: data.compact ? 76 : 92,
        maxWidth: data.compact ? 98 : 140,
      }}
    >
      <Handle type="target" position={Position.Top} className="!opacity-0" />
      <div className="flex items-center justify-center gap-1 sm:gap-1.5">
        <span
          className={`w-1.5 h-1.5 rounded-full shrink-0 ${
            data.active
              ? 'bg-research-blue animate-ping'
              : isInsight
              ? 'bg-research-green'
              : isPlaywright
              ? 'bg-research-blue'
              : 'bg-research-border'
          }`}
        />
        <span className="font-mono text-[9px] sm:text-[10px] tracking-wider uppercase opacity-80 truncate">
          {data.tag}
        </span>
      </div>
      <div className="font-sans text-[11px] sm:text-xs font-medium mt-0.5 text-research-ink leading-tight line-clamp-2">
        {data.label}
      </div>
      <Handle type="source" position={Position.Bottom} className="!opacity-0" />
    </div>
  );
};

const nodeTypes = {
  network: NetworkNode,
};

const AgenticHeroGraphContent: React.FC<AgenticHeroGraphProps> = ({ isResearching = false }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isCompact, setIsCompact] = useState(false);
  const { fitView } = useReactFlow();

  // Responsive container width detection
  useEffect(() => {
    if (!containerRef.current) return;

    const checkWidth = (width: number) => {
      setIsCompact(width < 560);
    };

    // Initial check
    checkWidth(containerRef.current.clientWidth);

    let rafId: number;
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(() => {
          checkWidth(entry.contentRect.width);
        });
      }
    });

    resizeObserver.observe(containerRef.current);

    return () => {
      cancelAnimationFrame(rafId);
      resizeObserver.disconnect();
    };
  }, []);

  // Smooth auto-fit on compact/desktop switch and window resize/orientation
  useEffect(() => {
    const timer = setTimeout(() => {
      fitView({
        padding: isCompact ? 0.08 : 0.15,
        duration: 250,
      });
    }, 60);

    return () => clearTimeout(timer);
  }, [isCompact, fitView]);

  useEffect(() => {
    let rafId: number;
    const handleWindowResize = () => {
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        fitView({
          padding: isCompact ? 0.08 : 0.15,
          duration: 200,
        });
      });
    };

    window.addEventListener('resize', handleWindowResize);
    window.addEventListener('orientationchange', handleWindowResize);

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', handleWindowResize);
      window.removeEventListener('orientationchange', handleWindowResize);
    };
  }, [isCompact, fitView]);

  // Topology node positioning: Compact coordinates for mobile (< 560px), expanded 3-column for desktop
  const nodes: Node[] = useMemo(() => {
    if (isCompact) {
      return [
        {
          id: 'q',
          type: 'network',
          position: { x: 130, y: 12 },
          data: { label: 'Query Formulation', tag: 'QUESTION', active: isResearching, compact: true },
        },
        {
          id: 'a1',
          type: 'network',
          position: { x: 15, y: 82 },
          data: { label: 'Economic Impact', tag: 'ANGLE 1', active: isResearching, compact: true },
        },
        {
          id: 'a2',
          type: 'network',
          position: { x: 130, y: 82 },
          data: { label: 'Technical Depth', tag: 'ANGLE 2', active: isResearching, compact: true },
        },
        {
          id: 'a3',
          type: 'network',
          position: { x: 245, y: 82 },
          data: { label: 'Historical Context', tag: 'ANGLE 3', active: isResearching, compact: true },
        },
        {
          id: 'src',
          type: 'network',
          position: { x: 15, y: 160 },
          data: { label: 'Tavily Sources', tag: 'SOURCES', active: isResearching, compact: true },
        },
        {
          id: 'pw',
          type: 'network',
          position: { x: 130, y: 160 },
          data: { label: 'Playwright Agent', tag: 'PLAYWRIGHT', active: isResearching, compact: true },
        },
        {
          id: 'ev',
          type: 'network',
          position: { x: 245, y: 160 },
          data: { label: 'ChromaDB Vectors', tag: 'EVIDENCE', active: isResearching, compact: true },
        },
        {
          id: 'ver',
          type: 'network',
          position: { x: 130, y: 238 },
          data: { label: 'Claim Verification', tag: 'VERIFY', active: isResearching, compact: true },
        },
        {
          id: 'ins',
          type: 'network',
          position: { x: 130, y: 310 },
          data: { label: 'Synthesized Dossier', tag: 'INSIGHT', active: isResearching, compact: true },
        },
      ];
    }

    // Standard Desktop / Tablet coordinates
    return [
      {
        id: 'q',
        type: 'network',
        position: { x: 260, y: 15 },
        data: { label: 'Query Formulation', tag: 'QUESTION', active: isResearching, compact: false },
      },
      {
        id: 'a1',
        type: 'network',
        position: { x: 60, y: 95 },
        data: { label: 'Economic Impact', tag: 'ANGLE 1', active: isResearching, compact: false },
      },
      {
        id: 'a2',
        type: 'network',
        position: { x: 260, y: 95 },
        data: { label: 'Technical Depth', tag: 'ANGLE 2', active: isResearching, compact: false },
      },
      {
        id: 'a3',
        type: 'network',
        position: { x: 460, y: 95 },
        data: { label: 'Historical Precedent', tag: 'ANGLE 3', active: isResearching, compact: false },
      },
      {
        id: 'src',
        type: 'network',
        position: { x: 60, y: 180 },
        data: { label: 'Tavily Sources', tag: 'SOURCES', active: isResearching, compact: false },
      },
      {
        id: 'pw',
        type: 'network',
        position: { x: 260, y: 180 },
        data: { label: 'Playwright Agent', tag: 'PLAYWRIGHT', active: isResearching, compact: false },
      },
      {
        id: 'ev',
        type: 'network',
        position: { x: 460, y: 180 },
        data: { label: 'ChromaDB Vectors', tag: 'EVIDENCE', active: isResearching, compact: false },
      },
      {
        id: 'ver',
        type: 'network',
        position: { x: 260, y: 265 },
        data: { label: 'Claim Verification', tag: 'VERIFY', active: isResearching, compact: false },
      },
      {
        id: 'ins',
        type: 'network',
        position: { x: 260, y: 345 },
        data: { label: 'Synthesized Dossier', tag: 'INSIGHT', active: isResearching, compact: false },
      },
    ];
  }, [isResearching, isCompact]);

  const edges: Edge[] = useMemo(
    () => [
      { id: 'e-q-a1', source: 'q', target: 'a1', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-q-a2', source: 'q', target: 'a2', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-q-a3', source: 'q', target: 'a3', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-a1-src', source: 'a1', target: 'src', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.2 } },
      { id: 'e-a2-pw', source: 'a2', target: 'pw', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-a3-ev', source: 'a3', target: 'ev', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.2 } },
      { id: 'e-src-pw', source: 'src', target: 'pw', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.3 } },
      { id: 'e-pw-ev', source: 'pw', target: 'ev', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.3 } },
      { id: 'e-src-ver', source: 'src', target: 'ver', animated: true, style: { stroke: isResearching ? '#168463' : '#D1CFCA', strokeWidth: 1.2 } },
      { id: 'e-pw-ver', source: 'pw', target: 'ver', animated: true, style: { stroke: isResearching ? '#168463' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-ev-ver', source: 'ev', target: 'ver', animated: true, style: { stroke: isResearching ? '#168463' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-ver-ins', source: 'ver', target: 'ins', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 2 } },
    ],
    [isResearching]
  );

  return (
    <div
      ref={containerRef}
      className="relative w-full h-[340px] sm:h-[400px] rounded-2xl border border-research-border/80 bg-gradient-to-b from-white/40 via-[#F6F5F1]/80 to-[#F6F5F1] overflow-hidden shadow-subtle min-w-0"
    >
      {/* Subtle top indicator */}
      <div className="absolute top-2.5 sm:top-3 left-3 sm:left-4 z-10 flex items-center gap-1.5 sm:gap-2 pointer-events-none">
        <span className="w-2 h-2 rounded-full bg-research-blue animate-pulse-glow" />
        <span className="font-mono text-[10px] sm:text-[11px] uppercase tracking-wider text-research-secondary font-medium truncate">
          Autonomous Investigation Topology
        </span>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: isCompact ? 0.08 : 0.15 }}
        zoomOnScroll={false}
        zoomOnPinch={false}
        panOnScroll={false}
        panOnDrag={false}
        preventScrolling={false}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#D8D6CF"
        />
      </ReactFlow>

      {/* Atmospheric bottom gradient fade */}
      <div className="absolute inset-x-0 bottom-0 h-10 sm:h-12 bg-gradient-to-t from-[#F6F5F1] to-transparent pointer-events-none" />
    </div>
  );
};

export const AgenticHeroGraph: React.FC<AgenticHeroGraphProps> = (props) => {
  return (
    <ReactFlowProvider>
      <AgenticHeroGraphContent {...props} />
    </ReactFlowProvider>
  );
};
