"""
main.py: Orchestrate full daily pipeline execution
"""

import logging
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fetch import fetch_events, save_raw_events
from normalize import load_raw_events, normalize_events, save_normalized_events
from run_llm import run_pipeline, save_pipeline_output
from validate import validate_output, save_validation_report
from shutdown import setup_pipeline_guard

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_full_pipeline(date: str = None) -> Dict[str, Any]:
    """
    Execute complete daily pipeline:
    1. Fetch raw events
    2. Normalize
    3. Run LLM steps
    4. Validate
    5. Enforce shutdown
    
    Args:
        date: execution date (YYYY-MM-DD), defaults to today
    
    Returns:
        Execution summary dict
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"=== STARTING PIPELINE FOR {date} ===")
    
    # Initialize execution guard
    config_path = Path(__file__).parent.parent / "config.yaml"
    guard = setup_pipeline_guard(config_path)
    
    try:
        # Step 1: Fetch
        logger.info("STEP 1: Fetching raw events")
        raw_events = fetch_events(date)
        save_raw_events(date, raw_events)
        guard.record_tokens(100)  # Placeholder token count
        
        if not guard.should_continue():
            logger.error("Guard stop: cannot continue to normalization")
            return {"status": "halted", "reason": "execution_guard"}
        
        # Step 2: Normalize
        logger.info("STEP 2: Normalizing events")
        raw_data = load_raw_events(date)
        normalized = normalize_events(raw_data.get('events', []))
        save_normalized_events(date, normalized)
        guard.record_tokens(150)
        
        if not guard.should_continue():
            logger.error("Guard stop: cannot continue to LLM")
            return {"status": "halted", "reason": "execution_guard"}
        
        # Step 3: Run LLM pipeline
        logger.info("STEP 3: Running LLM reasoning pipeline")
        pipeline_output = run_pipeline(date, normalized)
        save_pipeline_output(date, pipeline_output)
        guard.record_tokens(2000)  # Placeholder for LLM token usage
        
        if not guard.should_continue():
            logger.warning("Guard stop: skipping validation due to time/token pressure")
            return {"status": "partial", "reason": "execution_guard", "steps_completed": 3}
        
        # Step 4: Validate
        logger.info("STEP 4: Validating output")
        validation_report = validate_output(pipeline_output)
        save_validation_report(date, validation_report)
        
        # Step 5: Report status
        status = guard.get_status()
        logger.info(f"=== PIPELINE COMPLETE ===")
        logger.info(f"Status: {status}")
        
        return {
            "status": "success",
            "date": date,
            "execution_guard": status,
            "validation": validation_report
        }
    
    except Exception as e:
        logger.exception(f"Pipeline failed with error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "execution_guard": guard.get_status()
        }


if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else None
    result = run_full_pipeline(date)
    print(yaml.dump(result, default_flow_style=False))
