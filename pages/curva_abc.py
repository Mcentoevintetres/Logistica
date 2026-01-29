import streamlit as st
import pandas as pd

# =========================
# LEITURA DA PLANILHA
# =========================

df_base = pd.read_excel("./assets/classificacao_abc/Porti.xlsx", sheet_name="Planilha_Vendas")
df_base = df_base.loc[:, ~df_base.columns.str.contains('^Unnamed')]

df_base["Valor Uni"] = pd.to_numeric(df_base["Valor Uni"], errors="coerce")
df_base["Quant Vendida"] = pd.to_numeric(df_base["Quant Vendida"], errors="coerce")

df_base["Valor Total"] = df_base["Quant Vendida"] * df_base["Valor Uni"]
valor_total_geral = df_base["Valor Total"].sum()

# =========================
# TABS PRINCIPAIS
# =========================

tab_abc, tab_xyz = st.tabs(["📊 Curva ABC", "📈 Curva XYZ"])

# ==========================================================
# ===================== DASHBOARD ABC ======================
# ==========================================================

with tab_abc:

    st.header("Dashboard de Agrupamento por Curva ABC")
    st.info("Performance de vendas dos itens agrupados pelo impacto no faturamento total.")

    df = df_base.copy()

    # ---- CURVA ABC ----
    df["%Vi"] = df["Valor Total"] / valor_total_geral * 100
    df["%Vi_str"] = df["%Vi"].apply(lambda x: f"{x:.2f}%".replace(".", ","))

    df = df.sort_values(by="%Vi", ascending=False).reset_index(drop=True)
    df["%Acumulado"] = df["%Vi"].cumsum()

    def classificar_abc(p):
        if p <= 80:
            return "A"
        elif p <= 95:
            return "B"
        else:
            return "C"

    df["Classe"] = df["%Acumulado"].apply(classificar_abc)

    ABC_final = df[["Descrição", "%Vi_str", "Classe"]]

    # ---- RESUMO ----
    resumo = df.groupby("Classe")["%Vi"].sum().reset_index()
    valor_por_classe = df.groupby("Classe")["Valor Total"].sum().reset_index()

    valor_A = valor_por_classe.loc[valor_por_classe["Classe"] == "A", "Valor Total"].sum()
    valor_B = valor_por_classe.loc[valor_por_classe["Classe"] == "B", "Valor Total"].sum()
    valor_C = valor_por_classe.loc[valor_por_classe["Classe"] == "C", "Valor Total"].sum()

    st.subheader("📌 Insight da Curva ABC")

    st.success(f"Valor total vendido: R${valor_total_geral:,.2f}")

    col1, col2 = st.columns(2)

    with col1:
        st.success(f"Classe A: R${valor_A:,.2f}")
        st.warning(f"Classe B: R${valor_B:,.2f}")
        st.error(f"Classe C: R${valor_C:,.2f}")

    with col2:
        st.bar_chart(resumo, x="Classe", y=["%Vi"], horizontal=True)

    # ---- INSIGHT POR CLASSE ----

    mapa_classes = {
        "Classe A": "A",
        "Classe B": "B",
        "Classe C": "C"
    }

    label_escolhido = st.selectbox(
        "Selecione a classe para analisar:",
        list(mapa_classes.keys()),
        key="abc_select"
    )

    classe_escolhida = mapa_classes[label_escolhido]

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

    # ---- TABS A/B/C ----

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

# ==========================================================
# ===================== DASHBOARD XYZ ======================
# ==========================================================

with tab_xyz:

    st.header("Dashboard de Agrupamento por Curva XYZ")
    st.info("Análise da previsibilidade da demanda dos itens com base na variabilidade de vendas.")

    df = df_base.copy()

    # ---- CURVA XYZ (estatística) ----

    media = df["Quant Vendida"].mean()
    desvio = df["Quant Vendida"].std()

    df["CV"] = abs(df["Quant Vendida"] - media) / desvio

    q1 = df["CV"].quantile(0.33)
    q2 = df["CV"].quantile(0.66)

    def classificar_xyz(cv):
        if cv <= q1:
            return "X"
        elif cv <= q2:
            return "Y"
        else:
            return "Z"

    df["Classe"] = df["CV"].apply(classificar_xyz)

    # reutilizando lógica de %Vi para manter visual igual ao ABC
    df["%Vi"] = df["Valor Total"] / valor_total_geral * 100
    df["%Vi_str"] = df["%Vi"].apply(lambda x: f"{x:.2f}%".replace(".", ","))

    XYZ_final = df[["Descrição", "%Vi_str", "Classe"]]

    # ---- RESUMO ----

    resumo = df.groupby("Classe")["%Vi"].sum().reset_index()
    valor_por_classe = df.groupby("Classe")["Valor Total"].sum().reset_index()

    valor_X = valor_por_classe.loc[valor_por_classe["Classe"] == "X", "Valor Total"].sum()
    valor_Y = valor_por_classe.loc[valor_por_classe["Classe"] == "Y", "Valor Total"].sum()
    valor_Z = valor_por_classe.loc[valor_por_classe["Classe"] == "Z", "Valor Total"].sum()

    st.subheader("📌 Insight da Curva XYZ")

    st.success(f"Valor total vendido: R${valor_total_geral:,.2f}")

    col1, col2 = st.columns(2)

    with col1:
        st.success(f"Classe X: R${valor_X:,.2f}")
        st.warning(f"Classe Y: R${valor_Y:,.2f}")
        st.error(f"Classe Z: R${valor_Z:,.2f}")

    with col2:
        st.bar_chart(resumo, x="Classe", y=["%Vi"], horizontal=True)

    # ---- INSIGHT POR CLASSE ----

    mapa_classes = {
        "Classe X": "X",
        "Classe Y": "Y",
        "Classe Z": "Z"
    }

    label_escolhido = st.selectbox(
        "Selecione a classe para analisar:",
        list(mapa_classes.keys()),
        key="xyz_select"
    )

    classe_escolhida = mapa_classes[label_escolhido]

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

    st.dataframe(XYZ_final)

    # ---- TABS X/Y/Z ----

    tab1, tab2, tab3 = st.tabs(["Grupo X", "Grupo Y", "Grupo Z"])

    Grupo_X = df[df["Classe"] == "X"][["SKU", "%Vi_str"]]
    Grupo_Y = df[df["Classe"] == "Y"][["SKU", "%Vi_str"]]
    Grupo_Z = df[df["Classe"] == "Z"][["SKU", "%Vi_str"]]

    with tab1:
        st.bar_chart(Grupo_X, x="%Vi_str", y="SKU")
    with tab2:
        st.bar_chart(Grupo_Y, x="%Vi_str", y="SKU")
    with tab3:
        st.bar_chart(Grupo_Z, x="%Vi_str", y="SKU")
