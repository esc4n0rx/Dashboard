"""
Módulo principal do aplicativo Streamlit para o Dashboard de Logística.
"""
import streamlit as st
import pandas as pd
import os

# Importações dos módulos do dashboard
from logistica_config import DEPOSITOS, CSS, SAP_EXPORT_PATH
from logistica_logger import log_info, log_erro, log_aviso, log_sucesso, log_debug
from logistica_sap import extrair_dados_sap
from logistica_processador import carregar_dados, processar_dados
from logistica_graficos import (
    criar_grafico_volume_total,
    criar_grafico_volume_tipo,
    criar_grafico_controle_nts
)

def main_app():
    """Função principal que cria a interface do Streamlit sem configurar a página."""
    # Cabeçalho
    st.title("Dashboard de Produção - Logística")
    
    # Barra de controles superiores
    col_refresh, col_selector, col_spacer = st.columns([1, 2, 3])
    
    with col_refresh:
        if st.button("🔄 Atualizar Dados"):
            with st.spinner("Extraindo dados do SAP..."):
                if extrair_dados_sap():
                    log_sucesso("Dados extraídos com sucesso!")
                else:
                    log_erro("Falha ao extrair dados do SAP.")
    
    with col_selector:
        setor = st.selectbox(
            "Selecione o setor:",
            list(DEPOSITOS.keys()),
            help="Selecione o setor para visualizar os dados"
        )
        deposito = DEPOSITOS[setor]
    
    # Carregar dados com logs detalhados
    log_info(f"Verificando existência do arquivo: {SAP_EXPORT_PATH}", mostrar_ui=False)
    if os.path.exists(SAP_EXPORT_PATH):
        log_info(f"Arquivo encontrado, tamanho: {os.path.getsize(SAP_EXPORT_PATH) / 1024:.2f} KB", mostrar_ui=False)
    else:
        log_aviso(f"Arquivo não encontrado: {SAP_EXPORT_PATH}")
    
    df = carregar_dados()
    
    # Verificar se existem dados
    if df.empty:
        log_aviso("Nenhum dado encontrado. Clique em 'Atualizar Dados' para extrair do SAP.")
        st.stop()
    
    # Log das informações gerais do DataFrame carregado
    log_debug(f"DataFrame carregado com {len(df)} registros e {len(df.columns)} colunas")
    log_debug(f"Colunas disponíveis: {df.columns.tolist()}")
    log_debug(f"Valores únicos de DEPOSITO: {df['DEPOSITO'].unique().tolist() if 'DEPOSITO' in df.columns else 'Coluna não encontrada'}")
    
    # Processar dados
    dados = processar_dados(df, deposito)
    
    if not dados:
        log_aviso(f"Nenhum dado encontrado para o depósito {deposito}.")
        st.stop()
    
    # Dividir a tela em seções
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📋 Dados Brutos", "📝 Logs"])
    
    with tab1:
        # Seção 1: Métricas principais
        st.subheader("📈 Métricas Principais")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Total de Linhas", 
                f"{dados['total_linhas']:,}".replace(",", "."),
                help="Número total de linhas no setor selecionado"
            )
        with col2:
            st.metric(
                "Finalizadas", 
                f"{dados['finalizadas']:,}".replace(",", "."), 
                f"{dados['finalizadas'] - dados['total_linhas']}" if dados['finalizadas'] > 0 else None,
                help="Número de linhas finalizadas"
            )
        with col3:
            st.metric(
                "Total de UM", 
                f"{dados['total_um']:,}".replace(",", "."),
                help="Soma total de unidades de medida"
            )
        with col4:
            p_linhas = round((dados["finalizadas"] / dados["total_linhas"]) * 100) if dados["total_linhas"] > 0 else 0
            st.metric(
                "% Finalizadas", 
                f"{p_linhas}%",
                help="Percentual de linhas finalizadas"
            )
        
        # Gráfico de Volume Total
        st.plotly_chart(criar_grafico_volume_total(dados), use_container_width=True)
        
        # Seção 2: Volume por Tipo
        st.subheader("🔍 Volume por Tipo")
        
        # Gráfico de Volume por Tipo
        st.plotly_chart(criar_grafico_volume_tipo(dados), use_container_width=True)
        
        # Seção 3: Controle de NTs
        st.subheader("📊 Controle de NTs")
        
        # Métricas de controle
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(
                dados["status_counts"],
                use_container_width=True,
            )
        
        # Gráfico de Controle de NTs
        st.plotly_chart(criar_grafico_controle_nts(dados["status_counts"]), use_container_width=True)
    
    with tab2:
        # Mostrar dados brutos em uma tabela interativa
        st.subheader("Dados Brutos")
        st.dataframe(
            dados["df"],
            use_container_width=True,
        )
    
    with tab3:
        # Mostrar logs e informações de diagnóstico
        st.subheader("Informações de Diagnóstico")
        
        st.markdown("### 📊 Estatísticas Gerais")
        st.code(f"""
        Arquivo de dados: {SAP_EXPORT_PATH}
        Existe arquivo: {"Sim" if os.path.exists(SAP_EXPORT_PATH) else "Não"}
        Tamanho do arquivo: {os.path.getsize(SAP_EXPORT_PATH) / 1024:.2f} KB se existir
        Registros carregados: {len(df)}
        Registros após filtro: {len(dados['df'])}
        """)
        
        st.markdown("### 🔍 Detalhes do DataFrame")
        st.code(f"""
        Colunas disponíveis: {df.columns.tolist()}
        Valores únicos DEPOSITO: {df['DEPOSITO'].unique().tolist() if 'DEPOSITO' in df.columns else 'Coluna não encontrada'}
        """)
        
        st.markdown("### 📋 Amostra de Dados")
        if not df.empty:
            st.dataframe(df.head(5))
        
        st.markdown("### 📈 Métricas Calculadas")
        st.code(f"""
        Total de linhas: {dados['total_linhas']}
        Finalizadas: {dados['finalizadas']}
        Total UM: {dados['total_um']}
        
        Normal:
          - Linhas: {dados['normal_linhas']}
          - UM: {dados['normal_um']}
        
        Reforço:
          - Linhas: {dados['reforco_linhas']}
          - UM: {dados['reforco_um']}
        """)
        
        st.markdown("### 💾 Status NTs")
        if not dados['status_nts'].empty:
            st.dataframe(
                dados['status_nts'].head(10),
                use_container_width=True,
            )

# Função original mantida para compatibilidade, mas não será usada
def main():
    log_info("A função main() não deve ser chamada diretamente. Use main_app() após configurar a página.", mostrar_ui=False)
    main_app()

if __name__ == "__main__":
    # Aviso quando o arquivo for executado diretamente
    log_aviso("Este arquivo não deve ser executado diretamente. Use main.py", mostrar_ui=True)
    st.warning("⚠️ Este arquivo não deve ser executado diretamente. Execute o arquivo main.py em vez disso.")