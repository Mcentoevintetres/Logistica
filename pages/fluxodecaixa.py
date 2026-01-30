import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fluxo de Caixa", layout="wide")


# Funções auxiliares
def card(titulo, valor, bg, borda):
    st.markdown(
        f"""
        <div style="
            padding:18px;
            border-radius:12px;
            margin-bottom:14px;
            background:{bg};
            border-left:6px solid {borda};
            box-shadow:0 4px 10px rgba(0,0,0,0.08);
        ">
            <div style="font-size:14px; color:#334155;">{titulo}</div>
            <div style="font-size:24px; font-weight:700; color:#0f172a;">
                {valor}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def autopct_filtrado(percent):
    return f"{percent:.1f}%" if percent >= 2 else ""


# Leitura dos dados
st.title("📊 Analisador de Fluxo de Caixa")

df = pd.read_excel(
    "./assets/FluxodeCaixa/FluxoCaixa.xlsx",
    sheet_name="FluxoCaixa",
    dtype=str
)

for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

col_meses = [c for c in df.columns if "Mês" in str(c)]
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul"]
df = df.rename(columns=dict(zip(col_meses, meses)))

linha_total_entradas = df[df.iloc[:, 0] == "TOTAL DE ENTRADAS"].index[0]
linha_total_saidas = df[df.iloc[:, 0] == "TOTAL DE SAÍDAS"].index[0]

bloco_entradas = df.iloc[1:linha_total_entradas].copy()
bloco_saidas = df.iloc[linha_total_entradas + 2:linha_total_saidas].copy()

bloco_entradas = bloco_entradas.rename(
    columns={bloco_entradas.columns[0]: "Categoria"}
)
bloco_saidas = bloco_saidas.rename(
    columns={bloco_saidas.columns[0]: "Categoria"}
)

bloco_entradas["Categoria"] = bloco_entradas["Categoria"].astype(str).str.strip()
bloco_saidas["Categoria"] = bloco_saidas["Categoria"].astype(str).str.strip()

# Seleção do mês
mes = st.selectbox("Selecione um mês", meses)
idx = meses.index(mes)

# Cálculos
entradas = bloco_entradas[mes].sum()
saidas = bloco_saidas[mes].sum()
saldo_mes = entradas - saidas

saldo_anterior = 0 if idx == 0 else (
    bloco_entradas[meses[idx - 1]].sum()
    - bloco_saidas[meses[idx - 1]].sum()
)

saldo_acumulado = sum(
    bloco_entradas[m].sum() - bloco_saidas[m].sum()
    for m in meses[:idx + 1]
)

ncg = max(saidas - entradas, 0)

# Cards
col1, col2 = st.columns(2)

with col1:
    card("💰 Entradas", f"R$ {entradas:,.2f}", "#ecfdf5", "#22c55e")
    card("💸 Saídas", f"R$ {saidas:,.2f}", "#fef2f2", "#ef4444")
    card("💹 Saldo do mês", f"R$ {saldo_mes:,.2f}", "#eff6ff", "#3b82f6")

with col2:
    card("📊 Saldo anterior", f"R$ {saldo_anterior:,.2f}", "#f5f3ff", "#8b5cf6")
    card("📈 Saldo acumulado", f"R$ {saldo_acumulado:,.2f}", "#ecfeff", "#06b6d4")
    card("🏦 Necessidade de capital de giro", f"R$ {ncg:,.2f}", "#fff7ed", "#f97316")

# Detalhamento por categoria
st.markdown("---")
st.subheader("🔎 Detalhamento de Entradas e Saídas")

col_e, col_s = st.columns(2)

with col_e:
    st.markdown("### 🟦 Entradas")
    entrada_sel = st.selectbox(
        "Selecione uma entrada",
        bloco_entradas["Categoria"]
    )
    valor_ent = bloco_entradas.loc[
        bloco_entradas["Categoria"] == entrada_sel, mes
    ].values[0]

    card(
        f"Entrada: {entrada_sel}",
        f"R$ {valor_ent:,.2f}",
        "#eff6ff",
        "#2563eb"
    )

with col_s:
    st.markdown("### 🟥 Saídas")
    saida_sel = st.selectbox(
        "Selecione uma saída",
        bloco_saidas["Categoria"]
    )
    valor_sai = bloco_saidas.loc[
        bloco_saidas["Categoria"] == saida_sel, mes
    ].values[0]

    card(
        f"Saída: {saida_sel}",
        f"R$ {valor_sai:,.2f}",
        "#fef2f2",
        "#dc2626"
    )

# Gráficos
tab1, tab2, tab3 = st.tabs(
    ["📊 Entradas vs Saídas", "📈 Evolução do saldo", "🥧 Distribuição (%)"]
)

with tab1:
    st.bar_chart(pd.DataFrame(
        {"Valor": [entradas, saidas]},
        index=["Entradas", "Saídas"]
    ))

with tab2:
    st.line_chart(pd.DataFrame({
        "Saldo": [
            bloco_entradas[m].sum() - bloco_saidas[m].sum()
            for m in meses
        ]
    }, index=meses))

with tab3:
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("### 🟦 Entradas (%)")

        df_pizza_ent = (
            bloco_entradas[["Categoria", mes]]
            .dropna()
            .query(f"`{mes}` > 0")
            .sort_values(by=mes, ascending=False)
        )

        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(
            df_pizza_ent[mes],
            autopct=autopct_filtrado,
            startangle=90,
            pctdistance=0.75
        )
        ax1.axis("equal")
        st.pyplot(fig1)

        st.dataframe(
            df_pizza_ent.assign(
                Percentual=lambda x: (x[mes] / x[mes].sum() * 100).round(2)
            ),
            use_container_width=True
        )

    with col_p2:
        st.markdown("### 🟥 Saídas (%)")

        df_pizza_sai = (
            bloco_saidas[["Categoria", mes]]
            .dropna()
            .query(f"`{mes}` > 0")
            .sort_values(by=mes, ascending=False)
        )

        fig2, ax2 = plt.subplots(figsize=(6, 6))
        ax2.pie(
            df_pizza_sai[mes],
            autopct=autopct_filtrado,
            startangle=90,
            pctdistance=0.75
        )
        ax2.axis("equal")
        st.pyplot(fig2)

        st.dataframe(
            df_pizza_sai.assign(
                Percentual=lambda x: (x[mes] / x[mes].sum() * 100).round(2)
            ),
            use_container_width=True
        )
