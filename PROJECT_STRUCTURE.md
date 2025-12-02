# Project Structure

## Directory Organization

```
GVC/
├── src/                      # Main source code
│   ├── agents/              # Agent implementations
│   ├── utils/               # Utility functions
│   ├── schemas.py           # Data models
│   ├── config.py            # Configuration
│   ├── graph.py             # LangGraph workflow
│   └── main.py              # Entry point
│
├── scripts/                 # Utility and analysis scripts
│   ├── show_results.py      # Run assessment and display results
│   ├── cost_estimator.py    # Estimate operation costs
│   ├── measure_time.py      # Measure execution time
│   ├── time_analysis.py     # Time analysis based on history
│   ├── analyze_pass_rate.py # Analyze revision patterns
│   ├── test_setup.py        # Setup validation
│   └── quick_test.py        # Quick schema test
│
├── examples/                # Example and test scripts
│   ├── test_full_workflow.py    # End-to-end test
│   └── test_individual_agents.py # Unit tests
│
├── docs/                    # Documentation
│   ├── API_KEYS.md          # API key management
│   ├── IMPROVEMENTS_SUMMARY.md # System improvements
│   └── revision_analysis.md # Revision analysis
│
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata
└── README.md                # Main documentation
```

## File Categories

### Source Code (`src/`)
- Core implementation of the multi-agent system
- All agent logic and workflow orchestration

### Scripts (`scripts/`)
- Testing and analysis utilities
- Can be run independently for various purposes

### Examples (`examples/`)
- Example usage and test cases
- Reference implementations

### Documentation (`docs/`)
- Project documentation
- Analysis reports
- API key management guide

