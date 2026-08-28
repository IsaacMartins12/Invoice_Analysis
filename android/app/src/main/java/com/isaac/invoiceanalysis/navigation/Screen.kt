package com.isaac.invoiceanalysis.navigation

sealed class Screen(val route: String, val label: String, val icon: String) {
    data object Dashboard : Screen("dashboard", "Home", "📊")
    data object Transactions : Screen("transactions", "Gastos", "💰")
    data object Receipts : Screen("receipts", "Mercado", "🛒")
    data object Upload : Screen("upload", "Upload", "📤")
    data object Invoices : Screen("invoices", "Faturas", "📁")

    // Detail screens (not in bottom nav)
    data object CategoryDetail : Screen("category/{name}", "Categoria", "")
    data object Categories : Screen("categories", "Categorias", "🏷️")
    data object Login : Screen("login", "Login", "")

    companion object {
        val bottomNavItems = listOf(Dashboard, Transactions, Receipts, Upload, Invoices)
    }
}
