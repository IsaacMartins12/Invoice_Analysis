import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const LOADING_MESSAGES = [
  '📄 Extraindo texto do PDF...',
  '🤖 Enviando para a IA analisar...',
  '🔍 Identificando transações...',
  '🏷️ Categorizando gastos...',
  '💾 Salvando no banco de dados...',
];

export default function Upload() {
  const [file, setFile] = useState(null);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [bank, setBank] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return setError('Selecione um arquivo PDF');

    setError('');
    setLoading(true);

    // Cycle through loading messages
    let messageIndex = 0;
    setLoadingMessage(LOADING_MESSAGES[0]);
    const interval = setInterval(() => {
      messageIndex = Math.min(messageIndex + 1, LOADING_MESSAGES.length - 1);
      setLoadingMessage(LOADING_MESSAGES[messageIndex]);
    }, 8000);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('month', month);
    formData.append('year', year);
    if (bank) formData.append('bank', bank);

    try {
      const { data } = await api.post('/invoices/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180000,
      });
      clearInterval(interval);
      navigate(`/invoices/${data.id}`);
    } catch (err) {
      clearInterval(interval);
      setError(err.response?.data?.detail || 'Erro ao processar fatura');
    } finally {
      setLoading(false);
      setLoadingMessage('');
    }
  }

  // Loading overlay
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="bg-white p-10 rounded-xl shadow-lg border text-center max-w-md w-full">
          {/* Spinner */}
          <div className="mx-auto mb-6 w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />

          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Processando fatura...
          </h2>

          <p className="text-indigo-600 font-medium mb-4 min-h-[24px]">
            {loadingMessage}
          </p>

          <p className="text-sm text-gray-400">
            Isso pode levar até 1 minuto dependendo do tamanho da fatura
          </p>

          {/* Progress bar animation */}
          <div className="mt-6 w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className="h-full bg-indigo-600 rounded-full animate-pulse" style={{ width: '80%' }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">📤 Upload de Fatura</h1>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-sm border space-y-4">
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded text-sm">{error}</div>
        )}

        {/* File input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Arquivo PDF</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100"
          />
        </div>

        {/* Month/Year */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mês</label>
            <select
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {[...Array(12)].map((_, i) => (
                <option key={i + 1} value={i + 1}>
                  {new Date(2000, i).toLocaleString('pt-BR', { month: 'long' })}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ano</label>
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              min={2020}
              max={2030}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        {/* Bank (optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Banco (opcional)</label>
          <input
            type="text"
            value={bank}
            onChange={(e) => setBank(e.target.value)}
            placeholder="Ex: Bradesco, Nubank, Inter..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition disabled:opacity-50"
        >
          Enviar Fatura
        </button>
      </form>
    </div>
  );
}
