"""
run_llm.py: Execute stepwise LLM reasoning pipeline
"""

import yaml
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import openai

logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """Load pipeline configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_prompt(step_name: str) -> Dict[str, str]:
    """Load prompt template for a given step"""
    prompts_dir = Path(__file__).parent.parent / "prompts" / "steps"
    prompt_file = prompts_dir / f"{step_name}.yaml"
    
    if not prompt_file.exists():
        logger.error(f"Prompt file not found: {prompt_file}")
        return {'prompt': ''}
    
    with open(prompt_file) as f:
        return yaml.safe_load(f)


def load_system_prompt() -> str:
    """Load system prompt (role definition)"""
    role_path = Path(__file__).parent.parent / "prompts" / "system" / "role.yaml"
    with open(role_path) as f:
        data = yaml.safe_load(f)
    return data.get('system_prompt', '')


def call_openai(system_prompt: str, user_message: str, config: Dict) -> str:
    """
    Call OpenAI API with system + user prompts.
    
    TODO:
    - Implement proper API error handling
    - Add retry logic with exponential backoff
    - Track token usage for budget enforcement
    - Support Azure OpenAI as fallback
    """
    logger.info("Calling OpenAI API")
    
    # Placeholder: in production, call actual API
    # response = openai.ChatCompletion.create(
    #     model=config['api']['model'],
    #     temperature=config['api']['temperature'],
    #     max_tokens=config['api']['max_tokens'],
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_message}
    #     ]
    # )
    # return response['choices'][0]['message']['content']
    
    return "Placeholder response from LLM"


def run_step(step_id: str, input_data: Dict[str, Any], config: Dict) -> Dict[str, Any]:
    """
    Execute a single reasoning step.
    
    Args:
        step_id: e.g., "01_filter_events"
        input_data: Output from previous step or raw normalized events
        config: Pipeline configuration
    
    Returns:
        Step output (YAML-serializable dict)
    """
    logger.info(f"Running step: {step_id}")
    
    prompt_template = load_prompt(step_id)
    system_prompt = load_system_prompt()
    
    # Build user message from input_data
    user_message = f"Analyze the following data:\n{yaml.dump(input_data)}"
    
    # Call LLM
    response_text = call_openai(system_prompt, user_message, config)
    
    # Parse output (expect YAML or JSON)
    try:
        output = yaml.safe_load(response_text)
    except:
        output = {"raw_response": response_text}
    
    return output


def run_pipeline(date: str, normalized_events: List[Dict]) -> Dict[str, Any]:
    """
    Run full 6-step pipeline.
    
    Returns:
        Complete analysis output with all steps
    """
    config = load_config()
    logger.info("Starting LLM pipeline")
    
    pipeline_output = {
        'date': date,
        'timestamp': datetime.now().isoformat(),
        'steps': {}
    }
    
    steps = [
        "01_filter_events",
        "02_macro_regime",
        "03_policy_impact",
        "04_second_order",
        "05_scenarios",
        "06_brief"
    ]
    
    # Run each step sequentially
    step_input = {'events': normalized_events}
    
    for step in steps:
        logger.info(f"Executing {step}")
        step_output = run_step(step, step_input, config)
        pipeline_output['steps'][step] = step_output
        step_input = step_output  # Feed output to next step
    
    return pipeline_output


def save_pipeline_output(date: str, output: Dict[str, Any]) -> Path:
    """Save complete pipeline output to data/archive/YYYY-MM-DD-analysis.yaml"""
    archive_dir = Path(__file__).parent.parent / "data" / "archive"
    output_path = archive_dir / f"{date}-analysis.yaml"
    
    with open(output_path, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True)
    
    logger.info(f"Saved pipeline output to {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    
    # Load normalized events from previous step
    from normalize import load_raw_events
    raw_data = load_raw_events(date)
    normalized = raw_data.get('events', [])
    
    # Run pipeline
    output = run_pipeline(date, normalized)
    save_pipeline_output(date, output)
