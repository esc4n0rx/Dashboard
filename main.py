"""
Arquivo principal para o Dashboard de Logística.
Este arquivo importa o módulo principal e inicia a aplicação.
"""
import os
import sys
import traceback
import streamlit as st

# Configuração da página (deve ser a primeira chamada do Streamlit)
st.set_page_config(
    page_title="Dashboard Logística", 
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Adiciona o diretório atual ao path do Python para resolver importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Tenta inicializar o aplicativo e capturar erros detalhados
try:
    # Importa os módulos necessários (exceto a inicialização da página)
    from logistica_logger import log_info, log_erro, log_debug
    from logistica_config import SAP_EXPORT_PATH, CSS
    
    # Aplica CSS personalizado
    st.markdown(CSS, unsafe_allow_html=True)
    
    # Verifica a existência do arquivo de dados e registra informações
    if os.path.exists(SAP_EXPORT_PATH):
        #log_info(f"Arquivo de dados encontrado: {SAP_EXPORT_PATH}")
        print(f"Arquivo encontrado, tamanho: {os.path.getsize(SAP_EXPORT_PATH) / 1024:.2f} KB")
    else:
        log_info(f"Arquivo de dados não encontrado: {SAP_EXPORT_PATH}")
    
    # Importa a função main sem a configuração de página
    from logistica_app import main_app
    
    # Executa a aplicação
    if __name__ == "__main__":
        #log_info("Iniciando Dashboard de Logística...")
        main_app()
        #log_info("Dashboard encerrado.")

except ImportError as e:
    st.error(f"Erro ao importar módulos: {str(e)}")
    st.write("Verifique se todos os arquivos estão na mesma pasta:")
    
    # Listar arquivos no diretório atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    arquivos = os.listdir(current_dir)
    
    st.code(f"""
    Arquivos encontrados em {current_dir}:
    {', '.join(arquivos)}
    
    Arquivos necessários:
    - main.py
    - logistica_app.py
    - logistica_config.py
    - logistica_logger.py
    - logistica_sap.py
    - logistica_processador.py
    - logistica_graficos.py
    """)

except Exception as e:
    st.error(f"Erro ao iniciar aplicação: {str(e)}")
    st.write("Detalhes do erro:")
    st.code(traceback.format_exc())
    
    # Adicionar informações extras para diagnóstico
    st.write("### Informações do Sistema:")
    st.code(f"""
    Python: {sys.version}
    Diretório atual: {os.getcwd()}
    Variáveis de ambiente: {list(os.environ.keys())}
    """)