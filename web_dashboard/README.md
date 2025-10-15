# TradingAgents Web Dashboard

Web interface para visualização de resultados do TradingAgents usando Streamlit.

## Instalação

```bash
pip install streamlit pandas
```

## Uso

Execute o dashboard a partir do diretório raiz do projeto:

```bash
streamlit run web_dashboard/app.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`

## Funcionalidades

### Dashboard Principal
- Visão geral de todos os tickers analisados
- Últimas decisões de trading (BUY/HOLD/SELL)
- Histórico de decisões por ticker
- Gráficos de distribuição

### Visualizador de Relatórios
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
- Download de relatórios

### Comparação
- Comparação entre múltiplos tickers
- Distribuição de decisões
- Tabelas comparativas

## Estrutura

```
web_dashboard/
├── app.py                      # Aplicação principal
├── utils/
│   └── data_loader.py         # Carregador de dados
├── pages/
│   ├── dashboard.py           # Página principal
│   ├── report_viewer.py       # Visualizador
│   └── comparison.py          # Comparação
└── README.md
```

## Requisitos

- Python 3.10+
- Streamlit 1.39+
- Resultados do TradingAgents em `./results/`

## Notas

- O dashboard lê diretamente da pasta `results/`
- Não modifica arquivos originais
- Suporta multi-idioma (EN/PT-BR)
- Atualiza automaticamente quando novos resultados são adicionados
