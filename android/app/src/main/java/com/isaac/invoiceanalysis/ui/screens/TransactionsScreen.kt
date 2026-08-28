package com.isaac.invoiceanalysis.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.isaac.invoiceanalysis.data.MockData
import com.isaac.invoiceanalysis.ui.theme.Gray100
import com.isaac.invoiceanalysis.ui.theme.Gray200
import com.isaac.invoiceanalysis.ui.theme.Gray400
import com.isaac.invoiceanalysis.ui.theme.Gray500
import com.isaac.invoiceanalysis.ui.theme.Gray800
import com.isaac.invoiceanalysis.ui.theme.Indigo100
import com.isaac.invoiceanalysis.ui.theme.Indigo600

@Composable
fun TransactionsScreen(onManageCategories: () -> Unit) {
    var search by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf<String?>(null) }

    val filtered = MockData.transactions.filter { txn ->
        (selectedCategory == null || txn.category == selectedCategory) &&
        (search.isBlank() || txn.description.contains(search, ignoreCase = true))
    }
    val total = filtered.sumOf { it.amount }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("💰 Todas as Transações", fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .background(Indigo100)
                    .clickable { onManageCategories() }
                    .padding(horizontal = 12.dp, vertical = 8.dp)
            ) {
                Text("🏷️ Categorias", fontSize = 12.sp, color = Indigo600, fontWeight = FontWeight.Medium)
            }
        }

        // Filters card
        Card(
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = search,
                    onValueChange = { search = it },
                    placeholder = { Text("Buscar por descrição...") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )

                // Category chips
                Row(
                    modifier = Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    FilterChip("Todas", selectedCategory == null) { selectedCategory = null }
                    MockData.categorySummaries.forEach { cat ->
                        FilterChip(
                            "${cat.emoji} ${cat.name}",
                            selectedCategory == cat.name
                        ) { selectedCategory = cat.name }
                    }
                }
            }
        }

        // Summary
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("${filtered.size} transações", fontSize = 14.sp, color = Gray500)
            Text(
                "Total: R$ ${"%.2f".format(total)}",
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                color = Indigo600
            )
        }

        // Transaction list
        Card(
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
        ) {
            Column {
                filtered.forEach { txn ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            MockData.categoryEmojis[txn.category] ?: "📦",
                            fontSize = 18.sp
                        )
                        Column(modifier = Modifier.padding(start = 12.dp).weight(1f)) {
                            Text(txn.description, fontSize = 14.sp, color = Gray800, maxLines = 1)
                            Text(
                                "${txn.date} · ${txn.invoiceBank ?: "—"} · ${
                                    "%02d".format(txn.invoiceMonth)
                                }/${txn.invoiceYear}",
                                fontSize = 12.sp,
                                color = Gray400
                            )
                        }
                        Text(
                            "R$ ${"%.2f".format(txn.amount)}",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = Gray800
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun FilterChip(label: String, selected: Boolean, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(50))
            .background(if (selected) Indigo600 else Gray100)
            .clickable { onClick() }
            .padding(horizontal = 12.dp, vertical = 6.dp)
    ) {
        Text(
            label,
            fontSize = 12.sp,
            color = if (selected) Color.White else Gray500,
            fontWeight = FontWeight.Medium
        )
    }
}
