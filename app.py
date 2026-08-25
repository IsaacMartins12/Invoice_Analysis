import streamlit as st
import pandas as pd
import json
import pdfplumber
import plotly.express as px
import requests

st.title("📊 Invoice Analysis")

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

uploaded_file = st.file_uploader("Choose your invoice PDF", type="pdf")

if uploaded_file:

    # --- Extract text from PDF ---
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    if not text.strip():
        st.error("Could not extract text from this PDF.")
        st.stop()

    # --- Send to Ollama for transaction extraction ---
    def extract_transactions_with_llm(pdf_text):
        """Use local LLM (Ollama) to extract transactions from invoice text."""

        prompt = f"""You are a financial data extraction assistant. 
Analyze the following credit card invoice text and extract ALL transactions.

Return ONLY a valid JSON array with no additional text. Each transaction must have:
- "date": the transaction date as shown (e.g. "24/03" or "27 JAN")
- "description": the merchant/store name (clean it up, remove city names and codes)
- "amount": the amount as a number (use dot as decimal separator, e.g. 17.45)
- "category": classify into one of these categories:
  - "Transporte" (Uber, 99, rides)
  - "Alimentação" (restaurants, bakeries, food delivery)
  - "Mercado" (supermarkets, grocery stores, mercadinhos)
  - "Telefone/Internet/Streaming" (phone bills, internet, Netflix, etc)
  - "Saúde/Academia" (gyms, clinics, pharmacies)
  - "Compras" (Amazon, Shopee, online/physical stores)
  - "Viagem/Lazer" (flights, tickets, entertainment)
  - "Taxas/Seguros" (IOF, insurance, card fees)
  - "Assinaturas" (recurring subscriptions)
  - "Outros" (anything else)

IMPORTANT RULES:
- Do NOT include payments of previous invoices (e.g. "PAG BOLETO BANCARIO")
- Do NOT include summary lines, totals, or credit lines
- Only include actual purchases/charges
- Return ONLY the JSON array, nothing else

Invoice text:
{pdf_text}"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 4096
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()["response"]

            # Try to extract JSON from the response
            # Sometimes the model wraps it in markdown code blocks
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]

            transactions = json.loads(result.strip())
            return transactions

        except requests.exceptions.ConnectionError:
            st.error(
                "⚠️ Could not connect to Ollama. Make sure it's running!\n\n"
                "Start it with: `ollama serve`"
            )
            return None
        except json.JSONDecodeError as e:
            st.error(f"⚠️ LLM returned invalid JSON. Error: {e}")
            st.expander("Raw LLM response").write(result)
            return None
        except Exception as e:
            st.error(f"⚠️ Error communicating with Ollama: {e}")
            return None

    # --- Display analysis ---
    def display_analysis(transactions):
        """Create DataFrame and display charts/tables."""
        df = pd.DataFrame(transactions)

        # Ensure amount is numeric
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df.dropna(subset=["amount"])
        df = df[df["amount"] > 0]

        if df.empty:
            st.warning("No valid transactions found.")
            return

        # --- Analysis ---
        # Add emoji to categories for display
        emoji_map = {
            "Transporte": "🚗 Transporte",
            "Alimentação": "🍔 Alimentação",
            "Mercado": "🛒 Mercado",
            "Telefone/Internet/Streaming": "📱 Telefone/Internet/Streaming",
            "Saúde/Academia": "💪 Saúde/Academia",
            "Compras": "🛍️ Compras",
            "Viagem/Lazer": "✈️ Viagem/Lazer",
            "Taxas/Seguros": "💳 Taxas/Seguros",
            "Assinaturas": "📋 Assinaturas",
            "Outros": "📦 Outros",
        }
        df["category_display"] = df["category"].map(emoji_map).fillna("📦 Outros")

        spending_by_category = df.groupby("category_display")["amount"].sum().sort_values(ascending=False)
        total_spending = df["amount"].sum()
        percentages = (spending_by_category / total_spending * 100).round(2)

        analysis = pd.DataFrame({
            "total_spent": spending_by_category,
            "percentage": percentages
        })

        # --- Display ---
        st.success(f"✅ {len(df)} transactions extracted successfully!")

        st.subheader("🔎 Spending by Category")
        st.dataframe(analysis)

        st.write(f"💰 **Total spending: R$ {total_spending:.2f}**")

        # Bar chart
        st.subheader("📊 Bar Chart")
        st.bar_chart(analysis["total_spent"])

        # Pie chart
        st.subheader("📊 Pie Chart")
        fig = px.pie(
            analysis,
            values="total_spent",
            names=analysis.index,
            title="Spending Distribution (%)"
        )
        st.plotly_chart(fig)

        # Items by category
        st.subheader("📌 Items by Category")
        for cat, group in df.groupby("category_display"):
            with st.expander(f"{cat} — R$ {group['amount'].sum():.2f} ({len(group)} items)"):
                for _, row in group.iterrows():
                    st.write(f"`{row['date']}` | {row['description']} | **R$ {row['amount']:.2f}**")

    # --- Main flow ---
    with st.spinner("🤖 Analyzing invoice with local AI..."):
        transactions = extract_transactions_with_llm(text)

    if transactions:
        display_analysis(transactions)
