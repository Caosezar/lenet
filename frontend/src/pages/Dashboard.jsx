import React, { useState, useRef } from 'react';
import { CameraStream } from '../components/CameraStream';
import { DataBlock } from '../components/DataBlock';
import { LatencyGraph } from '../components/LatencyGraph';
import { ExpressionRegister } from '../components/ExpressionRegister';
import { useWebSocket } from '../hooks/useWebSocket';

/**
 * Dashboard principal da aplicação.
 * Layout: câmera à esquerda (grande), dados + gráfico + input à direita (coluna).
 */
export function Dashboard() {
  const { connectionStatus, lastData, latencyHistory, sendFrame } = useWebSocket();
  const [isRegistering, setIsRegistering] = useState(false);
  const currentFrameRef = useRef(null);

  const isConnected = connectionStatus === 'connected';

  // Callback quando frame é capturado
  const handleFrameCapture = (frameBase64) => {
    currentFrameRef.current = frameBase64;
    sendFrame(frameBase64, 'predict');
  };

  // Callback para registrar expressão
  const handleRegisterExpression = async (label) => {
    if (!currentFrameRef.current) {
      throw new Error('Nenhum frame disponível. Por favor, espere um momento e tente novamente.');
    }

    setIsRegistering(true);
    try {
      sendFrame(currentFrameRef.current, 'register', label);
      // Aguardar feedback do servidor
      await new Promise(resolve => setTimeout(resolve, 500));
      setIsRegistering(false);
    } catch (err) {
      setIsRegistering(false);
      throw err;
    }
  };

  return (
    <div className="min-h-screen bg-[#121212] text-[#E0E0E0]">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-[#1a1a1a] border-b border-[#444444] z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold font-jetbrains text-[#E0E0E0]">Expression Recognition</h1>
          <div className="text-sm font-jetbrains">
            <span className="text-[#B0B0B0]">Status: </span>
            <span className={isConnected ? 'text-green-400' : 'text-red-500'}>
              {isConnected ? 'ACTIVE' : 'OFFLINE'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-20 max-w-7xl mx-auto px-4 py-6">
        {/* Camera and Data Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Camera - Full width on top, spans 2 cols on large screens */}
          <div className="lg:col-span-2">
            <CameraStream 
              onFrameCapture={handleFrameCapture} 
              isConnected={isConnected}
              detectionData={lastData}
            />
          </div>

          {/* Data Block - Right column */}
          <div className="flex flex-col gap-6">
            <DataBlock data={lastData} />
            <LatencyGraph data={latencyHistory} />
          </div>
        </div>

        {/* Expression Register - Below Camera */}
        <div className="max-w-2xl">
          <ExpressionRegister
            onSubmit={handleRegisterExpression}
            isLoading={isRegistering}
          />
        </div>
      </main>
    </div>
  );
}
