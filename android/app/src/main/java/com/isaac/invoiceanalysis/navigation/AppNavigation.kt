package com.isaac.invoiceanalysis.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.isaac.invoiceanalysis.ui.components.BottomNavBar
import com.isaac.invoiceanalysis.ui.components.TopBar
import com.isaac.invoiceanalysis.ui.screens.CategoriesScreen
import com.isaac.invoiceanalysis.ui.screens.CategoryDetailScreen
import com.isaac.invoiceanalysis.ui.screens.DashboardScreen
import com.isaac.invoiceanalysis.ui.screens.InvoicesScreen
import com.isaac.invoiceanalysis.ui.screens.ReceiptsScreen
import com.isaac.invoiceanalysis.ui.screens.TransactionsScreen
import com.isaac.invoiceanalysis.ui.screens.UploadScreen

@Composable
fun AppNavigation(navController: NavHostController = rememberNavController()) {
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    val showBottomBar = Screen.bottomNavItems.any { it.route == currentRoute }

    Scaffold(
        topBar = { TopBar() },
        bottomBar = {
            if (showBottomBar) {
                BottomNavBar(
                    currentRoute = currentRoute,
                    onNavigate = { route ->
                        navController.navigate(route) {
                            popUpTo(Screen.Dashboard.route) { saveState = true }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                )
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Dashboard.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Dashboard.route) {
                DashboardScreen(
                    onCategoryClick = { name ->
                        navController.navigate("category/$name")
                    }
                )
            }
            composable(Screen.Transactions.route) {
                TransactionsScreen(
                    onManageCategories = { navController.navigate(Screen.Categories.route) }
                )
            }
            composable(Screen.Receipts.route) { ReceiptsScreen() }
            composable(Screen.Upload.route) { UploadScreen() }
            composable(Screen.Invoices.route) { InvoicesScreen() }
            composable(Screen.Categories.route) {
                CategoriesScreen(onBack = { navController.popBackStack() })
            }
            composable(Screen.CategoryDetail.route) { entry ->
                val name = entry.arguments?.getString("name") ?: ""
                CategoryDetailScreen(
                    categoryName = name,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
