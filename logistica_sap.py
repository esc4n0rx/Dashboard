"""
Módulo de conexão com o SAP para o Dashboard de Logística.
Gerencia a extração de dados do SAP usando automação.
"""
import time
import pythoncom
import win32com.client
import streamlit as st
from datetime import datetime, timedelta
from logistica_logger import log_info, log_erro, log_sucesso, log_debug

def extrair_dados_sap():
    log_info("Iniciando extração de dados do SAP...", mostrar_ui=False)
    
    try:
        hoje = datetime.now()
        ontem = hoje - timedelta(days=1)
        
        data_alta = hoje.strftime("%d.%m.%Y")
        data_baixa = ontem.strftime("%d.%m.%Y")
        
        log_debug(f"Data de início da extração: {data_baixa}")
        log_debug(f"Data de fim da extração: {data_alta}")

        # Inicializa COM para thread atual
        log_debug("Inicializando COM...")
        pythoncom.CoInitialize()
        
        # Conecta ao SAP GUI
        log_debug("Conectando ao SAP GUI...")
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        application = SapGuiAuto.GetScriptingEngine
        connection = application.Children(0)
        session = connection.Children(0)
        
        log_debug("Conexão SAP estabelecida. Executando comandos...")
        
        # Executa comandos SAP
        session.findById("wnd[0]/tbar[0]/okcd").Text = "/nzbi"
        session.findById("wnd[0]").sendVKey(0)
        log_debug("Navegando para transação ZBI...")
        
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        log_debug("Pressionado botão de seleção de usuário...")
        
        session.findById("wnd[1]/usr/txtENAME-LOW").Text = "paul.cunha"
        log_debug("Preenchido usuário para extração...")
        
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").selectedRows = "0"
        session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").doubleClickCurrentCell
        session.findById("wnd[0]").sendVKey(0)
        
        # Inserção das datas dinâmicas
        session.findById("wnd[0]/usr/ctxtSO_PDATU-LOW").text = data_baixa
        session.findById("wnd[0]/usr/ctxtSO_PDATU-HIGH").text = data_alta
        
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        log_debug("Iniciada extração de dados...")
        
        # Aguarda a extração finalizar
        time.sleep(3)
        log_sucesso("Dados extraídos com sucesso do SAP", mostrar_ui=False)
        return True
    
    except Exception as e:
        log_erro("Erro ao extrair dados do SAP", mostrar_ui=False, exception=e)
        return False
    
    finally:
        # Libera recursos COM
        log_debug("Finalizando COM...")
        pythoncom.CoUninitialize()