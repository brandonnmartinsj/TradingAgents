# 📋 Plano de Implementação: Análise de Sentimento em Tempo Real (Reddit)

## 🔍 Análise do Estado Atual

**Descobertas:**
- ✅ Projeto já tem `praw` (Python Reddit API Wrapper) como dependência
- ✅ Existe `reddit_utils.py` com funções para buscar posts (mas usa dados locais offline)
- ✅ Existe `social_media_analyst.py` mas não usa Reddit diretamente
- ✅ Dashboard já tem análise de sentimento básica em `news_utils.py` (keyword-based)
- ⚠️ Não há integração com Reddit API em tempo real
- ⚠️ Não há credenciais Reddit no `.env`

---

## 🏗️ Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB DASHBOARD                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  📊 Sentiment Page (NEW)                           │    │
│  │  - Real-time sentiment score                       │    │
│  │  - Trending tickers on Reddit                      │    │
│  │  - Sentiment timeline chart                        │    │
│  │  - Top posts with sentiment                        │    │
│  │  - Word cloud                                      │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  🏠 Dashboard Page (ENHANCED)                      │    │
│  │  - Add Reddit sentiment badge to ticker cards      │    │
│  │  - Sentiment trend indicator                       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴─────────────────────────────────┐
│           utils/reddit_sentiment_utils.py (NEW)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  RedditClient                                        │  │
│  │  - fetch_posts(ticker, subreddits, limit)           │  │
│  │  - fetch_trending_tickers()                         │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SentimentAnalyzer                                   │  │
│  │  - analyze_text(text) -> score                      │  │
│  │  - batch_analyze(posts) -> results                  │  │
│  │  - get_sentiment_trend(ticker, hours=24)            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                  EXTERNAL SERVICES                          │
│  - Reddit API (PRAW)                                        │
│  - Subreddits: r/wallstreetbets, r/stocks, r/investing     │
│  - VADER Sentiment Analysis (nltk)                          │
│  - TextBlob (optional fallback)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Plano Detalhado de Implementação

### **FASE 1: Setup e Infraestrutura** ⏱️ ~30min

#### 1.1 Configuração de Credenciais Reddit
**Arquivo**: `.env`, `settings.example.json`

```bash
# Adicionar ao .env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=TradingAgents/1.0
```

**Tarefas**:
- [ ] Adicionar campos Reddit em `settings.example.json`
- [ ] Atualizar `.env.example` com variáveis Reddit
- [ ] Documentar como obter credenciais Reddit API

#### 1.2 Atualizar Dependências
**Arquivo**: `web_dashboard/requirements.txt`

```txt
# Adicionar:
praw>=7.7.0           # Reddit API
vaderSentiment>=3.3.2 # Sentiment analysis optimized for social media
textblob>=0.17.1      # Alternative sentiment analysis
wordcloud>=1.9.0      # Word cloud visualization
nltk>=3.8.0           # NLP toolkit
```

**Tarefas**:
- [ ] Adicionar dependências ao requirements.txt
- [ ] Testar instalação: `pip install -r web_dashboard/requirements.txt`

---

### **FASE 2: Módulo Reddit Sentiment** ⏱️ ~2-3h

#### 2.1 Criar `utils/reddit_sentiment_utils.py`

**Componentes principais**:

```python
# Estrutura do arquivo:

1. RedditClient Class
   - __init__(client_id, client_secret, user_agent)
   - fetch_posts(ticker, subreddits, limit, time_filter)
   - fetch_trending_tickers(subreddits, limit)
   - get_company_mentions(ticker, hours=24)

2. SentimentAnalyzer Class
   - __init__(method='vader')  # vader, textblob, hybrid
   - analyze_text(text) -> {'score': float, 'label': str, 'confidence': float}
   - batch_analyze(posts) -> List[dict]
   - get_aggregate_sentiment(posts) -> dict
   - get_sentiment_trend(ticker, hours=24) -> timeseries

3. Utility Functions
   - normalize_ticker(text) -> List[str]  # Extract $AAPL, AAPL mentions
   - clean_text(text) -> str
   - calculate_post_weight(upvotes, comments, awards) -> float
   - get_sentiment_emoji(score) -> str
   - get_sentiment_color(score) -> str
```

**Funcionalidades**:
- ✅ Busca posts de múltiplos subreddits
- ✅ Análise de sentimento com VADER (otimizado para social media)
- ✅ Peso por engagement (upvotes + comments + awards)
- ✅ Cache com Streamlit @st.cache_data (TTL 15min)
- ✅ Rate limiting para Reddit API
- ✅ Error handling robusto

---

### **FASE 3: Página de Sentimento** ⏱️ ~3-4h

#### 3.1 Criar `pages/reddit_sentiment.py`

**Layout da página**:

```
┌─────────────────────────────────────────────────────────┐
│  📊 Reddit Sentiment Analysis                           │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │ Avg Score   │ │ Total Posts │ │ Bullish %   │      │
│  │    +0.45    │ │     156     │ │    68%      │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│  [Ticker Selector: AAPL ▼]  [Timeframe: 24h ▼]         │
│  [Subreddits: ☑ WSB ☑ Stocks ☑ Investing]              │
├─────────────────────────────────────────────────────────┤
│  📈 Sentiment Timeline (Plotly Line Chart)              │
│     - Sentiment score over time                         │
│     - Volume bars below                                 │
├─────────────────────────────────────────────────────────┤
│  🔥 Trending Tickers (Today)                            │
│     1. NVDA  🟢 +0.62  (234 mentions)                   │
│     2. TSLA  🔴 -0.21  (189 mentions)                   │
│     3. AAPL  🟢 +0.45  (156 mentions)                   │
├─────────────────────────────────────────────────────────┤
│  💬 Top Reddit Posts                                    │
│     [Card with sentiment badge, upvotes, comments]      │
│     [Card with sentiment badge, upvotes, comments]      │
├─────────────────────────────────────────────────────────┤
│  ☁️ Word Cloud (Most mentioned terms)                   │
├─────────────────────────────────────────────────────────┤
│  📊 Sentiment Distribution (Pie Chart)                  │
│     - Bullish / Neutral / Bearish                       │
└─────────────────────────────────────────────────────────┘
```

**Tabs dentro da página**:
1. **Overview**: Métricas principais + timeline
2. **Posts**: Lista de posts com sentimento
3. **Trends**: Trending tickers + word cloud
4. **Analytics**: Distribuição, correlações

**Tarefas**:
- [ ] Implementar layout responsivo
- [ ] Criar visualizações Plotly interativas
- [ ] Implementar filtros (ticker, timeframe, subreddits)
- [ ] Adicionar export de dados (CSV, JSON)
- [ ] Implementar auto-refresh opcional

---

### **FASE 4: Integração com Dashboard Existente** ⏱️ ~1-2h

#### 4.1 Atualizar `app.py`
```python
# Adicionar página ao menu
page = st.sidebar.radio("Select Page", [
    "🏠 Dashboard",
    "📄 Report Viewer",
    "🔍 Comparison",
    "💼 Portfolio",
    "🔔 Alerts",
    "📈 Analytics",
    "🤖 Reddit Sentiment",  # NEW
    "⚙️ Settings"
])
```

#### 4.2 Atualizar `pages/dashboard.py`
- Adicionar badge de sentimento Reddit nos ticker cards
- Mostrar trending status (🔥 if trending)
- Link para página de sentimento detalhado

```python
# Exemplo de badge:
sentiment_score = get_reddit_sentiment(ticker)
if sentiment_score:
    st.markdown(f"Reddit: {get_sentiment_emoji(sentiment_score)} {sentiment_score:+.2f}")
```

#### 4.3 Atualizar `pages/settings.py`
- Adicionar seção "Reddit API" para configurar credenciais
- Seleção de subreddits default
- Configuração de cache TTL

---

### **FASE 5: Visualizações e Métricas** ⏱️ ~2h

#### 5.1 Gráficos Plotly

**1. Sentiment Timeline**
```python
def create_sentiment_timeline(data):
    fig = go.Figure()

    # Line chart: sentiment score over time
    fig.add_trace(go.Scatter(
        x=data['timestamp'],
        y=data['sentiment_score'],
        mode='lines+markers',
        name='Sentiment',
        line=dict(color='rgb(75, 192, 192)')
    ))

    # Bar chart: post volume
    fig.add_trace(go.Bar(
        x=data['timestamp'],
        y=data['post_count'],
        name='Volume',
        yaxis='y2',
        opacity=0.3
    ))

    fig.update_layout(
        title='Reddit Sentiment Timeline',
        yaxis=dict(title='Sentiment Score'),
        yaxis2=dict(title='Post Volume', overlaying='y', side='right')
    )

    return fig
```

**2. Sentiment Distribution (Pie Chart)**
```python
def create_sentiment_distribution(sentiments):
    bullish = sum(1 for s in sentiments if s > 0.15)
    neutral = sum(1 for s in sentiments if -0.15 <= s <= 0.15)
    bearish = sum(1 for s in sentiments if s < -0.15)

    fig = go.Figure(data=[go.Pie(
        labels=['🟢 Bullish', '⚪ Neutral', '🔴 Bearish'],
        values=[bullish, neutral, bearish],
        marker=dict(colors=['#10b981', '#6b7280', '#ef4444'])
    )])

    return fig
```

**3. Trending Tickers Heatmap**
```python
def create_trending_heatmap(tickers_data):
    # Heatmap: ticker x time with sentiment intensity
    fig = go.Figure(data=go.Heatmap(
        z=sentiment_matrix,
        x=timestamps,
        y=tickers,
        colorscale='RdYlGn'
    ))

    return fig
```

**4. Word Cloud**
```python
from wordcloud import WordCloud

def create_word_cloud(texts):
    text = ' '.join(texts)
    wordcloud = WordCloud(width=800, height=400).generate(text)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')

    return fig
```

---

### **FASE 6: Testes e Validação** ⏱️ ~1h

#### 6.1 Testes Unitários

**Arquivo**: `web_dashboard/tests/test_reddit_sentiment.py`

```python
def test_reddit_client_fetch():
    # Test fetching posts

def test_sentiment_analyzer():
    # Test VADER sentiment

def test_ticker_extraction():
    # Test $AAPL extraction

def test_weighted_sentiment():
    # Test engagement weighting
```

#### 6.2 Testes de Integração
- [ ] Testar com API keys reais
- [ ] Validar rate limiting
- [ ] Testar cache behavior
- [ ] Validar visualizações

#### 6.3 Validação de Performance
- [ ] Medir tempo de carregamento
- [ ] Otimizar queries Reddit
- [ ] Validar uso de cache

---

## 📊 Estrutura de Dados

### Reddit Post Object
```python
{
    'id': 'abc123',
    'title': 'AAPL to the moon! 🚀',
    'text': 'Apple just announced...',
    'ticker': 'AAPL',
    'subreddit': 'wallstreetbets',
    'created_utc': 1234567890,
    'upvotes': 1250,
    'num_comments': 87,
    'awards': 5,
    'url': 'https://reddit.com/...',
    'sentiment': {
        'score': 0.652,
        'label': 'bullish',
        'confidence': 0.87
    },
    'weight': 0.45  # Based on engagement
}
```

### Sentiment Aggregate Object
```python
{
    'ticker': 'AAPL',
    'period': '24h',
    'avg_sentiment': 0.45,
    'weighted_sentiment': 0.52,
    'total_posts': 156,
    'bullish_count': 106,
    'neutral_count': 32,
    'bearish_count': 18,
    'total_engagement': 45230,  # upvotes + comments
    'trending_rank': 3,
    'sentiment_trend': 'increasing',  # vs previous period
    'top_keywords': ['earnings', 'vision', 'ai'],
    'timestamp': '2025-10-15T14:00:00Z'
}
```

---

## 🎯 Subreddits Target

**Primários** (alta qualidade):
- `r/wallstreetbets` - 15M members, high volume, meme stocks
- `r/stocks` - 6M members, serious discussion
- `r/investing` - 2M members, long-term focus

**Secundários** (opcional):
- `r/StockMarket` - 2M members
- `r/options` - 400K members
- `r/pennystocks` - 300K members

---

## ⚙️ Configurações Recomendadas

```json
// settings.json
{
  "reddit": {
    "enabled": true,
    "subreddits": ["wallstreetbets", "stocks", "investing"],
    "posts_per_subreddit": 50,
    "time_filter": "day",
    "cache_ttl": 900,
    "sentiment_method": "vader",
    "min_upvotes": 10,
    "show_trending": true
  }
}
```

---

## 📈 Métricas de Sucesso

- ✅ Latência < 3s para carregar sentimento
- ✅ Cache hit rate > 80%
- ✅ Accuracy sentimento > 75% (vs manual labeling)
- ✅ Suporte para 100+ posts simultâneos
- ✅ Zero crashes em 24h de operação

---

## 🚀 Roadmap Futuro (Pós-MVP)

**V2 Features**:
- Sentiment alerts (notificar quando sentimento muda drasticamente)
- Historical sentiment data storage (SQLite/PostgreSQL)
- Correlation analysis (sentiment vs price movement)
- Multi-language support (PT-BR posts)
- Advanced NLP (FinBERT, custom fine-tuned models)
- Reddit user influence scoring (weight by karma/age)

---

## ✅ Checklist de Implementação

### Fase 1: Setup
- [ ] Adicionar credenciais Reddit ao `.env`
- [ ] Atualizar `requirements.txt`
- [ ] Instalar dependências

### Fase 2: Core Module
- [ ] Implementar `RedditClient` class
- [ ] Implementar `SentimentAnalyzer` class
- [ ] Adicionar utility functions
- [ ] Implementar caching

### Fase 3: UI
- [ ] Criar `reddit_sentiment.py` page
- [ ] Implementar tabs (Overview, Posts, Trends, Analytics)
- [ ] Adicionar filtros e controles

### Fase 4: Integração
- [ ] Atualizar `app.py` navigation
- [ ] Adicionar badges em `dashboard.py`
- [ ] Adicionar settings em `settings.py`

### Fase 5: Visualizações
- [ ] Sentiment timeline chart
- [ ] Distribution pie chart
- [ ] Trending heatmap
- [ ] Word cloud

### Fase 6: Testes
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Validação de performance
- [ ] Documentação

---

## 📚 Como Obter Credenciais Reddit API

1. Acesse https://www.reddit.com/prefs/apps
2. Clique em "create another app..." ou "create app"
3. Preencha:
   - **name**: TradingAgents
   - **App type**: script
   - **description**: Real-time sentiment analysis for stocks
   - **about url**: (deixe em branco)
   - **redirect uri**: http://localhost:8080
4. Clique em "create app"
5. Copie as credenciais:
   - **client_id**: string abaixo de "personal use script"
   - **client_secret**: string ao lado de "secret"
   - **user_agent**: "TradingAgents/1.0"

---

**Tempo Total Estimado**: 8-12 horas

**Ordem de Prioridade**:
1. Fase 1 + 2 (Core functionality)
2. Fase 3 (Basic UI)
3. Fase 4 (Integration)
4. Fase 5 (Polish visualizations)
5. Fase 6 (Testing)

---

**Data de Criação**: 2025-10-15
**Versão**: 1.0
**Autor**: Claude Code + Brandon
