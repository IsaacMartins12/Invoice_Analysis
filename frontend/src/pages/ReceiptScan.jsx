import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function ReceiptScan() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!url.trim()) return setError('Cole a URL do QR Code da nota fiscal');

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

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
        )}

        <div className="bg-green-50 p-4 rounded-lg text-sm text-green-800">
          <p className="font-medium mb-1">Como usar:</p>
          <ol className="list-decimal ml-4 space-y-1">
            <li>Escaneie o QR Code da nota fiscal com a câmera do celular</li>
            <li>Copie a URL que aparece (começa com http://nfce... ou similar)</li>
            <li>Cole aqui abaixo</li>
          </ol>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            URL da Nota Fiscal (QR Code)
          </label>
          <textarea
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="http://nfce.sefaz.am.gov.br/nfce/..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition font-medium disabled:opacity-50"
        >
          Processar Nota Fiscal
        </button>
      </form>
    </div>
  );
}
