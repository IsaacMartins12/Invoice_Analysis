import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import jsQR from 'jsqr';
import api from '../services/api';
import { getErrorMessage } from '../services/errors';

export default function ReceiptScan() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [scanning, setScanning] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const animFrameRef = useRef(null);
  const navigate = useNavigate();

  const stopCamera = useCallback(() => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setScanning(false);
  }, []);

  useEffect(() => {
    return () => stopCamera();
  }, [stopCamera]);

  async function startCamera() {
    setCameraError('');
    setError('');
    setScanning(true);
  }

  // Start camera when scanning state changes to true
  useEffect(() => {
    if (!scanning) return;

    let cancelled = false;

    async function initCamera() {
      // Wait for video element to be rendered
      await new Promise((resolve) => setTimeout(resolve, 100));

      if (cancelled || !videoRef.current) return;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' },
        });

        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }

        streamRef.current = stream;
        const video = videoRef.current;
        video.srcObject = stream;
        video.setAttribute('playsinline', true);
        await video.play();
        scanFrame();
      } catch (err) {
        console.error('Camera error:', err);
        setCameraError(
          `Não foi possível acessar a câmera: ${err.message}. Verifique as permissões do navegador.`
        );
        setScanning(false);
      }
    }

    initCamera();

    return () => {
      cancelled = true;
    };
  }, [scanning]);

  function scanFrame() {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || video.readyState !== video.HAVE_ENOUGH_DATA) {
      animFrameRef.current = requestAnimationFrame(scanFrame);
      return;
    }

    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: 'dontInvert',
    });

    if (code && code.data) {
      setUrl(code.data);
      stopCamera();
      return;
    }

    animFrameRef.current = requestAnimationFrame(scanFrame);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) return setError('Escaneie o QR Code ou cole a URL da nota fiscal');

    setError('');
    setLoading(true);

    try {
      const { data } = await api.post('/receipts/scan', { url: url.trim() });
      navigate(`/receipts/${data.id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  // Loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="bg-white p-10 rounded-xl shadow-lg border text-center max-w-md w-full">
          <div className="mx-auto mb-6 w-16 h-16 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Processando nota fiscal...</h2>
          <p className="text-green-600 font-medium mb-4">🛒 Identificando produtos...</p>
          <p className="text-sm text-gray-400">Buscando dados na SEFAZ e normalizando descrições</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">🛒 Escanear Nota Fiscal</h1>

      <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
        )}

        {/* Camera scanner */}
        {!scanning ? (
          <button
            onClick={startCamera}
            className="w-full py-4 bg-green-600 text-white rounded-xl hover:bg-green-700 transition font-medium text-lg"
          >
            📷 Abrir Câmera e Escanear QR Code
          </button>
        ) : (
          <div className="space-y-3">
            <div className="relative rounded-lg overflow-hidden bg-black">
              <video
                ref={videoRef}
                className="w-full"
                playsInline
                muted
              />
              {/* Scan overlay */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-48 h-48 border-2 border-green-400 rounded-lg opacity-70" />
              </div>
              <p className="absolute bottom-2 left-0 right-0 text-center text-white text-xs bg-black/50 py-1">
                Aponte para o QR Code da nota fiscal
              </p>
            </div>
            <button
              onClick={stopCamera}
              className="w-full py-2 bg-gray-200 text-gray-700 rounded-lg text-sm"
            >
              Cancelar
            </button>
          </div>
        )}

        {/* Hidden canvas for QR processing */}
        <canvas ref={canvasRef} className="hidden" />

        {cameraError && (
          <div className="bg-orange-50 text-orange-700 p-3 rounded-lg text-sm">
            {cameraError}
          </div>
        )}

        {/* URL detected badge */}
        {url && !scanning && (
          <div className="bg-green-50 border border-green-200 p-3 rounded-lg">
            <p className="text-xs text-green-600 font-medium mb-1">✅ QR Code detectado!</p>
            <p className="text-xs text-green-800 break-all">{url.slice(0, 100)}...</p>
          </div>
        )}

        {/* Divider */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-xs text-gray-400">ou cole a URL manualmente</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        {/* Manual URL input */}
        <form onSubmit={handleSubmit} className="space-y-3">
          <textarea
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="http://nfce.sefaz.am.gov.br/nfce/..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
          />

          <button
            type="submit"
            disabled={!url.trim() || loading}
            className="w-full py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition font-medium disabled:opacity-50"
          >
            Processar Nota Fiscal
          </button>
        </form>
      </div>
    </div>
  );
}
