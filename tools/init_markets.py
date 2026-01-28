#!/usr/bin/env python3
"""
init_markets.py: Initialize market calendars with sample data

Run this once to populate calendars from the manual YAML source.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from market_calendars import Market, MarketCalendarManager
from data_sources import CalendarFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=== Initializing Market Calendars ===\n")
    
    # Initialize components
    fetcher = CalendarFetcher()
    mgr = MarketCalendarManager()
    
    # Populate each market
    for market in Market:
        logger.info(f"Populating {market.value.upper()} calendar...")
        calendar = mgr.get_calendar(market)
        fetcher.populate_calendar(calendar, days_ahead=180)
        logger.info(f"✓ {market.value.upper()} calendar populated")
    
    # Save all calendars
    logger.info("\nSaving calendars to disk...")
    mgr.save_all('yaml')
    
    # Show summary
    logger.info("\n=== Calendar Summary ===\n")
    summary = mgr.get_summary()
    
    for market, stats in summary.items():
        logger.info(f"{market.upper()}:")
        logger.info(f"  Tickers: {stats.get('total_tickers', 0)}")
        logger.info(f"  Events: {stats.get('total_events', 0)}")
        if stats.get('event_types'):
            logger.info(f"  Types: {stats.get('event_types')}")
        logger.info("")
    
    logger.info("✓ Market calendar initialization complete!")
    logger.info("\nNext steps:")
    logger.info("  - Query calendars: python tools/query_calendars.py --upcoming 30")
    logger.info("  - Update calendars: python tools/update_calendars.py --all")
    logger.info("  - Read docs: docs/MARKET_CALENDARS.md")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
