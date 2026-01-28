#!/bin/bash
# QUICK REFERENCE: Market Calendar Commands

# ============================================
# INITIALIZATION (First Time)
# ============================================

# Populate calendars with sample data
python tools/init_markets.py

# ============================================
# QUERYING
# ============================================

# Upcoming NASDAQ events (next 60 days)
python tools/query_calendars.py --market nasdaq --upcoming 60

# All FTSE earnings
python tools/query_calendars.py --market ftse --type earnings

# Specific stock (Apple)
python tools/query_calendars.py --market nasdaq --ticker AAPL

# All dividend events
python tools/query_calendars.py --market all --type dividend

# Date range
python tools/query_calendars.py --market nasdaq --date-from 2026-02-01 --date-to 2026-02-28

# Export to JSON
python tools/query_calendars.py --market all --upcoming 90 --export-json events.json

# Show calendar summary
python tools/query_calendars.py --market nasdaq --summary

# ============================================
# UPDATING CALENDARS
# ============================================

# Update all markets
python tools/update_calendars.py --all

# Update just NASDAQ
python tools/update_calendars.py --market nasdaq

# Update next 180 days
python tools/update_calendars.py --all --days 180

# Update and show summary
python tools/update_calendars.py --all --show-summary

# Export as JSON instead of YAML
python tools/update_calendars.py --all --export json

# ============================================
# VIEWING STORED CALENDARS
# ============================================

# View NASDAQ calendar (YAML)
cat data/markets/nasdaq/calendar.yaml

# View FTSE calendar (JSON)
cat data/markets/ftse/calendar.json

# Count events
wc -l data/markets/nasdaq/calendar.yaml

# Find all upcoming earnings dates
grep -A2 "event_type: earnings" data/markets/nasdaq/calendar.yaml | grep "date:"

# ============================================
# PYTHON API USAGE
# ============================================

python3 << 'EOF'
from pipeline.market_calendars import Market, MarketCalendarManager, EventType

mgr = MarketCalendarManager()
nasdaq = mgr.get_calendar(Market.NASDAQ)

# Get all AAPL events
aapl = nasdaq.get_events_by_ticker('AAPL')
for event in aapl:
    print(f"{event.date} | {event.event_type.value}")

# Get next 30 days
upcoming = nasdaq.get_upcoming_events(30)
print(f"Events in next 30 days: {sum(len(e) for e in upcoming.values())}")

# Get summary
summary = nasdaq.get_summary()
print(f"Total events: {summary['total_events']}")
EOF

# ============================================
# MAINTENANCE
# ============================================

# Clear and rebuild calendars
rm -f data/markets/*/calendar.*
python tools/init_markets.py

# Verify calendar files exist
ls -lh data/markets/*/calendar.*

# Check file sizes
du -sh data/markets/

# ============================================
# TROUBLESHOOTING
# ============================================

# Check if manual calendar source is valid
python3 -c "import yaml; print(yaml.safe_load(open('data/sources/market_calendars.yaml'))['nasdaq']['earnings'][0])"

# Test market_calendars import
python3 -c "from pipeline.market_calendars import MarketCalendarManager; print('OK')"

# Test data_sources import
python3 -c "from pipeline.data_sources import CalendarFetcher; print('OK')"

# ============================================
# SCHEDULED UPDATES (Cron)
# ============================================

# Add this to crontab -e for daily updates at 8 AM
0 8 * * 1-5 cd /path/to/AI-Trading-Bot && source venv/bin/activate && python tools/update_calendars.py --all

# ============================================
# HELPFUL LINKS
# ============================================

# Full documentation: docs/MARKET_CALENDARS.md
# Build summary: docs/MARKET_CALENDARS_BUILD.md
