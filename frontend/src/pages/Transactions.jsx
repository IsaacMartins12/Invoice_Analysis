import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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

const CATEGORIES = [
  'Transporte', 'Alimentação', 'Mercado', 'Telefone/Internet/Streaming',
  'Saúde/Academia', 'Compras', 'Viagem/Lazer', 'Taxas/Seguros', 'Assinaturas', 'Outros',
];

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    search: '',
    date_from: '',
    date_to: '',
  });
  const [allCategories, setAllCategories] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editCategory, setEditCategory] = useState('');

  useEffect(() => {
    api.get('/categories/').then(({ data }) => setAllCategories(data));
  }, []);

  useEffect(() => {
    const params = {};
    if (filters.category) params.category = filters.category;
    if (filters.search) params.search = filters.search;
    if (filters.date_from) params.month = filters.date_from;
    if (filters.date_to) params.year = filters.date_to;

    api.get('/transactions/', { params })
      .then(({ data }) => setTransactions(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters]);

  async function saveCategory(txnId) {
    await api.put(`/transactions/${txnId}/category`, { category: editCategory });
    setTransactions(transactions.map((t) =>
      t.id === txnId ? { ...t, category: editCategory } : t
    ));
    setEditingId(null);
  }

  const total = transactions.reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">💰 Todas as Transações</h1>
        <Link
          to="/categories"
          className="px-3 py-2 bg-indigo-100 text-indigo-700 rounded-xl hover:bg-indigo-200 transition text-xs font-medium whitespace-nowrap"
        >
          🏷️ Categorias
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 border shadow-sm space-y-3">
        {/* Search */}
        <input
          type="text"
          placeholder="Buscar por descrição..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />

        {/* Date range - filter by invoice period */}
        <div className="flex gap-2">
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1">Mês</label>
            <select
              value={filters.date_from}
              onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Todos</option>
              {[...Array(12)].map((_, i) => (
                <option key={i + 1} value={i + 1}>
                  {new Date(2000, i).toLocaleString('pt-BR', { month: 'long' })}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-xs text-gray-500 mb-1">Ano</label>
            <select
              value={filters.date_to}
              onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Todos</option>
              <option value="2025">2025</option>
              <option value="2026">2026</option>
              <option value="2027">2027</option>
            </select>
          </div>
        </div>

        {/* Category filter chips */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilters({ ...filters, category: '' })}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
              !filters.category
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Todas
          </button>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilters({ ...filters, category: cat })}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
                filters.category === cat
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {EMOJI_MAP[cat]} {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="flex justify-between items-center px-1">
        <span className="text-sm text-gray-500">
          {transactions.length} transações
        </span>
        <span className="text-sm font-semibold text-indigo-600">
          Total: R$ {total.toFixed(2)}
        </span>
      </div>

      {/* Transaction list */}
      {loading ? (
        <div className="flex items-center justify-center py-10">
          <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
        </div>
      ) : transactions.length === 0 ? (
        <p className="text-center text-gray-400 py-10">Nenhuma transação encontrada.</p>
      ) : (
        <div className="bg-white rounded-xl border shadow-sm divide-y overflow-hidden">
          {transactions.map((t) => (
            <div key={t.id} className="px-4 py-3">
              {editingId === t.id ? (
                <div className="flex items-center gap-2">
                  <select
                    value={editCategory}
                    onChange={(e) => setEditCategory(e.target.value)}
                    className="flex-1 px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {allCategories.map((cat) => (
                      <option key={cat.name} value={cat.name}>{cat.emoji} {cat.name}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => saveCategory(t.id)}
                    className="px-3 py-1 bg-indigo-600 text-white rounded text-xs"
                  >
                    Salvar
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    className="px-3 py-1 bg-gray-200 text-gray-600 rounded text-xs"
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <span className="text-lg">{EMOJI_MAP[t.category] || '📦'}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-800 truncate">{t.description}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {t.date} · {t.invoice_bank || '—'} · {String(t.invoice_month).padStart(2, '0')}/{t.invoice_year}
                    </p>
                  </div>
                  <span className="font-medium text-gray-800 whitespace-nowrap text-sm">
                    R$ {t.amount.toFixed(2)}
                  </span>
                  <button
                    onClick={() => { setEditingId(t.id); setEditCategory(t.category); }}
                    className="text-xs text-indigo-500 hover:underline ml-1"
                  >
                    Editar
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
