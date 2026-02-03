import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

# DASHBOARD – VERSÃO VAREJO PEQUENO (5–6 FUNCIONÁRIOS)
# Lógica adaptada para supermercados / lojas de bairro
# Planejamento por TURNOS

st.set_page_config(page_title="Demanda Horária – Varejo", layout="wide")

PRIMARY = "#4F6BED"
LIGHT = "#EEF2FF"
DARK = "#1E293B"

st.markdown(
    f"""
    <style>
    .card {{
        background:{LIGHT};
        padding:16px;
        border-radius:14px;
        border:1px solid #DDE3FF;
        text-align:center;
    }}
    .card h3 {{color:{PRIMARY}; margin-bottom:6px; font-size:14px}}
    .card p {{font-size:26px; font-weight:700; color:{DARK}}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛒 Análise de Fluxo Operacional – Varejo Pequeno")
st.caption("Escala de equipe por turno • Reposição de seção • Horários de pico de atendimento")

# GERADOR DE DADOS REALISTA PARA SUPERMERCADO

# Simula movimentação de vendas/reposição por hora
# foco em fluxo de clientes e saída de produtos

def gerar_dados():
    inicio = datetime(2026, 1, 1)
    registros = []

    skus = [f"PROD-{i:03}" for i in range(1, 121)]

    for d in range(30):
        dia = inicio + timedelta(days=d)

        fim_semana = dia.weekday() >= 5
        fator_dia = 1.25 if fim_semana else 1.0

        for _ in range(int(700 * fator_dia)):
            hora = random.randint(7, 22)  # horário comercial

            # picos típicos de supermercado
            if 11 <= hora <= 13:  # almoço
                base = random.randint(8, 18)
            elif 17 <= hora <= 20:  # pós trabalho
                base = random.randint(12, 28)
            else:
                base = random.randint(2, 8)

            qtd = int(base * random.uniform(0.85, 1.15))

            registros.append([
                dia + timedelta(hours=hora, minutes=random.randint(0, 59)),
                random.choice(skus),
                "Saída",
                qtd
            ])

    return pd.DataFrame(registros, columns=["data_hora", "sku", "tipo", "quantidade"])

# SIDEBAR – AGORA FOCA EM EQUIPE TOTAL (NÃO PRODUTIVIDADE)

st.sidebar.header("👥 Planejamento de Escala")

func_totais = st.sidebar.slider(
    "Funcionários disponíveis no dia",
    3, 12, 6,
    help="Quantidade total de pessoas que trabalham no dia inteiro"
)

min_turno = st.sidebar.slider(
    "Mínimo por turno",
    1, 3, 1,
    help="Sempre manter pelo menos esse número por segurança"
)

arquivo = st.sidebar.file_uploader("Upload CSV próprio (opcional)")

# CARGA

if arquivo:
    df = pd.read_csv(arquivo, parse_dates=["data_hora"])
else:
    df = gerar_dados()

# PRÉ-PROCESSAMENTO

df["data"] = df["data_hora"].dt.date
df["hora"] = df["data_hora"].dt.hour


# CAMADA 1 – DEMANDA HORÁRIA 

hora_dia = df.groupby(["data", "hora"])['quantidade'].sum().reset_index()
por_hora = hora_dia.groupby('hora')['quantidade'].mean().reset_index()
por_dia = df.groupby('data')['quantidade'].sum().reset_index()

media = por_hora['quantidade'].mean()
std = por_hora['quantidade'].std()
por_hora['z'] = (por_hora['quantidade'] - media) / std

por_hora['perfil'] = np.select(
    [por_hora['z'] > 1, por_hora['z'] < -1],
    ['🔥 Pico', '🧊 Baixo'],
    default='Normal'
)

mov_total = int(round(df['quantidade'].sum()))
media_diaria = int(round(por_dia['quantidade'].mean()))
media_hora = int(round(media))
hora_pico = int(por_hora.loc[por_hora['quantidade'].idxmax(), 'hora'])
hora_vale = int(por_hora.loc[por_hora['quantidade'].idxmin(), 'hora'])


# CARDS
cols = st.columns(5)

cards = [
    ("Itens movimentados", f"{mov_total:,}"),
    ("Média diária", f"{media_diaria:,}"),
    ("Média por hora", f"{media_hora:,}"),
    ("Pico", f"{hora_pico}h"),
    ("Baixo fluxo", f"{hora_vale}h"),
]

for col, (t, v) in zip(cols, cards):
    col.markdown(f"<div class='card'><h3>{t}</h3><p>{v}</p></div>", unsafe_allow_html=True)


# TABS – MANTIDO MESMO LAYOUT

aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "Por Hora",
    "Diário",
    "Heatmap",
    "Top Produtos",
    "Turnos"
])

with aba1:
    fig = px.bar(por_hora, x='hora', y='quantidade', color='perfil', height=320,
                 title='Fluxo médio por hora')
    st.plotly_chart(fig, use_container_width=True)

with aba2:
    fig = px.line(por_dia, x='data', y='quantidade', height=320,
                  title='Volume diário')
    st.plotly_chart(fig, use_container_width=True)

with aba3:
    heat = hora_dia.pivot(index='data', columns='hora', values='quantidade').fillna(0)
    fig = px.imshow(heat, aspect='auto', height=380, title='Heatmap Dia x Hora')
    st.plotly_chart(fig, use_container_width=True)

with aba4:
    top = (
        df.groupby('sku')['quantidade']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(top, x='sku', y='quantidade', height=320,
                 title='Produtos mais vendidos (priorizar reposição)')
    st.plotly_chart(fig, use_container_width=True)


# CAMADA 2 – ESCALA POR TURNOS 


# definição fixa de turnos varejo
TURNOS = {
    "Manhã (07–12)": (7, 12),
    "Tarde (12–18)": (12, 18),
    "Noite (18–22)": (18, 22)
}


def classificar_turno(h):
    for nome, (ini, fim) in TURNOS.items():
        if ini <= h < fim:
            return nome


df['turno'] = df['hora'].apply(classificar_turno)

por_turno = df.groupby('turno')['quantidade'].sum().reset_index()

por_turno['percentual'] = por_turno['quantidade'] / por_turno['quantidade'].sum()

por_turno['funcionarios_sugeridos'] = (
    por_turno['percentual'] * func_totais
).round().astype(int)

por_turno['funcionarios_sugeridos'] = por_turno['funcionarios_sugeridos'].clip(lower=min_turno)


with aba5:
    fig = px.bar(por_turno, x='turno', y='funcionarios_sugeridos', height=320,
                 title='Distribuição sugerida de funcionários por turno')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(por_turno, use_container_width=True)



# RECOMENDAÇÕES


st.divider()
st.subheader("🧠 Recomendações Operacionais")

picos = por_hora[por_hora['perfil']=='🔥 Pico']['hora'].tolist()
baixos = por_hora[por_hora['perfil']=='🧊 Baixo']['hora'].tolist()


# AJUSTE DE UX
# Se não houver horas classificadas como 'Baixo',
# pegamos automaticamente as 3 menores médias
# para nunca exibir lista vazia

if not baixos:
    baixos = (
        por_hora
        .sort_values('quantidade')
        .head(3)['hora']
        .tolist()
    )

if not picos:
    picos = (
        por_hora
        .sort_values('quantidade', ascending=False)
        .head(3)['hora']
        .tolist()
    )

# formatação amigável
def fmt(lista):
    return ", ".join([f"{h}h" for h in sorted(lista)])

c1, c2, c3 = st.columns(3)

c1.success(f"Reforçar atendimento/reposição: {fmt(picos)}")
c2.info(f"Inventário/limpeza recomendados: {fmt(baixos)}")
c3.warning(f"Equipe considerada no planejamento: {func_totais} funcionários/dia")
