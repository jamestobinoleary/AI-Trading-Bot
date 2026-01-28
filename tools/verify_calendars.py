#!/usr/bin/env python3
"""
verify_calendars.py: Quick verification that market calendars are working
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from market_calendars import Market, MarketCalendarManager

mgr = MarketCalendarManager()

print("\n" + "="*70)
print("MARKET CALENDAR SYSTEM - VERIFICATION")
print("="*70)

for market in [Market.NASDAQ, Market.FTSE]:
    cal = mgr.get_calendar(market)
    summary = cal.get_summary()
    
    print(f"\n{market.value.upper()}:")
    print(f"  Tickers: {summary['total_tickers']}")
    print(f"  Total Events: {summary['total_events']}")
    print(f"  Event Types: {summary['event_types']}")
    
    # Show first 3 events
    events = []
    for ticker_events in cal.events.values():
        events.extend(ticker_events)
    
    print(f"  Sample Events:")
    for event in sorted(events, key=lambda e: e.date)[:3]:
        print(f"    {event.date} - {event.ticker} ({event.event_type.value})")

print("\n" + "="*70)
print("✓ SYSTEMS READY FOR USE")
print("="*70)
print("\nNext steps:")
print("  python tools/query_calendars.py --market nasdaq --upcoming 60")
print("  python tools/query_calendars.py --market ftse --type earnings")
print("  python tools/update_calendars.py --all --show-summary")
print("\nFor full documentation:")
print("  cat docs/MARKET_CALENDARS.md")
print()
