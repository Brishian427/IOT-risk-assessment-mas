# Dual-Factor Risk Assessment Update
Created: 2025-12-09

## Overview

The system has been updated to support **dual-factor risk assessment** with separate Frequency and Impact scores that multiply to form the Final Risk Score (1-25).

## Changes Summary

### 1. Schema Updates (`src/schemas.py`)

**New Model**: `RiskAssessmentBreakdown`
- `frequency_score`: Integer 1-5 (Historical frequency)
- `frequency_rationale`: String (Justification for frequency)
- `impact_score`: Integer 1-5 (Impact severity)
- `impact_rationale`: String (Justification for impact)
- `final_risk_score`: Integer 1-25 (frequency × impact)
- `risk_classification`: String (Low/Medium/High/Critical)

**Updated Model**: `RiskAssessment`
- Added optional `risk_assessment: Optional[RiskAssessmentBreakdown]` field
- Maintains backward compatibility with legacy `score` field (1-5)

### 2. Generator Prompt Updates (`src/utils/prompt_templates.py`)

**New Instructions**:
- **DIMENSION 1: HISTORICAL FREQUENCY (1-5)**
  - Score 5 (Systemic/Default): Happens by default or via automated widespread attacks
  - Score 4 (Common): Frequently reported vulnerabilities
  - Score 3 (Occasional): Requires targeted effort or specific conditions
  - Score 2 (Rare): Proof-of-concept only
  - Score 1 (Theoretical): Never observed in the wild

- **DIMENSION 2: IMPACT SEVERITY (1-5)**
  - Score 5 (Catastrophic): Loss of life, severe physical harm, permanent infrastructure damage
  - Score 4 (Severe): Major privacy breach, financial loss, identity theft
  - Score 3 (Moderate): Service disruption or reversible damage
  - Score 1-2 (Minor): Nuisance or minimal loss

- **RISK CLASSIFICATION**:
  - Critical: 20-25
  - High: 12-19
  - Medium: 6-11
  - Low: 1-5

**New JSON Output Format**:
```json
{
    "score": <1-5>,  // Legacy score for backward compatibility
    "reasoning": {...},
    "risk_assessment": {
        "frequency_score": <1-5>,
        "frequency_rationale": "...",
        "impact_score": <1-5>,
        "impact_rationale": "...",
        "final_risk_score": <1-25>,  // frequency × impact
        "risk_classification": "Low/Medium/High/Critical"
    }
}
```

### 3. Challenger A Updates (`src/agents/challenger_a.py`, `src/utils/prompt_templates.py`)

**New Audit Checks**:
1. **CHECK 1: FREQUENCY SCORE (Tolerance Applied)**
   - Requires at least one historical case or real-world incident
   - Does NOT demand statistical tables or exhaustive evidence
   - Flags high frequency (4-5) without case studies

2. **CHECK 2: IMPACT SCORE (Strict)**
   - Verifies impact score matches described harm
   - Rejects mismatches (e.g., Impact 5 for "Ad tracking")

3. **CHECK 3: CALCULATION VERIFICATION**
   - Verifies: Frequency × Impact = Final Risk Score
   - Calculation errors are CRITICAL and cause rejection

4. **CHECK 4: RISK CLASSIFICATION**
   - Verifies classification matches final_risk_score ranges

5. **CHECK 5: LEGACY SCORE CONSISTENCY**
   - Minor check for backward compatibility

**Tolerance Maintained**:
- Core logic sound → accept even with minor gaps
- Only reject for SIGNIFICANT inconsistencies or calculation errors
- Minor issues noted but don't require rejection

### 4. Aggregator Updates (`src/agents/aggregator.py`, `src/utils/prompt_templates.py`)

**Synthesis Logic**:
- Synthesizes frequency_score from consensus across models
- Synthesizes impact_score from consensus across models
- Calculates final_risk_score = frequency_score × impact_score
- Determines risk_classification based on final_risk_score

**Revision Logic**:
- Addresses frequency-related critiques
- Addresses impact-related critiques
- Fixes calculation errors if identified

### 5. Result Saving Updates (`src/utils/result_saver.py`)

- Saves `risk_assessment` breakdown in JSON output
- Maintains backward compatibility with legacy format

### 6. Logging Updates (`src/utils/logger.py`, `src/main.py`)

- Logs dual-factor assessment breakdown
- Displays frequency, impact, final score, and classification
- Shows calculation verification

## Example Outputs

### Mass Data Inference
```json
{
    "risk_assessment": {
        "frequency_score": 5,
        "frequency_rationale": "Data collection is a default function of the device and occurs continuously without requiring a hack, making the frequency 'Systemic'.",
        "impact_score": 4,
        "impact_rationale": "Detailed occupancy data can lead to burglary (physical security) and severe privacy profiling, warranting a 'Severe' impact rating.",
        "final_risk_score": 20,
        "risk_classification": "Critical"
    }
}
```

### Remote Direct Control
```json
{
    "risk_assessment": {
        "frequency_score": 3,
        "frequency_rationale": "Requires targeted hacking effort and specific vulnerabilities (e.g., Finland HVAC case), making it 'Occasional' rather than default behavior.",
        "impact_score": 5,
        "impact_rationale": "Can cause freezing pipes, hypothermia, or unauthorized physical entry, posing a direct threat to life and safety ('Catastrophic').",
        "final_risk_score": 15,
        "risk_classification": "High"
    }
}
```

## Backward Compatibility

- Legacy `score` field (1-5) is maintained for backward compatibility
- Mapping: final_risk_score 1-5→1, 6-10→2, 11-15→3, 16-20→4, 21-25→5
- System works with or without `risk_assessment` breakdown
- Existing result files remain valid

## Files Modified

1. `src/schemas.py` - Added RiskAssessmentBreakdown model
2. `src/utils/prompt_templates.py` - Updated Generator, Aggregator, Challenger A prompts
3. `src/agents/generator_ensemble.py` - Parse and validate risk_assessment
4. `src/agents/aggregator.py` - Synthesize and revise risk_assessment
5. `src/agents/challenger_a.py` - Audit dual-factor assessment
6. `src/utils/result_saver.py` - Save risk_assessment in JSON
7. `src/utils/logger.py` - Log dual-factor assessment
8. `src/main.py` - Display dual-factor assessment

## Testing

The system maintains all existing functionality while adding dual-factor assessment. Test with:
```bash
python src/main.py
```

Expected: Output includes both legacy score (1-5) and new dual-factor breakdown (frequency × impact = 1-25).

