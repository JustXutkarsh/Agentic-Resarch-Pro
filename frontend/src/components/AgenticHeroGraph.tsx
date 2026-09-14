import React, { useMemo } from 'react';
import {
  ReactFlow,
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
  data: { label: string; tag: string; active?: boolean; pulse?: boolean };
}) => {
  const isInsight = data.tag === 'INSIGHT';
  const isQuestion = data.tag === 'QUESTION';

  return (
    <div
      className={`px-3 py-1.5 rounded-md border text-center transition-all duration-500 select-none ${
        data.active
          ? 'bg-research-blue/10 border-research-blue text-research-blue shadow-[0_0_16px_rgba(49,91,255,0.25)]'
          : isInsight
          ? 'bg-white/90 border-research-green text-research-green font-semibold shadow-sm'
          : isQuestion
          ? 'bg-white/95 border-research-primary text-research-primary font-semibold shadow-subtle'
          : 'bg-white/80 border-research-border text-research-secondary shadow-subtle hover:border-research-blue/60'
      }`}
      style={{ minWidth: 90 }}
    >
      <Handle type="target" position={Position.Top} className="!opacity-0" />
      <div className="flex items-center justify-center gap-1.5">
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            data.active
              ? 'bg-research-blue animate-ping'
              : isInsight
              ? 'bg-research-green'
              : 'bg-research-border'
          }`}
        />
        <span className="font-mono text-[10px] tracking-wider uppercase opacity-80">
          {data.tag}
        </span>
      </div>
      <div className="font-sans text-xs font-medium mt-0.5 text-research-ink">
        {data.label}
      </div>
      <Handle type="source" position={Position.Bottom} className="!opacity-0" />
    </div>
  );
};

const nodeTypes = {
  network: NetworkNode,
};

export const AgenticHeroGraph: React.FC<AgenticHeroGraphProps> = ({ isResearching = false }) => {
  const nodes: Node[] = useMemo(
    () => [
      {
        id: 'q',
        type: 'network',
        position: { x: 260, y: 15 },
        data: { label: 'Query Formulation', tag: 'QUESTION', active: isResearching },
      },
      {
        id: 'a1',
        type: 'network',
        position: { x: 60, y: 95 },
        data: { label: 'Economic Impact', tag: 'ANGLE 1', active: isResearching },
      },
      {
        id: 'a2',
        type: 'network',
        position: { x: 260, y: 95 },
        data: { label: 'Technical Depth', tag: 'ANGLE 2', active: isResearching },
      },
      {
        id: 'a3',
        type: 'network',
        position: { x: 460, y: 95 },
        data: { label: 'Historical Precedent', tag: 'ANGLE 3', active: isResearching },
      },
      {
        id: 'ev',
        type: 'network',
        position: { x: 150, y: 180 },
        data: { label: 'ChromaDB Vectors', tag: 'EVIDENCE', active: isResearching },
      },
      {
        id: 'src',
        type: 'network',
        position: { x: 370, y: 180 },
        data: { label: 'Tavily Sources', tag: 'SOURCES', active: isResearching },
      },
      {
        id: 'ver',
        type: 'network',
        position: { x: 260, y: 260 },
        data: { label: 'Claim Verification', tag: 'VERIFY', active: isResearching },
      },
      {
        id: 'ins',
        type: 'network',
        position: { x: 260, y: 340 },
        data: { label: 'Synthesized Dossier', tag: 'INSIGHT', active: isResearching },
      },
    ],
    [isResearching]
  );

  const edges: Edge[] = useMemo(
    () => [
      { id: 'e-q-a1', source: 'q', target: 'a1', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-q-a2', source: 'q', target: 'a2', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-q-a3', source: 'q', target: 'a3', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-a1-ev', source: 'a1', target: 'ev', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.2 } },
      { id: 'e-a2-ev', source: 'a2', target: 'ev', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.2 } },
      { id: 'e-a2-src', source: 'a2', target: 'src', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.2 } },
      { id: 'e-a3-src', source: 'a3', target: 'src', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 1.2 } },
      { id: 'e-ev-ver', source: 'ev', target: 'ver', animated: true, style: { stroke: isResearching ? '#168463' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-src-ver', source: 'src', target: 'ver', animated: true, style: { stroke: isResearching ? '#168463' : '#D1CFCA', strokeWidth: 1.5 } },
      { id: 'e-ver-ins', source: 'ver', target: 'ins', animated: true, style: { stroke: isResearching ? '#315BFF' : '#D1CFCA', strokeWidth: 2 } },
    ],
    [isResearching]
  );

  return (
    <div className="relative w-full h-[400px] rounded-2xl border border-research-border/80 bg-gradient-to-b from-white/40 via-[#F6F5F1]/80 to-[#F6F5F1] overflow-hidden shadow-subtle">
      {/* Subtle top indicator */}
      <div className="absolute top-3 left-4 z-10 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-research-blue animate-pulse-glow" />
        <span className="font-mono text-[11px] uppercase tracking-wider text-research-secondary font-medium">
          Autonomous Investigation Topology
        </span>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.15 }}
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
      <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-[#F6F5F1] to-transparent pointer-events-none" />
    </div>
  );
};
