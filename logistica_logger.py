"""
Módulo de logging para o Dashboard de Logística.
Gerencia o registro de eventos e mensagens do sistema.
"""
import logging
import os
import streamlit as st
from datetime import datetime

# Configuração básica do logger
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Nome do arquivo baseado na data
LOG_FILE = os.path.join(LOG_DIR, f"dashboard_{datetime.now().strftime('%Y%m%d')}.log")

# Configurar o logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("dashboard_logistica")

# Funções de log para o Streamlit
def log_info(mensagem, mostrar_ui=True):
    """Registra informação e opcionalmente mostra na UI."""
    logger.info(mensagem)
    if mostrar_ui:
        st.info(mensagem)

def log_erro(mensagem, mostrar_ui=True, exception=None):
    """Registra erro e opcionalmente mostra na UI."""
    if exception:
        mensagem_completa = f"{mensagem}: {str(exception)}"
        logger.error(mensagem_completa, exc_info=True)
    else:
        logger.error(mensagem)
    
    if mostrar_ui:
        st.error(mensagem)

def log_aviso(mensagem, mostrar_ui=True):
    """Registra aviso e opcionalmente mostra na UI."""
    logger.warning(mensagem)
    if mostrar_ui:
        st.warning(mensagem)

def log_sucesso(mensagem, mostrar_ui=True):
    """Registra sucesso e opcionalmente mostra na UI."""
    logger.info(f"SUCESSO: {mensagem}")
    if mostrar_ui:
        st.success(mensagem)

def log_debug(mensagem):
    """Registra mensagem de debug apenas no arquivo de log."""
    logger.debug(mensagem)