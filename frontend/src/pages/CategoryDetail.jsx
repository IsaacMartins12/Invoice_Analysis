import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
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

export default function CategoryDetail() {
  const { name } = useParams();
  const categoryName = decodeURIComponent(name);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/transactions/', { params: { category: categoryName } })
      .then(({ data }) => setTransactions(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [categoryName]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    );
  }

  const total = transactions.reduce((sum, t) => sum + t.amount, 0);
  const emoji = EMOJI_MAP[categoryName] || '📦';

  // Group by month
  const byMonth = {};
  transactions.forEach((t) => {
    const key = `${t.invoice_year}-${String(t.invoice_month).padStart(2, '0')}`;
    if (!byMonth[key]) byMonth[key] = { total: 0, transactions: [] };
    byMonth[key].total += t.amount;
    byMonth[key].transactions.push(t);
  });

  const chartData = Object.entries(byMonth)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, data]) => ({
      name: month.slice(5),
      total: data.total,
    }));

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Link to="/" className="text-indigo-600 hover:text-indigo-800 text-sm">
          ← Voltar
        </Link>
      </div>

      <div className="bg-white rounded-2xl p-5 border shadow-sm">
        <div className="flex items-center gap-3 mb-1">
          <span className="text-3xl">{emoji}</span>
          <div>
            <h1 className="text-xl font-bold text-gray-800">{categoryName}</h1>
            <p className="text-sm text-gray-400">
              {transactions.length} transações em {Object.keys(byMonth).length} mês(es)
            </p>
          </div>
        </div>
        <p className="text-2xl font-bold text-indigo-600 mt-3">
          R$ {total.toFixed(2)}
        </p>
      </div>

      {/* Chart by month */}
      {chartData.length > 1 && (
        <div className="bg-white rounded-xl p-4 border shadow-sm">
          <h2 className="text-sm font-semibold text-gray-600 mb-3">Evolução mensal</h2>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={(v) => `R$${v}`} tick={{ fontSize: 11 }} width={55} />
              <Tooltip formatter={(v) => `R$ ${v.toFixed(2)}`} />
              <Bar dataKey="total" fill="#6366f1" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Transactions grouped by month */}
      <div className="space-y-4">
        {Object.entries(byMonth)
          .sort(([a], [b]) => b.localeCompare(a))
          .map(([month, data]) => (
            <div key={month} className="bg-white rounded-xl border shadow-sm overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 flex justify-between items-center">
                <span className="font-medium text-gray-700">{month}</span>
                <span className="text-sm font-semibold text-indigo-600">
                  R$ {data.total.toFixed(2)}
                </span>
              </div>
              <div className="divide-y">
                {data.transactions.map((t) => (
                  <div key={t.id} className="px-4 py-3 flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm text-gray-800 truncate">{t.description}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {t.date} · {t.invoice_bank || 'N/A'}
                      </p>
                    </div>
                    <span className="ml-3 font-medium text-gray-800 whitespace-nowrap">
                      R$ {t.amount.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
