"""
Módulo de visualizações para o Dashboard de Logística.
Gerencia a criação de gráficos e elementos visuais.
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from logistica_config import CORES
from logistica_logger import log_debug

def criar_grafico_volume_total(dados):
    """
    Cria gráfico de barras horizontais para volume total.
    
    Args:
        dados (dict): Dicionário com as métricas calculadas.
        
    Returns:
        Figure: Objeto de figura do Plotly.
    """
    log_debug("Criando gráfico de volume total...")
    
    # Calcular percentuais
    perc_linhas = round((dados["finalizadas"] / dados["total_linhas"]) * 100) if dados["total_linhas"] > 0 else 0
    
    # AJUSTE: Calcular percentual de UM com base nos itens finalizados
    # Isso reflete melhor o progresso real, mostrando quanta quantidade já foi separada
    perc_um = perc_linhas  # Usar o mesmo percentual das linhas finalizadas
    
    log_debug(f"Valores para gráfico volume total: finalizadas={dados['finalizadas']}, "
              f"total_linhas={dados['total_linhas']}, total_um={dados['total_um']}, "
              f"perc_linhas={perc_linhas}%, perc_um={perc_um}%")
    
    # Criar figura
    fig = make_subplots(
        rows=1, cols=2, 
        subplot_titles=[
            f"LINHAS<br>{dados['finalizadas']}/{dados['total_linhas']}",
            f"UM<br>{dados['total_um']:,}".replace(",", ".")
        ]
    )
    
    # Adicionar barras para LINHAS
    fig.add_trace(
        go.Bar(
            y=["LINHAS"],
            x=[dados["finalizadas"]],
            name="Separado",
            orientation="h",
            marker=dict(color=CORES["sucesso"]),
            text=[f"{perc_linhas}%"],
            textposition="inside",
            insidetextanchor="middle",
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            y=["LINHAS"],
            x=[dados["total_linhas"] - dados["finalizadas"]],
            name="Pendente",
            orientation="h",
            marker=dict(color=CORES["secundaria"]),
        ),
        row=1, col=1
    )
    
    # Adicionar barras para UM - agora mostrando progresso com base no percentual de finalizados
    fig.add_trace(
        go.Bar(
            y=["UM"],
            x=[dados["total_um"] * perc_linhas / 100],  # Quantidade separada estimada
            name="Separado UM",
            orientation="h",
            marker=dict(color=CORES["sucesso"]),
            text=[f"{perc_um}%"],
            textposition="inside",
            insidetextanchor="middle",
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            y=["UM"],
            x=[dados["total_um"] * (100 - perc_linhas) / 100],  # Quantidade pendente estimada
            name="Pendente UM",
            orientation="h",
            marker=dict(color=CORES["secundaria"]),
        ),
        row=1, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        title="Volume Total",
        barmode="stack",
        height=200,
        margin=dict(l=60, r=20, t=80, b=20),
        showlegend=False,
        plot_bgcolor="white",
    )
    
    return fig

def criar_grafico_volume_tipo(dados):
    """
    Cria gráficos para volume por tipo (Normal e Reforço).
    
    Args:
        dados (dict): Dicionário com as métricas calculadas.
        
    Returns:
        Figure: Objeto de figura do Plotly.
    """
    log_debug("Criando gráfico de volume por tipo...")
    
    # Calcular percentuais
    perc_normal_linhas = round((dados["normal_linhas"] / dados["total_linhas"]) * 100) if dados["total_linhas"] > 0 else 0
    perc_reforco_linhas = round((dados["reforco_linhas"] / dados["total_linhas"]) * 100) if dados["total_linhas"] > 0 else 0
    
    log_debug(f"Valores para gráfico volume por tipo: normal_linhas={dados['normal_linhas']}, normal_um={dados['normal_um']}, "
              f"reforco_linhas={dados['reforco_linhas']}, reforco_um={dados['reforco_um']}, "
              f"perc_normal={perc_normal_linhas}%, perc_reforco={perc_reforco_linhas}%")
    
    # Criar figura com subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"Volume Normal<br>{perc_normal_linhas}%",
            f"Reforço<br>{perc_reforco_linhas}%"
        ],
    )
    
    # Dados para o gráfico Normal
    fig.add_trace(
        go.Bar(
            y=["LINHAS", "UM"],
            x=[dados["normal_linhas"], dados["normal_um"]],
            name="Normal",
            orientation="h",
            marker=dict(color=CORES["primaria"]),
            text=[f"{dados['normal_linhas']}", f"{dados['normal_um']:,}".replace(",", ".")],
            textposition="inside",
        ),
        row=1, col=1
    )
    
    # Dados para o gráfico Reforço - garantir que os valores sejam exibidos mesmo se zero
    fig.add_trace(
        go.Bar(
            y=["LINHAS", "UM"],
            x=[dados["reforco_linhas"], dados["reforco_um"]],
            name="Reforço",
            orientation="h",
            marker=dict(color=CORES["primaria"]),
            text=[f"{dados['reforco_linhas']}", f"{dados['reforco_um']:,}".replace(",", ".")],
            textposition="inside",
        ),
        row=1, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        height=200,
        margin=dict(l=60, r=20, t=80, b=20),
        showlegend=False,
        plot_bgcolor="white",
    )
    
    return fig

def criar_grafico_controle_nts(status_counts):
    """
    Cria gráfico de barras para controle de NTs.
    
    Args:
        status_counts (DataFrame): DataFrame com contagem de status por tipo.
        
    Returns:
        Figure: Objeto de figura do Plotly.
    """
    log_debug("Criando gráfico de controle de NTs...")
    log_debug(f"Status counts recebidos: \n{status_counts}")
    
    # Preparar os dados - garantir que todas as colunas existam
    for coluna in ['Finalizadas', 'Em Separação', 'Pendentes']:
        if coluna not in status_counts.columns:
            status_counts[coluna] = 0
    
    # Verificar que ambos os tipos estão presentes
    for tipo in ['Normal', 'Reforço']:
        if tipo not in status_counts.index:
            status_counts.loc[tipo] = [0, 0, 0]
    
    log_debug(f"Status counts após correção: \n{status_counts}")
    
    # Criar figura
    fig = go.Figure()
    
    # Adicionar barras para cada status
    fig.add_trace(go.Bar(
        x=status_counts.index,
        y=status_counts['Finalizadas'],
        name='Finalizadas',
        marker_color=CORES["sucesso"],
        text=status_counts['Finalizadas'],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        x=status_counts.index,
        y=status_counts['Em Separação'],
        name='Em Separação',
        marker_color=CORES["processando"],
        text=status_counts['Em Separação'],
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        x=status_counts.index,
        y=status_counts['Pendentes'],
        name='Pendentes',
        marker_color=CORES["pendente"],
        text=status_counts['Pendentes'],
        textposition='auto',
    ))
    
    # Atualizar layout
    fig.update_layout(
        title="Controle de NTs",
        barmode='stack',
        xaxis_title="Tipo",
        yaxis_title="Quantidade de NTs",
        plot_bgcolor="white",
        height=300,
    )
    
    return fig