"""
market_calendars.py: Manage market-specific calendar events (FTSE, NASDAQ)

Handles:
- Fetching earnings, dividends, splits, IPO calendars
- Storing locally as YAML/JSON for offline access
- Querying by date range, ticker, event type
"""

import yaml
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class Market(Enum):
    """Supported stock markets"""
    FTSE = "ftse"
    NASDAQ = "nasdaq"


class EventType(Enum):
    """Calendar event types"""
    EARNINGS = "earnings"
    DIVIDEND = "dividend"
    SPLIT = "stock_split"
    IPO = "ipo"
    CONFERENCE = "conference"
    ECONOMIC = "economic_indicator"
    MERGER = "merger_acquisition"


class CalendarEvent:
    """Represents a single calendar event"""
    
    def __init__(self, ticker: str, market: Market, event_type: EventType, 
                 date: str, description: str, **kwargs):
        self.ticker = ticker
        self.market = market
        self.event_type = event_type
        self.date = date  # YYYY-MM-DD
        self.description = description
        self.timestamp = datetime.now().isoformat()
        self.metadata = kwargs  # Additional fields (eps_estimate, dividend_amount, etc.)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for YAML/JSON serialization"""
        return {
            'ticker': self.ticker,
            'market': self.market.value,
            'event_type': self.event_type.value,
            'date': self.date,
            'description': self.description,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CalendarEvent':
        """Create from dict"""
        return CalendarEvent(
            ticker=data['ticker'],
            market=Market(data['market']),
            event_type=EventType(data['event_type']),
            date=data['date'],
            description=data['description'],
            **data.get('metadata', {})
        )


class MarketCalendar:
    """Manages calendars for a single market (FTSE or NASDAQ)"""
    
    def __init__(self, market: Market, data_dir: Path = None):
        self.market = market
        self.data_dir = data_dir or Path(__file__).parent.parent / "data" / "markets" / market.value
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.events: Dict[str, List[CalendarEvent]] = {}  # {ticker: [events]}
        self.last_updated = None
        
        self._load_local_calendar()
    
    def _load_local_calendar(self):
        """Load all locally stored calendar data"""
        logger.info(f"Loading local calendar for {self.market.value}")
        
        events_file = self.data_dir / "calendar.yaml"
        if events_file.exists():
            with open(events_file) as f:
                data = yaml.safe_load(f) or {}
            
            self.events = {}
            for ticker, ticker_events in data.get('events', {}).items():
                self.events[ticker] = [
                    CalendarEvent.from_dict(e) for e in ticker_events
                ]
            
            self.last_updated = data.get('last_updated')
            logger.info(f"Loaded {sum(len(e) for e in self.events.values())} events")
    
    def add_event(self, event: CalendarEvent):
        """Add event to calendar"""
        if event.ticker not in self.events:
            self.events[event.ticker] = []
        
        # Prevent duplicates
        existing = [e for e in self.events[event.ticker] 
                   if e.date == event.date and e.event_type == event.event_type]
        if not existing:
            self.events[event.ticker].append(event)
            logger.debug(f"Added event: {event.ticker} {event.event_type.value} on {event.date}")
    
    def add_events_bulk(self, events: List[CalendarEvent]):
        """Add multiple events"""
        for event in events:
            self.add_event(event)
    
    def save_calendar(self, format_type: str = 'yaml'):
        """Save calendar to disk (YAML or JSON)"""
        if format_type == 'yaml':
            self._save_yaml()
        elif format_type == 'json':
            self._save_json()
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _save_yaml(self):
        """Save as YAML"""
        output_file = self.data_dir / "calendar.yaml"
        
        data = {
            'market': self.market.value,
            'last_updated': datetime.now().isoformat(),
            'event_count': sum(len(e) for e in self.events.values()),
            'tickers': list(self.events.keys()),
            'events': {
                ticker: [e.to_dict() for e in events]
                for ticker, events in self.events.items()
            }
        }
        
        with open(output_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Saved calendar to {output_file}")
    
    def _save_json(self):
        """Save as JSON"""
        output_file = self.data_dir / "calendar.json"
        
        data = {
            'market': self.market.value,
            'last_updated': datetime.now().isoformat(),
            'event_count': sum(len(e) for e in self.events.values()),
            'tickers': list(self.events.keys()),
            'events': {
                ticker: [e.to_dict() for e in events]
                for ticker, events in self.events.items()
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved calendar to {output_file}")
    
    def get_events_by_ticker(self, ticker: str) -> List[CalendarEvent]:
        """Get all events for a specific ticker"""
        return self.events.get(ticker, [])
    
    def get_events_by_date_range(self, start_date: str, end_date: str) -> Dict[str, List[CalendarEvent]]:
        """Get events within date range (YYYY-MM-DD format)"""
        result = {}
        
        for ticker, events in self.events.items():
            filtered = [e for e in events if start_date <= e.date <= end_date]
            if filtered:
                result[ticker] = filtered
        
        return result
    
    def get_events_by_type(self, event_type: EventType) -> Dict[str, List[CalendarEvent]]:
        """Get all events of specific type"""
        result = {}
        
        for ticker, events in self.events.items():
            filtered = [e for e in events if e.event_type == event_type]
            if filtered:
                result[ticker] = filtered
        
        return result
    
    def get_upcoming_events(self, days_ahead: int = 30) -> Dict[str, List[CalendarEvent]]:
        """Get events in next N days"""
        today = datetime.now().strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        return self.get_events_by_date_range(today, future_date)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get calendar summary statistics"""
        all_events = []
        for events in self.events.values():
            all_events.extend(events)
        
        event_types = {}
        for event in all_events:
            event_types[event.event_type.value] = event_types.get(event.event_type.value, 0) + 1
        
        return {
            'market': self.market.value,
            'total_tickers': len(self.events),
            'total_events': len(all_events),
            'event_types': event_types,
            'date_range': {
                'first': min(e.date for e in all_events) if all_events else None,
                'last': max(e.date for e in all_events) if all_events else None
            },
            'last_updated': self.last_updated
        }


class MarketCalendarManager:
    """Manages calendars for all markets"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data" / "markets"
        self.calendars = {
            market: MarketCalendar(market, self.data_dir / market.value)
            for market in Market
        }
    
    def get_calendar(self, market: Market) -> MarketCalendar:
        """Get calendar for specific market"""
        return self.calendars[market]
    
    def add_event_to_market(self, market: Market, event: CalendarEvent):
        """Add event to specific market calendar"""
        self.calendars[market].add_event(event)
    
    def save_all(self, format_type: str = 'yaml'):
        """Save all calendars"""
        for calendar in self.calendars.values():
            calendar.save_calendar(format_type)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary for all markets"""
        return {
            market.value: calendar.get_summary()
            for market, calendar in self.calendars.items()
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    mgr = MarketCalendarManager()
    
    # Add sample events
    event1 = CalendarEvent(
        ticker='AAPL',
        market=Market.NASDAQ,
        event_type=EventType.EARNINGS,
        date='2026-02-05',
        description='Apple Q1 2026 Earnings',
        eps_estimate=2.15,
        revenue_estimate=95000
    )
    
    event2 = CalendarEvent(
        ticker='HSBA',
        market=Market.FTSE,
        event_type=EventType.EARNINGS,
        date='2026-02-10',
        description='HSBC Holdings PLC Full Year Results 2025',
        dividend_forecast=0.50
    )
    
    mgr.add_event_to_market(Market.NASDAQ, event1)
    mgr.add_event_to_market(Market.FTSE, event2)
    
    mgr.save_all('yaml')
    
    print("\n=== Calendar Summary ===")
    print(yaml.dump(mgr.get_summary(), default_flow_style=False))
