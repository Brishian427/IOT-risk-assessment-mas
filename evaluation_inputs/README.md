# Evaluation Inputs

This directory contains test scenarios and evaluation inputs for the Multi-Agent Risk Assessment System.

## Format

Each input file should contain a plain text description of an IoT device scenario. The format is flexible, but should include:

- Device type/name
- Connectivity features (WiFi, Bluetooth, etc.)
- Security characteristics (encryption, authentication, etc.)
- Known vulnerabilities (CVE numbers, if applicable)
- Compliance status (PSTI Act 2022, ISO standards, etc.)
- Any other security-relevant information

## Usage

You can use these inputs in several ways:

### Method 1: Direct File Reading

```python
from src.main import run_risk_assessment

# Read from file
with open('evaluation_inputs/example_1_smart_thermostat.txt', 'r', encoding='utf-8') as f:
    risk_input = f.read()

result = run_risk_assessment(risk_input)
```

### Method 2: Batch Processing

```python
import os
from pathlib import Path
from src.main import run_risk_assessment

inputs_dir = Path('evaluation_inputs')
for input_file in inputs_dir.glob('*.txt'):
    with open(input_file, 'r', encoding='utf-8') as f:
        risk_input = f.read()
    
    print(f"\nProcessing: {input_file.name}")
    result = run_risk_assessment(risk_input)
```

## File Naming Convention

- Use descriptive names: `example_<number>_<device_type>.txt`
- Keep filenames lowercase with underscores
- Include a brief description in the filename

## Real-World Scenarios

### Usage Phase Scenarios (Primary)
- `scenario_1_mass_data_inference.txt` - Privacy risks from legitimate data collection and metadata analysis during normal device operation
- `scenario_2_remote_direct_control.txt` - Physical safety risks from unauthorized remote control of connected devices
- `scenario_3_data_hacking_breaching.txt` - Technical security failures leading to large-scale data theft and credential exposure
- `scenario_4_user_awareness_deficit.txt` - Human behavior risks from user negligence and security awareness gaps

### End-of-Life (EOL) Scenarios
- `scenario_9_physical_safety_fire_hazards.txt` - Physical safety risks from improper disposal of IoT devices with lithium-ion batteries
- `scenario_10_data_security_secondhand_market.txt` - Data privacy risks from second-hand market circulation without proper data wiping
- `scenario_11_environmental_toxicity.txt` - Environmental and public health risks from toxic materials in IoT waste

## Scenario Format

Each scenario includes:
- **Lifecycle Stage**: The stage of the device lifecycle (e.g., End-of-Life)
- **Risk Category**: The type of risk being assessed
- **Scenario Description**: Detailed description of the risk situation
- **Risk Mechanism**: How the risk manifests
- **Context Data**: Supporting statistics and facts
- **Task**: Specific evaluation instructions

Created: 2025-12-09
Updated: 2025-12-09

