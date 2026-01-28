#!/usr/bin/env python3
"""
query_calendars.py: Interactive query tool for market calendars

Usage:
  python tools/query_calendars.py --market nasdaq --ticker AAPL
  python tools/query_calendars.py --market ftse --type earnings
  python tools/query_calendars.py --upcoming 30
  python tools/query_calendars.py --export-json all_events.json
"""

import sys
import json
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from market_calendars import Market, MarketCalendarManager, EventType


def main():
    parser = ArgumentParser(description='Query market calendars')
    
    parser.add_argument('--market',
                       choices=['ftse', 'nasdaq', 'all'],
                       default='all',
                       help='Market to query')
    
    parser.add_argument('--ticker',
                       help='Stock ticker to query')
    
    parser.add_argument('--type',
                       choices=['earnings', 'dividend', 'split', 'ipo', 'conference', 'economic', 'merger'],
                       help='Event type to filter')
    
    parser.add_argument('--upcoming',
                       type=int,
                       help='Show events in next N days')
    
    parser.add_argument('--date-from',
                       help='Date range start (YYYY-MM-DD)')
    
    parser.add_argument('--date-to',
                       help='Date range end (YYYY-MM-DD)')
    
    parser.add_argument('--summary',
                       action='store_true',
                       help='Show calendar summary')
    
    parser.add_argument('--export-json',
                       help='Export results to JSON file')
    
    args = parser.parse_args()
    
    # Initialize manager
    mgr = MarketCalendarManager()
    
    # Determine markets
    markets = [Market(args.market)] if args.market != 'all' else list(Market)
    
    results = {}
    
    for market in markets:
        market_name = market.value.upper()
        calendar = mgr.get_calendar(market)
        
        print(f"\n{'='*60}")
        print(f"  {market_name} Calendar Query")
        print(f"{'='*60}\n")
        
        # Handle different query types
        
        if args.ticker:
            # Query by ticker
            events = calendar.get_events_by_ticker(args.ticker)
            if not events:
                print(f"No events found for {args.ticker}")
            else:
                print(f"Events for {args.ticker}:\n")
                for event in sorted(events, key=lambda e: e.date):
                    print(f"  {event.date} | {event.event_type.value.upper():10s} | {event.description}")
            
            results[market_name] = {args.ticker: [e.to_dict() for e in events]}
        
        elif args.type:
            # Query by event type
            event_type = EventType(args.type)
            events = calendar.get_events_by_type(event_type)
            
            print(f"All {args.type.upper()} events:\n")
            for ticker in sorted(events.keys()):
                ticker_events = events[ticker]
                for event in sorted(ticker_events, key=lambda e: e.date):
                    print(f"  {event.date} | {ticker:6s} | {event.description}")
            
            results[market_name] = {
                ticker: [e.to_dict() for e in events[ticker]]
                for ticker in events
            }
        
        elif args.upcoming:
            # Upcoming events
            events = calendar.get_upcoming_events(days_ahead=args.upcoming)
            
            print(f"Events in next {args.upcoming} days:\n")
            for ticker in sorted(events.keys()):
                ticker_events = events[ticker]
                for event in sorted(ticker_events, key=lambda e: e.date):
                    print(f"  {event.date} | {ticker:6s} | {event.event_type.value.upper():10s} | {event.description}")
            
            results[market_name] = {
                ticker: [e.to_dict() for e in events[ticker]]
                for ticker in events
            }
        
        elif args.date_from and args.date_to:
            # Date range
            events = calendar.get_events_by_date_range(args.date_from, args.date_to)
            
            print(f"Events from {args.date_from} to {args.date_to}:\n")
            for ticker in sorted(events.keys()):
                ticker_events = events[ticker]
                for event in sorted(ticker_events, key=lambda e: e.date):
                    print(f"  {event.date} | {ticker:6s} | {event.event_type.value.upper():10s} | {event.description}")
            
            results[market_name] = {
                ticker: [e.to_dict() for e in events[ticker]]
                for ticker in events
            }
        
        elif args.summary:
            # Calendar summary
            summary = calendar.get_summary()
            
            print(f"Summary:")
            print(f"  Total Tickers: {summary['total_tickers']}")
            print(f"  Total Events: {summary['total_events']}")
            print(f"  Event Types: {summary['event_types']}")
            if summary['date_range']['first']:
                print(f"  Date Range: {summary['date_range']['first']} to {summary['date_range']['last']}")
            print(f"  Last Updated: {summary['last_updated']}")
            
            results[market_name] = summary
        
        else:
            # Default: show summary
            summary = calendar.get_summary()
            
            print(f"Summary:")
            print(f"  Total Tickers: {summary['total_tickers']}")
            print(f"  Total Events: {summary['total_events']}")
            print(f"  Event Types: {summary['event_types']}")
            if summary['date_range']['first']:
                print(f"  Date Range: {summary['date_range']['first']} to {summary['date_range']['last']}")
            
            results[market_name] = summary
    
    # Export if requested
    if args.export_json:
        print(f"\nExporting results to {args.export_json}...")
        with open(args.export_json, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"✓ Exported to {args.export_json}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
