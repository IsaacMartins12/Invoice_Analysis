package com.isaac.invoiceanalysis.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.isaac.invoiceanalysis.ui.theme.Gray200
import com.isaac.invoiceanalysis.ui.theme.Gray400
import com.isaac.invoiceanalysis.ui.theme.Gray700
import com.isaac.invoiceanalysis.ui.theme.Indigo600

@Composable
fun UploadScreen() {
    var bank by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("📤 Upload de Fatura", fontSize = 22.sp, fontWeight = FontWeight.Bold)

        Card(
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text("Arquivo PDF", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Gray700)

                // File picker placeholder
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(100.dp)
                        .border(1.dp, Gray200, RoundedCornerShape(8.dp))
                        .background(Color(0xFFF9FAFB), RoundedCornerShape(8.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("📄", fontSize = 28.sp)
                        Text(
                            "Toque para selecionar o PDF",
                            fontSize = 13.sp,
                            color = Gray400,
                            modifier = Modifier.padding(top = 4.dp)
                        )
                    }
                }

                Text(
                    "Banco (opcional)",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = Gray700
                )
                OutlinedTextField(
                    value = bank,
                    onValueChange = { bank = it },
                    placeholder = { Text("Ex: Bradesco, Nubank, Inter...") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )

                Text(
                    "O mês e ano serão detectados automaticamente da fatura.",
                    fontSize = 12.sp,
                    color = Gray400
                )

                Button(
                    onClick = { },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Indigo600)
                ) {
                    Text("Enviar Fatura", fontSize = 15.sp)
                }
            }
        }
    }
}
