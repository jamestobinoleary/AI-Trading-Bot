"""
shutdown.py: Enforce execution time & token budget limits
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ExecutionGuard:
    """Enforces time and token budgets for pipeline execution"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize guard with config limits.
        
        Args:
            config: config.yaml loaded as dict
        """
        self.config = config
        self.start_time = None
        self.tokens_used = 0
        self.daily_token_budget = config['limits']['daily_token_budget']
        self.execution_window_minutes = config['limits']['execution_window_minutes']
        self.max_runtime_seconds = (self.execution_window_minutes - 5) * 60  # 5 min buffer
    
    def start(self):
        """Mark pipeline start time"""
        self.start_time = time.time()
        logger.info(f"Pipeline execution started. Max duration: {self.max_runtime_seconds}s")
    
    def check_time_remaining(self) -> float:
        """
        Get seconds remaining before hard cutoff.
        
        Returns:
            Seconds remaining, or negative if overdue
        """
        if not self.start_time:
            return self.max_runtime_seconds
        
        elapsed = time.time() - self.start_time
        remaining = self.max_runtime_seconds - elapsed
        return remaining
    
    def should_continue(self) -> bool:
        """Check if execution should continue (time & tokens OK)"""
        remaining_secs = self.check_time_remaining()
        remaining_tokens = self.daily_token_budget - self.tokens_used
        
        # Stop if <30 seconds left or <1000 tokens
        if remaining_secs < 30:
            logger.warning(f"Time budget nearly exhausted: {remaining_secs:.0f}s remaining")
            return False
        
        if remaining_tokens < 1000:
            logger.warning(f"Token budget nearly exhausted: {remaining_tokens} tokens remaining")
            return False
        
        return True
    
    def record_tokens(self, count: int):
        """Record tokens used by LLM call"""
        self.tokens_used += count
        budget_pct = (self.tokens_used / self.daily_token_budget) * 100
        logger.info(f"Tokens used: {self.tokens_used} / {self.daily_token_budget} ({budget_pct:.1f}%)")
    
    def force_shutdown(self):
        """Enforce immediate shutdown"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        logger.error(f"Force shutdown triggered after {elapsed:.0f}s")
        
        report = {
            'shutdown_reason': 'execution_guard_exceeded',
            'elapsed_seconds': elapsed,
            'tokens_used': self.tokens_used,
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def get_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        remaining_secs = self.check_time_remaining()
        remaining_tokens = self.daily_token_budget - self.tokens_used
        
        return {
            'elapsed_seconds': elapsed,
            'remaining_seconds': remaining_secs,
            'tokens_used': self.tokens_used,
            'remaining_tokens': remaining_tokens,
            'budget_exhaustion_pct': (self.tokens_used / self.daily_token_budget) * 100
        }


def setup_pipeline_guard(config_path: Path) -> ExecutionGuard:
    """Create and initialize ExecutionGuard from config"""
    import yaml
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    guard = ExecutionGuard(config)
    guard.start()
    return guard


if __name__ == "__main__":
    # Test guard
    import yaml
    
    config_path = Path(__file__).parent.parent / "config.yaml"
    guard = setup_pipeline_guard(config_path)
    
    print("Guard initialized:")
    print(guard.get_status())
    
    # Simulate some work
    time.sleep(2)
    guard.record_tokens(500)
    
    print("After 2s + 500 tokens:")
    print(guard.get_status())
    print(f"Should continue? {guard.should_continue()}")
