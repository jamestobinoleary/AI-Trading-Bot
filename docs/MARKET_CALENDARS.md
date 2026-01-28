# Market Calendar & Data Sources Guide

**Build local calendars of stock market events for FTSE and NASDAQ**

This document covers:
- Setting up market calendars
- Fetching data from APIs or manual sources
- Storing locally (YAML/JSON)
- Querying and analyzing calendar data

---

## Overview

The market calendar system provides:

### 🎯 Core Components

1. **`market_calendars.py`** — In-memory calendar management
   - `CalendarEvent` — Individual events (earnings, dividends, splits, etc.)
   - `MarketCalendar` — Per-market calendar storage + queries
   - `MarketCalendarManager` — Manages all markets

2. **`data_sources.py`** — Data fetching with API fallback
   - `FinnhubSource` — Primary API integration
   - `YFinanceSource` — Yahoo Finance fallback
   - `ManualYAMLSource` — Curated YAML data
   - `CalendarFetcher` — Orchestrator with failover logic

3. **`tools/update_calendars.py`** — CLI for on-demand updates

4. **`data/sources/market_calendars.yaml`** — Manual calendar data source

5. **`data/markets/{ftse,nasdaq}/`** — Local storage for calendars

---

## Setup

### 1. Install Dependencies

```bash
# Already installed in venv/
pip install pyyaml

# Optional: for Yahoo Finance integration
pip install yfinance

# Optional: if using Finnhub API
# Get free tier: https://finnhub.io/
export FINNHUB_API_KEY="your-api-key"
```

### 2. Configure Data Sources

#### Option A: Use Manual YAML (Recommended for Testing)

No setup needed. The system reads from `data/sources/market_calendars.yaml` which includes sample data for:

**NASDAQ Stocks:**
- AAPL (Apple), MSFT (Microsoft), NVDA (Nvidia), TSLA (Tesla), AMZN (Amazon)

**FTSE Stocks:**
- HSBA (HSBC), LLOY (Lloyds), BARC (Barclays), ULVR (Unilever), DGE (Diageo), SHEL (Shell), BP

**Economic Indicators:**
- US Non-Farm Payroll, CPI, PCE, UK Inflation, Fed Rate Decisions

#### Option B: Use Finnhub API

1. Get free API key: https://finnhub.io/register
2. Set environment variable:

```bash
export FINNHUB_API_KEY="your-key-here"
```

#### Option C: Use Yahoo Finance

```bash
pip install yfinance
```

---

## Quick Start

### Run Calendar Update

```bash
cd AI-Trading-Bot
source venv/bin/activate

# Update all markets (FTSE + NASDAQ)
python tools/update_calendars.py --all

# Update just NASDAQ
python tools/update_calendars.py --market nasdaq --days 180

# Update and show summary
python tools/update_calendars.py --all --show-summary

# Export as JSON
python tools/update_calendars.py --all --export json
```

### Check Output

```bash
# View saved calendars
ls -la data/markets/ftse/
ls -la data/markets/nasdaq/

# YAML format (human-readable)
cat data/markets/nasdaq/calendar.yaml

# JSON format (programmatic)
cat data/markets/nasdaq/calendar.json
```

---

## Programmatic Usage

### Example 1: Load & Query Calendar

```python
from pipeline.market_calendars import Market, MarketCalendarManager

# Initialize
mgr = MarketCalendarManager()

# Get NASDAQ calendar
nasdaq_cal = mgr.get_calendar(Market.NASDAQ)

# Query by ticker
aapl_events = nasdaq_cal.get_events_by_ticker('AAPL')
for event in aapl_events:
    print(f"{event.ticker} {event.event_type.value} on {event.date}")

# Query by date range
jan_events = nasdaq_cal.get_events_by_date_range('2026-01-01', '2026-01-31')

# Query upcoming events (next 30 days)
upcoming = nasdaq_cal.get_upcoming_events(days_ahead=30)

# Summary stats
summary = nasdaq_cal.get_summary()
print(summary)
```

### Example 2: Fetch & Populate

```python
from pipeline.data_sources import CalendarFetcher
from pipeline.market_calendars import Market, MarketCalendarManager

fetcher = CalendarFetcher()
mgr = MarketCalendarManager()

# Fetch earnings for NASDAQ
nasdaq_cal = mgr.get_calendar(Market.NASDAQ)
fetcher.populate_calendar(nasdaq_cal, days_ahead=90)

# Save to disk
nasdaq_cal.save_calendar('yaml')

# Show what we fetched
print(nasdaq_cal.get_summary())
```

### Example 3: Add Custom Events

```python
from pipeline.market_calendars import Market, MarketCalendar, CalendarEvent, EventType

calendar = MarketCalendar(Market.NASDAQ)

# Create and add event
event = CalendarEvent(
    ticker='GOOGL',
    market=Market.NASDAQ,
    event_type=EventType.EARNINGS,
    date='2026-03-15',
    description='Google Q4 2025 Earnings',
    eps_estimate=2.05,
    revenue_estimate=90000000000
)

calendar.add_event(event)
calendar.save_calendar('yaml')
```

---

## Data Format

### Calendar Storage (YAML)

```yaml
market: nasdaq
last_updated: '2026-01-28T14:30:00'
event_count: 15
tickers:
  - AAPL
  - MSFT
  - NVDA

events:
  AAPL:
    - ticker: AAPL
      market: nasdaq
      event_type: earnings
      date: '2026-02-05'
      description: 'Apple Q1 2026 Earnings'
      timestamp: '2026-01-28T14:30:00'
      metadata:
        fiscal_quarter: Q1
        fiscal_year: 2026
        eps_estimate: 2.15
        revenue_estimate: 95000000000
    
    - ticker: AAPL
      market: nasdaq
      event_type: dividend
      date: '2026-02-12'
      description: 'Apple Dividend Payment'
      metadata:
        dividend_per_share: 0.25
        payment_frequency: Quarterly

  MSFT:
    - ticker: MSFT
      market: nasdaq
      event_type: earnings
      date: '2026-02-12'
      ...
```

### Manual Calendar Source (YAML)

Edit `data/sources/market_calendars.yaml`:

```yaml
nasdaq:
  earnings:
    - ticker: AAPL
      date: '2026-02-05'
      description: 'Apple Q1 2026 Earnings'
      metadata:
        eps_estimate: 2.15
        revenue_estimate: 95000000000

ftse:
  earnings:
    - ticker: HSBA
      date: '2026-02-23'
      description: 'HSBC FY 2025 Results'
      metadata:
        eps_estimate: 1.45

economic:
  - ticker: 'US.NFP'
    date: '2026-02-06'
    description: 'US Non-Farm Payroll'
    metadata:
      forecast: 180000
      importance: 'High'
```

---

## API Integration Reference

### Finnhub (Recommended)

**Endpoints:**
- `/calendar/earnings` — Earnings calendar
- `/calendar/dividend` — Dividend calendar
- `/calendar/economic` — Economic calendar

**Free tier:** 60 calls/min, sufficient for daily updates

**Tickers:**
- NASDAQ: AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, NFLX, etc.
- FTSE: 0001.L (FTSE 100 members), e.g., HSBA.L, LLOY.L, BARC.L, etc.

### Yahoo Finance (yfinance)

**Library:** `pip install yfinance`

**Features:**
- No API key required
- Rate limiting handled automatically
- Can get earnings dates, dividends

**Limitation:** No calendar endpoint, requires scraping ticker pages

### Alpha Vantage (Alternative)

**Site:** https://www.alphavantage.co/

**Features:**
- Economic calendar
- Earnings calendar

**Limitation:** Free tier is 5 calls/min

---

## Event Types Supported

| Type | Description | Typical Impact |
|------|-------------|-----------------|
| `earnings` | Company earnings report | High (stock-specific) |
| `dividend` | Dividend payment | Medium (income) |
| `stock_split` | Stock split/consolidation | Low (structural) |
| `ipo` | Initial public offering | High (new listings) |
| `conference` | Earnings call or conference | Medium (commentary) |
| `economic_indicator` | Macro economic release | High (market-wide) |
| `merger_acquisition` | M&A activity | High (restructuring) |

---

## Querying Examples

### Get all earnings in next 30 days

```python
from pipeline.market_calendars import Market, MarketCalendarManager, EventType

mgr = MarketCalendarManager()
nasdaq_cal = mgr.get_calendar(Market.NASDAQ)

upcoming = nasdaq_cal.get_upcoming_events(days_ahead=30)
for ticker, events in upcoming.items():
    earnings = [e for e in events if e.event_type == EventType.EARNINGS]
    if earnings:
        print(f"{ticker}: {len(earnings)} earnings events")
```

### Get all dividends by FTSE company

```python
from pipeline.market_calendars import Market, MarketCalendarManager, EventType

mgr = MarketCalendarManager()
ftse_cal = mgr.get_calendar(Market.FTSE)

dividends = ftse_cal.get_events_by_type(EventType.DIVIDEND)
for ticker, events in dividends.items():
    for event in events:
        print(f"{ticker}: ${event.metadata.get('dividend_per_share')} on {event.date}")
```

### Export specific calendar slice

```python
import json
from pipeline.market_calendars import Market, MarketCalendarManager

mgr = MarketCalendarManager()
nasdaq_cal = mgr.get_calendar(Market.NASDAQ)

# Get Q1 earnings
q1_earnings = nasdaq_cal.get_events_by_date_range('2026-01-01', '2026-03-31')
q1_dict = {
    ticker: [e.to_dict() for e in events]
    for ticker, events in q1_earnings.items()
}

with open('q1_earnings.json', 'w') as f:
    json.dump(q1_dict, f, indent=2)
```

---

## Integration with Pipeline

### Fetch Stage

Update `pipeline/fetch.py` to include market calendars:

```python
from pipeline.market_calendars import MarketCalendarManager, Market
from pipeline.data_sources import CalendarFetcher

def fetch_events(date: str):
    """Fetch both economic and market calendar events"""
    
    events = []
    
    # 1. Fetch market calendars
    fetcher = CalendarFetcher()
    mgr = MarketCalendarManager()
    
    for market in Market:
        calendar = mgr.get_calendar(market)
        fetcher.populate_calendar(calendar, days_ahead=30)
        
        # Get today's events
        today_events = calendar.get_events_by_date_range(date, date)
        for ticker, ticker_events in today_events.items():
            for event in ticker_events:
                events.append(event.to_dict())
    
    # 2. Fetch traditional macro events
    # ... existing code ...
    
    return events
```

### Normalize Stage

Transform market calendar events into analysis-ready format.

### Run LLM Stage

Use market events as context for:
- Earnings season impact
- Dividend announcements
- M&A activity
- IPO calendar (new market entrants)

---

## Troubleshooting

### Issue: "No data in calendar"

**Solution:**
1. Check `data/sources/market_calendars.yaml` exists
2. Verify entries use correct date format (YYYY-MM-DD)
3. Ensure `data/markets/{ftse,nasdaq}/` directories exist

### Issue: "API key not found" (Finnhub)

**Solution:**
```bash
# Option 1: Set environment variable
export FINNHUB_API_KEY="your-key"

# Option 2: Or just use manual YAML source (default fallback)
# No action needed - system uses manual data automatically
```

### Issue: "yfinance not installed"

**Solution:**
```bash
source venv/bin/activate
pip install yfinance
```

### Issue: Calendar shows old data

**Solution:**
```bash
# Force refresh
python tools/update_calendars.py --all --days 180

# Or clear and rebuild
rm -f data/markets/*/calendar.*
python tools/update_calendars.py --all
```

---

## Next Steps

1. **Populate Initial Calendars**
   ```bash
   python tools/update_calendars.py --all --show-summary
   ```

2. **Integrate with Pipeline**
   - Update `pipeline/fetch.py` to pull market calendar events
   - Wire calendar events into `pipeline/normalize.py`

3. **Add to LLM Analysis**
   - Include market events in step 01 (filter events)
   - Analyze earnings seasons and their macro impact

4. **Monitor & Update**
   - Set calendar update in scheduler (daily or weekly)
   - Maintain `data/sources/market_calendars.yaml` with Q upcoming events

5. **Extend to More Markets**
   - Add DAX (Germany), CAC (France), Nikkei (Japan), etc.
   - Use same `Market` enum + calendar structure

---

## File Structure

```
data/
├── sources/
│   └── market_calendars.yaml        # Manual calendar source
└── markets/
    ├── ftse/
    │   ├── calendar.yaml            # FTSE calendar (generated)
    │   └── calendar.json            # FTSE calendar (JSON)
    └── nasdaq/
        ├── calendar.yaml            # NASDAQ calendar (generated)
        └── calendar.json            # NASDAQ calendar (JSON)

pipeline/
├── market_calendars.py              # Calendar management
└── data_sources.py                  # Data fetching

tools/
└── update_calendars.py              # CLI update tool
```

---

## References

- **Finnhub API:** https://finnhub.io/docs/api
- **Yahoo Finance:** https://pypi.org/project/yfinance/
- **Alpha Vantage:** https://www.alphavantage.co/
- **NASDAQ Listed Stocks:** https://www.nasdaq.com/market-activity/stocks
- **FTSE 100 Index:** https://www.londonstockexchange.com/indices/ftse100

