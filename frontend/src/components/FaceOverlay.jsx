import React, { useEffect, useRef } from 'react';

/**
 * Componente que desenha os landmarks e bounding box do MediaPipe
 * sobreposto à câmera em tempo real.
 */
export function FaceOverlay({ canvasRef, data, videoWidth, videoHeight }) {
  const overlayCanvasRef = useRef(null);

  useEffect(() => {
    if (!overlayCanvasRef.current || !data || !data.face_detected) {
      return;
    }

    const ctx = overlayCanvasRef.current.getContext('2d');
    
    // Limpar canvas
    ctx.clearRect(0, 0, videoWidth, videoHeight);

    // Desenhar bounding box
    if (data.bounding_box) {
      const bbox = data.bounding_box;
      
      // Cor: pastel amarelo como mencionado
      ctx.strokeStyle = 'rgba(255, 223, 128, 0.8)';  // Amarelo pastel
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.rect(bbox.xmin, bbox.ymin, bbox.xmax - bbox.xmin, bbox.ymax - bbox.ymin);
      ctx.stroke();
      
      // Texto com a expressão acima do bounding box
      if (data.expression) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(bbox.xmin - 2, bbox.ymin - 28, 250, 25);
        
        ctx.fillStyle = 'rgba(255, 223, 128, 1)';
        ctx.font = "12px 'JetBrains Mono', monospace";
        ctx.fillText(data.expression, bbox.xmin + 3, bbox.ymin - 10);
      }
    }

    // Desenhar landmarks
    if (data.landmarks && data.landmarks.length > 0) {
      // Cor: branca-esverdeada suave (como no webcam_mediapipe)
      ctx.fillStyle = 'rgba(200, 230, 200, 0.9)';
      
      data.landmarks.forEach((landmark) => {
        ctx.beginPath();
        ctx.arc(landmark.x, landmark.y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      });
    }
  }, [data, videoWidth, videoHeight]);

  return (
    <canvas
      ref={overlayCanvasRef}
      width={videoWidth}
      height={videoHeight}
      className="absolute top-0 left-1/2 -translate-x-1/2 h-full object-contain pointer-events-none"
      style={{ zIndex: 10 }}
    />
  );
}
