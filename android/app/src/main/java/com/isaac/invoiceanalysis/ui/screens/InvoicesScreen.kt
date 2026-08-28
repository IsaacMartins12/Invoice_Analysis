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
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.isaac.invoiceanalysis.data.MockData
import com.isaac.invoiceanalysis.ui.theme.Gray400
import com.isaac.invoiceanalysis.ui.theme.Gray800
import com.isaac.invoiceanalysis.ui.theme.Indigo100
import com.isaac.invoiceanalysis.ui.theme.Indigo600
import com.isaac.invoiceanalysis.ui.theme.Red500

@Composable
fun InvoicesScreen() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("📁 Faturas", fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .background(Indigo600)
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Text("+ Nova", fontSize = 14.sp, color = Color.White, fontWeight = FontWeight.Medium)
            }
        }

        MockData.invoices.forEach { inv ->
            Card(
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.Top
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    "${"%02d".format(inv.month)}/${inv.year}",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = Gray800
                                )
                                inv.bank?.let {
                                    Box(
                                        modifier = Modifier
                                            .padding(start = 8.dp)
                                            .clip(RoundedCornerShape(50))
                                            .background(Indigo100)
                                            .padding(horizontal = 8.dp, vertical = 2.dp)
                                    ) {
                                        Text(it, fontSize = 11.sp, color = Indigo600)
                                    }
                                }
                            }
                            Text(
                                "${inv.fileName} · ${inv.transactionCount} transações",
                                fontSize = 12.sp,
                                color = Gray400,
                                modifier = Modifier.padding(top = 2.dp)
                            )
                        }
                        Text(
                            "R$ ${"%.2f".format(inv.totalAmount)}",
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = Gray800
                        )
                    }
                    HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        Text("Ver detalhes", fontSize = 13.sp, color = Indigo600, fontWeight = FontWeight.Medium)
                        Text("Excluir", fontSize = 13.sp, color = Red500, fontWeight = FontWeight.Medium)
                    }
                }
            }
        }
    }
}
