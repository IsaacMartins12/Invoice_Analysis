import streamlit as st
import pandas as pd
import re
import pdfplumber

st.title("📊 Invoice Analysis")

uploaded_file = st.file_uploader("Choose your invoice PDF", type="pdf")

if uploaded_file:
    
    def extract(text):
        # Bradesco pattern
        pattern = re.compile(r"(\d{2}/\d{2})\s+(.+?)\s+(\d+,\d{2})")
        # Nubank pattern
        # pattern = re.compile(r"(\d{2}\s\w{3})\s+(.+?)\s+R\$ (\d+,\d{2})")
       
        transactions = []
        for date, description, amount in pattern.findall(text):
            description_upper = description.strip().upper()
            # Filter unwanted words
            if any(word in description_upper for word in ["FATURA", "BOLETO", "BANCARIO"]):
                continue  # skip this line
            transactions.append({
                "date": date,
                "description": description.strip(),
                "amount": amount
            })
        return transactions


    # --- Function to create DataFrame ---
    def create_dataframe(processed_data):
        print(processed_data)
        df = pd.DataFrame(processed_data)
        df["amount"] = df["amount"].str.replace(",", ".").astype(float)

        def categorize(desc):
            desc = desc.upper()
            if any(x in desc for x in ["99 TECNOLOGIA","99","99*", "UBER"]):
                return "Transport"
            elif "BEMOL" in desc:
                return "Bemol"
            elif any(x in desc for x in ["SUPERMARKET","PHARMACY"]):
                return "Grocery"
            elif any(x in desc for x in ["TIM","CLARO","VIVO"]):
                return "Phone/Internet"
            else:
                return "Others"

        df["category"] = df["description"].apply(categorize)

        # --- Analysis ---
        spending_by_category = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        total_spending = df["amount"].sum()
        percentages = (spending_by_category / total_spending * 100).round(2)

        analysis = pd.DataFrame({
            "total_spent": spending_by_category,
            "percentage": percentages
        })

        # Display tables in Streamlit
        st.subheader("🔎 Spending by Category")
        st.dataframe(analysis)

        st.write(f"💰 Total spending: R$ {total_spending:.2f}")

        # --- Charts ---
        st.subheader("📊 Bar Chart")
        st.bar_chart(analysis["total_spent"])

        st.subheader("📊 Pie Chart")
        import plotly.express as px
        fig = px.pie(analysis, values="total_spent", names=analysis.index, title="Spending Distribution (%)")
        st.plotly_chart(fig)

        # Show items for each category
        st.subheader("📌 Items by Category")
        for cat, group in df.groupby("category"):
            st.markdown(f"**{cat} (R$ {group['amount'].sum():.2f})**")
            for _, row in group.iterrows():
                st.write(f"{row['date']} | {row['description']} | R$ {row['amount']:.2f}")

    # Extract text from PDF
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
             text += page.extract_text() + "\n"
    # Run functions
    processed_lines = extract(text)
    create_dataframe(processed_lines)
