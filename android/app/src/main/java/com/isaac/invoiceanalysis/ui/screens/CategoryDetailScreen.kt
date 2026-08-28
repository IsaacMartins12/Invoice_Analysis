package com.isaac.invoiceanalysis.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.isaac.invoiceanalysis.data.MockData
import com.isaac.invoiceanalysis.ui.theme.Gray400
import com.isaac.invoiceanalysis.ui.theme.Gray700
import com.isaac.invoiceanalysis.ui.theme.Gray800
import com.isaac.invoiceanalysis.ui.theme.Indigo600

@Composable
fun CategoryDetailScreen(categoryName: String, onBack: () -> Unit) {
    val transactions = MockData.transactions.filter { it.category == categoryName }
    val total = transactions.sumOf { it.amount }
    val emoji = MockData.categoryEmojis[categoryName] ?: "📦"

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            "← Voltar",
            fontSize = 14.sp,
            color = Indigo600,
            modifier = Modifier.clickable { onBack() }
        )

        // Header card
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(emoji, fontSize = 28.sp)
                    Column(modifier = Modifier.padding(start = 12.dp)) {
                        Text(categoryName, fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Gray800)
                        Text("${transactions.size} transações", fontSize = 13.sp, color = Gray400)
                    }
                }
                Text(
                    "R$ ${"%.2f".format(total)}",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Indigo600,
                    modifier = Modifier.padding(top = 12.dp)
                )
            }
        }

        // Transactions
        Card(
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
        ) {
            Column {
                transactions.forEachIndexed { index, txn ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(txn.description, fontSize = 14.sp, color = Gray800, maxLines = 1)
                            Text(
                                "${txn.date} · ${txn.invoiceBank ?: "—"}",
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
                    if (index < transactions.size - 1) HorizontalDivider()
                }
            }
        }
    }
}
