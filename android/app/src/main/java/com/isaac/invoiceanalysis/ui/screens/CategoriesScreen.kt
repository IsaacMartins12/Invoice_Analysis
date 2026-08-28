package com.isaac.invoiceanalysis.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import com.isaac.invoiceanalysis.ui.theme.Indigo600
import com.isaac.invoiceanalysis.ui.theme.Red500

@Composable
fun CategoriesScreen(onBack: () -> Unit) {
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

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("🏷️ Categorias", fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .background(Indigo600)
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Text("+ Nova", fontSize = 14.sp, color = Color.White, fontWeight = FontWeight.Medium)
            }
        }

        Card(
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
        ) {
            Column {
                MockData.categories.forEachIndexed { index, cat ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(cat.emoji, fontSize = 20.sp)
                            Column(modifier = Modifier.padding(start = 12.dp)) {
                                Text(cat.name, fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Gray800)
                                if (cat.isDefault) {
                                    Text("Padrão", fontSize = 11.sp, color = Gray400)
                                }
                            }
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Text("Editar", fontSize = 12.sp, color = Indigo600)
                            if (!cat.isDefault) {
                                Text("Excluir", fontSize = 12.sp, color = Red500)
                            }
                        }
                    }
                    if (index < MockData.categories.size - 1) {
                        HorizontalDivider()
                    }
                }
            }
        }
    }
}
