import React, { useEffect, useRef, useState } from 'react';
import { getCameraStream, stopCameraStream, drawVideoToCanvas, canvasToBase64 } from '../utils/canvasUtils';
import { FaceOverlay } from './FaceOverlay';

/**
 * Componente de stream de câmera em tempo real.
 * Captura frames e emite para o WebSocket em 30 FPS.
 * Sobrepõe landmarks e bounding box do MediaPipe.
 */
export function CameraStream({ onFrameCapture, isConnected, detectionData }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  const [error, setError] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [videoDimensions, setVideoDimensions] = useState({ width: 640, height: 480 });
  
  const frameRateRef = useRef(0);
  const lastTimeRef = useRef(Date.now());
  const frameCountRef = useRef(0);

  // Inicializar stream de câmera
  useEffect(() => {
    const initCamera = async () => {
      try {
        const stream = await getCameraStream({
          video: { 
            width: { ideal: 640 },
            height: { ideal: 480 }
          },
          audio: false
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
          
          // Capturar dimensões reais do vídeo
          videoRef.current.onloadedmetadata = () => {
            const width = videoRef.current.videoWidth;
            const height = videoRef.current.videoHeight;
            setVideoDimensions({ width, height });
            
            // Também atualizar o canvas
            if (canvasRef.current) {
              canvasRef.current.width = width;
              canvasRef.current.height = height;
            }
          };
          
          setIsStreaming(true);
          setError(null);
        }
      } catch (err) {
        setError(`Camera access error: ${err.message}`);
        setIsStreaming(false);
      }
    };

    initCamera();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        stopCameraStream(videoRef.current.srcObject);
      }
    };
  }, []);

  // Capturar frames em 30 FPS
  useEffect(() => {
    if (!isStreaming || !isConnected || !videoRef.current || !canvasRef.current) {
      return;
    }

    const frameInterval = 1000 / 30; // 30 FPS
    let lastFrameTime = Date.now();

    const captureFrame = () => {
      const now = Date.now();
      
      if (now - lastFrameTime >= frameInterval) {
        try {
          // Desenhar video no canvas
          const success = drawVideoToCanvas(videoRef.current, canvasRef.current);
          
          if (success) {
            // Converter canvas para Base64
            const base64Frame = canvasToBase64(canvasRef.current, 0.7);
            
            if (base64Frame && onFrameCapture) {
              onFrameCapture(base64Frame);
            }
          }
          
          lastFrameTime = now;
          
          // Atualizar FPS counter
          frameCountRef.current++;
          if (now - lastTimeRef.current >= 1000) {
            frameRateRef.current = frameCountRef.current;
            frameCountRef.current = 0;
            lastTimeRef.current = now;
          }
        } catch (err) {
          console.error('Erro ao capturar frame:', err);
        }
      }

      animationFrameRef.current = requestAnimationFrame(captureFrame);
    };

    animationFrameRef.current = requestAnimationFrame(captureFrame);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isStreaming, isConnected, onFrameCapture]);

  return (
    <div className="flex flex-col gap-4">
      {/* Video feed */}
      <div className="relative bg-[#0a0a0a] rounded-lg overflow-hidden shadow-2xl aspect-video border border-[#444444]">
        <video
          ref={videoRef}
          className="w-full h-full object-contain scale-x-[-1]"
          playsInline
        />
        
        {/* Face Landmarks Overlay */}
        <FaceOverlay 
          canvasRef={canvasRef}
          data={detectionData}
          videoWidth={videoDimensions.width}
          videoHeight={videoDimensions.height}
        />
        
        {/* Status indicator */}
        <div className="absolute top-3 right-3 flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-500'}`} />
          <span className="text-xs font-jetbrains text-[#B0B0B0]">
            {isConnected ? 'ACTIVE' : 'OFFLINE'}
          </span>
        </div>

        {/* FPS counter */}
        <div className="absolute bottom-3 left-3 text-sm font-jetbrains text-[#888888] opacity-70">
          {frameRateRef.current} fps
        </div>
      </div>

      {/* Hidden canvas for frame processing */}
      <canvas
        ref={canvasRef}
        className="hidden"
      />

      {/* Error display */}
      {error && (
        <div className="p-3 bg-red-900 bg-opacity-30 border border-red-700 rounded text-red-300 text-sm font-jetbrains">
          {error}
        </div>
      )}

      {/* Status message */}
      {!isStreaming && (
        <div className="p-3 bg-yellow-900 bg-opacity-30 border border-yellow-700 rounded text-yellow-300 text-sm font-jetbrains">
          Waiting for camera...
        </div>
      )}
    </div>
  );
}
