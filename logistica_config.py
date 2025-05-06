"""
Módulo de configuração para o Dashboard de Logística.
Contém constantes e configurações usadas pelo aplicativo.
"""
import os

# Constantes de sistema
SAP_EXPORT_PATH = r"\\srv-ameixa\Area de Troca\mod.csv"
USUARIOS_NORMAL = ["FERN.PINTO", "ANDR.DACOSTA", "GABY.DACOSTA", "WILL.CARNEIR", "CLAU.OLIVEIR"]

# Cores para o dashboard - Tema escuro
CORES = {
    "primaria": "#BB8674",       # Marrom claro (cor principal)
    "secundaria": "#A3786A",     # Marrom médio (elementos secundários)
    "destaque": "#FFB74D",       # Âmbar claro (para destaques)
    "texto": "#F5F5F5",          # Branco (texto)
    "texto_secundario": "#E0E0E0", # Cinza claro (texto secundário)
    "fundo": "#121212",          # Preto (fundo)
    "fundo_secundario": "#1E1E1E", # Cinza escuro (fundo de cards)
    "fundo_terciario": "#2D2D2D", # Cinza médio (fundo de elementos)
    "sucesso": "#66BB6A",        # Verde (finalizados)
    "processando": "#42A5F5",    # Azul (em separação)
    "pendente": "#EF5350",       # Vermelho (pendentes)
    "ouro": "#FFD54F",           # Ouro (1º lugar)
    "prata": "#B0BEC5",          # Prata (2º lugar)
    "bronze": "#BCAAA4",         # Bronze (3º lugar)
    "alerta": "#FFECB3",         # Alerta leve
    "aviso": "#FFAB91",          # Aviso
}

# Mapeamento de depósitos para setores
DEPOSITOS = {
    "Mercearia": "DP01",
    "Perecíveis": "DP40"
}

# Configurações de estilo CSS - Tema escuro
CSS = """
<style>
/* Configurações globais */
body {
    background-color: #121212;
    color: #F5F5F5;
}

.stApp {
    background-color: #121212;
}

/* Estilos gerais */
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    background-color: #121212;
}

/* Cards e métricas */
.metric-card {
    background-color: #1E1E1E;
    border-radius: 5px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    margin-bottom: 15px;
    color: #F5F5F5;
}

/* Cabeçalhos */
h1, h2, h3 {
    color: #BB8674;
}

h4 {
    margin-top: 10px;
    margin-bottom: 5px;
    color: #F5F5F5;
    font-weight: 600;
}

/* Texto normal */
p {
    color: #E0E0E0;
}

/* Estilo para cards de métricas */
.stMetric > div {
    border-radius: 5px;
    background-color: #1E1E1E;
    padding: 15px 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    transition: transform 0.2s ease;
}

.stMetric > div:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.4);
}

.stMetric label {
    color: #BB8674 !important;
}

.stMetric .css-1xarl3l {
    color: #F5F5F5 !important;
}

/* Classes para diferentes tipos de alertas */
.highlight {
    background-color: #2D2D2D;
    padding: 15px;
    border-left: 3px solid #FFB74D;
    margin: 15px 0;
    border-radius: 0 5px 5px 0;
    color: #F5F5F5;
}

.warning {
    background-color: #2D2D2D;
    padding: 15px;
    border-left: 3px solid #EF5350;
    margin: 15px 0;
    border-radius: 0 5px 5px 0;
    color: #F5F5F5;
}

.success {
    background-color: #2D2D2D;
    padding: 15px;
    border-left: 3px solid #66BB6A;
    margin: 15px 0;
    border-radius: 0 5px 5px 0;
    color: #F5F5F5;
}

/* Estilo para a barra lateral */
[data-testid="stSidebar"] {
    background-color: #1E1E1E;
    border-right: 1px solid #333333;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Botões na sidebar */
[data-testid="stSidebar"] .stButton > button {
    background-color: #A3786A;
    color: #F5F5F5;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    width: 100%;
    transition: all 0.3s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #BB8674;
    transform: translateY(-2px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.4);
}

/* Radio buttons */
.stRadio > div {
    padding: 10px 0;
}

.stRadio label span {
    color: #E0E0E0 !important;
}

/* Seletores */
.stSelectbox label {
    color: #E0E0E0 !important;
}

.stSelectbox > div > div {
    background-color: #2D2D2D;
    color: #F5F5F5;
    border: 1px solid #444444;
}

/* Expanders */
.stExpander {
    background-color: #1E1E1E;
    border-radius: 5px;
    margin-bottom: 10px;
}

.stExpander > details {
    background-color: #1E1E1E;
    color: #F5F5F5;
}

.stExpander > details > summary {
    background-color: #2D2D2D;
    color: #E0E0E0;
    padding: 10px;
    border-radius: 5px;
}

/* Tabelas */
.stDataFrame {
    background-color: #1E1E1E;
}

[data-testid="stTable"] {
    background-color: #1E1E1E;
}

.stDataFrame th {
    background-color: #2D2D2D;
    color: #BB8674;
}

.stDataFrame td {
    background-color: #1E1E1E;
    color: #E0E0E0;
}

/* Blocos de código */
.stCodeBlock {
    background-color: #2D2D2D;
}

.stCodeBlock > div > pre {
    background-color: #2D2D2D;
    color: #E0E0E0;
}

/* Dataframes e tabelas */
div[data-testid="stTable"] {
    background-color: #1E1E1E;
    border-radius: 5px;
    overflow: hidden;
}

div[data-testid="stTable"] table {
    border-collapse: collapse;
}

div[data-testid="stTable"] th {
    background-color: #2D2D2D;
    color: #BB8674;
    border: 1px solid #444444;
    padding: 8px;
}

div[data-testid="stTable"] td {
    border: 1px solid #333333;
    color: #E0E0E0;
    padding: 8px;
}

/* Estilo para o ranking de usuários */
.ranking-card {
    background-color: #1E1E1E;
    border-radius: 5px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    color: #F5F5F5;
}

.ranking-item {
    display: flex;
    align-items: center;
    padding: 8px 5px;
    border-bottom: 1px solid #333333;
    color: #E0E0E0;
}

.ranking-position {
    font-weight: bold;
    min-width: 30px;
}

.ranking-first {
    color: #FFD54F;
}

.ranking-second {
    color: #B0BEC5;
}

.ranking-third {
    color: #BCAAA4;
}

/* Ajustes do cartão de previsão */
.success h3, .warning h3, .highlight h3, .metric-card h3 {
    color: #F5F5F5;
    font-weight: 600;
}

/* Ajustes para responsividade em telas menores */
@media (max-width: 768px) {
    .stMetric > div {
        padding: 10px 5px;
    }
    
    h1 {
        font-size: 1.8rem;
    }
    
    h2 {
        font-size: 1.5rem;
    }
    
    h3 {
        font-size: 1.2rem;
    }
}
</style>
"""