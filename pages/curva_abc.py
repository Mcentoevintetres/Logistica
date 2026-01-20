import streamlit as st
import pandas as pd

# ==========================
# LEITURA DA PLANILHA
# ==========================
df = pd.read_excel("./assets/classificacao_abc/Porti.xlsx", sheet_name="Planilha_Vendas")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

st.header("Dashboard de Agrupamento por Curva ABC")
st.info("Essa apresentação tem como intuito demonstrar a performance de vendas de alguns itens durante um intervalo de tempo, agrupando eles pelo seu percentual de vendas sobre o valor total.")

# ==========================
# PRÉ-PROCESSAMENTO
# ==========================

df["Valor Uni"] = pd.to_numeric(df["Valor Uni"], errors="coerce")
df["Quant Vendida"] = pd.to_numeric(df["Quant Vendida"], errors="coerce")

df["Valor Total"] = df["Quant Vendida"] * df["Valor Uni"]
valor_total_geral = df["Valor Total"].sum()

df["%Vi"] = df["Valor Total"] / valor_total_geral * 100
df["%Vi_str"] = df["%Vi"].apply(lambda x: f"{x:.2f}%".replace(".", ","))

df = df.sort_values(by="%Vi", ascending=False).reset_index(drop=True)
df["%Acumulado"] = df["%Vi"].cumsum()

def classificar(p):
    if p <= 80:
        return "A"
    elif p <= 95:
        return "B"
    else:
        return "C"

df["Classe"] = df["%Acumulado"].apply(classificar)

ABC_final = df[["Descrição", "%Vi_str", "Classe"]]

# ==========================
# RESUMO POR CLASSE
# ==========================
resumo = df.groupby("Classe")["%Vi"].sum().reset_index()
valor_por_classe = df.groupby("Classe")["Valor Total"].sum().reset_index()

valor_A = valor_por_classe.loc[valor_por_classe["Classe"] == "A", "Valor Total"].sum()
valor_B = valor_por_classe.loc[valor_por_classe["Classe"] == "B", "Valor Total"].sum()
valor_C = valor_por_classe.loc[valor_por_classe["Classe"] == "C", "Valor Total"].sum()

# ==========================
# 🔥 INSIGHT DINÂMICO ABC
# ==========================
st.subheader("📌 Insight da Curva ABC")

# ==========================
# VISÃO GERAL DE FATURAMENTO
# ==========================

st.success(f"Valor total vendido: R${valor_total_geral:,.2f}")

col1, col2 = st.columns(2)

with col1:
    st.success(f"Classe A: R${valor_A:,.2f}")
    st.warning(f"Classe B: R${valor_B:,.2f}")
    st.error(f"Classe C: R${valor_C:,.2f}")

with col2:
    st.bar_chart(resumo, x="Classe", y=["%Vi"], horizontal=True)

# ==========================
# 📌 TABELA FINAL — Insight agora está ACIMA daqui
# ==========================
df["Classe"] = df["Classe"].astype(str)

# --- 🔧 Correção do selectbox ---
mapa_classes = {
    "Classe A": "A",
    "Classe B": "B",
    "Classe C": "C"
}

label_escolhido = st.selectbox(
    "Selecione a classe para analisar:",
    list(mapa_classes.keys())
)

classe_escolhida = mapa_classes[label_escolhido]
# --------------------------------

df_classe = df[df["Classe"] == classe_escolhida]

total_skus = len(df)
skus_classe = len(df_classe)
perc_skus = (skus_classe / total_skus) * 100

valor_total_classe = df_classe["Valor Total"].sum()
perc_faturamento = (valor_total_classe / valor_total_geral) * 100

st.success(
    f"📊 Na {label_escolhido}, identificamos que "
    f"**{perc_skus:.1f}%** dos SKUs representam "
    f"**{perc_faturamento:.1f}%** do faturamento total."
)

st.dataframe(ABC_final)

# ==========================
# TABS DE GRUPOS A/B/C
# ==========================

tab1, tab2, tab3 = st.tabs(["Grupo A", "Grupo B", "Grupo C"])

Grupo_A = df[df["Classe"] == "A"][["SKU", "%Vi_str"]]
Grupo_B = df[df["Classe"] == "B"][["SKU", "%Vi_str"]]
Grupo_C = df[df["Classe"] == "C"][["SKU", "%Vi_str"]]

with tab1:
    st.bar_chart(Grupo_A, x="%Vi_str", y="SKU")
with tab2:
    st.bar_chart(Grupo_B, x="%Vi_str", y="SKU")
with tab3:
    st.bar_chart(Grupo_C, x="%Vi_str", y="SKU")
