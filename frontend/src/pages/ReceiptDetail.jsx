import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';

export default function ReceiptDetail() {
  const { id } = useParams();
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingItem, setEditingItem] = useState(null);
  const [editName, setEditName] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    Promise.all([
      api.get(`/receipts/${id}`),
      api.get('/receipts/categories'),
    ])
      .then(([receiptRes, catRes]) => {
        setReceipt(receiptRes.data);
        setCategories(catRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  function startEdit(item) {
    setEditingItem(item.id);
    setEditName(item.description);
    setEditCategory(item.category);
  }

  async function saveEdit(itemId) {
    try {
      await api.put(`/receipts/items/${itemId}`, {
        description: editName,
        category: editCategory,
        save_to_dictionary: true,
      });
      // Update local state
      setReceipt({
        ...receipt,
        items: receipt.items.map((item) =>
          item.id === itemId
            ? { ...item, description: editName, category: editCategory }
            : item
        ),
      });
      setEditingItem(null);
    } catch (err) {
      alert('Erro ao salvar');
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!receipt) return <p className="text-red-500">Nota não encontrada.</p>;

  // Group by category
  const grouped = {};
  receipt.items.forEach((item) => {
    if (!grouped[item.category]) grouped[item.category] = [];
    grouped[item.category].push(item);
  });

  return (
    <div className="space-y-4">
      <Link to="/receipts" className="text-green-600 hover:text-green-800 text-sm">
        ← Voltar
      </Link>

      {/* Header */}
      <div className="bg-white rounded-2xl p-5 border shadow-sm">
        <h1 className="text-xl font-bold text-gray-800">{receipt.store_name}</h1>
        {receipt.store_cnpj && (
          <p className="text-xs text-gray-400 mt-0.5">CNPJ: {receipt.store_cnpj}</p>
        )}
        <p className="text-sm text-gray-500 mt-1">{receipt.date}</p>
        <p className="text-2xl font-bold text-green-600 mt-2">R$ {receipt.total.toFixed(2)}</p>
        <p className="text-sm text-gray-400">{receipt.items.length} itens</p>
      </div>

      {/* Info */}
      <div className="bg-yellow-50 p-3 rounded-lg text-xs text-yellow-800">
        💡 Clique em "Editar" para corrigir nomes de produtos. A correção é salva no dicionário e será aplicada automaticamente nas próximas notas.
      </div>

      {/* Items by category */}
      <div className="space-y-3">
        {Object.entries(grouped)
          .sort((a, b) => {
            const totalA = a[1].reduce((s, i) => s + i.total_price, 0);
            const totalB = b[1].reduce((s, i) => s + i.total_price, 0);
            return totalB - totalA;
          })
          .map(([category, items]) => {
            const catTotal = items.reduce((s, i) => s + i.total_price, 0);
            return (
              <div key={category} className="bg-white rounded-xl border shadow-sm overflow-hidden">
                <div className="px-4 py-3 bg-gray-50 flex justify-between items-center">
                  <span className="font-medium text-gray-700">{category}</span>
                  <span className="text-sm font-semibold text-green-600">
                    R$ {catTotal.toFixed(2)}
                  </span>
                </div>
                <div className="divide-y">
                  {items.map((item) => (
                    <div key={item.id} className="px-4 py-3">
                      {editingItem === item.id ? (
                        <div className="space-y-2">
                          <input
                            type="text"
                            value={editName}
                            onChange={(e) => setEditName(e.target.value)}
                            className="w-full px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                          />
                          <select
                            value={editCategory}
                            onChange={(e) => setEditCategory(e.target.value)}
                            className="w-full px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                          >
                            {categories.map((cat) => (
                              <option key={cat} value={cat}>{cat}</option>
                            ))}
                          </select>
                          <div className="flex gap-2">
                            <button
                              onClick={() => saveEdit(item.id)}
                              className="px-3 py-1 bg-green-600 text-white rounded text-xs"
                            >
                              Salvar
                            </button>
                            <button
                              onClick={() => setEditingItem(null)}
                              className="px-3 py-1 bg-gray-200 text-gray-600 rounded text-xs"
                            >
                              Cancelar
                            </button>
                          </div>
                          <p className="text-xs text-gray-400">
                            Original: {item.raw_description}
                          </p>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between">
                          <div className="min-w-0 flex-1">
                            <p className="text-sm text-gray-800 truncate">{item.description}</p>
                            <p className="text-xs text-gray-400 mt-0.5">
                              {item.quantity} {item.unit || 'un'} × R$ {item.unit_price.toFixed(2)}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 ml-3">
                            <span className="font-medium text-gray-800 whitespace-nowrap text-sm">
                              R$ {item.total_price.toFixed(2)}
                            </span>
                            <button
                              onClick={() => startEdit(item)}
                              className="text-xs text-indigo-500 hover:underline"
                            >
                              Editar
                            </button>
                          </div>
                        </div>
                      )}
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
