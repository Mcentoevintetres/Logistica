import streamlit as st
import pandas as pd
import math

# ============================
# CARREGAMENTO DAS PLANILHAS
# ============================

df = pd.read_excel("../assets/Calculo_ES/Porti.xlsx")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

Movimentacao_df = pd.read_excel("../assets/Calculo_ES/Porti.xlsx", sheet_name="Movimentação")

MovimentacaoMeses_df = pd.read_excel("../assets/Calculo_ES/Porti.xlsx", sheet_name="Movimentação_Meses")
MovimentacaoMeses_df = MovimentacaoMeses_df.loc[:, ~MovimentacaoMeses_df.columns.str.contains('^Unnamed')]
MovimentacaoMeses_df.columns = (
    MovimentacaoMeses_df.columns
    .str.strip()
    .str.replace("\n", "")
    .str.title()
)
MovimentacaoMeses_df.columns = MovimentacaoMeses_df.columns.str.strip()

# ============================
# DASHBOARD
# ============================

st.title('Dashboard de Estoque de Segurança')
st.info('Todos os dados abaixo são somente demonstrativos', icon="ℹ️")
st.info('A taxa de serviço utilizada para esse demonstrativo é de 95%', icon="ℹ️")

valor_selecionado = st.selectbox(
    "Selecione um item dos SKUs",
    df["SKU"].unique()
)

st.markdown("## 📦 Dados do Produto Selecionado")

col1, col2 = st.columns(2)

# ============================
# COLUNA 1 - DADOS DO PRODUTO
# ============================

with col1:
    linha_filtrada = df[df["SKU"] == valor_selecionado]

    PrecoUni = linha_filtrada["Preço unit"].values[0]
    produtoSelecionado = linha_filtrada["Descrição"].values[0]
    produtoCategoria = linha_filtrada["Categoria"].values[0]
    VendaMensal = linha_filtrada["Venda Mensal"].values[0]
    VendaMediaDiaria = VendaMensal / 30

    LeadTime_filtrada = Movimentacao_df[Movimentacao_df["SKU"] == valor_selecionado]
    LT = LeadTime_filtrada["Lead time"].values[0]

    st.success(produtoSelecionado)
    st.success(produtoCategoria)
    st.success(f"Valor Unitário do Item: R$ {PrecoUni}")
    st.success(f"Média de Venda Diária: {round(VendaMediaDiaria)} unidades")

# ============================
# COLUNA 2 - ESTOQUE E CÁLCULOS
# ============================

with col2:
    st.success(f"Média de Venda Mensal: {VendaMensal} unidades")
    st.success(f"Tempo médio de reposição (Lead Time): {LT} dias")

    # Estoque de Segurança
    EstoqueSeguranca = 1.65 * (VendaMediaDiaria * math.sqrt(LT))

    # Ponto de Pedido
    PontoPedido = (VendaMediaDiaria * LT) + EstoqueSeguranca

    st.success(f"Estoque de Segurança: {round(EstoqueSeguranca)} unidades")
    st.success(f"Ponto de Pedido: {round(PontoPedido)} unidades")

# ============================
# ANÁLISE MENSAL
# ============================

meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]

Mes_selecionado = st.selectbox(
    "Selecione um mês",
    [col for col in MovimentacaoMeses_df.columns if col in meses]
)

Estoque_filtrada = Movimentacao_df[Movimentacao_df["SKU"] == valor_selecionado]
Estoque_Atual = Estoque_filtrada["Quant Atual"].values[0]

Mes_filtrado = MovimentacaoMeses_df[MovimentacaoMeses_df["Sku"] == valor_selecionado]
Valor_mes = Mes_filtrado[Mes_selecionado].values[0]
valores_mensais = Mes_filtrado[meses].values[0].tolist()

# ============================
# ALERTAS OPERACIONAIS
# ============================

if int(Estoque_Atual) < int(Valor_mes):
    st.error("⚠️ O estoque está abaixo do esperado, risco de ruptura!")

if int(Estoque_Atual) > int(PontoPedido):
    st.warning("⚠️ O estoque está acima do ponto de pedido (possível excesso).")

st.success(f"Vendas de {Mes_selecionado}: {Valor_mes} unidades")

# ============================
# 💰 ANÁLISE ECONÔMICA DO ESTOQUE
# ============================

st.markdown("## 💰 Análise Econômica do Estoque")

# parâmetros econômicos (editáveis futuramente)
taxa_custo_estoque = 0.25  # 25% ao ano
margem_lucro = 0.30        # 30%

# Estoque médio estimado
EstoqueMedio = Estoque_Atual / 2 if Estoque_Atual > 0 else 0

# Custo de manter estoque
CustoManterEstoque = EstoqueMedio * PrecoUni * taxa_custo_estoque

# Demanda não atendida (ruptura)
DemandaNaoAtendida = max(0, Valor_mes - Estoque_Atual)

# Margem unitária
MargemUnitaria = PrecoUni * margem_lucro

# Custo de ruptura
CustoRuptura = DemandaNaoAtendida * MargemUnitaria

# Custo total
CustoTotalEstoque = CustoManterEstoque + CustoRuptura

st.success(f"Custo anual de manter estoque: R$ {CustoManterEstoque:,.2f}")
st.success(f"Custo estimado de ruptura: R$ {CustoRuptura:,.2f}")
st.success(f"Custo total do estoque: R$ {CustoTotalEstoque:,.2f}")

# ============================
# DECISÃO ECONÔMICA AUTOMÁTICA
# ============================

if CustoManterEstoque > CustoRuptura:
    st.warning("📉 Estoque economicamente excessivo (custo de manter > custo de ruptura).")
elif CustoRuptura > CustoManterEstoque:
    st.error("📈 Estoque insuficiente (perda financeira por ruptura).")
else:
    st.success("✅ Nível de estoque próximo do ideal econômico.")

# ============================
# 📊 SIMULAÇÃO DE CENÁRIOS
# ============================

st.markdown("## 📊 Simulação de Cenários de Estoque")

cenarios = {
    "Baixo": EstoqueSeguranca,
    "Ideal": PontoPedido,
    "Atual": Estoque_Atual
}

resultados = []

for nome, estoque in cenarios.items():
    estoque_medio = estoque / 2
    custo_manter = estoque_medio * PrecoUni * taxa_custo_estoque
    ruptura = max(0, Valor_mes - estoque) * MargemUnitaria
    custo_total = custo_manter + ruptura

    resultados.append({
        "Cenário": nome,
        "Estoque (unid)": round(estoque),
        "Custo Manter (R$)": round(custo_manter, 2),
        "Custo Ruptura (R$)": round(ruptura, 2),
        "Custo Total (R$)": round(custo_total, 2)
    })

df_cenarios = pd.DataFrame(resultados)
st.dataframe(df_cenarios, use_container_width=True)

# ============================
# GRÁFICOS
# ============================

AnaliseMensal = pd.DataFrame({
    "Mês": meses,
    "Vendas": valores_mensais
})

AnaliseEstoqueDF = pd.DataFrame(
    {
        "Mês": [Mes_selecionado],
        "Estoque Segurança": [round(EstoqueSeguranca)],
        "Ponto de Pedido": [round(PontoPedido)],
        "Venda Mensal": [Valor_mes],
        "Estoque Atual": [Estoque_Atual]
    }
)

st.bar_chart(
    AnaliseEstoqueDF,
    x="Mês",
    y=["Estoque Segurança", "Ponto de Pedido", "Venda Mensal", "Estoque Atual"],
    stack=False
)

st.line_chart(AnaliseMensal, x="Mês", y="Vendas")
