/**
 * Utilitários para conversão de canvas para Base64 e manipulação de video frames.
 */

/**
 * Converter canvas para Base64 JPEG comprimido.
 * @param {HTMLCanvasElement} canvas - Canvas a converter
 * @param {number} quality - Qualidade JPEG (0-1, default 0.7)
 * @returns {string} Base64 string com prefixo data URI removido
 */
export function canvasToBase64(canvas, quality = 0.7) {
  try {
    // Converter canvas para data URI
    const dataUri = canvas.toDataURL('image/jpeg', quality);
    // Remover prefixo 'data:image/jpeg;base64,' para enviar apenas o conteúdo
    return dataUri.split(',')[1];
  } catch (err) {
    console.error('Error converting canvas to base64:', err);
    return null;
  }
}

/**
 * Desenhar video stream no canvas.
 * @param {HTMLVideoElement} video - Elemento vídeo
 * @param {HTMLCanvasElement} canvas - Canvas destino
 * @returns {boolean} Sucesso ou falha
 */
export function drawVideoToCanvas(video, canvas) {
  try {
    const ctx = canvas.getContext('2d');
    if (!ctx) return false;
    
    // Resize canvas para match video dimensions
    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    }
    
    // Flip horizontal para comportamento de espelho (match com webcam_mediapipe.py original)
    ctx.save();
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    
    // Desenhar frame atual do vídeo
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    ctx.restore();
    return true;
  } catch (err) {
    console.error('Error drawing video to canvas:', err);
    return false;
  }
}

/**
 * Obter stream de câmera com getUserMedia.
 * @param {Object} constraints - getUserMedia constraints
 * @returns {Promise<MediaStream>} Stream de mídia
 */
export async function getCameraStream(constraints = {
  video: { width: 640, height: 480 },
  audio: false
}) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    return stream;
  } catch (err) {
    console.error('Error accessing camera:', err);
    throw err;
  }
}

/**
 * Parar stream de câmera.
 * @param {MediaStream} stream - Stream a parar
 */
export function stopCameraStream(stream) {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
}
