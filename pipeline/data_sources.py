"""
data_sources.py: Fetch market calendar data from APIs

Supported sources:
- Finnhub (earnings, dividends, economic calendar)
- Yahoo Finance (via yfinance)
- Alpha Vantage (alternative)
- Manual YAML feeds (fallback)

Each source maps to Market (FTSE/NASDAQ) and EventType (earnings/dividend/etc)
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from market_calendars import Market, EventType, CalendarEvent, MarketCalendar

logger = logging.getLogger(__name__)


class DataSource(ABC):
    """Abstract base for market data sources"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    def fetch_earnings_calendar(self, market: Market, days_ahead: int = 90) -> List[CalendarEvent]:
        """Fetch upcoming earnings events"""
        pass
    
    @abstractmethod
    def fetch_dividend_calendar(self, market: Market, days_ahead: int = 90) -> List[CalendarEvent]:
        """Fetch upcoming dividend events"""
        pass
    
    @abstractmethod
    def fetch_economic_calendar(self, days_ahead: int = 90) -> List[CalendarEvent]:
        """Fetch economic indicator releases (macroeconomic)"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Verify API connectivity and credentials"""
        pass


class FinnhubSource(DataSource):
    """Finnhub API integration
    
    Requires: FINNHUB_API_KEY environment variable
    Free tier: 60 API calls/min
    """
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('FINNHUB_API_KEY')
        if not api_key:
            logger.warning("Finnhub API key not found. Set FINNHUB_API_KEY env var.")
        super().__init__(api_key)
    
    def health_check(self) -> bool:
        """Check if API is accessible"""
        if not self.api_key:
            logger.error("Finnhub API key not configured")
            return False
        
        try:
            # Placeholder: actual API call would go here
            logger.info("Finnhub API: OK (placeholder check)")
            return True
        except Exception as e:
            logger.error(f"Finnhub API health check failed: {e}")
            return False
    
    def fetch_earnings_calendar(self, market: Market, days_ahead: int = 90) -> List[CalendarEvent]:
        """Fetch earnings calendar from Finnhub"""
        logger.info(f"Fetching earnings calendar for {market.value} (next {days_ahead} days)")
        
        # TODO: Implement actual Finnhub API call
        # GET /calendar/earnings?from=2026-01-28&to=2026-04-28&symbol=AAPL
        
        events = []
        return events
    
    def fetch_dividend_calendar(self, market: Market, days_ahead: int = 90) -> List[CalendarEvent]:
        """Fetch dividend calendar from Finnhub"""
        logger.info(f"Fetching dividend calendar for {market.value}")
        
        # TODO: Implement actual Finnhub API call
        # GET /calendar/dividend?from=2026-01-28&to=2026-04-28
        
        events = []
        return events
    
    def fetch_economic_calendar(self, days_ahead: int = 90) -> List[CalendarEvent]:
        """Fetch economic calendar from Finnhub"""
        logger.info(f"Fetching economic calendar (next {days_ahead} days)")
        
        # TODO: Implement actual Finnhub API call
        # GET /calendar/economic?from=2026-01-28&to=2026-04-28
        
        events = []
        return events


class YFinanceSource(DataSource):
    """Yahoo Finance via yfinance library
    
    Requires: yfinance package (pip install yfinance)
    Rate limit: Automatic backoff
    """
    
    def __init__(self):
        super().__init__()
        try:
            import yfinance
            self.yf = yfinance
            logger.info("yfinance initialized")
        except ImportError:
            logger.error("yfinance not installed. Run: pip install yfinance")
            self.yf = None
    
    def health_check(self) -> bool:
        """Check if yfinance is available"""
        return self.yf is not None
    
    def fetch_earnings_calendar(self, market: Market, days_ahead: int = 90) -> List[CalendarEvent]:
        """Fetch earnings from Yahoo Finance"""
        logger.info(f"Fetching earnings calendar for {market.value}")
        
        if not self.yf:
            logger.error("yfinance not available")
            return []
        
        # TODO: Implement actual yfinance calls with market-specific tickers
        # For NASDAQ: fetch AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, etc.
        # For FTSE: fetch HSBA, RKH, LLOY, BATS, etc.
        
        events = []
        return events
    
    def fetch_dividend_calendar(self, market: Market, days_ahead: int = 90) -> List[CalendarEvent]:
        logger.info(f"Fetching dividend calendar for {market.value}")
        return []
    
    def fetch_economic_calendar(self, days_ahead: int = 90) -> List[CalendarEvent]:
        logger.info(f"Fetching economic calendar")
        return []


class ManualYAMLSource(DataSource):
    """Manual calendar data in YAML format
    
    Fallback when API quotas are exceeded or for curated data.
    Format: data/sources/market_calendars.yaml
    """
    
    def __init__(self, yaml_file: Path = None):
        super().__init__()
        self.yaml_file = yaml_file or Path(__file__).parent.parent / "data" / "sources" / "market_calendars.yaml"
        self.data = self._load_yaml()
    
    def _load_yaml(self) -> Dict[str, Any]:
        """Load manual calendar data"""
        if self.yaml_file.exists():
            with open(self.yaml_file) as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def health_check(self) -> bool:
        """Check if source file exists and is readable"""
        return self.yaml_file.exists() and len(self.data) > 0
    
    def fetch_earnings_calendar(self, market: Market, days_ahead: int = 90) -> List[CalendarEvent]:
        """Parse earnings from YAML"""
        events = []
        
        market_data = self.data.get(market.value, {})
        earnings_data = market_data.get('earnings', [])
        
        for item in earnings_data:
            try:
                metadata = item.get('metadata', {}).copy()
                event = CalendarEvent(
                    ticker=item['ticker'],
                    market=market,
                    event_type=EventType.EARNINGS,
                    date=item['date'],
                    description=item.get('description', f"{item['ticker']} Earnings"),
                    **metadata
                )
                events.append(event)
            except Exception as e:
                logger.warning(f"Failed to parse earnings event: {e}")
        
        logger.info(f"Loaded {len(events)} earnings events from YAML")
        return events
    
    def fetch_dividend_calendar(self, market: Market, days_ahead: int = 90) -> List[CalendarEvent]:
        """Parse dividends from YAML"""
        events = []
        
        market_data = self.data.get(market.value, {})
        dividend_data = market_data.get('dividends', [])
        
        for item in dividend_data:
            try:
                metadata = item.get('metadata', {}).copy()
                event = CalendarEvent(
                    ticker=item['ticker'],
                    market=market,
                    event_type=EventType.DIVIDEND,
                    date=item['date'],
                    description=item.get('description', f"{item['ticker']} Dividend"),
                    **metadata
                )
                events.append(event)
            except Exception as e:
                logger.warning(f"Failed to parse dividend event: {e}")
        
        logger.info(f"Loaded {len(events)} dividend events from YAML")
        return events
    
    def fetch_economic_calendar(self, days_ahead: int = 90) -> List[CalendarEvent]:
        """Parse economic indicators from YAML"""
        events = []
        
        economic_data = self.data.get('economic', [])
        
        for item in economic_data:
            try:
                event = CalendarEvent(
                    ticker='MACRO',
                    market=Market.NASDAQ,  # Macro events aren't market-specific
                    event_type=EventType.ECONOMIC,
                    date=item['date'],
                    description=item.get('description', 'Economic Indicator'),
                    **item.get('metadata', {})
                )
                events.append(event)
            except Exception as e:
                logger.warning(f"Failed to parse economic event: {e}")
        
        logger.info(f"Loaded {len(events)} economic events from YAML")
        return events


class CalendarFetcher:
    """Orchestrates fetching from multiple sources with fallback"""
    
    def __init__(self):
        self.sources = []
        self._init_sources()
    
    def _init_sources(self):
        """Initialize available sources in priority order"""
        # Priority: Finnhub > Yahoo Finance > Manual YAML
        
        if os.getenv('FINNHUB_API_KEY'):
            self.sources.append(FinnhubSource())
        
        yf_source = YFinanceSource()
        if yf_source.health_check():
            self.sources.append(yf_source)
        
        # Always include manual source as fallback
        self.sources.append(ManualYAMLSource())
    
    def fetch_all_calendars(self, market: Market, days_ahead: int = 90) -> Dict[str, List[CalendarEvent]]:
        """Fetch all calendar types for a market"""
        result = {}
        
        for source in self.sources:
            try:
                if source.health_check():
                    logger.info(f"Fetching from {source.__class__.__name__}")
                    
                    earnings = source.fetch_earnings_calendar(market, days_ahead)
                    dividends = source.fetch_dividend_calendar(market, days_ahead)
                    
                    result['earnings'] = earnings
                    result['dividends'] = dividends
                    
                    # Only fetch economic from first available source
                    if 'economic' not in result:
                        economic = source.fetch_economic_calendar(days_ahead)
                        result['economic'] = economic
                    
                    logger.info(f"Fetched {len(earnings)} earnings, {len(dividends)} dividends from {source.__class__.__name__}")
                    break  # Use first available source
            except Exception as e:
                logger.warning(f"Failed to fetch from {source.__class__.__name__}: {e}")
                continue
        
        return result
    
    def populate_calendar(self, calendar: MarketCalendar, days_ahead: int = 90):
        """Populate a market calendar with fetched data"""
        calendars = self.fetch_all_calendars(calendar.market, days_ahead)
        
        all_events = []
        for event_list in calendars.values():
            all_events.extend(event_list)
        
        calendar.add_events_bulk(all_events)
        logger.info(f"Populated {calendar.market.value} calendar with {len(all_events)} events")
    
    def populate_all_markets(self, days_ahead: int = 90):
        """Populate calendars for all markets"""
        from market_calendars import MarketCalendarManager
        
        mgr = MarketCalendarManager()
        
        for market in Market:
            logger.info(f"=== Populating {market.value.upper()} calendar ===")
            self.populate_calendar(mgr.get_calendar(market), days_ahead)
        
        mgr.save_all('yaml')
        
        return mgr


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    fetcher = CalendarFetcher()
    mgr = fetcher.populate_all_markets(days_ahead=90)
    
    print("\n=== Calendar Population Complete ===")
    print(yaml.dump(mgr.get_summary(), default_flow_style=False))
