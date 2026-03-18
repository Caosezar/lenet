import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook para gerenciar WebSocket connection com servidor FastAPI.
 * Lida com envio de frames em 30 FPS e recebimento de dados em tempo real.
 */
export function useWebSocket(serverUrl = 'ws://localhost:8000/ws/process-video') {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastData, setLastData] = useState(null);
  const [latencyHistory, setLatencyHistory] = useState([]);
  const [error, setError] = useState(null);
  
  const wsRef = useRef(null);
  const frameQueueRef = useRef([]);
  const isSendingRef = useRef(false);

  // Conectar ao WebSocket
  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(serverUrl);
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          setConnectionStatus('connected');
          setError(null);
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setLastData(data);
            
            // Atualizar histórico de latência
            if (data.latency_ms) {
              setLatencyHistory(prev => {
                const updated = [...prev, {
                  timestamp: Date.now(),
                  latency: data.latency_ms
                }];
                // Manter apenas últimos 900 frames (30s em 30 FPS)
                return updated.slice(-900);
              });
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };
        
        ws.onerror = (event) => {
          console.error('WebSocket error:', event);
          setConnectionStatus('error');
          setError('WebSocket connection error');
        };
        
        ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          setConnectionStatus('disconnected');
          // Tentar reconectar após 3 segundos
          setTimeout(connect, 3000);
        };
        
        wsRef.current = ws;
      } catch (err) {
        console.error('Failed to connect WebSocket:', err);
        setConnectionStatus('error');
        setError(err.message);
      }
    };
    
    connect();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [serverUrl]);

  // Função para enviar frame ao servidor
  const sendFrame = useCallback((frameBase64, action = 'predict', label = null, userId = 'Usuario Principal') => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, queueing frame');
      frameQueueRef.current.push({ frameBase64, action, label, userId });
      return;
    }

    const message = {
      action,
      frame_base64: frameBase64.substring(0, 50) + '...',  // Log apenas o início para not flood console
      user_id: userId,
      ...(label && { label })
    };
    
    const fullMessage = {
      action,
      frame_base64: frameBase64,
      user_id: userId,
      ...(label && { label })
    };

    try {
      wsRef.current.send(JSON.stringify(fullMessage));
      if (frameBase64 && frameBase64.length > 1000) {  // Apenas se frame válido
        console.debug(`[Frontend] Frame sent (${action}, size: ${frameBase64.length})`);
      }
    } catch (err) {
      console.error('Error sending frame:', err);
      frameQueueRef.current.push({ frameBase64, action, label, userId });
    }
  }, []);

  // Enviar frames enfileirados quando reconectar
  useEffect(() => {
    if (connectionStatus === 'connected' && frameQueueRef.current.length > 0) {
      while (frameQueueRef.current.length > 0) {
        const frame = frameQueueRef.current.shift();
        sendFrame(frame.frameBase64, frame.action, frame.label, frame.userId);
      }
    }
  }, [connectionStatus, sendFrame]);

  return {
    connectionStatus,
    lastData,
    latencyHistory,
    error,
    sendFrame
  };
}
