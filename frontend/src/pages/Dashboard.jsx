import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import api from '../services/api';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f97316', '#10b981', '#06b6d4', '#eab308', '#ef4444', '#64748b', '#84cc16'];

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

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/dashboard/summary')
      .then(({ data }) => setSummary(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!summary || summary.transaction_count === 0) {
    return (
      <div className="text-center py-16 px-4">
        <div className="text-6xl mb-4">📊</div>
        <h2 className="text-xl font-semibold text-gray-700 mb-2">Nenhuma fatura ainda</h2>
        <p className="text-gray-400 mb-6">Faça upload da sua primeira fatura para começar a acompanhar seus gastos</p>
        <Link
          to="/upload"
          className="inline-block px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition font-medium"
        >
          📤 Enviar Fatura
        </Link>
      </div>
    );
  }

  const categoryData = Object.entries(summary.by_category)
    .map(([name, data]) => ({
      name,
      emoji: EMOJI_MAP[name] || '📦',
      value: data.total,
      count: data.count,
    }))
    .sort((a, b) => b.value - a.value);

  const monthData = Object.entries(summary.by_month).map(([month, total]) => ({
    name: month.slice(5), // just MM
    fullName: month,
    total,
  }));

  return (
    <div className="space-y-6">
      {/* Total card */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <p className="text-sm opacity-80">Total gasto</p>
        <p className="text-3xl font-bold mt-1">R$ {summary.total_spending.toFixed(2)}</p>
        <div className="flex gap-4 mt-3 text-sm opacity-80">
          <span>{summary.transaction_count} transações</span>
          <span>•</span>
          <span>{Object.keys(summary.by_category).length} categorias</span>
        </div>
      </div>

      {/* Category cards - clickable */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Gastos por Categoria</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {categoryData.map((cat, index) => {
            const percentage = ((cat.value / summary.total_spending) * 100).toFixed(0);
            return (
              <Link
                key={cat.name}
                to={`/category/${encodeURIComponent(cat.name)}`}
                className="bg-white rounded-xl p-4 border shadow-sm hover:shadow-md transition active:scale-[0.98]"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className="w-11 h-11 rounded-full flex items-center justify-center text-xl"
                    style={{ backgroundColor: `${COLORS[index % COLORS.length]}20` }}
                  >
                    {cat.emoji}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-800 truncate">{cat.name}</p>
                    <p className="text-xs text-gray-500">{cat.count} transações</p>
                  </div>
                </div>
                {/* Progress bar */}
                <div className="w-full bg-gray-100 rounded-full h-2 mb-2">
                  <div
                    className="h-2 rounded-full transition-all"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: COLORS[index % COLORS.length],
                    }}
                  />
                </div>
                <div className="flex justify-between items-center">
                  <span
                    className="text-sm font-bold"
                    style={{ color: COLORS[index % COLORS.length] }}
                  >
                    {percentage}%
                  </span>
                  <span className="text-sm font-bold text-gray-800">
                    R$ {cat.value.toFixed(2)}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Monthly evolution chart */}
      {monthData.length > 0 && (
        <div className="bg-white rounded-xl p-4 border shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Evolução Mensal</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={monthData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={(v) => `R$${v}`} tick={{ fontSize: 11 }} width={60} />
              <Tooltip
                formatter={(v) => `R$ ${v.toFixed(2)}`}
                labelFormatter={(label) => `Mês ${label}`}
              />
              <Bar dataKey="total" radius={[6, 6, 0, 0]}>
                {monthData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
