"""
__init__.py: Pipeline package initialization
"""

__version__ = "0.1.0"
__package__ = "econ-llm-pipeline"

from .fetch import fetch_events, save_raw_events
from .normalize import normalize_events, save_normalized_events
from .run_llm import run_pipeline, save_pipeline_output
from .validate import validate_output, save_validation_report
from .shutdown import ExecutionGuard, setup_pipeline_guard

__all__ = [
    'fetch_events',
    'save_raw_events',
    'normalize_events',
    'save_normalized_events',
    'run_pipeline',
    'save_pipeline_output',
    'validate_output',
    'save_validation_report',
    'ExecutionGuard',
    'setup_pipeline_guard',
]
