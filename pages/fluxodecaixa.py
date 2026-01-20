import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fluxo de Caixa", layout="wide")

# ================================
# Função de card colorido
# ================================
def card(texto, cor):
    st.markdown(
        f"""
        <div style="
            padding:12px;
            border-radius:8px;
            margin-bottom:10px;
            background-color:{cor};
            color:white;
            font-size:18px;
            font-weight:600;">
            {texto}
        </div>
        """,
        unsafe_allow_html=True
    )

# ================================
# Código principal
# ================================
st.title("📊 Analisador de Fluxo de Caixa")

# Leitura direta da planilha (CORRIGIDO → texto 100% fiel ao Excel)
df = pd.read_excel(
    "./assets/FluxodeCaixa/FluxoCaixa.xlsx",
    sheet_name="FluxoCaixa",
    dtype=str    # ← garante texto exatamente como no arquivo
)

# Converter colunas numéricas após leitura segura
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Renomear colunas
col_meses = [c for c in df.columns if "Mês" in str(c)]
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul"]

colmap = {old: new for old, new in zip(col_meses, meses)}
df = df.rename(columns=colmap)

# Identificar blocos
linha_total_entradas = df[df.iloc[:, 0] == "TOTAL DE ENTRADAS"].index[0]
linha_total_saidas = df[df.iloc[:, 0] == "TOTAL DE SAÍDAS"].index[0]

# Blocos
bloco_entradas = df.iloc[1:linha_total_entradas].copy()
bloco_saidas = df.iloc[linha_total_entradas + 2:linha_total_saidas].copy()

# Renomear primeira coluna
bloco_entradas = bloco_entradas.rename(columns={bloco_entradas.columns[0]: "Categoria"})
bloco_saidas = bloco_saidas.rename(columns={bloco_saidas.columns[0]: "Categoria"})

# CORREÇÃO → apenas strip
bloco_entradas["Categoria"] = bloco_entradas["Categoria"].astype(str).str.strip()
bloco_saidas["Categoria"] = bloco_saidas["Categoria"].astype(str).str.strip()

# Selectbox do mês
mes = st.selectbox("Selecione um mês", meses)

# Cálculos principais
entradas = bloco_entradas[mes].sum()
saidas = bloco_saidas[mes].sum()
saldo_mes = entradas - saidas

idx = meses.index(mes)

# Saldo anterior
if idx == 0:
    saldo_anterior = 0
else:
    m_ant = meses[idx - 1]
    saldo_anterior = bloco_entradas[m_ant].sum() - bloco_saidas[m_ant].sum()

# Saldo acumulado
saldo_acumulado = 0
for m in meses[:idx + 1]:
    saldo_acumulado += bloco_entradas[m].sum() - bloco_saidas[m].sum()

# NCG
ncg = max(saidas - entradas, 0)

# Indicador
if entradas > saidas:
    indicador = ("🟢 Situação saudável", "#1B8E5A")
elif entradas == saidas:
    indicador = ("🟡 Equilíbrio financeiro", "#b59f00")
else:
    indicador = ("🔴 Risco — Saídas maiores que entradas", "#a83232")


# EXIBIR CARDS

col1, col2 = st.columns(2)
with col1:
    card(f"💰 Entradas: R$ {entradas:,.2f}", "#14532d")
    card(f"💸 Saídas: R$ {saidas:,.2f}", "#f10c0c")
    card(f"💹 Saldo: R$ {saldo_mes:,.2f}", "#1e3a8a")

with col2:
    card(f"📊 Saldo anterior: R$ {saldo_anterior:,.2f}", "#3b0764")
    card(f"📈 Saldo acumulado: R$ {saldo_acumulado:,.2f}", "#25cf41")
    card(f"🏦 Necessidade de capital de giro: R$ {ncg:,.2f}", "#f10c0c")

card(f"{indicador[0]}", indicador[1])

# SELECTBOX DE ENTRADAS E SAÍDAS

st.markdown("---")
st.subheader("🔎 Detalhamento de Entradas e Saídas")

col_e, col_s = st.columns(2)

# ====== ENTRADAS ======
with col_e:
    st.markdown("### 🟦 Entradas")

    # Cria coluna de texto totalmente normalizada para comparação
    bloco_entradas["Categoria_norm"] = (
        bloco_entradas["Categoria"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.normalize("NFKC")
    )

    lista_entradas = bloco_entradas["Categoria_norm"].tolist()

    entrada_sel = st.selectbox("Selecione uma entrada", lista_entradas)

    linha = bloco_entradas.loc[bloco_entradas["Categoria_norm"] == entrada_sel]

    if linha.empty:
        card("⚠️ Erro: Categoria não encontrada. Texto inconsistente no Excel.", "#660000")
    else:
        valor_ent = linha[mes].values[0]
        card(f"Valor da entrada {entrada_sel}: R$ {valor_ent:,.2f}", "#003366")

# ====== SAÍDAS ======
with col_s:
    st.markdown("### 🟥 Saídas")

    bloco_saidas["Categoria_norm"] = (
        bloco_saidas["Categoria"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.normalize("NFKC")
    )

    lista_saidas = bloco_saidas["Categoria_norm"].tolist()

    saida_sel = st.selectbox("Selecione uma saída", lista_saidas)

    linha = bloco_saidas.loc[bloco_saidas["Categoria_norm"] == saida_sel]

    if linha.empty:
        card("⚠️ Erro: Categoria não encontrada. Texto inconsistente no Excel.", "#660000")
    else:
        valor_sai = linha[mes].values[0]
        card(f"Valor da saída {saida_sel}: R$ {valor_sai:,.2f}", "#660000")


# GRÁFICOS

df_barras = pd.DataFrame(
    {"Valor": [entradas, saidas]},
    index=["Entradas", "Saídas"],
)

df_saldo = pd.DataFrame({
    "Saldo": [
        bloco_entradas[m].sum() - bloco_saidas[m].sum()
        for m in meses
    ]
}, index=meses)

tab1, tab2 = st.tabs(["📊 Entradas vs Saídas", "📈 Evolução do saldo"])
with tab1:
    st.bar_chart(df_barras)
with tab2:
    st.line_chart(df_saldo)
