# AI-Trading-Bot
Prompt to Openai to check latest news and save data to make decisions on stock directions and economic decisions. This is just a test project for fun.


econ-llm/
├── prompts/
│   ├── system/          # System & constraint prompts
│   ├── steps/           # Stepwise reasoning prompts
│   └── output/          # Output format definitions
│
├── data/
│   ├── sources.yaml     # Source registry
│   ├── events/          # Daily event snapshots
│   ├── archive/         # Historical runs
│   └── embeddings/      # Optional (future)
│
├── pipeline/
│   ├── fetch.py         # Fetch raw events
│   ├── normalize.py    # Clean & structure events
│   ├── run_llm.py      # Execute prompt pipeline
│   ├── validate.py     # Schema & sanity checks
│   └── shutdown.py     # Enforce time window
│
├── schedules/
│   └── daily.yaml       # Execution schedule
│
├── config.yaml
└── README.md
