import streamlit as st

st.set_page_config(page_title="Portfólio Logístico", layout="wide")

st.markdown("""
<style>
section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.card {
    margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)

# ====== CSS GLOBAL PARA FIXAR CORES E TAMANHO ======
st.markdown("""
<style>

.card-container {
    max-width: 350px;      /* Limita a largura */
    width: 100%;
}

.card {
    padding: 20px;
    border-radius: 14px;
    background-color: #D2F0E2 !important;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.20);
    transition: 0.2s;
    cursor: pointer;
    border: 1px solid #2CB67D;
}

.card:hover {
    transform: translateY(-3px);
    background-color: #ffffff !important;
    box-shadow: 0px 6px 16px rgba(0,0,0,0.30);
}

.card-title {
    font-size: 20px;
    font-weight: 700;
    color: #222 !important;     /* FORÇA PRETO */
    margin-bottom: 6px;
}

.card-desc {
    font-size: 14px;
    color: #444 !important;     /* FORÇA CINZA ESCURO */
}

a {
    text-decoration: none !important;
}

</style>
""", unsafe_allow_html=True)

# ====== TÍTULO ======
st.title("Portfólio de Algoritmos Logísticos", text_alignment="center" )

st.info("Esses são alguns dos algoritmos que desenvolvi com intuito de demonstrar meu conhecimento com processos logísticos integrados a programação com manipulação e análise de dados")
st.info("Todos os dados utilizados são genéricos")
# ====== ANY CARD ======
def card(title, desc, page):
    st.markdown(f"""
    <a href="/{page}" target="_self">
        <div class="card-container">
            <div class="card">
                <div class="card-title">{title}</div>
                <div class="card-desc">{desc}</div>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)


# ====== LAYOUT ======
col1, col2, col3 = st.columns([1,1,1])

with col1:
    card("📊 Curva ABC",
         "Classifique itens pelo valor acumulado.",
         "curva_abc")

with col2:
    card("💸 Fluxo de Caixa",
         "Controle entradas e saídas financeiras.",
         "fluxodecaixa")

with col3:
    card("📦 Estoque Segurança",
         "Cálculo de ES, PP e risco de ruptura.",
         "EstoqueSegurança")
