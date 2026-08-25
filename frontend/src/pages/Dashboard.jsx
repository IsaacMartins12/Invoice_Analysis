import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
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

  if (loading) return <p className="text-gray-500">Carregando...</p>;
  if (!summary || summary.transaction_count === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 text-lg">Nenhuma fatura encontrada.</p>
        <p className="text-gray-400 mt-2">Faça upload da sua primeira fatura para começar!</p>
      </div>
    );
  }

  const categoryData = Object.entries(summary.by_category).map(([name, data]) => ({
    name: `${EMOJI_MAP[name] || '📦'} ${name}`,
    value: data.total,
    count: data.count,
  }));

  const monthData = Object.entries(summary.by_month).map(([month, total]) => ({
    name: month,
    total,
  }));

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Total Gasto</p>
          <p className="text-2xl font-bold text-indigo-600">R$ {summary.total_spending.toFixed(2)}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Transações</p>
          <p className="text-2xl font-bold text-gray-800">{summary.transaction_count}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <p className="text-sm text-gray-500">Categorias</p>
          <p className="text-2xl font-bold text-gray-800">{Object.keys(summary.by_category).length}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar chart - by category */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Gastos por Categoria</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData} layout="vertical" margin={{ left: 120 }}>
              <XAxis type="number" tickFormatter={(v) => `R$${v}`} />
              <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v) => `R$ ${v.toFixed(2)}`} />
              <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Distribuição (%)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name.split(' ').slice(1).join(' ')} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {categoryData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => `R$ ${v.toFixed(2)}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Monthly evolution */}
      {monthData.length > 1 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Evolução Mensal</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={monthData}>
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(v) => `R$${v}`} />
              <Tooltip formatter={(v) => `R$ ${v.toFixed(2)}`} />
              <Bar dataKey="total" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Category table */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-lg font-semibold mb-4">Detalhamento por Categoria</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Categoria</th>
              <th className="text-right py-2">Total</th>
              <th className="text-right py-2">%</th>
              <th className="text-right py-2">Itens</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(summary.by_category).map(([name, data]) => (
              <tr key={name} className="border-b last:border-0">
                <td className="py-2">{EMOJI_MAP[name] || '📦'} {name}</td>
                <td className="text-right py-2">R$ {data.total.toFixed(2)}</td>
                <td className="text-right py-2 text-gray-500">
                  {((data.total / summary.total_spending) * 100).toFixed(1)}%
                </td>
                <td className="text-right py-2 text-gray-500">{data.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
