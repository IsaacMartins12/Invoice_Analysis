# 📱 Invoice Analysis — Android App

Versão mobile nativa do Invoice Analysis, construída com **Kotlin + Jetpack Compose**.

## Status

🚧 **UI only** — nesta fase, o app replica toda a interface do web app usando dados mockados. A integração com a API (Retrofit) e funcionalidades (QR scanner, upload) virão em etapas seguintes.

## Telas implementadas

- **Dashboard** — total gasto, cards de categoria com barra de progresso
- **Gastos (Transactions)** — lista com busca e filtro por categoria (chips)
- **Mercado (Receipts)** — resumo e lista de notas fiscais
- **Upload** — formulário de envio de fatura
- **Faturas (Invoices)** — lista de faturas processadas
- **Categorias** — gerenciamento de categorias
- **Detalhe de Categoria** — transações de uma categoria específica

## Stack

- Kotlin 2.0
- Jetpack Compose (Material 3)
- Navigation Compose
- Bottom navigation com 5 abas

## Estrutura

```
android/
├── app/
│   └── src/main/java/com/isaac/invoiceanalysis/
│       ├── MainActivity.kt
│       ├── navigation/       ← Screen (rotas) + AppNavigation
│       ├── data/             ← MockData (dados de exemplo)
│       └── ui/
│           ├── theme/        ← Cores, tipografia (paleta indigo/purple)
│           ├── components/   ← TopBar, BottomNavBar
│           └── screens/      ← Todas as telas
```

## Como rodar

Abra a pasta `android/` no Android Studio, sincronize o Gradle e rode em um emulador ou dispositivo (minSdk 26 / Android 8.0+).

## Próximos passos

1. Camada de dados com Retrofit consumindo a API FastAPI
2. Autenticação JWT com DataStore
3. Scanner de QR Code com CameraX + ML Kit
4. Seletor de arquivos para upload de PDF
5. Gráficos (Vico ou MPAndroidChart)
