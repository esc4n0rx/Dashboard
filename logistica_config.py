"""
Módulo de configuração para o Dashboard de Logística.
Contém constantes e configurações usadas pelo aplicativo.
"""
import os

# Constantes de sistema
SAP_EXPORT_PATH = r"\\srv-ameixa\Area de Troca\mod.csv"
USUARIOS_NORMAL = ["FERN.PINTO", "ANDR.DACOSTA", "GABY.DACOSTA", "WILL.CARNEIR", "CLAU.OLIVEIR"]

# Cores para o dashboard
CORES = {
    "primaria": "#5D4037",       # Marrom (cor principal)
    "secundaria": "#8D6E63",     # Marrom claro (elementos secundários)
    "destaque": "#FFA000",       # Âmbar (para destaques)
    "texto": "#3E2723",          # Marrom escuro (texto)
    "fundo": "#EFEBE9",          # Bege muito claro (fundo)
    "sucesso": "#2E7D32",        # Verde (finalizados)
    "processando": "#1976D2",    # Azul (em separação)
    "pendente": "#D32F2F",       # Vermelho (pendentes)
}

# Mapeamento de depósitos para setores
DEPOSITOS = {
    "Mercearia": "DP01",
    "Perecíveis": "DP40"
}

# Configurações de estilo CSS
CSS = """
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
.metric-card {
    background-color: #F5F5F5;
    border-radius: 5px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
h1, h2, h3 {
    color: #5D4037;
}
.stMetric > div {
    border-radius: 5px;
    background-color: #F5F5F5;
    padding: 15px 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.highlight {
    background-color: #FFF8E1;
    padding: 10px;
    border-left: 3px solid #FFA000;
    margin: 10px 0;
}
.warning {
    background-color: #FFEBEE;
    padding: 10px;
    border-left: 3px solid #D32F2F;
    margin: 10px 0;
}
.success {
    background-color: #E8F5E9;
    padding: 10px;
    border-left: 3px solid #2E7D32;
    margin: 10px 0;
}
</style>
"""