package com.isaac.invoiceanalysis

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.isaac.invoiceanalysis.navigation.AppNavigation
import com.isaac.invoiceanalysis.ui.theme.Gray50
import com.isaac.invoiceanalysis.ui.theme.InvoiceAnalysisTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            InvoiceAnalysisTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Gray50
                ) {
                    AppNavigation()
                }
            }
        }
    }
}
