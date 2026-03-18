import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

/**
 * Bloco de dados em estilo "terminal" monocromático.
 * Exibe resumo com opção de expandir para ver detalhes (52 blendshapes).
 */
export function DataBlock({ data = null, isExpanded = false, onToggleExpand = null }) {
  const [expanded, setExpanded] = useState(isExpanded);

  const handleToggle = () => {
    setExpanded(!expanded);
    if (onToggleExpand) {
      onToggleExpand(!expanded);
    }
  };

  const user_id = data?.user_id || 'Usuario Principal';
  const expression = data?.expression || 'Waiting for detection...';
  const confidence = data?.confidence || 0;
  const latency = data?.latency_ms || 0;
  const timestamp = data?.timestamp_ms || Date.now();
  const blendshapesCount = data?.blendshapes_count || 0;
  const topBlendshapes = data?.top_blendshapes || [];

  const dateStr = new Date(timestamp).toLocaleTimeString('pt-BR');

  return (
    <div className="flex flex-col gap-3 font-jetbrains bg-[#0a0a0a] rounded-lg border border-[#444444] overflow-hidden shadow-xl">
      {/* Header */}
      <div className="bg-[#1a1a1a] px-4 py-3 border-b border-[#444444] flex items-center justify-between">
        <h3 className="text-[#E0E0E0] font-bold text-sm">AI Expression Data</h3>
        <button
          onClick={handleToggle}
          className="text-[#B0B0B0] hover:text-[#E0E0E0] transition-colors"
          title="Expand/Collapse"
        >
          <ChevronDown
            size={18}
            className={`transform transition-transform ${expanded ? 'rotate-180' : ''}`}
          />
        </button>
      </div>

      {/* Summary */}
      <div className="px-4 py-3 space-y-2">
        <div className="text-[#E0E0E0] text-xs leading-relaxed">
          <div className="flex justify-between items-baseline">
            <span className="text-[#888888]">user</span>
            <span className="ml-2">{user_id}</span>
          </div>
          <div className="flex justify-between items-baseline">
            <span className="text-[#888888]">expression</span>
            <span className="ml-2">{expression}</span>
          </div>
          <div className="flex justify-between items-baseline">
            <span className="text-[#888888]">confidence</span>
            <span className="ml-2">{confidence.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between items-baseline">
            <span className="text-[#888888]">latency</span>
            <span className="ml-2">{latency.toFixed(2)}ms</span>
          </div>
          <div className="flex justify-between items-baseline">
            <span className="text-[#888888]">timestamp</span>
            <span className="ml-2 text-xs">{dateStr}</span>
          </div>
        </div>

        {/* Confidence bar */}
        <div className="mt-3 pt-3 border-t border-[#444444]">
          <div className="text-[#888888] text-xs mb-1">confidence_level</div>
          <div className="w-full bg-[#1a1a1a] rounded h-2 overflow-hidden">
            <div
              className="h-full bg-[#888888] transition-all duration-300"
              style={{ width: `${Math.min(confidence, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-[#444444] px-4 py-3 bg-[#161616] max-h-64 overflow-y-auto">
          <div className="text-[#E0E0E0] text-xs space-y-2">
            <div className="text-[#B0B0B0] font-bold mb-2">top_blendshapes:</div>
            
            {topBlendshapes && topBlendshapes.length > 0 ? (
              topBlendshapes.map((bs, idx) => (
                <div key={idx} className="flex justify-between items-baseline pl-2 py-1 border-l border-[#444444]">
                  <span className="text-[#B0B0B0]">{bs.name || bs.category_name}</span>
                  <span className="ml-2">{(bs.score * 100).toFixed(1)}%</span>
                </div>
              ))
            ) : (
              <div className="text-[#888888] italic">No active features</div>
            )}

            <div className="pt-2 mt-3 border-t border-[#444444]">
              <div className="text-[#B0B0B0] font-bold">metadata:</div>
              <div className="flex justify-between items-baseline pl-2 py-1">
                <span className="text-[#B0B0B0]">count</span>
                <span className="ml-2">{blendshapesCount}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
