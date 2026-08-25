# 📊 Invoice Analysis

**Controle financeiro inteligente com IA local. Seus dados nunca saem do seu computador.**

Faça upload das suas faturas de cartão de crédito em PDF e tenha uma visão completa dos seus gastos — categorizado automaticamente por inteligência artificial, com gráficos interativos e histórico mensal.

## 🔒 Privacidade em Primeiro Lugar

Diferente de apps como Guiabolso, Organizze ou Olivia, este sistema roda **100% na sua máquina**:

- 🤖 **IA local** — Ollama processa suas faturas sem internet
- 💾 **Banco de dados local** — PostgreSQL na sua máquina
- 🚫 **Zero telemetria** — nenhum dado é enviado para servidores externos
- 🔓 **Open source** — audite o código você mesmo

## ✨ Funcionalidades

- **Upload de fatura PDF** — suporta Bradesco e Nubank (extensível para outros bancos)
- **Extração precisa** — regex com 100% de acurácia nos valores
- **Categorização por IA** — LLM local classifica cada gasto automaticamente
- **Dashboard interativo** — total gasto, distribuição por categoria, evolução mensal
- **Drill-down por categoria** — clique em qualquer categoria e veja o histórico completo
- **Filtros e busca** — encontre qualquer transação por texto, categoria ou período
- **Mobile-first** — interface responsiva que funciona bem no celular
- **Multi-usuário** — cada pessoa com sua conta e seus dados separados

## 🛠️ Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | React + Vite + Tailwind CSS + Recharts |
| Backend | FastAPI (Python) |
| Banco de dados | PostgreSQL |
| IA | Ollama (llama3.1:8b) — 100% local |
| Deploy | Docker Compose |

## 🚀 Como Rodar

### Pré-requisito

- [Docker](https://docs.docker.com/get-docker/) instalado

### Um comando sobe tudo:

```bash
docker-compose up --build
```

Na primeira execução, o modelo de IA (~4.7GB) será baixado automaticamente. Depois fica em cache.

Acesse: **http://localhost:3000**

### Com GPU NVIDIA (opcional, pra performance):

Descomente o bloco `deploy` no serviço `ollama` do `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### Desenvolvimento local (sem Docker):

```bash
# PostgreSQL
docker run -d --name pg-invoice -e POSTGRES_DB=invoice_analysis -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16-alpine

# Ollama
ollama pull llama3.1:8b

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## 📱 Screenshots

<!-- TODO: adicionar screenshots da nova interface -->

## 🏦 Bancos Suportados

| Banco | Status |
|-------|--------|
| Bradesco | ✅ Suportado |
| Nubank | ✅ Suportado |
| Inter | 🔜 Em breve |
| C6 Bank | 🔜 Em breve |
| Itaú | 🔜 Em breve |

Quer adicionar suporte a outro banco? Basta criar um novo extrator em `backend/app/services/extractor.py` com o regex do formato da fatura.

## 🏗️ Arquitetura

```
Invoice_Analysis/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── api/            ← Rotas (auth, invoices, transactions, dashboard)
│   │   ├── models/         ← User, Invoice, Transaction
│   │   ├── services/
│   │   │   ├── extractor.py  ← Regex por banco (100% preciso)
│   │   │   ├── llm.py        ← Categorização via Ollama
│   │   │   ├── auth.py       ← JWT auth
│   │   │   └── pdf.py        ← Extração de texto do PDF
│   │   └── main.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/          ← Dashboard, Upload, Invoices, CategoryDetail, Transactions
│   │   ├── components/     ← Layout com nav mobile
│   │   └── services/       ← Axios config
│   └── Dockerfile
```

## 🤝 Contribuição

Contribuições são bem-vindas! Especialmente:

- **Novos bancos** — adicione regex para extrair transações de outros bancos
- **Melhorias na categorização** — refine o prompt do LLM ou adicione regras
- **Interface** — melhorias de UX, novos gráficos, dark mode

### Como contribuir

1. Fork o projeto
2. Crie sua branch (`git checkout -b feat/novo-banco`)
3. Commit suas mudanças (`git commit -m 'feat: suporte ao banco X'`)
4. Push (`git push origin feat/novo-banco`)
5. Abra um Pull Request

## 📜 Licença

[MIT](LICENSE)
