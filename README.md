# Dashboard de Produção - Logística

![Badge Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Badge Streamlit](https://img.shields.io/badge/Streamlit-1.24.0-red)
![Badge Plotly](https://img.shields.io/badge/Plotly-5.13.0-green)

Dashboard para acompanhamento em tempo real da produção no setor de logística, com integração SAP.

![Dashboard Screenshot](https://via.placeholder.com/800x400?text=Dashboard+de+Logística)

## 📋 Descrição

Este dashboard foi desenvolvido para substituir uma planilha VBA antiga, oferecendo uma visualização mais moderna e interativa dos dados de separação de produtos do SAP. O sistema permite monitorar a produção de dois setores (Mercearia e Perecíveis) com métricas de acompanhamento em tempo real.

### Funcionalidades Principais

- Extração automática de dados do SAP
- Visualização de métricas de produção (linhas, UM)
- Segmentação por tipo (Normal e Reforço)
- Controle de status de NTs (Finalizadas, Em Separação, Pendentes)
- Dashboard interativo com gráficos e tabelas
- Suporte para múltiplos depósitos (DP01 e DP40)

## 🚀 Como Usar

### Pré-requisitos

- Python 3.9 ou superior
- Acesso ao SAP com permissões para transação específica
- Bibliotecas Python conforme `requirements.txt`
- Conexão com a rede onde está localizado o arquivo CSV exportado pelo SAP

### Instalação

1. Clone este repositório:
   ```bash
   git clone https://seu-repositorio/dashboard-logistica.git
   cd dashboard-logistica
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o aplicativo:
   ```bash
   streamlit run main.py
   ```

4. Acesse pelo navegador em `http://localhost:8501`

### Uso em Rede (Ambiente Empresarial)

Para disponibilizar o dashboard para toda a empresa:

```bash
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

Compartilhe o link http://[seu-ip]:8501 com os usuários.

## 🏗️ Estrutura do Projeto

```
dashboard-logistica/
├── main.py                   # Ponto de entrada do aplicativo
├── logistica_app.py          # Interface principal do Streamlit
├── logistica_config.py       # Configurações e constantes
├── logistica_logger.py       # Sistema de logs
├── logistica_sap.py          # Conector com o SAP
├── logistica_processador.py  # Processamento de dados
├── logistica_graficos.py     # Visualizações e gráficos
├── requirements.txt          # Dependências do projeto
├── .gitignore                # Arquivos ignorados pelo git
└── logs/                     # Diretório para armazenamento de logs
└── backup_dados/             # Diretório para backup de dados brutos
```

## 📊 Explicação das Métricas

- **Total de Linhas**: Número total de itens a serem separados
- **Finalizadas**: Itens já separados (ITEM_FINALIZADO = "X")
- **Total de UM**: Soma das quantidades de todos os itens (QUANT_NT)
- **% Finalizadas**: Percentual de linhas já finalizadas

### Classificação de Status (NTs)

- **Finalizadas**: Todas as linhas da NT estão com ITEM_FINALIZADO = "X"
- **Em Separação**: Ao menos uma linha tem um separador atribuído (NOME_USUARIO preenchido)
- **Pendentes**: Nenhuma linha tem separador e ao menos uma não está finalizada

## 🔧 Configuração

As principais configurações estão no arquivo `logistica_config.py`:

- `SAP_EXPORT_PATH`: Caminho para o arquivo CSV exportado pelo SAP
- `USUARIOS_NORMAL`: Lista de usuários classificados como "Normal" (vs. "Reforço")
- `DEPOSITOS`: Mapeamento de setores para códigos de depósito

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é para uso interno da empresa. Todos os direitos reservados.

## 📞 Contato

Para suporte ou dúvidas, entre em contato com a equipe de desenvolvimento.