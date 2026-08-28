package com.isaac.invoiceanalysis.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
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
import com.isaac.invoiceanalysis.data.MockData
import com.isaac.invoiceanalysis.ui.theme.CategoryColors
import com.isaac.invoiceanalysis.ui.theme.Gray200
import com.isaac.invoiceanalysis.ui.theme.Gray500
import com.isaac.invoiceanalysis.ui.theme.Gray800
import com.isaac.invoiceanalysis.ui.theme.Indigo600
import com.isaac.invoiceanalysis.ui.theme.Purple600

@Composable
fun DashboardScreen(onCategoryClick: (String) -> Unit) {
    LazyColumn(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Total card with gradient
        item { TotalCard() }

        // Section title
        item {
            Text(
                text = "Gastos por Categoria",
                fontSize = 18.sp,
                fontWeight = FontWeight.SemiBold,
                color = Gray800
            )
        }

        // Category cards
        itemsIndexed(MockData.categorySummaries) { index, cat ->
            CategoryCard(
                emoji = cat.emoji,
                name = cat.name,
                count = cat.count,
                value = cat.total,
                percentage = ((cat.total / MockData.totalSpending) * 100).toInt(),
                color = CategoryColors[index % CategoryColors.size],
                onClick = { onCategoryClick(cat.name) }
            )
        }
    }
}

@Composable
private fun TotalCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.Transparent)
    ) {
        Box(
            modifier = Modifier
                .background(
                    Brush.horizontalGradient(listOf(Indigo600, Purple600)),
                    RoundedCornerShape(16.dp)
                )
                .padding(24.dp)
                .fillMaxWidth()
        ) {
            Column {
                Text("Total gasto", fontSize = 14.sp, color = Color.White.copy(alpha = 0.8f))
                Text(
                    "R$ ${"%.2f".format(MockData.totalSpending)}",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    "${MockData.transactionCount} transações · ${MockData.categorySummaries.size} categorias",
                    fontSize = 13.sp,
                    color = Color.White.copy(alpha = 0.8f),
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
        }
    }
}

@Composable
private fun CategoryCard(
    emoji: String,
    name: String,
    count: Int,
    value: Double,
    percentage: Int,
    color: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .clip(CircleShape)
                        .background(color.copy(alpha = 0.12f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(emoji, fontSize = 20.sp)
                }
                Column(modifier = Modifier.padding(start = 12.dp)) {
                    Text(name, fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = Gray800)
                    Text("$count transações", fontSize = 12.sp, color = Gray500)
                }
            }

            // Progress bar
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .padding(top = 12.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .background(Gray200)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(percentage / 100f)
                        .height(8.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(color)
                )
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("$percentage%", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = color)
                Text(
                    "R$ ${"%.2f".format(value)}",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = Gray800
                )
            }
        }
    }
}
