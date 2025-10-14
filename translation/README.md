# Translation Module - TradingAgents

Módulo para traduzir relatórios do TradingAgents para Português do Brasil (pt-BR).

## 📋 Características

- ✅ Tradução automática usando OpenAI GPT
- ✅ Preserva formatação markdown
- ✅ Mantém termos técnicos e tickers em inglês
- ✅ Interface CLI simples
- ✅ Suporta tradução individual ou em lote
- ✅ Não interfere com código principal da aplicação

## 🚀 Instalação

O módulo já está incluso no projeto. Certifique-se de ter instalado as dependências:

```bash
pip install langchain-openai
```

## 🔑 Configuração

Configure sua chave de API da OpenAI:

```bash
export OPENAI_API_KEY=sua_chave_aqui
```

Ou adicione ao arquivo `.env` na raiz do projeto:

```bash
OPENAI_API_KEY=sua_chave_aqui
```

## 💻 Uso

### Listar tickers disponíveis

```bash
python -m translation --list-tickers
```

### Traduzir relatórios específicos

```bash
# Traduzir relatórios de um ticker e data específicos
python -m translation --ticker ITSA4.SA --date 2025-10-10
```

### Traduzir todos os relatórios de um ticker

```bash
python -m translation --ticker ITSA4.SA --all-dates
```

### Traduzir todos os relatórios

```bash
python -m translation --all
```

### Opções avançadas

```bash
# Usar modelo diferente (padrão: gpt-4o-mini)
python -m translation --ticker IBM --date 2025-10-10 --model gpt-4o

# Ajustar temperatura (padrão: 0.3)
python -m translation --ticker IBM --date 2025-10-10 --temperature 0.5
```

## 📁 Estrutura de Saída

Os arquivos traduzidos são salvos ao lado dos originais com o sufixo `_pt-BR`:

```
results/
├── ITSA4.SA/
│   └── 2025-10-10/
│       └── reports/
│           ├── final_trade_decision.md
│           ├── final_trade_decision_pt-BR.md  ← Traduzido
│           ├── market_report.md
│           ├── market_report_pt-BR.md         ← Traduzido
│           └── ...
```

## ⚙️ Configuração Avançada

Você pode customizar o comportamento da tradução editando `translation/config.py`:

```python
@dataclass
class TranslationConfig:
    target_language: str = "pt-BR"
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    max_tokens: int = 4000
    preserve_formatting: bool = True
```

## 📝 Prompt de Tradução

O módulo usa um prompt especializado que:

1. Preserva toda formatação markdown
2. Mantém termos técnicos (MACD, RSI, SMA, etc.)
3. Mantém tickers de ações (ITSA4.SA, NVDA, etc.)
4. Mantém nomes de empresas originais
5. Usa terminologia financeira brasileira adequada

## 🎯 Exemplos

### Exemplo 1: Traduzir um único relatório

```bash
python -m translation --ticker BBAS3.SA --date 2025-10-10
```

Saída:
```
Using OpenAI model: gpt-4o-mini
Target language: pt-BR

============================================================
Translating reports: BBAS3.SA - 2025-10-10
============================================================

Found 7 report(s) to translate

Translating final_trade_decision.md...
✓ Saved to results/BBAS3.SA/2025-10-10/reports/final_trade_decision_pt-BR.md
...

============================================================
✓ Successfully translated 7 file(s)
============================================================
```

### Exemplo 2: Traduzir múltiplos tickers

```bash
python -m translation --all
```

## 🔍 Arquivos Traduzíveis

O módulo traduz automaticamente todos os arquivos `.md` na pasta `reports/`:

- `final_trade_decision.md` - Decisão final de trade
- `trader_investment_plan.md` - Plano de investimento do trader
- `investment_plan.md` - Plano de investimento
- `market_report.md` - Relatório de mercado
- `sentiment_report.md` - Relatório de sentimento
- `news_report.md` - Relatório de notícias
- `fundamentals_report.md` - Relatório de fundamentos

## ⚠️ Notas Importantes

1. **Custo**: Cada tradução consome tokens da API OpenAI. Use `gpt-4o-mini` para economia.
2. **Idioma**: Os relatórios originais permanecem intactos - apenas cópias traduzidas são criadas.
3. **Cache**: Arquivos já traduzidos (com `_pt-BR`) são automaticamente ignorados.
4. **Rate Limits**: Respeite os limites de taxa da API OpenAI.

## 🐛 Troubleshooting

### Erro: "No module named 'langchain_openai'"

```bash
pip install langchain-openai
```

### Erro: "OpenAI API key is required"

Configure a variável de ambiente:
```bash
export OPENAI_API_KEY=sua_chave_aqui
```

### Erro: "No reports found"

Certifique-se de ter executado o TradingAgents ao menos uma vez para gerar relatórios:
```bash
python -m cli.main
```

## 🤝 Contribuindo

Melhorias são bem-vindas! Sinta-se livre para:

- Adicionar suporte para outros idiomas
- Melhorar o prompt de tradução
- Adicionar outros providers (DeepL, Google Translate, etc.)
- Otimizar custos de API

## 📄 Licença

Mesmo da aplicação principal TradingAgents.
