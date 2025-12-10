# Project Structure - Clean MAS System

This document describes the clean project structure with only MAS (Multi-Agent System) core files and Input/Output directories.

## Core MAS System

```
GVC/
├── src/                          # Core MAS implementation
│   ├── agents/                   # Agent implementations
│   │   ├── generator_ensemble.py    # 9-model generator ensemble
│   │   ├── aggregator.py            # Assessment aggregator
│   │   ├── challenger_a.py          # Logic challenger
│   │   ├── challenger_b.py          # Source verification challenger
│   │   ├── challenger_c.py          # Compliance challenger
│   │   └── verifier.py              # Workflow verifier
│   ├── utils/                   # Utility modules
│   │   ├── prompt_templates.py      # Agent prompts
│   │   ├── reference_sources.py     # Reference sources
│   │   ├── logger.py                # Logging utilities
│   │   ├── result_saver.py          # Result saving
│   │   ├── conversation_recorder.py  # Conversation recording
│   │   ├── citation_parser.py       # Citation parsing
│   │   └── search_helpers.py        # Search utilities
│   ├── config.py                # Configuration
│   ├── schemas.py               # Pydantic schemas
│   ├── graph.py                 # LangGraph workflow
│   └── main.py                  # Main entry point
│
├── scripts/                     # Core MAS scripts only
│   ├── formal_assessment.py     # Main assessment runner
│   └── test_system_health.py    # System health check
│
├── evaluation_inputs/            # Input scenarios
│   ├── scenario_1_protocol_weaknesses.txt
│   ├── scenario_2_remote_direct_control.txt
│   ├── scenario_3_user_awareness_risk.txt
│   ├── scenario_4_data_hacking_breaching.txt
│   ├── scenario_5_mass_data_inference.txt
│   ├── scenario_6_lack_of_continuous_updates.txt
│   ├── scenario_7_cloud_dependency.txt
│   ├── scenario_8_iot_as_medium_for_broader_network_attacks.txt
│   ├── scenario_9_physical_safety_fire_hazards.txt
│   ├── scenario_10_data_security_secondhand_market.txt
│   ├── scenario_11_environmental_toxicity.txt
│   └── README.md
│
├── results/                     # Assessment results (output)
│   └── formal_assessment_*/      # Timestamped assessment directories
│       └── assessment_iot_risk_*.json
│
├── logs/                        # System logs (output)
│   └── assessment_iot_risk_*.log
│
├── examples/                    # Example usage
│   ├── test_full_workflow.py
│   └── test_individual_agents.py
│
├── docs/                        # System documentation only
│   ├── README.md                # System documentation
│   ├── API_KEYS.md              # API key setup
│   ├── SYSTEM_OUTPUT_REFERENCE.md
│   ├── LOGGING_AND_RESULTS.md
│   ├── DIAGRAM_GUIDE.md
│   ├── DUAL_FACTOR_ASSESSMENT_UPDATE.md
│   └── LIKELIHOOD_FREQUENCY_ALIGNMENT.md
│
├── analysis/                    # Analysis scripts and reports (separated)
│   ├── scripts/                 # Analysis scripts
│   └── docs/                    # Analysis reports
│
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
├── README.md                   # Main project README
└── .env                        # Environment variables (not in repo)
```

## Directory Purposes

### Core System (`src/`)
Contains the complete Multi-Agent System implementation:
- **Agents**: All agent implementations (Generator, Aggregator, Challengers, Verifier)
- **Utils**: Supporting utilities for prompts, logging, results, etc.
- **Core**: Configuration, schemas, workflow graph, main entry point

### Input (`evaluation_inputs/`)
Risk scenario input files in text format. Each file contains:
- Lifecycle Stage (Usage Phase or EOL)
- Risk Category
- Scenario Description
- Risk Mechanism
- Context Data
- Task instructions

### Output (`results/` and `logs/`)
- **results/**: JSON files containing complete assessment results
- **logs/**: Detailed conversation logs from all agents

### Scripts (`scripts/`)
Only core MAS execution scripts:
- `formal_assessment.py`: Run batch assessments
- `test_system_health.py`: Verify system functionality

### Documentation (`docs/`)
System documentation only (no analysis reports):
- Setup and configuration guides
- System architecture documentation
- API references

### Analysis (`analysis/`)
All analysis scripts and evaluation reports have been moved here to keep the core system clean.

## Usage

### Running an Assessment

```bash
# Run formal assessment for all scenarios
python scripts/formal_assessment.py

# Run single assessment
python src/main.py
```

### Input Format

Place scenario files in `evaluation_inputs/` following the format:
```
Lifecycle Stage: Usage Phase
Risk Category: [Category Name]

Scenario Description:
[Description]

Risk Mechanism:
[Mechanism]

Context Data:
- [Data point 1]
- [Data point 2]

Task:
[Task instructions]
```

### Output Format

Results are saved to `results/formal_assessment_YYYYMMDD/` as JSON files containing:
- Metadata (timestamp, revision count, etc.)
- Input scenario
- Output (synthesized draft, draft assessments, critiques)
- Complete conversation trace

## Clean Separation

- **MAS Core**: `src/`, `scripts/` (core only), `docs/` (system docs only)
- **Input**: `evaluation_inputs/`
- **Output**: `results/`, `logs/`
- **Analysis**: `analysis/` (separated from core system)

