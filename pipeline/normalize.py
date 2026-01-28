"""
normalize.py: Clean, structure, and validate raw events
"""

import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_raw_events(date: str) -> Dict[str, Any]:
    """Load raw events from data/events/YYYY-MM-DD.yaml"""
    events_dir = Path(__file__).parent.parent / "data" / "events"
    raw_path = events_dir / f"{date}.yaml"
    
    if not raw_path.exists():
        logger.error(f"Raw events file not found: {raw_path}")
        return {'events': []}
    
    with open(raw_path) as f:
        return yaml.safe_load(f)


def normalize_events(raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize raw events to structured format.
    
    TODO:
    - Deduplicate events (same event from multiple sources)
    - Standardize fields: source, time, category, description
    - Remove noise (minor announcements, revisions)
    - Add tags for downstream filtering
    """
    logger.info(f"Normalizing {len(raw_events)} raw events")
    
    normalized = []
    for event in raw_events:
        # Placeholder normalization
        normalized_event = {
            'event_id': event.get('id', 'unknown'),
            'source': event.get('source', 'unknown'),
            'category': event.get('category', 'other'),
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
            'description': event.get('description', ''),
            'tags': event.get('tags', []),
        }
        normalized.append(normalized_event)
    
    return normalized


def save_normalized_events(date: str, events: List[Dict[str, Any]]) -> Path:
    """Save normalized events to data/events/YYYY-MM-DD-normalized.yaml"""
    events_dir = Path(__file__).parent.parent / "data" / "events"
    output_path = events_dir / f"{date}-normalized.yaml"
    
    with open(output_path, 'w') as f:
        yaml.dump({
            'date': date,
            'timestamp': datetime.now().isoformat(),
            'event_count': len(events),
            'events': events
        }, f, default_flow_style=False)
    
    logger.info(f"Saved {len(events)} normalized events to {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    
    raw_data = load_raw_events(date)
    normalized = normalize_events(raw_data.get('events', []))
    save_normalized_events(date, normalized)
