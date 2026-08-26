import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Html5Qrcode } from 'html5-qrcode';
import api from '../services/api';

export default function ReceiptScan() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [scanning, setScanning] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const scannerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    return () => {
      // Cleanup scanner on unmount
      if (scannerRef.current) {
        scannerRef.current.stop().catch(() => {});
      }
    };
  }, []);

  async function startScanner() {
    setCameraError('');
    setScanning(true);

    try {
      const scanner = new Html5Qrcode('qr-reader');
      scannerRef.current = scanner;

      await scanner.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        (decodedText) => {
          // QR Code detected
          setUrl(decodedText);
          scanner.stop().catch(() => {});
          setScanning(false);
        },
        () => {} // ignore errors during scan
      );
    } catch (err) {
      setScanning(false);
      setCameraError(
        'Não foi possível acessar a câmera. Verifique as permissões ou cole a URL manualmente.'
      );
    }
  }

  function stopScanner() {
    if (scannerRef.current) {
      scannerRef.current.stop().catch(() => {});
    }
    setScanning(false);
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
      setError(err.response?.data?.detail || 'Erro ao processar nota fiscal');
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

        {/* QR Scanner */}
        <div>
          {!scanning ? (
            <button
              onClick={startScanner}
              className="w-full py-4 bg-green-600 text-white rounded-xl hover:bg-green-700 transition font-medium text-lg"
            >
              📷 Abrir Câmera e Escanear QR Code
            </button>
          ) : (
            <div className="space-y-3">
              <div
                id="qr-reader"
                className="w-full rounded-lg overflow-hidden"
              />
              <button
                onClick={stopScanner}
                className="w-full py-2 bg-gray-200 text-gray-700 rounded-lg text-sm"
              >
                Cancelar scan
              </button>
            </div>
          )}

          {cameraError && (
            <p className="text-sm text-orange-600 mt-2">{cameraError}</p>
          )}
        </div>

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

        {/* Help */}
        <div className="bg-green-50 p-4 rounded-lg text-sm text-green-800">
          <p className="font-medium mb-1">Como funciona:</p>
          <ol className="list-decimal ml-4 space-y-1">
            <li>Aponte a câmera para o QR Code do cupom fiscal</li>
            <li>A URL será capturada automaticamente</li>
            <li>Clique em "Processar" para extrair os itens</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
