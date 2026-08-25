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

  if (loading) return <p className="text-gray-500">Carregando...</p>;
  if (!invoice) return <p className="text-red-500">Fatura não encontrada.</p>;

  const total = invoice.transactions.reduce((sum, t) => sum + t.amount, 0);

  // Group by category
  const grouped = {};
  invoice.transactions.forEach((t) => {
    if (!grouped[t.category]) grouped[t.category] = [];
    grouped[t.category].push(t);
  });

  return (
    <div>
      <Link to="/invoices" className="text-indigo-600 hover:underline text-sm">
        ← Voltar
      </Link>

      <div className="mt-4 mb-6">
        <h1 className="text-2xl font-bold">
          Fatura {String(invoice.month).padStart(2, '0')}/{invoice.year}
          {invoice.bank && <span className="text-gray-400 ml-2">({invoice.bank})</span>}
        </h1>
        <p className="text-gray-500 mt-1">
          {invoice.transactions.length} transações · Total: R$ {total.toFixed(2)}
        </p>
      </div>

      {/* By category */}
      <div className="space-y-4">
        {Object.entries(grouped)
          .sort((a, b) => {
            const totalA = a[1].reduce((s, t) => s + t.amount, 0);
            const totalB = b[1].reduce((s, t) => s + t.amount, 0);
            return totalB - totalA;
          })
          .map(([category, transactions]) => {
            const catTotal = transactions.reduce((s, t) => s + t.amount, 0);
            return (
              <div key={category} className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <div className="px-4 py-3 bg-gray-50 flex justify-between items-center">
                  <span className="font-medium">
                    {EMOJI_MAP[category] || '📦'} {category}
                  </span>
                  <span className="text-sm text-gray-600">
                    R$ {catTotal.toFixed(2)} ({transactions.length} itens)
                  </span>
                </div>
                <table className="w-full text-sm">
                  <tbody>
                    {transactions.map((t) => (
                      <tr key={t.id} className="border-t">
                        <td className="px-4 py-2 text-gray-500 w-20">{t.date}</td>
                        <td className="px-4 py-2">{t.description}</td>
                        <td className="px-4 py-2 text-right font-medium">
                          R$ {t.amount.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })}
      </div>
    </div>
  );
}
