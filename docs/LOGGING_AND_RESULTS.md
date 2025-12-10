# Logging and Results Management

Created: 2025-12-08

## Overview

The system now automatically saves assessment results and logs complete workflow execution for audit and analysis purposes.

## Features

### 1. Automatic JSON Result Saving

Every assessment run automatically saves a complete JSON file containing:
- **Metadata**: Timestamp, input scenario, revision count, statistics
- **Input**: Original risk scenario description
- **Output**: Complete assessment results including:
  - Synthesized draft (final assessment)
  - All 9 initial draft assessments
  - All critiques from challengers
- **Workflow Stats**: Revision count, total assessments, total critiques

**File Location**: `results/assessment_YYYYMMDD_HHMMSS.json`

**Example**:
```json
{
  "metadata": {
    "timestamp": "2025-12-08T22:36:38.906673",
    "risk_input": "IoT device: WiFi connection...",
    "revision_count": 3,
    "total_assessments": 9,
    "total_critiques": 63
  },
  "input": { ... },
  "output": { ... },
  "workflow_stats": { ... }
}
```

### 2. Complete Workflow Logging

Every assessment run creates a detailed log file recording:
- Workflow start with input scenario
- Final assessment result (score, summary, arguments, citations, vulnerabilities)
- All critiques with status and recommendations
- Workflow statistics
- Result file path

**File Location**: `logs/assessment_YYYYMMDD_HHMMSS.log`

**Log Format**:
```
2025-12-08 22:35:28 - INFO - RISK ASSESSMENT WORKFLOW STARTED
2025-12-08 22:35:28 - INFO - Input Scenario: ...
2025-12-08 22:36:38 - INFO - FINAL ASSESSMENT RESULT
2025-12-08 22:36:38 - INFO - Risk Score: 5/5
...
```

## Usage

### Default Behavior (Automatic)

By default, both logging and result saving are enabled:

```python
from src.main import run_risk_assessment

result = run_risk_assessment("IoT device scenario...")
# Automatically:
# - Saves JSON to results/ directory
# - Creates log file in logs/ directory
```

### Disable Saving/Logging

You can disable either feature:

```python
# Disable result saving
result = run_risk_assessment(
    "IoT device scenario...",
    save_result=False
)

# Disable logging
result = run_risk_assessment(
    "IoT device scenario...",
    enable_logging=False
)

# Disable both
result = run_risk_assessment(
    "IoT device scenario...",
    save_result=False,
    enable_logging=False
)
```

## Directory Structure

```
project_root/
├── results/              # JSON result files (auto-created)
│   └── assessment_*.json
├── logs/                 # Log files (auto-created)
│   └── assessment_*.log
└── ...
```

## File Naming Convention

Both JSON and log files use the same timestamp format:
- **Format**: `assessment_YYYYMMDD_HHMMSS.{json|log}`
- **Example**: `assessment_20251208_223638.json`

The timestamp reflects when the workflow **completed**, ensuring chronological ordering.

## Benefits

1. **Audit Trail**: Complete record of all assessments for regulatory compliance
2. **Analysis**: Historical data for pattern analysis and system improvement
3. **Debugging**: Detailed logs help identify issues in workflow execution
4. **Reproducibility**: Saved results enable result review and comparison
5. **Compliance**: Structured JSON format suitable for regulatory reporting

## File Management

- Files are automatically created in `results/` and `logs/` directories
- Directories are created automatically if they don't exist
- Files are **not** committed to Git (see `.gitignore`)
- Old files can be manually archived or deleted as needed

## Accessing Saved Results

### Read JSON Result

```python
import json

with open('results/assessment_20251208_223638.json', 'r') as f:
    result_data = json.load(f)
    
print(f"Risk Score: {result_data['output']['synthesized_draft']['score']}/5")
print(f"Summary: {result_data['output']['synthesized_draft']['reasoning']['summary']}")
```

### Search Logs

```python
import glob
from pathlib import Path

# Find all log files
log_files = glob.glob('logs/assessment_*.log')

# Find logs from specific date
date_logs = glob.glob('logs/assessment_20251208_*.log')
```

## Integration with Existing Scripts

All existing scripts automatically benefit from logging and saving:
- `scripts/quick_verify.py` - Results saved automatically
- `scripts/show_results.py` - Results saved automatically
- `src/main.py` - Results saved automatically

No changes needed to existing code!

