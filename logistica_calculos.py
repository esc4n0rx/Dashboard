"""
Módulo de cálculos avançados para o Dashboard de Logística.
Gerencia o ranking de operação e previsão de conclusão.
"""
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
from logistica_logger import log_debug, log_info, log_aviso
from logistica_config import CORES

# Variável global para armazenar o histórico de progresso
# Formato: {timestamp: {deposito: {'total': X, 'finalizadas': Y}}}
historico_progresso = {}

def calcular_ranking_usuarios(df, deposito=None):
    """
    Calcula o ranking de usuários baseado em linhas finalizadas.
    
    Args:
        df (DataFrame): DataFrame com os dados carregados.
        deposito (str, optional): Código do depósito para filtrar os dados. 
                                 Se None, calcula para todos.
    
    Returns:
        DataFrame: DataFrame com o ranking dos usuários.
    """
    log_debug(f"Calculando ranking de usuários para depósito: {deposito}")
    
    if df.empty:
        log_aviso("DataFrame vazio, impossível calcular ranking")
        return pd.DataFrame(columns=["NOME_USUARIO", "TOTAL_FINALIZADAS", "POSICAO"])
    
    # Verificar se as colunas necessárias existem
    colunas_necessarias = ["NOME_USUARIO", "ITEM_FINALIZADO", "DEPOSITO"]
    for coluna in colunas_necessarias:
        if coluna not in df.columns:
            log_aviso(f"Coluna '{coluna}' não encontrada no DataFrame")
            return pd.DataFrame(columns=["NOME_USUARIO", "TOTAL_FINALIZADAS", "POSICAO"])
    
    # Filtrar por depósito se especificado
    if deposito:
        df_filtrado = df[df["DEPOSITO"] == deposito].copy()
        log_debug(f"Filtrado para depósito {deposito}: {len(df_filtrado)} registros")
    else:
        df_filtrado = df.copy()
    
    # Filtrar apenas itens finalizados (ITEM_FINALIZADO = "X")
    df_finalizados = df_filtrado[df_filtrado["ITEM_FINALIZADO"] == "X"].copy()
    log_debug(f"Itens finalizados: {len(df_finalizados)} registros")
    
    # Remover usuários vazios
    df_finalizados = df_finalizados[df_finalizados["NOME_USUARIO"] != ""]
    
    if df_finalizados.empty:
        log_aviso("Nenhum item finalizado encontrado com nome de usuário")
        return pd.DataFrame(columns=["NOME_USUARIO", "TOTAL_FINALIZADAS", "POSICAO"])
    
    # Contar itens finalizados por usuário
    ranking = df_finalizados.groupby("NOME_USUARIO").size().reset_index()
    ranking.columns = ["NOME_USUARIO", "TOTAL_FINALIZADAS"]
    
    # Ordenar por total de itens finalizados (decrescente)
    ranking = ranking.sort_values("TOTAL_FINALIZADAS", ascending=False).reset_index(drop=True)
    
    # Adicionar posição no ranking (1º, 2º, etc.)
    ranking["POSICAO"] = ranking.index + 1
    
    # Formatar a posição com ordinal
    ranking["POSICAO_TEXTO"] = ranking["POSICAO"].apply(formatar_posicao)
    
    log_debug(f"Ranking calculado: {len(ranking)} usuários")
    return ranking

def formatar_posicao(posicao):
    """
    Formata a posição com ordinal (1º, 2º, etc.).
    
    Args:
        posicao (int): Número da posição.
        
    Returns:
        str: Posição formatada.
    """
    return f"{posicao}º"

def registrar_progresso(dados, deposito):
    """
    Registra o progresso atual no histórico.
    
    Args:
        dados (dict): Dicionário com as métricas calculadas.
        deposito (str): Código do depósito.
    """
    agora = datetime.datetime.now()
    timestamp = agora.strftime("%Y-%m-%d %H:%M:%S")
    
    # Inicializar o dicionário do timestamp se for a primeira vez
    if timestamp not in historico_progresso:
        historico_progresso[timestamp] = {}
    
    # Registrar progresso para o depósito
    historico_progresso[timestamp][deposito] = {
        'total': dados['total_linhas'],
        'finalizadas': dados['finalizadas'],
        'timestamp': agora
    }
    
    # Limitar o tamanho do histórico (manter apenas os últimos 20 registros por depósito)
    if len(historico_progresso) > 20:
        # Ordenar timestamps e remover o mais antigo
        timestamps_ordenados = sorted(historico_progresso.keys())
        timestamp_antigo = timestamps_ordenados[0]
        del historico_progresso[timestamp_antigo]
    
    log_debug(f"Progresso registrado para {deposito} em {timestamp}: total={dados['total_linhas']}, finalizadas={dados['finalizadas']}")

def calcular_previsao_conclusao(deposito):
    """
    Calcula a previsão de conclusão baseado no histórico de progresso.
    
    Args:
        deposito (str): Código do depósito.
        
    Returns:
        dict: Dicionário com informações da previsão.
    """
    log_debug(f"Calculando previsão de conclusão para depósito: {deposito}")
    
    # Verificar se há histórico suficiente (pelo menos 2 registros)
    timestamps = sorted(historico_progresso.keys())
    
    # Filtrar apenas timestamps que contêm o depósito especificado
    timestamps_deposito = [ts for ts in timestamps if deposito in historico_progresso[ts]]
    
    if len(timestamps_deposito) < 2:
        log_aviso(f"Histórico insuficiente para depósito {deposito}. Necessário pelo menos 2 registros.")
        return {
            'status': 'insuficiente',
            'mensagem': 'Histórico insuficiente para calcular previsão. Atualize mais vezes.',
            'ultimo_progresso': historico_progresso[timestamps_deposito[-1]][deposito] if timestamps_deposito else None
        }
    
    # Pegar o registro mais recente e o anterior
    ultimo_ts = timestamps_deposito[-1]
    penultimo_ts = timestamps_deposito[-2]
    
    ultimo = historico_progresso[ultimo_ts][deposito]
    penultimo = historico_progresso[penultimo_ts][deposito]
    
    # Calcular a taxa de progresso (itens finalizados por minuto)
    delta_finalizadas = ultimo['finalizadas'] - penultimo['finalizadas']
    
    # Converter strings para objetos datetime
    if isinstance(ultimo['timestamp'], str):
        ultimo_time = datetime.datetime.strptime(ultimo['timestamp'], "%Y-%m-%d %H:%M:%S")
    else:
        ultimo_time = ultimo['timestamp']
        
    if isinstance(penultimo['timestamp'], str):
        penultimo_time = datetime.datetime.strptime(penultimo['timestamp'], "%Y-%m-%d %H:%M:%S")
    else:
        penultimo_time = penultimo['timestamp']
    
    delta_tempo = (ultimo_time - penultimo_time).total_seconds() / 60  # em minutos
    
    # Verificar se houve progresso
    if delta_finalizadas <= 0 or delta_tempo <= 0:
        return {
            'status': 'sem_progresso',
            'mensagem': 'Nenhum progresso detectado desde a última atualização.',
            'ultimo_progresso': ultimo
        }
    
    # Calcular taxa de progresso (itens por minuto)
    taxa_progresso = delta_finalizadas / delta_tempo
    
    # Calcular itens restantes
    itens_restantes = ultimo['total'] - ultimo['finalizadas']
    
    # Calcular tempo restante em minutos
    if taxa_progresso > 0:
        tempo_restante_min = itens_restantes / taxa_progresso
    else:
        tempo_restante_min = float('inf')  # Infinito se a taxa for zero
    
    # Calcular horário previsto de conclusão
    horario_conclusao = ultimo_time + datetime.timedelta(minutes=tempo_restante_min)
    
    # Formatar resultados
    return {
        'status': 'ok',
        'delta_finalizadas': delta_finalizadas,
        'delta_tempo_min': delta_tempo,
        'taxa_progresso': taxa_progresso,  # itens por minuto
        'itens_restantes': itens_restantes,
        'tempo_restante_min': tempo_restante_min,
        'horario_conclusao': horario_conclusao,
        'horario_conclusao_formatado': horario_conclusao.strftime("%H:%M - %d/%m/%Y"),
        'ultimo_progresso': ultimo
    }

def criar_grafico_ranking(ranking, top_n=10):
    """
    Cria um gráfico de barras horizontais para o ranking de usuários.
    
    Args:
        ranking (DataFrame): DataFrame com o ranking dos usuários.
        top_n (int): Número de usuários a serem exibidos no ranking.
        
    Returns:
        Figure: Objeto de figura do Plotly.
    """
    if ranking.empty or len(ranking) == 0:
        # Retornar um gráfico vazio
        fig = go.Figure()
        fig.update_layout(
            title="Ranking de Operação - Nenhum dado disponível",
            height=400,
            plot_bgcolor="#121212",
            paper_bgcolor="#121212",
            font=dict(color="#F5F5F5"),
        )
        return fig
    
    # Limitar ao top N
    if len(ranking) > top_n:
        ranking_plot = ranking.head(top_n).copy()
    else:
        ranking_plot = ranking.copy()
    
    # Reverter para exibição do menor para o maior (de baixo para cima)
    ranking_plot = ranking_plot.iloc[::-1].reset_index(drop=True)
    
    # Preparar lista de cores (destacar o primeiro colocado)
    cores = [CORES["destaque"] if i == len(ranking_plot) - 1 else CORES["primaria"] for i in range(len(ranking_plot))]
    
    # Criar o gráfico
    fig = go.Figure()
    
    # Adicionar barras
    fig.add_trace(go.Bar(
        y=ranking_plot["NOME_USUARIO"],
        x=ranking_plot["TOTAL_FINALIZADAS"],
        orientation='h',
        marker_color=cores,
        text=ranking_plot["TOTAL_FINALIZADAS"],
        textposition='inside',
        textfont=dict(color="#121212"),
    ))
    
    # Adicionar posição ao lado do nome
    nomes_com_posicao = [f"{pos}. {nome}" for nome, pos in zip(ranking_plot["NOME_USUARIO"], ranking_plot["POSICAO_TEXTO"])]
    
    # Atualizar layout para tema escuro
    fig.update_layout(
        title={
            'text': "Ranking de Operação",
            'font': {'color': "#BB8674", 'size': 20}
        },
        yaxis=dict(
            title="Usuário",
            titlefont=dict(color="#F5F5F5"),
            tickmode='array',
            tickvals=ranking_plot["NOME_USUARIO"],
            ticktext=nomes_com_posicao,
            tickfont=dict(color="#F5F5F5"),
            gridcolor="#333333",
        ),
        xaxis=dict(
            title="Total de Linhas Finalizadas",
            titlefont=dict(color="#F5F5F5"),
            tickfont=dict(color="#F5F5F5"),
            gridcolor="#333333",
        ),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="#121212",
        paper_bgcolor="#121212",
    )
    
    # Adicionar anotação de coroa para o primeiro lugar
    if len(ranking_plot) > 0:
        primeiro_lugar_idx = len(ranking_plot) - 1  # Último na lista (invertida)
        fig.add_annotation(
            x=0,
            y=ranking_plot["NOME_USUARIO"][primeiro_lugar_idx],
            text="👑",
            showarrow=False,
            font=dict(size=20),
            xanchor="right",
            xshift=-15,
        )
    
    return fig

def criar_cartao_previsao(previsao, deposito):
    """
    Cria um cartão HTML com a previsão de conclusão.
    
    Args:
        previsao (dict): Dicionário com informações da previsão.
        deposito (str): Código do depósito.
        
    Returns:
        str: HTML formatado para o cartão.
    """
    if previsao['status'] == 'insuficiente':
        return f"""
        <div class="warning">
            <h3>Previsão de Conclusão - Depósito {deposito}</h3>
            <p>Histórico insuficiente para calcular previsão.</p>
            <p>Atualize o dashboard pelo menos 2 vezes para obter uma previsão.</p>
        </div>
        """
    
    if previsao['status'] == 'sem_progresso':
        return f"""
        <div class="warning">
            <h3>Previsão de Conclusão - Depósito {deposito}</h3>
            <p>Nenhum progresso detectado desde a última atualização.</p>
            <p>Último registro: {previsao['ultimo_progresso']['finalizadas']} de {previsao['ultimo_progresso']['total']} itens finalizados.</p>
        </div>
        """
    
    # Formatação de tempo restante
    horas_restantes = int(previsao['tempo_restante_min'] // 60)
    minutos_restantes = int(previsao['tempo_restante_min'] % 60)
    tempo_restante_formatado = f"{horas_restantes}h {minutos_restantes}min"
    
    # Calcular percentual concluído
    total = previsao['ultimo_progresso']['total']
    finalizadas = previsao['ultimo_progresso']['finalizadas']
    percentual = round((finalizadas / total) * 100) if total > 0 else 0
    
    # Definir classe CSS baseada no tempo restante
    if horas_restantes < 1:
        classe = "success"
    elif horas_restantes < 3:
        classe = "highlight"
    else:
        classe = "metric-card"
    
    return f"""
    <div class="{classe}">
        <h3>Previsão de Conclusão - Depósito {deposito}</h3>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <div>
                <h4>Status Atual</h4>
                <p><b>{finalizadas}</b> de <b>{total}</b> itens finalizados</p>
                <p><b>{percentual}%</b> concluído</p>
            </div>
            <div>
                <h4>Taxa de Progresso</h4>
                <p><b>{round(previsao['taxa_progresso'], 2)}</b> itens/min</p>
                <p><b>{round(previsao['delta_finalizadas'])}</b> itens em <b>{round(previsao['delta_tempo_min'])}</b> min</p>
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
            <div>
                <h4>Tempo Restante</h4>
                <p><b>{tempo_restante_formatado}</b></p>
                <p><b>{previsao['itens_restantes']}</b> itens restantes</p>
            </div>
            <div>
                <h4>Previsão de Conclusão</h4>
                <p style="font-size: 1.2em; font-weight: bold; color: #FFB74D;">
                    {previsao['horario_conclusao_formatado']}
                </p>
            </div>
        </div>
    </div>
    """

def exibir_pagina_calculos(df, deposito):
    """
    Exibe a página de cálculos no Streamlit.
    
    Args:
        df (DataFrame): DataFrame com os dados carregados.
        deposito (str): Código do depósito selecionado.
        
    Returns:
        None
    """
    import streamlit as st
    
    st.title("Cálculos Avançados")
    
    # Seção 1: Ranking da Operação
    st.subheader("🏆 Ranking da Operação")
    
    # Calcular o ranking
    ranking = calcular_ranking_usuarios(df, deposito)
    
    # Exibir o gráfico
    st.plotly_chart(criar_grafico_ranking(ranking), use_container_width=True)
    
    # Exibir uma tabela com o ranking completo
    if not ranking.empty:
        st.write("Ranking completo:")
        # Criar cópia do DataFrame para exibição
        ranking_display = ranking[["POSICAO_TEXTO", "NOME_USUARIO", "TOTAL_FINALIZADAS"]].copy()
        ranking_display.columns = ["Posição", "Usuário", "Total Finalizado"]
        st.dataframe(ranking_display, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para o ranking.")
    
    # Seção 2: Previsão de Conclusão
    st.subheader("⏱️ Previsão de Conclusão da Operação")
    
    # Calcular a previsão
    previsao = calcular_previsao_conclusao(deposito)
    
    # Exibir o cartão de previsão
    st.markdown(criar_cartao_previsao(previsao, deposito), unsafe_allow_html=True)
    
    # Informações adicionais
    st.info("""
    **Como funciona a previsão?** 
    
    O sistema analisa o progresso das operações entre as atualizações e calcula uma taxa média de
    conclusão. Com base nessa taxa, estima o tempo necessário para finalizar os itens restantes.
    
    Para melhorar a precisão da previsão, atualize o dashboard periodicamente.
    """)
    
    # Mostrar histórico de atualizações (expander)
    with st.expander("Histórico de Atualizações"):
        if historico_progresso:
            # Converter o histórico para um formato tabular
            historico_list = []
            for timestamp, depositos in historico_progresso.items():
                if deposito in depositos:
                    historico_list.append({
                        "Timestamp": timestamp,
                        "Total": depositos[deposito]["total"],
                        "Finalizadas": depositos[deposito]["finalizadas"],
                        "% Concluído": f"{round((depositos[deposito]['finalizadas'] / depositos[deposito]['total']) * 100) if depositos[deposito]['total'] > 0 else 0}%"
                    })
            
            if historico_list:
                historico_df = pd.DataFrame(historico_list).sort_values("Timestamp", ascending=False)
                st.dataframe(historico_df, use_container_width=True)
            else:
                st.info(f"Nenhum registro histórico encontrado para o depósito {deposito}.")
        else:
            st.info("Nenhum histórico de atualizações disponível.")