# TradingAgents Web Dashboard

Web interface completa para visualização e análise de resultados do TradingAgents usando Streamlit.

## Instalação

```bash
pip install -r web_dashboard/requirements.txt
```

## Uso

Execute o dashboard a partir do diretório raiz do projeto:

```bash
streamlit run web_dashboard/app.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`

## Funcionalidades

### 🏠 Dashboard Principal
- Visão geral de todos os tickers analisados
- Últimas decisões de trading (BUY/HOLD/SELL)
- Gráficos de preços em tempo real com candlesticks
- Volume de negociação
- Histórico de decisões por ticker
- Indicadores técnicos
- Fontes de notícias com links
- Métricas fundamentalistas

### 📄 Visualizador de Relatórios
- Visualização de relatórios markdown formatados
- Suporte para EN e PT-BR
- Todos os tipos de relatórios:
  - Final Decision
  - Trader Investment Plan
  - Investment Plan
  - Market Analysis
  - Sentiment Analysis
  - News Analysis
  - Fundamentals
- Download de relatórios individuais

### 🔍 Comparação Multi-Ticker
- Comparação entre múltiplos tickers
- Gráficos de preços normalizados sobrepostos
- Comparação de volume
- Matriz de correlação de retornos
- Análise de volatilidade comparativa
- Histórico de decisões em timeline
- Exportação de dados (CSV, JSON, Excel, Markdown)

### 💼 Gerenciador de Portfólio
- Adicionar e gerenciar posições
- Cálculo automático de P&L
- Métricas de risco:
  - Volatilidade do portfólio
  - Sharpe Ratio
  - Maximum Drawdown
  - Value at Risk (VaR)
- Gráficos de alocação (pie chart)
- Gráficos de performance por posição
- Gráfico waterfall de ganhos/perdas
- Matriz de correlação de ativos
- Análise de risco individual por posição

### 🔔 Sistema de Alertas
- Criar alertas personalizados:
  - **Alertas de Preço**: notificação quando preço cruza um valor
  - **Alertas de Decisão**: notificação quando há nova decisão BUY/SELL/HOLD
  - **Alertas de Volatilidade**: notificação quando volatilidade excede threshold
- Monitoramento em tempo real
- Histórico de alertas disparados
- Exportar/importar configurações de alertas (JSON)

### 📈 Analytics e Backtesting
- **Backtesting de Estratégias**:
  - Simulação de trading baseada em decisões históricas
  - Capital inicial configurável
  - Métricas de performance:
    - Retorno total
    - Sharpe Ratio
    - Max Drawdown
    - Win Rate
  - Gráfico de evolução do portfólio
  - Histórico detalhado de trades
- **Análise de Padrões de Decisão**:
  - Distribuição de decisões (BUY/HOLD/SELL)
  - Timeline de decisões
  - Estatísticas por ticker
- **Comparação de Performance**:
  - Backtest de múltiplos tickers
  - Comparação de retornos
  - Gráficos sobrepostos de performance

### ⚙️ Configurações
- **Display**:
  - Tema (light/dark)
  - Intervalo de auto-refresh
  - Número máximo de tickers exibidos
  - Visibilidade de widgets
  - Personalização de cores para BUY/HOLD/SELL
- **Dados**:
  - Moeda padrão
  - Período de tempo padrão
  - Fonte de dados (Yahoo Finance, Alpha Vantage)
  - Duração de cache
  - Formato de exportação padrão
- **Notificações**:
  - Habilitar/desabilitar notificações
  - Thresholds de alertas
  - Email e webhook para notificações
- **API Keys**:
  - Alpha Vantage
  - News API
- Exportar/importar configurações

## Estrutura

```
web_dashboard/
├── app.py                      # Aplicação principal
├── requirements.txt            # Dependências
├── settings.json              # Configurações do usuário (gerado)
├── utils/
│   ├── data_loader.py         # Carregador de dados
│   └── export_utils.py        # Utilitários de exportação
└── pages/
    ├── dashboard.py           # Dashboard principal
    ├── report_viewer.py       # Visualizador de relatórios
    ├── comparison.py          # Comparação multi-ticker
    ├── portfolio.py           # Gerenciador de portfólio
    ├── alerts.py              # Sistema de alertas
    ├── analytics.py           # Analytics e backtesting
    └── settings.py            # Página de configurações
```

## Requisitos

- Python 3.10+
- Streamlit 1.39+
- Pandas 2.0+
- Plotly 6.3+
- yfinance 0.2+
- xlsxwriter 3.1+
- openpyxl 3.1+
- Resultados do TradingAgents em `./results/`

## Exportação de Dados

O dashboard suporta exportação em múltiplos formatos:

- **CSV**: Dados tabulares simples
- **JSON**: Dados estruturados com metadados
- **Excel**: Planilhas formatadas com múltiplas sheets
- **Markdown**: Relatórios formatados e legíveis

## Notas

- O dashboard lê diretamente da pasta `results/`
- Não modifica arquivos originais
- Suporta multi-idioma (EN/PT-BR)
- Atualiza automaticamente quando novos resultados são adicionados
- Dados de preços em tempo real via Yahoo Finance
- Portfolio e alertas são salvos no session state do Streamlit
- Configurações são persistidas em `settings.json`

## Roadmap Futuro

- [ ] Integração com mais fontes de dados (Alpha Vantage, etc)
- [ ] Notificações por email e webhook
- [ ] Suporte a múltiplos portfólios
- [ ] Análise de sentimento de notícias em tempo real
- [ ] Recomendações baseadas em ML
- [ ] Testes A/B de estratégias
- [ ] API REST para acesso programático
