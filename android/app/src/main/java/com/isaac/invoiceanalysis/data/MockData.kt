package com.isaac.invoiceanalysis.data

/**
 * Mock data models and sample data for UI development.
 * These will be replaced by real API models later.
 */

data class Transaction(
    val id: Int,
    val date: String,
    val description: String,
    val amount: Double,
    val category: String,
    val invoiceMonth: Int,
    val invoiceYear: Int,
    val invoiceBank: String?,
)

data class CategorySummary(
    val name: String,
    val emoji: String,
    val total: Double,
    val count: Int,
)

data class InvoiceItem(
    val id: Int,
    val bank: String?,
    val month: Int,
    val year: Int,
    val fileName: String,
    val totalAmount: Double,
    val transactionCount: Int,
)

data class Category(
    val id: Int?,
    val name: String,
    val emoji: String,
    val isDefault: Boolean,
)

object MockData {

    val categoryEmojis = mapOf(
        "Transporte" to "🚗",
        "Alimentação" to "🍔",
        "Mercado" to "🛒",
        "Telefone/Internet/Streaming" to "📱",
        "Saúde/Academia" to "💪",
        "Compras" to "🛍️",
        "Viagem/Lazer" to "✈️",
        "Taxas/Seguros" to "💳",
        "Assinaturas" to "📋",
        "Outros" to "📦",
    )

    val totalSpending = 2222.43
    val transactionCount = 63

    val categorySummaries = listOf(
        CategorySummary("Viagem/Lazer", "✈️", 593.04, 5),
        CategorySummary("Transporte", "🚗", 437.73, 30),
        CategorySummary("Alimentação", "🍔", 428.71, 8),
        CategorySummary("Saúde/Academia", "💪", 248.99, 2),
        CategorySummary("Compras", "🛍️", 169.19, 6),
        CategorySummary("Mercado", "🛒", 108.90, 8),
        CategorySummary("Telefone/Internet/Streaming", "📱", 82.56, 3),
        CategorySummary("Taxas/Seguros", "💳", 10.31, 1),
    )

    val monthlyEvolution = listOf(
        "01" to 1850.20,
        "02" to 2100.50,
        "03" to 1980.75,
        "04" to 2222.43,
    )

    val transactions = listOf(
        Transaction(1, "24/03", "MERCADINHO GR MANAUS", 8.00, "Mercado", 4, 2026, "Bradesco"),
        Transaction(2, "24/03", "DL*UberRides Sao Paulo", 7.92, "Transporte", 4, 2026, "Bradesco"),
        Transaction(3, "14/01", "Tkt Aer*LATAM AIRLIN", 346.48, "Viagem/Lazer", 4, 2026, "Bradesco"),
        Transaction(4, "09/01", "SHOPEE *TRADENOECOME", 26.45, "Compras", 4, 2026, "Bradesco"),
        Transaction(5, "28/03", "TIM*92981651778", 60.99, "Telefone/Internet/Streaming", 4, 2026, "Bradesco"),
        Transaction(6, "11/04", "Wellhub ISAAC DAVI", 149.99, "Saúde/Academia", 4, 2026, "Bradesco"),
        Transaction(7, "27/02", "CLINICA*J A ODONT", 99.00, "Saúde/Academia", 4, 2026, "Bradesco"),
        Transaction(8, "31/03", "BOLO FIT CARLA RE", 150.99, "Alimentação", 4, 2026, "Bradesco"),
        Transaction(9, "21/04", "EBN *CRUNCHYROLL", 19.90, "Telefone/Internet/Streaming", 4, 2026, "Bradesco"),
        Transaction(10, "20/04", "SEGURO SUPERPROTEGIDO", 9.99, "Taxas/Seguros", 4, 2026, "Bradesco"),
    )

    val invoices = listOf(
        InvoiceItem(1, "Bradesco", 4, 2026, "Bradesco_Fatura.pdf", 2222.43, 63),
        InvoiceItem(2, "Nubank", 3, 2026, "Nubank_2026-03-03.pdf", 422.89, 25),
    )

    val categories = listOf(
        Category(null, "Transporte", "🚗", true),
        Category(null, "Alimentação", "🍔", true),
        Category(null, "Mercado", "🛒", true),
        Category(null, "Telefone/Internet/Streaming", "📱", true),
        Category(null, "Saúde/Academia", "💪", true),
        Category(null, "Compras", "🛍️", true),
        Category(null, "Viagem/Lazer", "✈️", true),
        Category(null, "Taxas/Seguros", "💳", true),
        Category(null, "Assinaturas", "📋", true),
        Category(null, "Outros", "📦", true),
        Category(1, "Pets", "🐶", false),
    )
}
