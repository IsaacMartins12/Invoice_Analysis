package com.isaac.invoiceanalysis.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.isaac.invoiceanalysis.ui.theme.Gray400
import com.isaac.invoiceanalysis.ui.theme.Gray800
import com.isaac.invoiceanalysis.ui.theme.Green600

// Mock receipt data local to this screen
private data class ReceiptRow(val store: String, val date: String, val total: Double, val items: Int)

private val mockReceipts = listOf(
    ReceiptRow("Supermercado Baratão", "15/04/2026", 187.45, 12),
    ReceiptRow("Farmácia Pague Menos", "12/04/2026", 45.90, 3),
)

@Composable
fun ReceiptsScreen() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("🛒 Mercado", fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .background(Green600)
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Text("+ Escanear", fontSize = 14.sp, color = Color.White, fontWeight = FontWeight.Medium)
            }
        }

        // Summary card with gradient
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(
                    Brush.horizontalGradient(listOf(Green600, Color(0xFF059669)))
                )
                .padding(20.dp)
        ) {
            Column {
                Text("Total gasto em mercado", fontSize = 14.sp, color = Color.White.copy(alpha = 0.8f))
                Text(
                    "R$ 233.35",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    "2 notas · 15 itens",
                    fontSize = 13.sp,
                    color = Color.White.copy(alpha = 0.8f),
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }

        // Receipt list
        mockReceipts.forEach { r ->
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(r.store, fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = Gray800)
                        Text("${r.date} · ${r.items} itens", fontSize = 12.sp, color = Gray400)
                    }
                    Text(
                        "R$ ${"%.2f".format(r.total)}",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = Gray800
                    )
                }
            }
        }
    }
}
