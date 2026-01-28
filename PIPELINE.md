# econ-llm: Daily Economic Analysis Pipeline

**A disciplined, auditable LLM pipeline for macro-economic and policy analysis** (not trading, not price prediction).

## Overview

This pipeline runs daily to:
1. **Fetch** curated economic events from whitelisted sources
2. **Normalize** data into structured YAML
3. **Reason** through 6 stepwise LLM prompts (filtering → regime → policy → 2nd order → scenarios → brief)
4. **Validate** outputs against schema & constraint rules
5. **Enforce** hard time/token budgets to prevent runaway execution

**Key constraints:**
- No price prediction
- No trading advice
- Evidence-grounded reasoning only
- Time-boxed (~1 hour/day)
- Cost-controlled API usage

---

## Repository Structure

```
econ-llm/
├── prompts/                 # Versioned prompt templates
│   ├── system/
│   │   ├── role.yaml        # Analyst role definition
│   │   └── constraints.yaml # Hard guardrails
│   ├── steps/
│   │   ├── 01_filter_events.yaml
│   │   ├── 02_macro_regime.yaml
│   │   ├── 03_policy_impact.yaml
│   │   ├── 04_second_order.yaml
│   │   ├── 05_scenarios.yaml
│   │   └── 06_brief.yaml
│   └── output/
│       └── schema.yaml      # Output format definition
│
├── data/
│   ├── sources.yaml         # Whitelisted data sources
│   ├── events/              # Daily event snapshots (YYYY-MM-DD.yaml)
│   └── archive/             # Historical analysis outputs
│
├── pipeline/
│   ├── __init__.py
│   ├── main.py              # Orchestrator (run this)
│   ├── fetch.py             # Fetch raw events
│   ├── normalize.py         # Clean & structure events
│   ├── run_llm.py           # Execute LLM reasoning
│   ├── validate.py          # Schema & constraint checks
│   └── shutdown.py          # Execution guard (time/token limits)
│
├── schedules/
│   └── daily.yaml           # Cron/scheduler config (9 AM ET, weekdays)
│
├── config.yaml              # Pipeline settings (API, limits, paths)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements:**
- `pyyaml` — YAML parsing
- `openai` — OpenAI API (or `azure-openai` for Azure)
- `python-dotenv` — Load API keys from .env

### 2. Configure API Keys

Create a `.env` file in the repo root:

```bash
OPENAI_API_KEY=your-key-here
# OR for Azure OpenAI:
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### 3. Edit `config.yaml`

Update API settings:
- `api.provider`: `"openai"` or `"azure_openai"`
- `api.model`: e.g., `"gpt-4o"` (recommended) or `"gpt-4-turbo"`
- `api.temperature`: reasoning temperature (0.7 = balanced)
- `limits.daily_token_budget`: total tokens/day (e.g., 100,000)
- `limits.execution_window_minutes`: max runtime (60 = 1 hour)

---

## Usage

### Run Manually (for testing)

```bash
# Run full pipeline for today
cd pipeline
python main.py

# Or specify a date
python main.py 2026-01-28
```

**Output:**
- Raw events: `data/events/2026-01-28.yaml`
- Normalized: `data/events/2026-01-28-normalized.yaml`
- Analysis: `data/archive/2026-01-28-analysis.yaml`
- Validation: `data/archive/2026-01-28-validation.yaml`

### Schedule Locally (macOS/Linux)

Use `cron` or `launchd`:

**macOS (launchd):**

1. Create `~/Library/LaunchAgents/com.econ-llm.daily.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.econ-llm.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/econ-llm/pipeline/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
        <key>Weekday</key>
        <integer>0</integer> <!-- 0=Sunday, skip; set to 1-5 for M-F -->
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/econ-llm.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/econ-llm-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OPENAI_API_KEY</key>
        <string>your-api-key</string>
    </dict>
</dict>
</plist>
```

2. Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.econ-llm.daily.plist
```

**Linux (cron):**

```bash
crontab -e
# Add line for 9 AM ET weekdays:
0 9 * * 1-5 cd /path/to/econ-llm && python pipeline/main.py >> /tmp/econ-llm.log 2>&1
```

### Schedule via GitHub Actions (cloud)

If hosted on GitHub, create `.github/workflows/daily-pipeline.yml`:

```yaml
name: Daily Econ LLM Pipeline

on:
  schedule:
    - cron: '0 9 * * 1-5'  # 9 AM ET, M-F
  workflow_dispatch:  # Manual trigger

jobs:
  pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run pipeline
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: cd pipeline && python main.py
      - name: Commit outputs
        run: |
          git config user.name "bot"
          git add data/archive/
          git commit -m "Daily analysis: $(date +%Y-%m-%d)" || true
          git push
```

---

## Pipeline Flow

### Step 1: Fetch
Read events from whitelisted sources (Fed calendar, BLS, Treasury, etc.).

**TODO:** Wire up actual API integrations.

### Step 2: Normalize
Deduplicate, clean, and structure raw events into YAML.

### Step 3-6: LLM Reasoning
Sequential prompts, each feeding into the next:

1. **Filter & Prioritize** — Rank events by macro significance
2. **Macro Regime** — Classify current state (inflationary, disinflationary, etc.)
3. **Policy Impact** — Direct & indirect effects of policy moves
4. **Second-Order Effects** — Cascading consequences
5. **Scenarios** — Bull, base, bear cases (6-12 month horizon)
6. **Executive Brief** — 3-5 min summary + watch list

### Step 7: Validate
Check outputs against schema and constraint rules (no price prediction, no trading advice, etc.).

### Step 8: Shutdown Guard
Enforce time and token limits to prevent runaway execution.

---

## Outputs

### Daily Analysis (`data/archive/YYYY-MM-DD-analysis.yaml`)

```yaml
date: 2026-01-28
timestamp: 2026-01-28T13:45:00Z
steps:
  01_filter_events:
    filtered_events:
      - rank: 1
        event: "Fed raises rates 0.25%"
        significance: high
        rationale: ...
  02_macro_regime:
    primary_regime:
      regime: "INFLATIONARY"
      confidence: 78
      drivers: ["Sticky services inflation", "Labor market strength", ...]
  03_policy_impact:
    ...
  04_second_order:
    ...
  05_scenarios:
    scenarios:
      - scenario_name: BULL
        probability: 0.30
      - scenario_name: BASE
        probability: 0.50
      - scenario_name: BEAR
        probability: 0.20
  06_brief:
    headline: "Fed stays restrictive; watch for growth signals"
    watch_list:
      - item: "PCE inflation release"
        timing_days: 14
```

### Validation Report (`data/archive/YYYY-MM-DD-validation.yaml`)

```yaml
timestamp: 2026-01-28T13:45:30Z
schema_valid: true
schema_errors: []
constraints_met: true
constraint_violations: []
overall_valid: true
```

---

## Constraints & Guardrails

### Hard Constraints (checked in prompts/system/constraints.yaml)

- ❌ **No price prediction** — "will go up/down", "target price", etc.
- ❌ **No trading advice** — "buy", "sell", "go long", etc.
- ❌ **Evidence-grounded only** — No speculation beyond provided data
- ✅ **Scope limited** — Macro regimes, policy effects, scenarios only

### Execution Guards (pipeline/shutdown.py)

- **Time limit**: 60 minutes max (enforced with 5-min buffer)
- **Token budget**: 100,000 tokens/day (configurable)
- **Shutdown**: Graceful halt if budget exceeded; fewer steps if needed

---

## Configuration

Edit `config.yaml` to adjust:

```yaml
api:
  provider: "openai"      # or "azure_openai"
  model: "gpt-4o"         # Model to use
  temperature: 0.7        # Reasoning balance
  max_tokens: 4000        # Per-call limit

limits:
  daily_token_budget: 100000      # Tokens/day
  execution_window_minutes: 60    # Max runtime
  max_retries: 3
  timeout_seconds: 300
```

---

## Development

### Adding a New Step

1. Create `prompts/steps/NN_step_name.yaml` with prompt template + output schema
2. Reference in `run_llm.py` steps list
3. Test with `python main.py`

### Modifying Prompts

All prompts are versioned in YAML. Edit directly:
- `prompts/system/role.yaml` — Analyst role
- `prompts/system/constraints.yaml` — Guardrails
- `prompts/steps/NN_*.yaml` — Reasoning steps

Changes take effect immediately on next run.

### Testing

Run manual pipeline for a test date:

```bash
python pipeline/main.py 2026-01-20
```

Check outputs in `data/archive/`.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `OpenAI API key not found` | Add to `.env` or environment variables |
| `Token budget exceeded` | Increase `limits.daily_token_budget` in config.yaml |
| `Constraint violated` | Check output for banned keywords; review constraint definitions |
| `Pipeline hangs` | Check `limits.execution_window_minutes`; may need to increase |

---

## Next Steps

1. **Wire up data sources** — Implement API calls in `fetch.py` for Fed, BLS, etc.
2. **Test with live data** — Run pipeline with real events from today
3. **Tune prompts** — Iterate on reasoning steps based on output quality
4. **Set up scheduling** — Choose cron, launchd, or GitHub Actions
5. **Monitor costs** — Track actual token usage vs. budget

---

## Philosophy

This system is intentionally **narrow and constrained**:
- ✅ Macro reasoning & policy analysis
- ✅ Scenario construction
- ✅ Regime classification
- ❌ Price prediction
- ❌ Trading advice
- ❌ Real-time execution

The discipline is enforced through:
1. **Prompts** — System role + explicit constraints
2. **Validation** — Keyword filtering post-execution
3. **Execution guards** — Hard time/token limits

This design keeps costs low, reasoning focused, and output auditable.

---

**Questions?** See [README.md](./README.md) or check prompt definitions in `prompts/`.
