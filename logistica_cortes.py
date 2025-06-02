"""
Módulo de análise de cortes para o Dashboard de Logística.
Gerencia a identificação, processamento e visualização de itens cortados.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import List, Dict, Any, Optional # Adicionado para type hinting mais preciso

# Supõe-se que estes módulos existam e funcionem como no original
from logistica_logger import log_debug, log_info, log_aviso, log_erro
from logistica_config import CORES # Ex: CORES = {"pendente": "blue", "destaque": "red", ...}

# Constantes para colunas e padrões
COLUNAS_NECESSARIAS_IDENTIFICAR_CORTES: List[str] = [
    "ITEM_FINALIZADO", "DT_PRODUCAO", "NUMERO_NT", "MATERIAL", "DESC_MATERIAL", "QUANT_NT"
]
DATA_ZERADA_PATTERNS: List[str] = ["0000-00-00", "00/00/0000", "00.00.0000", ""]
COLUNAS_DF_OPERADOR: List[str] = ["NUMERO_NT", "NOME_USUARIO"]


def _verificar_colunas_necessarias(df: pd.DataFrame, colunas: List[str], nome_funcao_log: str) -> bool:
    """Verifica se todas as colunas necessárias existem no DataFrame."""
    for coluna in colunas:
        if coluna not in df.columns:
            log_aviso(f"Coluna '{coluna}' não encontrada no DataFrame para {nome_funcao_log}")
            return False
    return True

def identificar_cortes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica itens cortados no DataFrame.

    Um item cortado é identificado quando:
    - ITEM_FINALIZADO = "X" (item finalizado)
    - DT_PRODUCAO é uma data zerada ou vazia.

    Args:
        df (pd.DataFrame): DataFrame com os dados carregados.

    Returns:
        pd.DataFrame: DataFrame com apenas os itens cortados.
    """
    log_debug("Identificando itens cortados...")

    if df.empty:
        log_aviso("DataFrame vazio, impossível identificar cortes.")
        return pd.DataFrame()

    if not _verificar_colunas_necessarias(df, COLUNAS_NECESSARIAS_IDENTIFICAR_CORTES, "análise de cortes"):
        return pd.DataFrame()

    df_analise = df.copy()

    # Garantir tipos e tratar nulos para colunas de condição
    df_analise["ITEM_FINALIZADO"] = df_analise["ITEM_FINALIZADO"].astype(str).fillna("").str.upper()
    df_analise["DT_PRODUCAO"] = df_analise["DT_PRODUCAO"].astype(str).fillna("").str.strip()

    condicao_item_finalizado = df_analise["ITEM_FINALIZADO"] == "X"
    condicao_data_zerada = df_analise["DT_PRODUCAO"].isin(DATA_ZERADA_PATTERNS)

    df_cortados = df_analise[condicao_item_finalizado & condicao_data_zerada].copy()

    log_debug(f"Total de itens cortados identificados: {len(df_cortados)}")
    return df_cortados

def identificar_operador_corte(df_completo: pd.DataFrame, df_cortados: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica o operador responsável pelo corte de forma otimizada.

    Args:
        df_completo (pd.DataFrame): DataFrame completo com todos os dados.
        df_cortados (pd.DataFrame): DataFrame com os itens cortados.

    Returns:
        pd.DataFrame: DataFrame de itens cortados com o operador identificado.
    """
    log_debug("Identificando operadores responsáveis pelos cortes...")

    if df_cortados.empty:
        return df_cortados.copy() # Retorna cópia para consistência

    if not _verificar_colunas_necessarias(df_completo, COLUNAS_DF_OPERADOR, "identificação de operador"):
        df_resultado = df_cortados.copy()
        df_resultado["OPERADOR_CORTE"] = "Erro: Colunas ausentes no DF principal"
        return df_resultado

    if "NUMERO_NT" not in df_cortados.columns:
        log_aviso("Coluna 'NUMERO_NT' não encontrada no DataFrame de cortes para identificar operador.")
        df_resultado = df_cortados.copy()
        df_resultado["OPERADOR_CORTE"] = "Erro: NUMERO_NT ausente nos cortes"
        return df_resultado
        
    df_resultado = df_cortados.copy()

    # 1. Preparar DataFrame de operadores: filtrar NOME_USUARIO válidos e pegar o primeiro por NUMERO_NT
    df_operadores_validos = df_completo[
        df_completo["NOME_USUARIO"].notna() & (df_completo["NOME_USUARIO"].astype(str).str.strip() != '')
    ][["NUMERO_NT", "NOME_USUARIO"]].drop_duplicates(subset=["NUMERO_NT"], keep="first")

    # 2. Criar um mapa de NUMERO_NT para NOME_USUARIO
    mapa_nt_operador = pd.Series(
        df_operadores_validos["NOME_USUARIO"].values,
        index=df_operadores_validos["NUMERO_NT"]
    ).to_dict()

    # 3. Mapear os operadores para o DataFrame de cortes
    df_resultado["OPERADOR_CORTE"] = df_resultado["NUMERO_NT"].map(mapa_nt_operador)
    df_resultado["OPERADOR_CORTE"] = df_resultado["OPERADOR_CORTE"].fillna("Não identificado")

    operadores_identificados_count = df_resultado[df_resultado["OPERADOR_CORTE"] != "Não identificado"]["OPERADOR_CORTE"].nunique()
    log_debug(f"Operadores identificados para {operadores_identificados_count} NTs diferentes (de {df_resultado['NUMERO_NT'].nunique()} NTs cortadas).")

    return df_resultado

def processar_dados_cortes(df: pd.DataFrame, deposito: Optional[str] = None) -> Dict[str, Any]:
    """
    Processa os dados de cortes para análise.

    Args:
        df (pd.DataFrame): DataFrame com os dados carregados.
        deposito (str, optional): Código do depósito para filtrar os dados.

    Returns:
        dict: Dicionário com os dados processados de cortes.
    """
    log_info(f"Processando dados de cortes{' para o depósito ' + deposito if deposito else ''}...")

    retorno_vazio = {
        "df_cortados": pd.DataFrame(),
        "total_cortes": 0,
        "cortes_por_operador": pd.DataFrame(),
        "cortes_por_material": pd.DataFrame(),
        "total_unidades_cortadas": 0
    }

    if df.empty:
        log_aviso("DataFrame vazio, impossível processar cortes.")
        return retorno_vazio

    df_filtrado = df.copy()
    if deposito and "DEPOSITO" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["DEPOSITO"] == deposito].copy()
        log_debug(f"Filtrado para depósito {deposito}: {len(df_filtrado)} registros.")
    elif deposito:
        log_aviso(f"Coluna 'DEPOSITO' não encontrada para filtrar pelo depósito {deposito}.")
        # Prossegue sem filtro de depósito ou retorna vazio, dependendo da regra de negócio.
        # Aqui, optou-se por prosseguir sem o filtro se a coluna não existe.

    df_cortados_identificados = identificar_cortes(df_filtrado)

    if df_cortados_identificados.empty:
        log_info("Nenhum item cortado encontrado após identificação.")
        return retorno_vazio

    df_cortados_com_operador = identificar_operador_corte(df_filtrado, df_cortados_identificados)

    # Converter QUANT_NT para numérico
    # Garantir que é string antes de aplicar métodos de string
    df_cortados_com_operador["QUANT_NT"] = df_cortados_com_operador["QUANT_NT"].astype(str)
    quant_nt_numerico = (
        df_cortados_com_operador["QUANT_NT"]
        .str.strip()
        .str.replace('.', '', regex=False)  # Remove separador de milhar
        .str.replace(',', '.', regex=False)  # Substitui vírgula decimal por ponto
    )
    df_cortados_com_operador["QUANT_NT_NUM"] = pd.to_numeric(quant_nt_numerico, errors='coerce').fillna(0)

    total_cortes = len(df_cortados_com_operador)
    total_unidades_cortadas = df_cortados_com_operador["QUANT_NT_NUM"].sum()

    if total_cortes == 0: # Dupla verificação, caso algo mude QUANT_NT_NUM para 0 e zere o df
        log_info("Nenhum item cortado válido encontrado após processamento.")
        return retorno_vazio

    cortes_por_operador = (
        df_cortados_com_operador.groupby("OPERADOR_CORTE")
        .agg(total_cortes=("NUMERO_NT", "count"), total_unidades=("QUANT_NT_NUM", "sum"))
        .reset_index()
        .sort_values("total_cortes", ascending=False)
    )

    cortes_por_material = (
        df_cortados_com_operador.groupby(["MATERIAL", "DESC_MATERIAL"])
        .agg(total_cortes=("NUMERO_NT", "count"), total_unidades=("QUANT_NT_NUM", "sum"))
        .reset_index()
        .sort_values("total_cortes", ascending=False)
    )

    log_info(f"Processamento de dados de cortes concluído: {total_cortes} cortes identificados.")

    return {
        "df_cortados": df_cortados_com_operador,
        "total_cortes": total_cortes,
        "cortes_por_operador": cortes_por_operador,
        "cortes_por_material": cortes_por_material,
        "total_unidades_cortadas": total_unidades_cortadas,
    }

def _criar_grafico_vazio(titulo: str, altura: int = 400) -> go.Figure:
    """Cria uma figura Plotly vazia com uma mensagem."""
    fig = go.Figure()
    fig.update_layout(
        title=f"{titulo} - Nenhum dado disponível",
        height=altura,
        plot_bgcolor="white",
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[{
            "text": "Sem dados para exibir.",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16}
        }]
    )
    return fig

def _criar_grafico_erro(titulo_erro: str, mensagem_erro: str, altura: int = 400) -> go.Figure:
    """Cria uma figura Plotly indicando um erro."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"Erro ao criar gráfico: {mensagem_erro}",
        x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
        font=dict(size=14, color="red")
    )
    fig.update_layout(title=titulo_erro, height=altura, plot_bgcolor="white")
    return fig

def criar_grafico_cortes_operador(cortes_por_operador: pd.DataFrame) -> go.Figure:
    """Cria um gráfico de barras para cortes por operador."""
    try:
        if cortes_por_operador.empty:
            return _criar_grafico_vazio("Cortes por Operador")

        colunas_necessarias = ["OPERADOR_CORTE", "total_cortes", "total_unidades"]
        if not all(col in cortes_por_operador.columns for col in colunas_necessarias):
            log_aviso("Colunas ausentes no DataFrame para gráfico de cortes por operador.")
            return _criar_grafico_erro("Cortes por Operador", "Dados de entrada incompletos", 400)

        df_plot = cortes_por_operador.copy()
        df_plot["total_unidades_display"] = df_plot["total_unidades"].round(0).astype(int)

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Total de Cortes", "Unidades Cortadas"],
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )

        fig.add_trace(
            go.Bar(
                x=df_plot["OPERADOR_CORTE"], y=df_plot["total_cortes"],
                name="Cortes", marker_color=CORES.get("pendente", "blue"),
                text=df_plot["total_cortes"], textposition="auto",
            ), row=1, col=1
        )
        fig.add_trace(
            go.Bar(
                x=df_plot["OPERADOR_CORTE"], y=df_plot["total_unidades"],
                name="Unidades", marker_color=CORES.get("destaque", "red"),
                text=df_plot["total_unidades_display"], textposition="auto",
            ), row=1, col=2
        )
        fig.update_layout(
            title_text="Cortes por Operador", height=400,
            plot_bgcolor="white", showlegend=False
        )
        return fig

    except Exception as e:
        log_erro(f"Erro ao criar gráfico de cortes por operador: {str(e)}", mostrar_ui=False)
        return _criar_grafico_erro("Erro no Gráfico de Cortes por Operador", str(e))

def criar_grafico_cortes_material(cortes_por_material: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Cria um gráfico de barras para cortes por material."""
    try:
        if cortes_por_material.empty:
            return _criar_grafico_vazio("Cortes por Material", altura=500)

        colunas_necessarias = ["MATERIAL", "DESC_MATERIAL", "total_cortes"]
        if not all(col in cortes_por_material.columns for col in colunas_necessarias):
            log_aviso("Colunas ausentes no DataFrame para gráfico de cortes por material.")
            return _criar_grafico_erro("Cortes por Material", "Dados de entrada incompletos", 500)

        df_plot = cortes_por_material.head(top_n).copy()
        df_plot["DESC_MATERIAL"] = df_plot["DESC_MATERIAL"].fillna("Sem descrição")
        df_plot["DESCRICAO_EXIBICAO"] = df_plot.apply(
            lambda row: f"{row['MATERIAL']}: {str(row['DESC_MATERIAL'])[:30]}{'...' if len(str(row['DESC_MATERIAL'])) > 30 else ''}",
            axis=1
        )
        df_plot = df_plot.sort_values("total_cortes", ascending=True) # Para barras horizontais, a ordem é invertida visualmente

        fig = go.Figure(go.Bar(
            y=df_plot["DESCRICAO_EXIBICAO"],
            x=df_plot["total_cortes"],
            orientation="h",
            marker_color=CORES.get("pendente", "lightblue"),
            name="Cortes",
            text=df_plot["total_cortes"],
            textposition="auto",
        ))
        fig.update_layout(
            title_text=f"Top {len(df_plot)} Materiais com Mais Cortes",
            xaxis_title="Total de Cortes", yaxis_title="Material",
            height=max(400, len(df_plot) * 40 + 150), # Altura dinâmica
            plot_bgcolor="white",
            yaxis=dict(autorange="reversed") # Garante que o maior valor fique no topo
        )
        return fig

    except Exception as e:
        log_erro(f"Erro ao criar gráfico de cortes por material: {str(e)}", mostrar_ui=False)
        return _criar_grafico_erro("Erro no Gráfico de Cortes por Material", str(e), altura=500)



def exibir_pagina_cortes(df_principal: pd.DataFrame, deposito_selecionado: Optional[str]):
    """
    Exibe a página de análise de cortes no Streamlit.

    Args:
        df_principal (pd.DataFrame): DataFrame com todos os dados carregados.
        deposito_selecionado (str, optional): Código do depósito selecionado.
    """
    import streamlit as st
    from logistica_processador import aplicar_filtro_datas_outras_telas
    
    st.title("Análise de Cortes")

    try:
        # Aplicar filtro de data específico para outras telas
        df_filtrado_data = aplicar_filtro_datas_outras_telas(df_principal)
        
        if df_filtrado_data.empty:
            st.warning("⚠️ Nenhum dado encontrado para a data atual (DT_PLANEJADA = hoje)")
            st.info("A página de Cortes usa apenas dados com DT_PLANEJADA igual à data atual do sistema.")
            return
        
        dados_cortes = processar_dados_cortes(df_filtrado_data, deposito_selecionado)

        if dados_cortes["total_cortes"] == 0:
            st.info(f"Nenhum item cortado encontrado{' para o depósito selecionado' if deposito_selecionado else ''} na data atual.")
            return

        # Seção 1: Métricas Gerais
        st.subheader("📊 Métricas de Cortes")
        try:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Total de Cortes",
                    f"{dados_cortes['total_cortes']:,}".replace(",", "."),
                    help="Número total de itens cortados."
                )
            with col2:
                st.metric(
                    "Total de Unidades Cortadas",
                    f"{int(dados_cortes['total_unidades_cortadas']):,}".replace(",", "."),
                    help="Soma das quantidades de todos os itens cortados."
                )
        except Exception as e:
            log_erro(f"Erro ao exibir métricas de cortes: {str(e)}", mostrar_ui=True)
            st.error("Erro ao exibir métricas. Veja os logs para mais detalhes.")

        # Seção 2: Cortes por Operador
        st.subheader("👤 Cortes por Operador")
        try:
            grafico_operador = criar_grafico_cortes_operador(dados_cortes["cortes_por_operador"])
            st.plotly_chart(grafico_operador, use_container_width=True)

            if not dados_cortes["cortes_por_operador"].empty:
                df_operadores_display = dados_cortes["cortes_por_operador"].copy()
                df_operadores_display.columns = ["Operador", "Total de Cortes", "Total de Unidades"]
                df_operadores_display["Total de Unidades"] = df_operadores_display["Total de Unidades"].round(0).astype(int)
                st.dataframe(df_operadores_display, use_container_width=True)
        except Exception as e:
            log_erro(f"Erro ao exibir seção de cortes por operador: {str(e)}", mostrar_ui=True)
            st.error("Erro ao exibir dados de cortes por operador. Veja os logs para mais detalhes.")

        # Seção 3: Cortes por Material
        st.subheader("📦 Materiais Mais Cortados")
        try:
            grafico_material = criar_grafico_cortes_material(dados_cortes["cortes_por_material"])
            st.plotly_chart(grafico_material, use_container_width=True)

            if not dados_cortes["cortes_por_material"].empty:
                df_materiais_display = dados_cortes["cortes_por_material"].copy()
                df_materiais_display.columns = ["Código", "Descrição", "Total de Cortes", "Total de Unidades"]
                df_materiais_display["Total de Unidades"] = df_materiais_display["Total de Unidades"].round(0).astype(int)
                st.dataframe(df_materiais_display.head(20), use_container_width=True) # Limitar a 20 materiais na tabela
        except Exception as e:
            log_erro(f"Erro ao exibir seção de cortes por material: {str(e)}", mostrar_ui=True)
            st.error("Erro ao exibir dados de cortes por material. Veja os logs para mais detalhes.")

        # Seção 4: Detalhes dos Cortes
        with st.expander("🔍 Detalhes dos Itens Cortados"):
            try:
                df_cortados_detalhe = dados_cortes["df_cortados"]
                if not df_cortados_detalhe.empty:
                    colunas_exibicao = ["NUMERO_NT", "MATERIAL", "DESC_MATERIAL", "QUANT_NT", "OPERADOR_CORTE"]
                    # Verificar se todas as colunas esperadas existem antes de tentar selecioná-las
                    colunas_presentes = [col for col in colunas_exibicao if col in df_cortados_detalhe.columns]
                    
                    df_exibicao = df_cortados_detalhe[colunas_presentes].copy()
                    
                    # Renomear colunas para exibição amigável
                    mapa_nomes_colunas = {
                        "NUMERO_NT": "NT", "MATERIAL": "Código Material", "DESC_MATERIAL": "Descrição Material",
                        "QUANT_NT": "Qtd. (Original)", "OPERADOR_CORTE": "Operador Identificado"
                    }
                    # Adicionar QUANT_NT_NUM se existir, para clareza
                    if "QUANT_NT_NUM" in df_cortados_detalhe.columns:
                         if "QUANT_NT_NUM" not in df_exibicao.columns: # Adiciona se não foi pega por colunas_presentes
                            df_exibicao["QUANT_NT_NUM"] = df_cortados_detalhe["QUANT_NT_NUM"]
                         mapa_nomes_colunas["QUANT_NT_NUM"] = "Qtd. (Numérico)"

                    df_exibicao.rename(columns=mapa_nomes_colunas, inplace=True)
                    
                    st.dataframe(df_exibicao, use_container_width=True)
                else:
                    st.info("Nenhum detalhe de item cortado disponível.")
            except Exception as e:
                log_erro(f"Erro ao exibir detalhes dos itens cortados: {str(e)}", mostrar_ui=True)
                st.error("Erro ao exibir detalhes dos itens cortados. Veja os logs para mais detalhes.")
        
        # Informação sobre o filtro de data
        st.info("📅 **Nota:** Esta análise considera apenas dados com DT_PLANEJADA igual à data atual do sistema.")

    except Exception as e:
        log_erro(f"Erro geral na página de análise de cortes: {str(e)}", mostrar_ui=True)
        st.error(f"Ocorreu um erro crítico ao processar a análise de cortes: {str(e)}")
        st.error("Verifique os logs para mais detalhes ou contate o suporte.")