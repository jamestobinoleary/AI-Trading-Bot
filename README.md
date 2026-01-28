# AI-Trading-Bot

**Disciplined, auditable LLM pipeline for economic & market analysis**

This project provides a structured framework for daily economic and market calendar analysis using OpenAI's API, with hard constraints to prevent price prediction and trading advice.

## 🎯 What This Does

- **Economic Analysis:** Macro regime classification, policy impact, second-order effects
- **Market Calendars:** Track earnings, dividends, and events for FTSE & NASDAQ stocks
- **Structured Reasoning:** 6-step LLM pipeline with versioned prompts
- **Local Storage:** All data stored as YAML/JSON for offline analysis
- **Constraints:** No price prediction, no trading advice, time/token budgets enforced

---

## 🚀 Quick Start

### 1. Setup

```bash
# Clone and navigate
cd AI-Trading-Bot

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Initialize Market Calendars

```bash
# Populate calendars with sample data (20 events)
python tools/init_markets.py

# Query upcoming events
python tools/query_calendars.py --market nasdaq --upcoming 60
```

### 3. Run Pipeline (when ready)

```bash
# Run daily economic analysis
python pipeline/main.py

# Check outputs
ls -la data/archive/
```

---

## 📂 Project Structure

```
AI-Trading-Bot/
├── prompts/
│   ├── system/              # Analyst role & constraints
│   │   ├── role.yaml
│   │   └── constraints.yaml
│   ├── steps/               # 6-step reasoning pipeline
│   │   ├── 01_filter_events.yaml
│   │   ├── 02_macro_regime.yaml
│   │   ├── 03_policy_impact.yaml
│   │   ├── 04_second_order.yaml
│   │   ├── 05_scenarios.yaml
│   │   └── 06_brief.yaml
│   └── output/
│       └── schema.yaml      # Output format definition
│
├── data/
│   ├── sources.yaml         # Economic data source registry
│   ├── sources/
│   │   └── market_calendars.yaml    # Manual calendar source (edit this)
│   ├── events/              # Daily event snapshots
│   ├── archive/             # Historical analysis outputs
│   └── markets/
│       ├── ftse/
│       │   ├── calendar.yaml        # FTSE events (generated)
│       │   └── calendar.json
│       └── nasdaq/
│           ├── calendar.yaml        # NASDAQ events (generated)
│           └── calendar.json
│
├── pipeline/
│   ├── __init__.py
│   ├── main.py              # Main pipeline orchestrator
│   ├── fetch.py             # Fetch raw economic events
│   ├── normalize.py         # Clean & structure events
│   ├── run_llm.py           # Execute LLM reasoning steps
│   ├── validate.py          # Schema & constraint validation
│   ├── shutdown.py          # Time/token budget enforcement
│   ├── market_calendars.py  # Market calendar management
│   └── data_sources.py      # API fetching (Finnhub, Yahoo, etc.)
│
├── tools/
│   ├── init_markets.py      # Initialize market calendars
│   ├── update_calendars.py  # Update calendars from APIs
│   ├── query_calendars.py   # Query calendar events
│   └── CALENDAR_COMMANDS.sh # Quick reference
│
├── schedules/
│   └── daily.yaml           # Execution schedule
│
├── docs/
│   ├── MARKET_CALENDARS.md  # Market calendar guide
│   └── MARKET_CALENDARS_BUILD.md
│
├── config.yaml              # Pipeline settings
├── requirements.txt         # Python dependencies
├── PIPELINE.md              # Full pipeline documentation
└── START_HERE_MARKETS.md    # Market calendar quick start
```

---

## 🛠 What's Been Built

### ✅ Core Pipeline (Base System)

- **Prompt System:** 6-step reasoning pipeline with versioned YAML prompts
- **Constraints:** Hard limits on price prediction, trading advice, token usage
- **Execution Guard:** Time/token budget enforcement with graceful shutdown
- **Validation:** Schema checking and constraint violation detection
- **Data Management:** YAML-based storage for auditability

### ✅ Market Calendar System (New)

- **Calendar Management:** Track earnings, dividends, IPOs, M&A for FTSE & NASDAQ
- **Multiple Data Sources:** Finnhub API, Yahoo Finance, manual YAML (automatic fallback)
- **Local Storage:** YAML + JSON formats for offline access
- **CLI Tools:** Query and update calendars on-demand
- **Python API:** Programmatic access to calendar data

**Current Data Loaded:**
- **NASDAQ:** 6 tickers (AAPL, MSFT, NVDA, TSLA, AMZN) × 12 events
- **FTSE:** 4 tickers (HSBA, LLOY, BARC, ULVR) × 8 events
- **Macro:** Economic indicators (NFP, CPI, Fed Rate, UK Inflation)

---

## 📊 Market Calendar Usage

### Query Events

```bash
# Upcoming events in next 60 days
python tools/query_calendars.py --market nasdaq --upcoming 60

# All earnings events
python tools/query_calendars.py --market ftse --type earnings

# Specific stock
python tools/query_calendars.py --market nasdaq --ticker AAPL

# Export to JSON
python tools/query_calendars.py --market all --upcoming 90 --export-json events.json
```

### Update Calendars

```bash
# Update all markets
python tools/update_calendars.py --all

# Update with summary
python tools/update_calendars.py --all --show-summary

# Update next 180 days
python tools/update_calendars.py --all --days 180
```

### Python API

```python
from pipeline.market_calendars import Market, MarketCalendarManager, EventType

mgr = MarketCalendarManager()
nasdaq = mgr.get_calendar(Market.NASDAQ)

# Query by ticker
aapl_events = nasdaq.get_events_by_ticker('AAPL')

# Query upcoming events
upcoming = nasdaq.get_upcoming_events(days_ahead=30)

# Query by event type
earnings = nasdaq.get_events_by_type(EventType.EARNINGS)
```

---

## 🔧 Configuration

### API Keys

Set up your API keys in `.env`:

```bash
# Required: OpenAI API
OPENAI_API_KEY=sk-your-key-here

# Optional: For market calendar updates
FINNHUB_API_KEY=your-finnhub-key
```

### Pipeline Settings

Edit `config.yaml`:

```yaml
api:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 4000

limits:
  daily_token_budget: 100000
  execution_window_minutes: 60
  max_retries: 3
```

### Add More Stocks

Edit `data/sources/market_calendars.yaml`:

```yaml
nasdaq:
  earnings:
    - ticker: GOOGL
      date: '2026-03-15'
      description: 'Google Q4 2025 Earnings'
      metadata:
        eps_estimate: 2.05
```

---

## 📖 Documentation

- **[PIPELINE.md](PIPELINE.md)** — Complete pipeline setup & scheduling guide
- **[START_HERE_MARKETS.md](START_HERE_MARKETS.md)** — Market calendar quick start
- **[docs/MARKET_CALENDARS.md](docs/MARKET_CALENDARS.md)** — Full market calendar API reference
- **[BUILD.md](BUILD.md)** — Initial build summary

---

## 🎓 Core Principles

1. **Prompts are versioned artifacts** — Not ad-hoc text
2. **Stepwise, constrained reasoning** — 6-step pipeline with explicit constraints
3. **Human-readable data** — All YAML, auditable, diff-friendly
4. **Cost-controlled** — Token budgets, scheduled execution, shutdown guards
5. **Provider-agnostic** — OpenAI or Azure OpenAI

---

## ⚙️ Next Steps

### 1. Wire Market Calendars into Main Pipeline

Update `pipeline/fetch.py` to include market events:

```python
from pipeline.market_calendars import MarketCalendarManager
from pipeline.data_sources import CalendarFetcher

def fetch_events(date: str):
    # Fetch market calendar events
    fetcher = CalendarFetcher()
    mgr = MarketCalendarManager()
    
    for market in [Market.NASDAQ, Market.FTSE]:
        calendar = mgr.get_calendar(market)
        fetcher.populate_calendar(calendar, days_ahead=30)
        # ... add events to pipeline
```

### 2. Set Up Scheduling

Add to crontab for daily execution:

```bash
# 9 AM ET, weekdays
0 9 * * 1-5 cd /path/to/AI-Trading-Bot && python pipeline/main.py
```

Or use GitHub Actions (see [PIPELINE.md](PIPELINE.md))

### 3. Expand Coverage

- Add more markets (DAX, CAC, Nikkei)
- Add more tickers to `data/sources/market_calendars.yaml`
- Implement real API integrations (Finnhub, Yahoo Finance)

---

## 🧪 Testing

```bash
# Test imports
python -c "from pipeline.market_calendars import MarketCalendarManager; print('OK')"

# Initialize calendars with sample data
python tools/init_markets.py

# Query events
python tools/query_calendars.py --market nasdaq --upcoming 60

# Run pipeline (dry run)
python pipeline/main.py 2026-01-28
```

---

## 📦 Dependencies

Core:
- `pyyaml` — YAML parsing
- `openai` — OpenAI API
- `python-dotenv` — Environment variables
- `requests` — HTTP requests

Optional:
- `yfinance` — Yahoo Finance integration
- `pytest` — Testing

Install all: `pip install -r requirements.txt`

---

## 🛡️ What This Is NOT

- ❌ Not a trading bot
- ❌ Not a price prediction system
- ❌ Not real-time market execution
- ❌ Not investment advice

**This is a macro reasoning assistant for economic and policy analysis.**

---

## 📝 License

This is a test/learning project. Use at your own risk.

---

## 🙏 Acknowledgments

Built with:
- OpenAI API (GPT-4)
- Finnhub (market data API)
- Yahoo Finance (yfinance)

---

**Status:** ✅ Core pipeline + market calendars complete and operational

For questions or issues, see documentation in `docs/` or open an issue.
