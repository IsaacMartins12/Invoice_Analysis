/**
 * Translates API error responses into user-friendly Portuguese messages.
 */

const ERROR_MAP = {
  // Auth
  'Invalid email or password': 'Email ou senha incorretos.',
  'Invalid credentials': 'Sessão expirada. Faça login novamente.',
  'Email already registered': 'Este email já está cadastrado.',

  // Upload
  'Only PDF files are accepted': 'Apenas arquivos PDF são aceitos.',
  'Could not extract text from PDF': 'Não foi possível ler o PDF. O arquivo pode estar vazio ou ser uma imagem escaneada.',

  // Generic
  'Not Found': 'Recurso não encontrado.',
  'Internal Server Error': 'Erro interno do servidor. Tente novamente.',
};

export function getErrorMessage(error) {
  // If no response (network error, timeout)
  if (!error.response) {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      return 'A requisição demorou demais. Verifique se o Ollama está rodando e tente novamente.';
    }
    return 'Sem conexão com o servidor. Verifique se o backend está rodando.';
  }

  const status = error.response.status;
  const detail = error.response.data?.detail;

  // If backend sent a Portuguese message (our new validations), use it directly
  if (detail && /[àáâãéêíóôõúç]/i.test(detail)) {
    return detail;
  }

  // Check mapped messages
  if (detail && ERROR_MAP[detail]) {
    return ERROR_MAP[detail];
  }

  // Status-based fallbacks
  switch (status) {
    case 400:
      return detail || 'Dados inválidos. Verifique os campos e tente novamente.';
    case 401:
      return 'Sessão expirada. Faça login novamente.';
    case 403:
      return 'Você não tem permissão para esta ação.';
    case 404:
      return 'Recurso não encontrado.';
    case 409:
      return detail || 'Este item já existe.';
    case 413:
      return 'Arquivo muito grande. O limite é 10MB.';
    case 422:
      return detail || 'Não foi possível processar os dados enviados.';
    case 500:
      return 'Erro interno do servidor. Tente novamente em alguns instantes.';
    case 503:
      return 'Serviço indisponível. Verifique se o Ollama está rodando.';
    default:
      return detail || 'Ocorreu um erro inesperado. Tente novamente.';
  }
}
