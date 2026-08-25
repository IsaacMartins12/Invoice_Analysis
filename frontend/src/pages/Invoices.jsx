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

  if (loading) return <p className="text-gray-500">Carregando...</p>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">📁 Minhas Faturas</h1>
        <Link
          to="/upload"
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition text-sm"
        >
          + Nova Fatura
        </Link>
      </div>

      {invoices.length === 0 ? (
        <p className="text-gray-400 text-center py-8">Nenhuma fatura cadastrada ainda.</p>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3">Período</th>
                <th className="text-left px-4 py-3">Banco</th>
                <th className="text-left px-4 py-3">Arquivo</th>
                <th className="text-right px-4 py-3">Total</th>
                <th className="text-right px-4 py-3">Transações</th>
                <th className="text-right px-4 py-3">Ações</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">
                    {String(inv.month).padStart(2, '0')}/{inv.year}
                  </td>
                  <td className="px-4 py-3">{inv.bank || '-'}</td>
                  <td className="px-4 py-3 text-gray-500">{inv.file_name}</td>
                  <td className="px-4 py-3 text-right font-medium">
                    R$ {inv.total_amount.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-500">
                    {inv.transaction_count}
                  </td>
                  <td className="px-4 py-3 text-right space-x-2">
                    <Link
                      to={`/invoices/${inv.id}`}
                      className="text-indigo-600 hover:underline"
                    >
                      Ver
                    </Link>
                    <button
                      onClick={() => handleDelete(inv.id)}
                      className="text-red-500 hover:underline"
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
