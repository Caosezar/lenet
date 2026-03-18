import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

/**
 * Gráfico de latência em tempo real.
 * Exibe histórico dos últimos 30 segundos de tempo de processamento.
 */
export function LatencyGraph({ data = [] }) {
  // Preparar dados para o gráfico
  const chartData = data.map((point, idx) => ({
    index: idx,
    latency: point.latency,
    timestamp: new Date(point.timestamp).toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    })
  }));

  const avgLatency = data.length > 0
    ? (data.reduce((sum, point) => sum + point.latency, 0) / data.length).toFixed(2)
    : 0;

  const maxLatency = data.length > 0
    ? Math.max(...data.map(p => p.latency)).toFixed(2)
    : 0;

  return (
    <div className="flex flex-col gap-3 bg-[#1a1a1a] rounded-lg border border-[#444444] p-4 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-[#E0E0E0] font-bold text-sm font-jetbrains">Processing Latency (ms)</h3>
        <div className="flex gap-4 text-xs font-jetbrains text-[#B0B0B0]">
          <div>
            <span className="text-[#888888]">avg: </span><span>{avgLatency}ms</span>
          </div>
          <div>
            <span className="text-[#888888]">max: </span><span>{maxLatency}ms</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#888888" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#888888" stopOpacity={0} />
              </linearGradient>
            </defs>
            
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(68, 68, 68, 0.2)"
              vertical={false}
            />
            
            <XAxis
              dataKey="index"
              stroke="rgba(136, 136, 136, 0.3)"
              tick={{ fill: 'rgba(136, 136, 136, 0.6)', fontSize: 10 }}
              interval={Math.max(0, Math.floor(chartData.length / 5))}
            />
            
            <YAxis
              stroke="rgba(136, 136, 136, 0.3)"
              tick={{ fill: 'rgba(136, 136, 136, 0.6)', fontSize: 10 }}
              domain={['dataMin - 5', 'dataMax + 5']}
            />
            
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(26, 26, 26, 0.95)',
                border: '1px solid rgba(68, 68, 68, 0.7)',
                borderRadius: '4px',
                fontFamily: "'JetBrains Mono', monospace",
                color: '#E0E0E0'
              }}
              labelStyle={{ color: '#E0E0E0' }}
              formatter={(value) => [`${value.toFixed(2)}ms`, 'Latency']}
              cursor={{ stroke: 'rgba(136, 136, 136, 0.5)' }}
            />
            
            <Area
              type="monotone"
              dataKey="latency"
              stroke="#888888"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorLatency)"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-[200px] flex items-center justify-center text-[#888888] text-sm font-jetbrains">
          Waiting for latency data...
        </div>
      )}

      {/* Legend */}
      <div className="text-xs font-jetbrains text-[#888888] mt-2 pt-2 border-t border-[#444444]">
        Processing time trend (last 30 seconds)
      </div>
    </div>
  );
}
