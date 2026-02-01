# 📦 Simulador de sistema logistico e admnistrativo

## Descrição do sistema

Este repositório reúne um conjunto de algoritmos logísticos e de análise de dados, desenvolvidos em Python e Streamlit.
Os algoritmos buscam simular algumas ferramentas de análise de movimentação de estoque em um comércio, visando agrupar itens pelo método de classificação ABC e XYZ, análise unitária de estoque de item e por último um simulador básico de fluxo de caixa.

O objetivo do projeto é demonstrar, de forma prática e técnica, como dados podem ser transformados em informação estratégica para tomada de decisão.

### O sistema é dividido em três funcionalidades diferentes:

#### 📦 Algoritmo de classificação ABC e XYZ
O algoritmo lê e manipula os dados de uma planilha excel anexada, classificando os itens pelos fatores:
<ul>
  <li>Fator financeiro para a classificação ABC</li>
  <li>Fator de criticidade operacional para a classificação XYZ</li>
</ul>

#### 📦 Algoritmo de análise de estoque
 O algoritmo lê e manipula os dados de uma planilha excel anexada, buscando os dados relacionados ao estoque daquele item escolhido, análisando pontos como:
 <ul>
   <li>Estoque de segurança</li>
   <li>Ponto de pedido</li>
   <li>Ruptura de Estoque</li>
   <li>Custo de Estoque</li>
 </ul>

 #### 📉 Algoritmo de Fluxo de caixa
 O algoritmo lê e manipula os dados de uma planilha excel anexada trazendo todos os dados relacionados a entrada e saída do caixa de um determinado período.

 
 ### 👨‍💻 Tecnologias utilizadas
 
  <img
      align="left"
      alt="Python"
      title="Python"
      width="30px"
      style="padding-right: 10px;"
      src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg"
  />
  
  <img
      align="left"
      alt="Pandas"
      title="Pandas"
      width="30px"
      style="padding-right: 10px;"
      src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/pandas/pandas-original.svg"
  />
  
  <img
      align="left"
      alt="Streamlit"
      title="Streamlit"
      width="30px"
      style="padding-right: 10px;"
      src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/streamlit/streamlit-original.svg"
  />
  
  <img
      align="left"
      alt="Matplotlib"
      title="Matplotlib"
      width="30px"
      style="padding-right: 10px;"
      src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/matplotlib/matplotlib-original.svg"
  />
  
  <img
      align="left"
      alt="Plotly"
      title="Plotly"
      width="30px"
      style="padding-right: 10px;"
      src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/plotly/plotly-original.svg"
  />
  
  <img
      align="left"
      alt="CSS"
      title="CSS"
      width="30px"
      style="padding-right: 10px;"
      src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/css3/css3-original.svg"
  />

<br/>
<br/>

## 🔧 instruções de instalação

**Clone o repositório:**

`git clone https://github.com/Mcentoevintetres/logistica.git`

**instale as dependências:**

`pip install -r requirements.txt`

**Execetue o streamlit:**

`streamlit run Home.py`


## 🧪 Fundamentos de Python para Análise e Aplicações

**Manipulação de Dados com Pandas**

 <ul>
   <li>read_excel() e read_csv() para leitura de planilha</li>
   <li>Tratamento de colunas Unnamed geradas pelo streamlit</li>
   <li>Filtragem por linhas e colunas utilizando selectbox</li>
   <li>Uso de .unique(), .loc[], .iloc[] para captura de valores unicos</li>
   <li>Conversão de tipos (astype, int(), float())</li>
 </ul>

**Estruturas Condicionais e Validações**

<ul>
   <li>Uso de if, elif, else</li>
   <li>Validação de entradas antes de cálculos</li>
   <li>Prevenção de erros de execução (ValueError, TypeError)</li>
 </ul>

 **Problemas resolvidos:**
 <ul>
   <li>Erro de leitura de caracteres especiais (acentuação)</li>
   <li>Conversão indevida de numpy.int64 para int</li>
 </ul>
