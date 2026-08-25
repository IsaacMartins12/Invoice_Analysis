import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';

const EMOJI_MAP = {
  'Transporte': '🚗',
  'Alimentação': '🍔',
  'Mercado': '🛒',
  'Telefone/Internet/Streaming': '📱',
  'Saúde/Academia': '💪',
  'Compras': '🛍️',
  'Viagem/Lazer': '✈️',
  'Taxas/Seguros': '💳',
  'Assinaturas': '📋',
  'Outros': '📦',
};

export default function InvoiceDetail() {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/invoices/${id}`)
      .then(({ data }) => setInvoice(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!invoice) return <p className="text-red-500">Fatura não encontrada.</p>;

  const total = invoice.transactions.reduce((sum, t) => sum + t.amount, 0);

  // Group by category
  const grouped = {};
  invoice.transactions.forEach((t) => {
    if (!grouped[t.category]) grouped[t.category] = [];
    grouped[t.category].push(t);
  });

  return (
    <div className="space-y-4">
      <Link to="/invoices" className="text-indigo-600 hover:text-indigo-800 text-sm">
        ← Voltar
      </Link>

      {/* Header */}
      <div className="bg-white rounded-2xl p-5 border shadow-sm">
        <h1 className="text-xl font-bold text-gray-800">
          Fatura {String(invoice.month).padStart(2, '0')}/{invoice.year}
        </h1>
        {invoice.bank && (
          <span className="inline-block mt-1 text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full">
            {invoice.bank}
          </span>
        )}
        <p className="text-2xl font-bold text-indigo-600 mt-2">
          R$ {total.toFixed(2)}
        </p>
        <p className="text-sm text-gray-400">
          {invoice.transactions.length} transações
        </p>
      </div>

      {/* By category */}
      <div className="space-y-3">
        {Object.entries(grouped)
          .sort((a, b) => {
            const totalA = a[1].reduce((s, t) => s + t.amount, 0);
            const totalB = b[1].reduce((s, t) => s + t.amount, 0);
            return totalB - totalA;
          })
          .map(([category, txns]) => {
            const catTotal = txns.reduce((s, t) => s + t.amount, 0);
            return (
              <div key={category} className="bg-white rounded-xl border shadow-sm overflow-hidden">
                <div className="px-4 py-3 bg-gray-50 flex justify-between items-center">
                  <span className="font-medium text-gray-700">
                    {EMOJI_MAP[category] || '📦'} {category}
                  </span>
                  <span className="text-sm font-semibold text-indigo-600">
                    R$ {catTotal.toFixed(2)}
                  </span>
                </div>
                <div className="divide-y">
                  {txns.map((t) => (
                    <div key={t.id} className="px-4 py-3 flex items-center justify-between">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-gray-800 truncate">{t.description}</p>
                        <p className="text-xs text-gray-400 mt-0.5">{t.date}</p>
                      </div>
                      <span className="ml-3 font-medium text-gray-800 whitespace-nowrap text-sm">
                        R$ {t.amount.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}
