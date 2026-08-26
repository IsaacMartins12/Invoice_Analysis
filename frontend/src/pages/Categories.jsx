import { useState, useEffect } from 'react';
import api from '../services/api';

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [name, setName] = useState('');
  const [emoji, setEmoji] = useState('📦');

  useEffect(() => {
    loadCategories();
  }, []);

  function loadCategories() {
    api.get('/categories/')
      .then(({ data }) => setCategories(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }

  function resetForm() {
    setName('');
    setEmoji('📦');
    setShowForm(false);
    setEditingId(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      if (editingId) {
        await api.put(`/categories/${editingId}`, { name, emoji });
      } else {
        await api.post('/categories/', { name, emoji });
      }
      resetForm();
      loadCategories();
    } catch (err) {
      alert(err.response?.data?.detail || 'Erro ao salvar categoria');
    }
  }

  function startEdit(cat) {
    setEditingId(cat.id);
    setName(cat.name);
    setEmoji(cat.emoji);
    setShowForm(true);
  }

  async function handleDelete(cat) {
    if (!confirm(`Excluir "${cat.name}"? Transações serão movidas para "Outros".`)) return;
    await api.delete(`/categories/${cat.id}`);
    loadCategories();
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">🏷️ Categorias</h1>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition text-sm font-medium"
          >
            + Nova
          </button>
        )}
      </div>

      {/* Create/Edit form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white p-4 rounded-xl border shadow-sm space-y-3">
          <p className="text-sm font-medium text-gray-700">
            {editingId ? 'Editar categoria' : 'Nova categoria'}
          </p>
          <div className="flex gap-3">
            <input
              type="text"
              value={emoji}
              onChange={(e) => setEmoji(e.target.value)}
              className="w-14 px-2 py-2 border rounded-lg text-center text-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
              maxLength={2}
            />
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nome da categoria"
              className="flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium"
            >
              {editingId ? 'Salvar' : 'Criar'}
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm"
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {/* Category list */}
      <div className="bg-white rounded-xl border shadow-sm divide-y overflow-hidden">
        {categories.map((cat) => (
          <div key={cat.name} className="px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xl">{cat.emoji}</span>
              <div>
                <p className="text-sm font-medium text-gray-800">{cat.name}</p>
                {cat.is_default && (
                  <p className="text-xs text-gray-400">Padrão</p>
                )}
              </div>
            </div>
            {!cat.is_default && (
              <div className="flex gap-2">
                <button
                  onClick={() => startEdit(cat)}
                  className="text-xs text-indigo-500 hover:underline"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(cat)}
                  className="text-xs text-red-500 hover:underline"
                >
                  Excluir
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
