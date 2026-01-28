"""
validate.py: Validate pipeline outputs against schema & constraints
"""

import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


def load_output_schema() -> Dict[str, Any]:
    """Load expected output schema from prompts/output/schema.yaml"""
    schema_path = Path(__file__).parent.parent / "prompts" / "output" / "schema.yaml"
    with open(schema_path) as f:
        return yaml.safe_load(f)


def load_constraints() -> Dict[str, Any]:
    """Load constraint definitions from prompts/system/constraints.yaml"""
    constraints_path = Path(__file__).parent.parent / "prompts" / "system" / "constraints.yaml"
    with open(constraints_path) as f:
        return yaml.safe_load(f)


def validate_schema(output: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate output against expected schema.
    
    TODO:
    - Implement full JSON Schema validation
    - Check required fields presence
    - Validate data types
    - Ensure numeric ranges (probabilities 0-1, etc.)
    
    Returns:
        (is_valid, list_of_errors)
    """
    logger.info("Validating output schema")
    
    errors = []
    
    # Basic checks
    if 'date' not in output:
        errors.append("Missing 'date' field")
    
    if 'steps' not in output:
        errors.append("Missing 'steps' field")
    
    expected_steps = [
        '01_filter_events',
        '02_macro_regime',
        '03_policy_impact',
        '04_second_order',
        '05_scenarios',
        '06_brief'
    ]
    
    for step in expected_steps:
        if step not in output.get('steps', {}):
            errors.append(f"Missing step: {step}")
    
    return len(errors) == 0, errors


def check_constraints(output: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Check for constraint violations.
    
    TODO:
    - Search for price prediction keywords
    - Search for trading advice keywords
    - Verify evidence grounding
    - Check token budget adherence
    
    Returns:
        (all_satisfied, list_of_violations)
    """
    logger.info("Checking constraints")
    
    constraints = load_constraints()
    violations = []
    
    # Check for price prediction keywords
    price_keywords = ['target price', 'will go up', 'will go down', 'bull run', 'crash']
    
    output_text = yaml.dump(output).lower()
    
    for keyword in price_keywords:
        if keyword in output_text:
            violations.append(f"Price prediction keyword detected: '{keyword}'")
    
    # Check for trading advice keywords
    trading_keywords = ['buy', 'sell', 'go long', 'go short', 'increase exposure']
    
    for keyword in trading_keywords:
        if keyword in output_text:
            violations.append(f"Trading advice keyword detected: '{keyword}'")
    
    return len(violations) == 0, violations


def validate_output(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run full validation suite.
    
    Returns:
        Validation report dict
    """
    logger.info("Starting output validation")
    
    schema_valid, schema_errors = validate_schema(output)
    constraints_met, constraint_violations = check_constraints(output)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'schema_valid': schema_valid,
        'schema_errors': schema_errors,
        'constraints_met': constraints_met,
        'constraint_violations': constraint_violations,
        'overall_valid': schema_valid and constraints_met
    }
    
    if not report['overall_valid']:
        logger.warning(f"Validation failed: {report}")
    else:
        logger.info("Validation passed")
    
    return report


def save_validation_report(date: str, report: Dict[str, Any]) -> Path:
    """Save validation report to data/archive/YYYY-MM-DD-validation.yaml"""
    archive_dir = Path(__file__).parent.parent / "data" / "archive"
    report_path = archive_dir / f"{date}-validation.yaml"
    
    with open(report_path, 'w') as f:
        yaml.dump(report, f, default_flow_style=False)
    
    logger.info(f"Saved validation report to {report_path}")
    return report_path


if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    
    # Load analysis output
    archive_dir = Path(__file__).parent.parent / "data" / "archive"
    analysis_path = archive_dir / f"{date}-analysis.yaml"
    
    if analysis_path.exists():
        with open(analysis_path) as f:
            output = yaml.safe_load(f)
        
        report = validate_output(output)
        save_validation_report(date, report)
    else:
        logger.error(f"Analysis output not found: {analysis_path}")
