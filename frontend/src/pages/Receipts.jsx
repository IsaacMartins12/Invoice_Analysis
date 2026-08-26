import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

export default function Receipts() {
  const [receipts, setReceipts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/receipts/'),
      api.get('/receipts/summary'),
    ])
      .then(([receiptsRes, summaryRes]) => {
        setReceipts(receiptsRes.data);
        setSummary(summaryRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(id) {
    if (!confirm('Tem certeza que deseja excluir esta nota?')) return;
    await api.delete(`/receipts/${id}`);
    setReceipts(receipts.filter((r) => r.id !== id));
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">🛒 Mercado</h1>
        <Link
          to="/receipts/scan"
          className="px-4 py-2 bg-green-600 text-white rounded-xl hover:bg-green-700 transition text-sm font-medium"
        >
          + Escanear
        </Link>
      </div>

      {/* Summary */}
      {summary && summary.total > 0 && (
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-5 text-white shadow-lg">
          <p className="text-sm opacity-80">Total gasto em mercado</p>
          <p className="text-2xl font-bold mt-1">R$ {summary.total.toFixed(2)}</p>
          <div className="flex gap-4 mt-2 text-sm opacity-80">
            <span>{summary.receipt_count} notas</span>
            <span>•</span>
            <span>{summary.item_count} itens</span>
          </div>
        </div>
      )}

      {/* Category breakdown */}
      {summary && Object.keys(summary.by_category).length > 0 && (
        <div className="bg-white rounded-xl p-4 border shadow-sm">
          <h2 className="text-sm font-semibold text-gray-600 mb-3">Por Categoria</h2>
          <div className="space-y-2">
            {Object.entries(summary.by_category).map(([cat, data]) => (
              <div key={cat} className="flex justify-between items-center">
                <span className="text-sm text-gray-700">{cat}</span>
                <div className="text-right">
                  <span className="text-sm font-medium">R$ {data.total.toFixed(2)}</span>
                  <span className="text-xs text-gray-400 ml-2">({data.count})</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Receipt list */}
      {receipts.length === 0 ? (
        <div className="text-center py-10">
          <p className="text-gray-400">Nenhuma nota fiscal ainda.</p>
          <p className="text-gray-400 text-sm mt-1">Escaneie o QR Code de um cupom fiscal pra começar.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {receipts.map((r) => (
            <div key={r.id} className="bg-white rounded-xl p-4 border shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-gray-800">{r.store_name}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {r.date} · {r.item_count} itens
                  </p>
                </div>
                <p className="font-bold text-gray-800">R$ {r.total.toFixed(2)}</p>
              </div>
              <div className="flex gap-3 mt-3 pt-3 border-t">
                <Link
                  to={`/receipts/${r.id}`}
                  className="text-sm text-green-600 font-medium hover:underline"
                >
                  Ver itens
                </Link>
                <button
                  onClick={() => handleDelete(r.id)}
                  className="text-sm text-red-500 font-medium hover:underline"
                >
                  Excluir
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
