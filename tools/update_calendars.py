#!/usr/bin/env python3
"""
update_calendars.py: CLI tool to fetch and update market calendars

Usage:
  python tools/update_calendars.py --all          # Update all markets
  python tools/update_calendars.py --market ftse  # Update FTSE only
  python tools/update_calendars.py --market nasdaq # Update NASDAQ only
  python tools/update_calendars.py --days 180     # Update next 180 days
  python tools/update_calendars.py --export json  # Export as JSON
"""

import sys
import logging
from pathlib import Path
from argparse import ArgumentParser

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))

from market_calendars import Market, MarketCalendarManager
from data_sources import CalendarFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = ArgumentParser(description='Update market calendars for FTSE and NASDAQ')
    
    parser.add_argument('--market', 
                       choices=['ftse', 'nasdaq', 'all'],
                       default='all',
                       help='Market to update (default: all)')
    
    parser.add_argument('--days',
                       type=int,
                       default=90,
                       help='Days ahead to fetch (default: 90)')
    
    parser.add_argument('--export',
                       choices=['yaml', 'json'],
                       default='yaml',
                       help='Export format (default: yaml)')
    
    parser.add_argument('--show-summary',
                       action='store_true',
                       help='Show calendar summary after update')
    
    args = parser.parse_args()
    
    logger.info("=== Market Calendar Updater ===")
    logger.info(f"Markets: {args.market}")
    logger.info(f"Days ahead: {args.days}")
    logger.info(f"Export format: {args.export}")
    
    # Initialize fetcher and manager
    fetcher = CalendarFetcher()
    mgr = MarketCalendarManager()
    
    # Determine which markets to update
    markets_to_update = []
    if args.market == 'all':
        markets_to_update = list(Market)
    else:
        markets_to_update = [Market(args.market)]
    
    # Fetch and populate calendars
    for market in markets_to_update:
        logger.info(f"\n--- Updating {market.value.upper()} calendar ---")
        try:
            calendar = mgr.get_calendar(market)
            fetcher.populate_calendar(calendar, args.days)
            logger.info(f"✓ {market.value.upper()} calendar updated")
        except Exception as e:
            logger.error(f"✗ Failed to update {market.value.upper()}: {e}")
    
    # Save calendars
    logger.info(f"\nSaving calendars ({args.export.upper()})...")
    mgr.save_all(args.export)
    
    # Show summary if requested
    if args.show_summary:
        logger.info("\n=== Calendar Summary ===")
        summary = mgr.get_summary()
        
        for market, stats in summary.items():
            logger.info(f"\n{market.upper()}:")
            logger.info(f"  Tickers: {stats.get('total_tickers', 0)}")
            logger.info(f"  Events: {stats.get('total_events', 0)}")
            if stats.get('event_types'):
                logger.info(f"  Event types: {stats.get('event_types')}")
            if stats.get('date_range'):
                logger.info(f"  Date range: {stats.get('date_range').get('first')} to {stats.get('date_range').get('last')}")
    
    logger.info("\n✓ Calendar update complete")
    return 0


if __name__ == '__main__':
    sys.exit(main())
