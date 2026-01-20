import streamlit as st
import pandas as pd
import math

#Carregamento da Planilha
df = pd.read_excel("Porti.xlsx")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

#Escolhendo a Tabela especifica de quantidade e fornecimento do estoque
Movimentacao_df = pd.read_excel("Porti.xlsx", sheet_name="Movimentação")

#Escolhendo a tabela da movimentação de venda por item
MovimentacaoMeses_df = pd.read_excel("Porti.xlsx", sheet_name="Movimentação_Meses")
MovimentacaoMeses_df = MovimentacaoMeses_df.loc[:, ~MovimentacaoMeses_df.columns.str.contains('^Unnamed')]
MovimentacaoMeses_df.columns = (
    MovimentacaoMeses_df.columns
    .str.strip()
    .str.replace("\n", "")
    .str.title()
)
#Transformando as colunas em strings sem espaços
MovimentacaoMeses_df.columns = MovimentacaoMeses_df.columns.str.strip()

#PEgando o lead time de cada fornecedor
Ld = Movimentacao_df["Lead time"].unique()


#titulo e header do Dashboard demonstrativo 
st.title('Olá, esse será nosso primeiro Dashboard')
st.write('texto simples.')
st.info('Todos os dados abaixo são somente demonstrativos', icon="ℹ️")
valor_selecionado = st.selectbox(
        "Selecione Um item dos SKUS",
     df["SKU"].unique()
    )
st.markdown("Dados da linha selecionada:")
 # Selectbox com valores únicos dos SKUS
col1, col2 = st.columns(2)

#Divisão em duas colunas, onde na primeira temos a seleção e retorno do item desejado
with col1:
    #conferindo o valor selecionado está na planilha.
    linha_filtrada = df[df["SKU"] == valor_selecionado]
    #buscando preço do item filtrado
    PrecoUni = linha_filtrada["Preço unit"].values[0]
    #buscando o lead time do item filtrado
    LeadTime_filtrada = Movimentacao_df[Movimentacao_df["SKU"] == valor_selecionado]
    LT = LeadTime_filtrada["Lead time"].values[0]
    #selecionando o nome do item filtrado
    produtoSelecionado = linha_filtrada["Descrição"].values[0]
    #Selecionado a categoria do item filtrado
    produtoCategoria = linha_filtrada["Categoria"].values[0]
    #Selecionando o valor de vendal mensal do item
    VendaMensal = linha_filtrada["Venda Mensal"].values[0]
    #calculo da venda media diaria do item
    VendaMediaDiaria = VendaMensal/30
    #Exposição dos valores filtrados acima
    st.success(produtoSelecionado)
    st.success(produtoCategoria)
    st.success(f"Valor Unitario do Item: R${PrecoUni}")
    st.success(f"Média  Venda Diaria: {round(VendaMediaDiaria)} unidades.")

#A segunda coluna nos fornece os valores relacionados ao estoque,preço e movimentação desse produto
with col2:

    #preço do item filtrado
    PrecoUni = linha_filtrada["Preço unit"].values[0]
    #expondo os valores filtrados acima
    st.success(f"Média Venda Mensal: {VendaMensal} unidades.")
    st.success(f"Tempo médio de reposição: {LT} dias.")

    #calculo do estoque de segurança
    EstoqueSegurança = 1.645 * ( VendaMediaDiaria * math.sqrt(LT) )
    #Calculo do ponto de pedido
    PontoPedido = (VendaMediaDiaria * LT) + EstoqueSegurança
    math.floor(PontoPedido)
    st.success(f"O Estoque de Segurança é: {round(EstoqueSegurança)}")
    st.success(f"O ponto de pedido é: {round(PontoPedido)}")

#Array que retorna uma lista com um periodo anul especifico
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
#Seleção e conferencia se o mês selecionado está na planilha
Mes_selecionado = st.selectbox(
        "Selecione Um item dos meses",
        [col for col in MovimentacaoMeses_df.columns if col in meses]
     
    )

#Busca o Estoque atual
Estoque_filtrada = Movimentacao_df[Movimentacao_df["SKU"] == valor_selecionado]
Estoque_Atual = Estoque_filtrada["Quant Atual"].values[0]
Mes_filtrado = MovimentacaoMeses_df[MovimentacaoMeses_df["Sku"] == valor_selecionado]
Valor_mes = Mes_filtrado[Mes_selecionado].values[0]
valores_mensais = Mes_filtrado[meses].values[0].tolist()
#Alertas de quebra e excesso de estoque
if int(Estoque_Atual) < int(Valor_mes):
    st.error(f"O estoque do está abaixo do esperado podendo gerar ruptura")
if int(Estoque_Atual) > int(PontoPedido):
    st.warning(f"O Estoque está acima do ponto de pedido de reposição")
st.success(f"o valor de vendas de {Mes_selecionado} para o {produtoSelecionado} é: {Valor_mes} unidades.")

#Criação da tabela com os dados de estoque para fins de comparação
AnaliseMensal= pd.DataFrame({
    "Mês": meses,
    "Vendas": valores_mensais
})
AnaliseEstoqueDF = pd.DataFrame(
    {
        "Mês": [Mes_selecionado],
        "Estoque Segurança": [round(EstoqueSegurança)],
        "Ponto de Pedido": [round(PontoPedido)],
        "Venda Mensal": [Valor_mes],
        "Estoque Atual": [Estoque_Atual]
    }
)
#Grafico em barra com os valores selecionados
st.bar_chart(
    AnaliseEstoqueDF,
    x="Mês",
    y=["Estoque Segurança","Ponto de Pedido","Venda Mensal", "Estoque Atual"],
    color=["#FF0000", "#0000FF", "#00AA00", "#FFFF00"],
    stack=False
)

st.line_chart(AnaliseMensal, x="Mês", y="Vendas", color="#FF0000")