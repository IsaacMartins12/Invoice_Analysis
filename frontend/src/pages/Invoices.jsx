import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/invoices/')
      .then(({ data }) => setInvoices(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(id) {
    if (!confirm('Tem certeza que deseja excluir esta fatura?')) return;
    await api.delete(`/invoices/${id}`);
    setInvoices(invoices.filter((inv) => inv.id !== id));
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">📁 Faturas</h1>
        <Link
          to="/upload"
          className="px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition text-sm font-medium"
        >
          + Nova
        </Link>
      </div>

      {invoices.length === 0 ? (
        <p className="text-gray-400 text-center py-10">Nenhuma fatura ainda.</p>
      ) : (
        <div className="space-y-3">
          {invoices.map((inv) => (
            <div
              key={inv.id}
              className="bg-white rounded-xl p-4 border shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-gray-800">
                    {String(inv.month).padStart(2, '0')}/{inv.year}
                    {inv.bank && (
                      <span className="ml-2 text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full">
                        {inv.bank}
                      </span>
                    )}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {inv.file_name} · {inv.transaction_count} transações
                  </p>
                </div>
                <p className="font-bold text-gray-800">
                  R$ {inv.total_amount.toFixed(2)}
                </p>
              </div>
              <div className="flex gap-3 mt-3 pt-3 border-t">
                <Link
                  to={`/invoices/${inv.id}`}
                  className="text-sm text-indigo-600 font-medium hover:underline"
                >
                  Ver detalhes
                </Link>
                <button
                  onClick={() => handleDelete(inv.id)}
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
