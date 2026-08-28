package com.isaac.invoiceanalysis.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.isaac.invoiceanalysis.navigation.Screen
import com.isaac.invoiceanalysis.ui.theme.Gray400
import com.isaac.invoiceanalysis.ui.theme.Indigo600
import com.isaac.invoiceanalysis.ui.theme.Red500

@Composable
fun TopBar() {
    Surface(shadowElevation = 2.dp, color = Color.White) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "📊 Invoice",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Indigo600
            )
            Text(
                text = "Sair",
                fontSize = 14.sp,
                color = Red500
            )
        }
    }
}

@Composable
fun BottomNavBar(
    currentRoute: String?,
    onNavigate: (String) -> Unit
) {
    Surface(shadowElevation = 8.dp, color = Color.White) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceAround
        ) {
            Screen.bottomNavItems.forEach { item ->
                val selected = currentRoute == item.route
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier
                        .clickable { onNavigate(item.route) }
                        .padding(horizontal = 12.dp, vertical = 4.dp)
                ) {
                    Text(text = item.icon, fontSize = 20.sp)
                    Text(
                        text = item.label,
                        fontSize = 11.sp,
                        color = if (selected) Indigo600 else Gray400,
                        fontWeight = if (selected) FontWeight.Medium else FontWeight.Normal
                    )
                }
            }
        }
    }
}
