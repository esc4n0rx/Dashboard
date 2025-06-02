"""
Módulo de processamento de dados para o Dashboard de Logística.
Gerencia o carregamento, transformação e análise dos dados.
"""
import pandas as pd
import os
import datetime
from logistica_logger import log_info, log_erro, log_debug, log_aviso, log_sucesso
from logistica_config import SAP_EXPORT_PATH, USUARIOS_NORMAL, USAR_NOVA_LOGICA_DATAS

# Pasta para backup de dados
BACKUP_DIR = "backup_dados"
os.makedirs(BACKUP_DIR, exist_ok=True)

def carregar_dados():
    """
    Carrega dados do arquivo CSV exportado pelo SAP sem transformações.
    
    Returns:
        DataFrame: DataFrame pandas com os dados ou DataFrame vazio se houver erro.
    """
    log_info("Tentando carregar dados do arquivo CSV...", mostrar_ui=False)
    
    if not os.path.exists(SAP_EXPORT_PATH):
        log_aviso(f"Arquivo não encontrado: {SAP_EXPORT_PATH}", mostrar_ui=False)
        return pd.DataFrame()
    
    try:
        log_debug(f"Lendo arquivo: {SAP_EXPORT_PATH}")
        
        # Ler o arquivo sem conversões automáticas
        df = pd.read_csv(SAP_EXPORT_PATH, sep=";", encoding="latin1", dtype=str)
        
        # Gerar backup dos dados brutos
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"dados_brutos_{timestamp}.csv")
        df.to_csv(backup_path, index=False)
        log_sucesso(f"Backup dos dados brutos criado em: {backup_path}", mostrar_ui=False)
        
        # Log das primeiras linhas para debug
        log_debug(f"Primeiras linhas do CSV:\n{df.head().to_string()}")
        log_debug(f"Colunas encontradas: {df.columns.tolist()}")
        
        # Manter QUANT_NT como está, sem conversão
        if "QUANT_NT" in df.columns:
            # Apenas para log, verificar os valores
            log_debug(f"Primeiros valores de QUANT_NT: {df['QUANT_NT'].head(10).tolist()}")
        else:
            log_aviso("Coluna 'QUANT_NT' não encontrada no CSV", mostrar_ui=False)
            df["QUANT_NT"] = "0"
        
        # Preenche valores NaN em NOME_USUARIO com string vazia para facilitar a lógica
        if "NOME_USUARIO" in df.columns:
            df["NOME_USUARIO"] = df["NOME_USUARIO"].fillna("")
        else:
            log_aviso("Coluna 'NOME_USUARIO' não encontrada no CSV", mostrar_ui=False)
            df["NOME_USUARIO"] = ""
        
        # Valores vazios para ITEM_FINALIZADO
        if "ITEM_FINALIZADO" in df.columns:
            df["ITEM_FINALIZADO"] = df["ITEM_FINALIZADO"].fillna("")
        
        log_info(f"Dados carregados com sucesso. Total de registros: {len(df)}", mostrar_ui=False)
        return df
    
    except Exception as e:
        log_erro("Erro ao carregar o arquivo CSV", mostrar_ui=False, exception=e)
        return pd.DataFrame()

def aplicar_filtro_datas_dashboard(df):
    """
    Aplica o filtro de datas específico para o dashboard baseado na nova lógica.
    
    Lógica da nova feature:
    - DT_PLANEJADA: pode ser hoje ou ontem
    - DT_PRODUCAO: deve ser hoje (data atual)
    
    Args:
        df (DataFrame): DataFrame com os dados carregados.
        
    Returns:
        DataFrame: DataFrame filtrado ou original se nova lógica estiver desabilitada.
    """
    if not USAR_NOVA_LOGICA_DATAS:
        log_debug("Nova lógica de datas desabilitada. Retornando dados sem filtro de data.")
        return df
    
    log_debug("Aplicando nova lógica de filtragem de datas para dashboard...")
    
    # Verificar se as colunas necessárias existem
    if "DT_PLANEJADA" not in df.columns or "DT_PRODUCAO" not in df.columns:
        log_aviso("Colunas DT_PLANEJADA ou DT_PRODUCAO não encontradas. Retornando dados sem filtro.")
        return df
    
    # Obter data atual e ontem
    hoje = datetime.date.today()
    ontem = hoje - datetime.timedelta(days=1)
    
    # Formatar datas para comparação (considerar possíveis formatos)
    hoje_str = hoje.strftime("%d.%m.%Y")
    ontem_str = ontem.strftime("%d.%m.%Y")
    hoje_str_alt = hoje.strftime("%d/%m/%Y")
    ontem_str_alt = ontem.strftime("%d/%m/%Y")
    hoje_str_iso = hoje.strftime("%Y-%m-%d")
    ontem_str_iso = ontem.strftime("%Y-%m-%d")
    
    log_debug(f"Filtrando dados para:")
    log_debug(f"  - DT_PLANEJADA: {ontem_str} ou {hoje_str} (e variações)")
    log_debug(f"  - DT_PRODUCAO: {hoje_str} (e variações)")
    
    try:
        # Criar cópia para não modificar o original
        df_filtrado = df.copy()
        
        # Garantir que as colunas são strings e remover espaços
        df_filtrado["DT_PLANEJADA"] = df_filtrado["DT_PLANEJADA"].astype(str).str.strip()
        df_filtrado["DT_PRODUCAO"] = df_filtrado["DT_PRODUCAO"].astype(str).str.strip()
        
        # Condição para DT_PLANEJADA (ontem OU hoje)
        condicao_planejada = (
            df_filtrado["DT_PLANEJADA"].isin([ontem_str, ontem_str_alt, ontem_str_iso]) |
            df_filtrado["DT_PLANEJADA"].isin([hoje_str, hoje_str_alt, hoje_str_iso])
        )
        
        # Condição para DT_PRODUCAO (apenas hoje)
        condicao_producao = df_filtrado["DT_PRODUCAO"].isin([hoje_str, hoje_str_alt, hoje_str_iso])
        
        # Aplicar filtros combinados
        df_resultado = df_filtrado[condicao_planejada & condicao_producao].copy()
        
        log_info(f"Filtro de datas aplicado: {len(df)} -> {len(df_resultado)} registros", mostrar_ui=False)
        log_debug(f"Registros filtrados por DT_PLANEJADA: {condicao_planejada.sum()}")
        log_debug(f"Registros filtrados por DT_PRODUCAO: {condicao_producao.sum()}")
        log_debug(f"Registros após filtro combinado: {len(df_resultado)}")
        
        return df_resultado
        
    except Exception as e:
        log_erro("Erro ao aplicar filtro de datas", mostrar_ui=False, exception=e)
        log_aviso("Retornando dados sem filtro devido ao erro", mostrar_ui=False)
        return df

def aplicar_filtro_datas_outras_telas(df):
    """
    Aplica filtro de data para outras telas (Cálculos, Cortes, etc.).
    
    Lógica: DT_PLANEJADA = data atual (hoje)
    
    Args:
        df (DataFrame): DataFrame com os dados carregados.
        
    Returns:
        DataFrame: DataFrame filtrado por data atual.
    """
    log_debug("Aplicando filtro de data atual para outras telas...")
    
    # Verificar se a coluna necessária existe
    if "DT_PLANEJADA" not in df.columns:
        log_aviso("Coluna DT_PLANEJADA não encontrada. Retornando dados sem filtro.")
        return df
    
    # Obter data atual
    hoje = datetime.date.today()
    
    # Formatar datas para comparação (considerar possíveis formatos)
    hoje_str = hoje.strftime("%d.%m.%Y")
    hoje_str_alt = hoje.strftime("%d/%m/%Y")
    hoje_str_iso = hoje.strftime("%Y-%m-%d")
    
    log_debug(f"Filtrando dados para DT_PLANEJADA = {hoje_str} (e variações)")
    
    try:
        # Criar cópia para não modificar o original
        df_filtrado = df.copy()
        
        # Garantir que a coluna é string e remover espaços
        df_filtrado["DT_PLANEJADA"] = df_filtrado["DT_PLANEJADA"].astype(str).str.strip()
        
        # Condição para DT_PLANEJADA (apenas hoje)
        condicao_planejada = df_filtrado["DT_PLANEJADA"].isin([hoje_str, hoje_str_alt, hoje_str_iso])
        
        # Aplicar filtro
        df_resultado = df_filtrado[condicao_planejada].copy()
        
        log_info(f"Filtro de data atual aplicado: {len(df)} -> {len(df_resultado)} registros", mostrar_ui=False)
        
        return df_resultado
        
    except Exception as e:
        log_erro("Erro ao aplicar filtro de data atual", mostrar_ui=False, exception=e)
        log_aviso("Retornando dados sem filtro devido ao erro", mostrar_ui=False)
        return df

def classificar_status(grupo):
    """
    Classifica o status de uma NT com base nas regras de negócio.
    
    Args:
        grupo (DataFrame): Grupo de linhas de uma NT.
        
    Returns:
        str: Status da NT ('Finalizadas', 'Pendentes', ou 'Em Separação').
    """
    # Log para debugging da classificação
    n_finalizado = (grupo["ITEM_FINALIZADO"] == "X").sum()
    total_itens = len(grupo)
    vazios = (grupo["NOME_USUARIO"] == "").sum()
    
    log_debug(f"NT {grupo['NUMERO_NT'].iloc[0]}: {n_finalizado}/{total_itens} finalizados, {vazios} vazios")
    
    if all(grupo["ITEM_FINALIZADO"] == "X"):
        return "Finalizadas"
    elif any(grupo["ITEM_FINALIZADO"] != "X") and all(grupo["NOME_USUARIO"] == ""):
        return "Pendentes"
    else:
        return "Em Separação"

def processar_dados(df, deposito, tipo_tela="dashboard"):
    """
    Processa os dados conforme requisitos de negócio e gera métricas.
    
    Args:
        df (DataFrame): DataFrame com os dados carregados.
        deposito (str): Código do depósito para filtrar os dados.
        tipo_tela (str): Tipo de tela ("dashboard", "calculos", "cortes", etc.)
        
    Returns:
        dict: Dicionário com todas as métricas processadas ou None se não houver dados.
    """
    log_info(f"Processando dados para o depósito {deposito} (tela: {tipo_tela})...", mostrar_ui=False)
    
    if df.empty:
        log_aviso("DataFrame vazio, nenhum dado para processar", mostrar_ui=False)
        return None
    
    # Aplicar filtro de datas baseado no tipo de tela
    if tipo_tela == "dashboard":
        df_com_filtro_data = aplicar_filtro_datas_dashboard(df)
    else:
        df_com_filtro_data = aplicar_filtro_datas_outras_telas(df)
    
    if df_com_filtro_data.empty:
        log_aviso(f"Nenhum registro encontrado após aplicar filtro de datas para {tipo_tela}", mostrar_ui=False)
        return None
    
    # Verificar se a coluna de depósito existe
    if "DEPOSITO" not in df_com_filtro_data.columns:
        log_aviso("Coluna 'DEPOSITO' não encontrada no DataFrame", mostrar_ui=False)
        return None
    
    # Filtra por depósito
    df_filtrado = df_com_filtro_data[df_com_filtro_data["DEPOSITO"] == deposito].copy()
    log_debug(f"Registros após filtro de depósito {deposito}: {len(df_filtrado)}")
    
    if df_filtrado.empty:
        log_aviso(f"Nenhum registro encontrado para o depósito {deposito}", mostrar_ui=False)
        return None
    
    # Calcula métricas básicas
    total_linhas = len(df_filtrado)
    finalizadas = (df_filtrado["ITEM_FINALIZADO"] == "X").sum()
    
    # Soma de QUANT_NT - tenta converter na hora de somar, sem modificar o DataFrame
    if "QUANT_NT" in df_filtrado.columns:
        # Substituir vírgulas por pontos para conversão numérica temporária
        quant_nt_ajustado = df_filtrado["QUANT_NT"].str.replace(',', '.', regex=False)
        try:
            # Tentar converter para float apenas para soma
            quant_nt_numerico = pd.to_numeric(quant_nt_ajustado, errors="coerce")
            total_um = quant_nt_numerico.sum()
            log_debug(f"Soma de QUANT_NT calculada: {total_um}")
        except Exception as e:
            log_erro(f"Erro ao somar QUANT_NT: {str(e)}", mostrar_ui=False)
            total_um = 0
    else:
        total_um = 0
        log_aviso("Coluna QUANT_NT não encontrada para soma", mostrar_ui=False)
    
    log_debug(f"Métricas básicas: total_linhas={total_linhas}, finalizadas={finalizadas}, total_um={total_um}")
    
    # Classifica registros como Normal ou Reforço
    if "USUARIO" in df_filtrado.columns:
        df_filtrado["TIPO"] = df_filtrado["USUARIO"].apply(
            lambda x: "Normal" if x in USUARIOS_NORMAL else "Reforço"
        )
        # Log de distribuição de tipos para debug
        tipo_counts = df_filtrado["TIPO"].value_counts()
        log_debug(f"Distribuição de tipos: {tipo_counts.to_dict()}")
    else:
        log_aviso("Coluna 'USUARIO' não encontrada no DataFrame", mostrar_ui=False)
        df_filtrado["TIPO"] = "Indefinido"
    
    # Separa dados por tipo
    df_normal = df_filtrado[df_filtrado["TIPO"] == "Normal"]
    df_reforco = df_filtrado[df_filtrado["TIPO"] == "Reforço"]
    
    normal_linhas = len(df_normal)
    reforco_linhas = len(df_reforco)
    
    # Soma de QUANT_NT para Normal e Reforço - novamente, convertendo temporariamente
    normal_um = 0
    reforco_um = 0
    
    if "QUANT_NT" in df_normal.columns:
        quant_nt_normal = df_normal["QUANT_NT"].str.replace(',', '.', regex=False)
        try:
            normal_um = pd.to_numeric(quant_nt_normal, errors="coerce").sum()
        except:
            normal_um = 0
    
    if "QUANT_NT" in df_reforco.columns:
        quant_nt_reforco = df_reforco["QUANT_NT"].str.replace(',', '.', regex=False)
        try:
            reforco_um = pd.to_numeric(quant_nt_reforco, errors="coerce").sum()
        except:
            reforco_um = 0
    
    log_debug(f"Métricas por tipo: normal_linhas={normal_linhas}, normal_um={normal_um}, "
              f"reforco_linhas={reforco_linhas}, reforco_um={reforco_um}")
    
    # Verifica se existe a coluna NUMERO_NT antes de processar status
    if "NUMERO_NT" not in df_filtrado.columns:
        log_aviso("Coluna 'NUMERO_NT' não encontrada no DataFrame", mostrar_ui=False)
        status_nts = pd.DataFrame(columns=["NUMERO_NT", "Status", "TIPO"])
        status_counts = pd.DataFrame(index=["Normal", "Reforço"], 
                                    columns=["Finalizadas", "Em Separação", "Pendentes"]).fillna(0)
    else:
        # Processa status das NTs
        status_list = []
        for numero_nt, grupo in df_filtrado.groupby("NUMERO_NT"):
            status = classificar_status(grupo)
            tipo = grupo["TIPO"].iloc[0]
            status_list.append({
                "NUMERO_NT": numero_nt,
                "Status": status,
                "TIPO": tipo
            })
        
        status_nts = pd.DataFrame(status_list)
        log_debug(f"Status processados para {len(status_list)} NTs")
        
        # Garantir que temos ambos os tipos no DataFrame de contagem
        if status_nts.empty:
            status_counts = pd.DataFrame(index=["Normal", "Reforço"], 
                                      columns=["Finalizadas", "Em Separação", "Pendentes"]).fillna(0)
        else:
            # Conta NTs por status e tipo
            try:
                status_counts = status_nts.groupby(["TIPO", "Status"]).count()["NUMERO_NT"].unstack().fillna(0).astype(int)
                
                # Garantir que ambos os tipos estão presentes
                if "Normal" not in status_counts.index:
                    status_counts.loc["Normal"] = 0
                if "Reforço" not in status_counts.index:
                    status_counts.loc["Reforço"] = 0
                
                # Garantir que todas as colunas de status estão presentes
                for status in ["Finalizadas", "Em Separação", "Pendentes"]:
                    if status not in status_counts.columns:
                        status_counts[status] = 0
                
                log_debug(f"Contagem de status após correções: \n{status_counts}")
            except Exception as e:
                log_erro("Erro ao criar contagem de status", mostrar_ui=False, exception=e)
                status_counts = pd.DataFrame(index=["Normal", "Reforço"], 
                                         columns=["Finalizadas", "Em Separação", "Pendentes"]).fillna(0)
    
    # Retorna dicionário com todas as métricas
    resultado = {
        "df": df_filtrado,
        "total_linhas": total_linhas,
        "finalizadas": finalizadas,
        "total_um": int(total_um),
        "normal_linhas": normal_linhas,
        "normal_um": int(normal_um),
        "reforco_linhas": reforco_linhas,
        "reforco_um": int(reforco_um),
        "status_counts": status_counts,
        "status_nts": status_nts
    }
    
    log_info("Processamento de dados concluído com sucesso", mostrar_ui=False)
    return resultado