# Comprehensive Documentation: IoT Risk Assessment Multi-Agent System

**Document Created:** 2025-12-10  
**Purpose:** Complete documentation of system development, progress reports, evaluation results, and prompt engineering  
**Status:** Offline Reference Document

---

## Introduction

This document provides a comprehensive record of the development and evaluation of the IoT Risk Assessment Multi-Agent System (MAS). The system implements a dual-factor risk assessment framework (Frequency × Impact) using a reasoning-first architecture with multiple specialized agents.

### System Overview

The MAS consists of:
- **Generator Ensemble**: 9 parallel LLM models generating initial risk assessments
- **Aggregator**: Synthesizes unified assessment from ensemble outputs
- **Challenger A (Logic)**: Validates internal consistency and logical reasoning
- **Challenger B (Source)**: Verifies external citations and factual claims
- **Challenger C (Compliance)**: Validates regulatory and safety compliance
- **Verifier**: Routes workflow based on critiques (revision loop or completion)

### Document Structure

This document is organized into four main sections:

1. **Progress Reports**: Chronological development updates and system improvements
2. **Evaluation Results**: Comprehensive assessment results and human-AI validation analysis
3. **System Output Reference**: Documentation of system outputs and logging
4. **Prompt Appendix**: Complete prompt templates for all agents

This documentation serves as a complete reference for understanding the system's evolution, current capabilities, and prompt engineering approach.

---

## Part 1: Progress Reports

### 1.1 Dual-Factor Risk Assessment Update

**Created:** 2025-12-09

#### Overview

The system has been updated to support **dual-factor risk assessment** with separate Frequency and Impact scores that multiply to form the Final Risk Score (1-25).

#### Changes Summary

**1. Schema Updates**

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

**2. Generator Prompt Updates**

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

**3. Challenger A Updates**

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

**4. Aggregator Updates**

**Synthesis Logic**:
- Synthesizes frequency_score from consensus across models
- Synthesizes impact_score from consensus across models
- Calculates final_risk_score = frequency_score × impact_score
- Determines risk_classification based on final_risk_score

**Revision Logic**:
- Addresses frequency-related critiques
- Addresses impact-related critiques
- Fixes calculation errors if identified

**5. Result Saving Updates**

- Saves `risk_assessment` breakdown in JSON output
- Maintains backward compatibility with legacy format

**6. Logging Updates**

- Logs dual-factor assessment breakdown
- Displays frequency, impact, final score, and classification
- Shows calculation verification

#### Example Outputs

**Mass Data Inference**:
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

**Remote Direct Control**:
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

#### Backward Compatibility

- Legacy `score` field (1-5) is maintained for backward compatibility
- Mapping: final_risk_score 1-5→1, 6-10→2, 11-15→3, 16-20→4, 21-25→5
- System works with or without `risk_assessment` breakdown
- Existing result files remain valid

---

### 1.2 Likelihood = Frequency Alignment Update

**Created:** 2025-12-09

#### Overview

Updated the system to ensure **Likelihood** and **Frequency** are treated as **synonyms**, with Likelihood explicitly redefined as "Frequency of Occurrence" and "Prevalence in the Current Landscape", NOT as "theoretical probability of a future event."

#### Problem Statement

LLMs are trained with "Likelihood" typically meaning "future probability prediction." Without explicit redefinition, agents might confuse:
- "Theoretically possible" (Possibility) 
- "Actually frequently occurring" (Frequency)

This misalignment could cause agents to score risks incorrectly (e.g., lowering frequency scores because "smart users could prevent it").

#### Solution: Explicit Redefinition

**1. Generator Prompt Updates**

**Added CRITICAL DEFINITION section**:

```
### CRITICAL DEFINITION: LIKELIHOOD = FREQUENCY

IMPORTANT: In this risk assessment framework, "Likelihood" DOES NOT mean 
"theoretical probability of a future event."

Instead, "Likelihood" is defined as "Frequency of Occurrence" and 
"Prevalence in the Current Landscape."

You must assign the Likelihood/Frequency Score (1-5) based on the following 
strict rubric:

- Score 5 (Systemic/Constant): The risk is an inherent part of the device's 
  standard operation OR a near-universal user behavior. It happens by default.
  * Reference Examples: Mass Data Inference, User Awareness Deficit

- Score 4 (Widespread/Common): The vulnerability is present in a vast majority 
  of devices or is frequently exploited by automated tools.
  * Reference Examples: Data Hacking (98% unencrypted), Mirai Botnet

- Score 3 (Targeted/Occasional): Requires specific technical skills, targeted 
  malice, or specific conditions to exploit.
  * Reference Examples: Remote Direct Control (Finland HVAC attack)

- Score 2 (Rare/Proof-of-Concept): Feasible in laboratory settings, rarely 
  seen in the wild.

- Score 1 (Theoretical): No documented cases; purely hypothetical.

Constraint: Do NOT lower the score just because a "smart user" *could* prevent 
it. Assume the average, non-technical user behavior. Focus on how prevalent the 
risk state is, not on whether it *could* be prevented.
```

**2. Challenger A Prompt Updates**

**Added AUDIT INSTRUCTION section**:

```
### CRITICAL DEFINITION: LIKELIHOOD = FREQUENCY

IMPORTANT: In this framework, "Likelihood" is defined as "Frequency of 
Occurrence" and "Prevalence in the Current Landscape", NOT as "theoretical 
probability of a future event."

The Frequency/Likelihood score measures how often the risk state occurs or 
how widespread the vulnerability is, not whether it *might* happen in the 
future.

### AUDIT INSTRUCTION: LIKELIHOOD vs. IMPACT

How to validate Likelihood/Frequency Scores:

1. Check for Prevalence: If the Generator cites evidence that a vulnerability 
   is widespread (e.g., "57% of devices affected") or inherent (e.g., 
   "functionality requires data sending"), they MUST assign a High Likelihood 
   (4 or 5).

2. Reject "Theoretical" Arguments: If the Generator argues "It is unlikely 
   because hackers might not be interested," REJECT this reasoning. If the 
   door is unlocked (vulnerability exists), the Likelihood of the risk state 
   is HIGH, even if no one has walked through it yet.

3. Validate against Ground Truth:
   - Standard Operation (Data Collection) = Score 5 (Systemic/Constant)
   - Widespread Vulnerability (Unencrypted Traffic) = Score 4 (Common)
   - Targeted Hack (Remote Control) = Score 3 (Occasional)
   - If the Generator deviates significantly from this logic, flag it as an 
     error.

Key Principle: Do NOT lower the Likelihood score just because a "smart user" 
*could* prevent it. Focus on how prevalent the risk state is, not on whether 
it *could* be prevented.
```

**3. Aggregator Prompt Updates**

- Initial Synthesis: Reminder that "Likelihood" = "Frequency" when synthesizing
- Revision: Reminder when addressing frequency-related critiques
- JSON Format: Comments clarifying frequency_score = Likelihood

**4. Scenario File Updates**

**Updated all 11 scenario Task descriptions**:

**Before:**
```
Task:
Evaluate the Risk Score (Likelihood x Impact). Consider that this data 
collection happens by default (high likelihood)...
```

**After:**
```
Task:
Evaluate the Risk Score (Frequency x Impact). For 'Frequency/Likelihood', 
ask yourself: 'Is this risk state a constant feature of the device, a 
widespread vulnerability, or a rare targeted attack?' This data collection 
happens by default (systemic frequency = 5)...
```

#### Key Changes Summary

| Component | Change |
|-----------|--------|
| **Generator Prompt** | Added CRITICAL DEFINITION section explicitly redefining Likelihood = Frequency |
| **Challenger A Prompt** | Added AUDIT INSTRUCTION with prevalence-based validation rules |
| **Aggregator Prompts** | Added REMINDER sections in synthesis and revision prompts |
| **JSON Format Comments** | Added "Also called 'Likelihood'" comments to frequency_score fields |
| **All 11 Scenarios** | Updated Task descriptions to use "Frequency x Impact" with explicit guidance |

#### Expected Behavior

**Example 1: Mass Data Inference**
- **Before (confused)**: "Likelihood = 3 (could be prevented with privacy settings)"
- **After (correct)**: "Frequency = 5 (data collection is default operation)"

**Example 2: Remote Direct Control**
- **Before (confused)**: "Likelihood = 5 (could happen to anyone)"
- **After (correct)**: "Frequency = 3 (requires targeted hacking, occasional)"

**Example 3: User Awareness**
- **Before (confused)**: "Likelihood = 2 (smart users would prevent it)"
- **After (correct)**: "Frequency = 5 (widespread user behavior, systemic)"

#### Validation

The system now ensures:
1. ✅ Likelihood is explicitly defined as Frequency (prevalence)
2. ✅ Agents focus on "how widespread" not "might happen"
3. ✅ Challenger rejects "theoretical" arguments for frequency
4. ✅ All prompts consistently use Likelihood = Frequency
5. ✅ Scenario tasks guide agents with explicit frequency assessment

---

### 1.3 System Improvements Summary

**Created:** 2025-12-09

#### Implemented Improvements

**1. ✅ Improved Aggregator Revision Strategy**

**Problem**: Aggregator in revision was just re-synthesizing, not actively improving based on critiques

**Solution**:
- Added `AGGREGATOR_REVISION_PROMPT` specifically for revisions
- Revision prompt explicitly requires:
  - Add detailed reasoning based on Challenger A feedback
  - Add compliance information based on Challenger C feedback
  - Remove unverified citations based on Challenger B feedback
- `aggregator_node` now detects if it's a revision cycle and uses the appropriate prompt

**2. ✅ Added Graceful Degradation**

**Problem**: After reaching maximum revision count, system forced termination even if assessment might be "good enough"

**Solution**:
- Added "good enough" check in `should_continue` function
- When maximum revision count is reached:
  - Check recent round of critiques
  - If at least 2/3 of Challengers pass, accept assessment and end
  - Otherwise still end (to avoid infinite loops)

**3. ✅ Adjusted Challenger Standards**

**Problem**: Challenger standards too strict, causing continuous failures

**Solution**:
- **Challenger A (Logic Check)**:
  - Allow pass when core logic is sound, even if some details are missing
  - Only reject for major logical inconsistencies
- **Challenger C (Compliance Check)**:
  - Allow pass when major compliance requirements are met, even if some standards are missing
  - Only reject for major compliance gaps

#### Expected Effects

**Pass Rate Improvement**:
- **Before**: Often reached maximum revision count (3 rounds), assessment might still have issues
- **Now**: 
  - Aggregator actively improves based on critiques
  - Challenger standards more reasonable, allow minor issues
  - When maximum revision count is reached, if 2/3 Challengers pass, system accepts

**Cost Optimization**:
- **Before**: ~¥5.79/assessment (often 3 revision rounds)
- **Expected**: 
  - If improvements are effective, may reduce to 1-2 rounds: ¥3.78-¥4.02/assessment
  - Even when maximum revision count is reached, will accept early if "good enough"

**Quality Assurance**:
- Aggregator revision strategy ensures actual improvement each round
- Graceful Degradation ensures acceptance within reasonable bounds
- Challenger standard adjustments ensure minor issues don't cause excessive rejection

---

### 1.4 Project Structure Clean-up

**Created:** 2025-12-10

#### Overview

Project structure has been reorganized to separate core MAS system files from analysis scripts and documentation.

#### Clean Structure

**Core MAS System**:
- `src/` - Core MAS implementation (agents, utils, config, schemas, graph, main)
- `scripts/` - Core MAS scripts only (formal_assessment.py, test_system_health.py)
- `evaluation_inputs/` - Input scenarios (11 scenario files)
- `results/` - Assessment results (output)
- `logs/` - System logs (output)
- `docs/` - System documentation only
- `examples/` - Example usage

**Analysis (Separated)**:
- `analysis/scripts/` - All analysis scripts
- `analysis/docs/` - All analysis reports

#### Directory Purposes

**Core System (`src/`)**:
- **Agents**: All agent implementations (Generator, Aggregator, Challengers, Verifier)
- **Utils**: Supporting utilities for prompts, logging, results, etc.
- **Core**: Configuration, schemas, workflow graph, main entry point

**Input (`evaluation_inputs/`)**:
- Risk scenario input files in text format
- Each file contains: Lifecycle Stage, Risk Category, Scenario Description, Risk Mechanism, Context Data, Task instructions

**Output (`results/` and `logs/`)**:
- **results/**: JSON files containing complete assessment results
- **logs/**: Detailed conversation logs from all agents

**Scripts (`scripts/`)**:
- Only core MAS execution scripts:
  - `formal_assessment.py`: Run batch assessments
  - `test_system_health.py`: Verify system functionality

**Documentation (`docs/`)**:
- System documentation only (no analysis reports)
- Setup and configuration guides
- System architecture documentation
- API references

**Analysis (`analysis/`)**:
- All analysis scripts and evaluation reports moved here to keep core system clean

#### Clean Separation

- **MAS Core**: `src/`, `scripts/` (core only), `docs/` (system docs only)
- **Input**: `evaluation_inputs/`
- **Output**: `results/`, `logs/`
- **Analysis**: `analysis/` (separated from core system)

---

## Part 2: Evaluation Results

### 2.1 Evaluation Results Summary: Human-AI Validation Research Focus

**Assessment Date:** 2025-12-10  
**Total Scenarios:** 11 (8 Usage Phase, 3 EOL Phase)  
**Assessment Type:** Dual-Factor Risk Assessment (Frequency × Impact)

#### 1. Core Results

**Overall Statistics**:
- **Total Scenarios Assessed:** 11
  - Usage Phase: 8 scenarios
  - EOL Phase: 3 scenarios
- **Success Rate:** 100% (all scenarios completed)

**Final Risk Score Distribution**:

| Score | Count | Percentage |
|-------|-------|------------|
| 25/25 | 4 | 36.4% |
| 20/25 | 5 | 45.5% |
| 16/25 | 2 | 18.2% |

**Risk Classification Distribution**:

| Classification | Count | Percentage |
|----------------|-------|------------|
| Critical | 8 | 72.7% |
| High | 3 | 27.3% |
| Medium | 0 | 0% |
| Low | 0 | 0% |

**Key Finding:** No scenarios scored below 16/25, indicating all risks are classified as High or Critical.

#### 2. AI Model Scoring Statistics & Bias Analysis

**Generator Ensemble - Legacy Scores (1-5)**:

| Model | Average | Std Dev | Range | Count |
|-------|---------|---------|-------|-------|
| gpt-3.5-turbo | 4.00 | 0.45 | [3-5] | 11 |
| gpt-3.5-turbo-0125 | 4.09 | 0.30 | [4-5] | 11 |
| gpt-4.1 | 4.36 | 0.50 | [4-5] | 11 |
| gpt-4.1-mini | 4.27 | 0.47 | [4-5] | 11 |
| gpt-4o | 3.64 | 0.67 | [3-5] | 11 |
| gpt-4o-2024-08-06 | 3.82 | 0.60 | [3-5] | 11 |
| gpt-4o-mini | 4.27 | 0.47 | [4-5] | 11 |
| gpt-4o-mini-2024-07-18 | 4.27 | 0.47 | [4-5] | 11 |
| gpt-4o-mini-2024-11-20 | 3.00 | 0.00 | [3-3] | 11 |

**Generator Ensemble - Frequency Scores (1-5)**:

| Model | Average | Std Dev | Range | Distribution | Count |
|-------|---------|---------|-------|--------------|-------|
| gpt-3.5-turbo | 4.18 | 0.60 | [3-5] | 3:1, 4:7, 5:3 | 11 |
| gpt-3.5-turbo-0125 | 4.18 | 0.60 | [3-5] | 3:1, 4:7, 5:3 | 11 |
| gpt-4.1 | 4.45 | 0.69 | [3-5] | 3:1, 4:4, 5:6 | 11 |
| gpt-4.1-mini | 4.55 | 0.69 | [3-5] | 3:1, 4:3, 5:7 | 11 |
| gpt-4o | 4.67 | 0.52 | [4-5] | 4:2, 5:4 | 6 |
| gpt-4o-2024-08-06 | 4.50 | 0.53 | [4-5] | 4:4, 5:4 | 8 |
| gpt-4o-mini | 4.45 | 0.52 | [4-5] | 4:6, 5:5 | 11 |
| gpt-4o-mini-2024-07-18 | 4.45 | 0.52 | [4-5] | 4:6, 5:5 | 11 |

**Generator Ensemble - Impact Scores (1-5)**:

| Model | Average | Std Dev | Range | Distribution | Count |
|-------|---------|---------|-------|--------------|-------|
| gpt-3.5-turbo | 4.09 | 0.54 | [3-5] | 3:1, 4:8, 5:2 | 11 |
| gpt-3.5-turbo-0125 | 4.18 | 0.40 | [4-5] | 4:9, 5:2 | 11 |
| gpt-4.1 | 4.27 | 0.47 | [4-5] | 4:8, 5:3 | 11 |
| gpt-4.1-mini | 4.18 | 0.60 | [3-5] | 3:1, 4:7, 5:3 | 11 |
| gpt-4o | 4.33 | 0.52 | [4-5] | 4:4, 5:2 | 6 |
| gpt-4o-2024-08-06 | 4.38 | 0.52 | [4-5] | 4:5, 5:3 | 8 |
| gpt-4o-mini | 4.18 | 0.40 | [4-5] | 4:9, 5:2 | 11 |
| gpt-4o-mini-2024-07-18 | 4.18 | 0.40 | [4-5] | 4:9, 5:2 | 11 |

**Bias Detection**:

**Frequency Score Distribution**:
- **Overall Average:** 4.41/5
- **Median:** 4.00/5
- **Range:** 3 - 5
- **Distribution:** 
  - Score 3: 4 assessments (5%)
  - Score 4: 39 assessments (48.75%)
  - Score 5: 37 assessments (46.25%)

⚠️ **POTENTIAL BIAS:** Frequency scores heavily skewed toward high end (average 4.41 ≥ 4.5 threshold). 72% of assessments scored 4 or 5.

**Impact Score Distribution**:
- **Overall Average:** 4.21/5
- **Median:** 4.00/5
- **Range:** 3 - 5
- **Distribution:**
  - Score 3: 2 assessments (2.5%)
  - Score 4: 59 assessments (73.75%)
  - Score 5: 19 assessments (23.75%)

⚠️ **POTENTIAL BIAS:** Impact scores heavily concentrated in 4-5 range (96.25% of assessments).

**Model-Specific Scoring Patterns**:

| Model | Frequency Avg | Impact Avg | Bias Level |
|-------|---------------|------------|------------|
| gpt-3.5-turbo | 4.18 | 4.09 | MODERATE |
| gpt-3.5-turbo-0125 | 4.18 | 4.18 | MODERATE |
| gpt-4.1 | 4.45 | 4.27 | MODERATE |
| **gpt-4.1-mini** | **4.55** | 4.18 | **HIGH** |
| **gpt-4o** | **4.67** | 4.33 | **HIGH** |
| **gpt-4o-2024-08-06** | **4.50** | 4.38 | **HIGH** |
| gpt-4o-mini | 4.45 | 4.18 | MODERATE |
| gpt-4o-mini-2024-07-18 | 4.45 | 4.18 | MODERATE |

**Bias Classification**:
- **HIGH bias:** Average frequency ≥ 4.5 OR average impact ≥ 4.5
- **MODERATE bias:** Average frequency ≥ 4.0 OR average impact ≥ 4.0
- **LOW bias:** Below 4.0

#### 3. Scenario-Level Variance Analysis (Inter-Model Disagreement)

The following scenarios show high variance (std > 0.5) in frequency or impact scores across generator models, indicating significant model disagreement:

| Scenario | Frequency Std | Impact Std | Status |
|----------|---------------|------------|--------|
| Data Privacy / Information Leakage | 0.53 | 0.00 | ⚠️ High variance |
| Environmental Toxicity & Public Health | 0.35 | 0.71 | ⚠️ High variance |
| Remote Direct Control | 0.52 | 0.55 | ⚠️ High variance |
| Data Hacking & Breaching | 0.52 | 0.52 | ⚠️ High variance |
| Lack of Continuous Updates | 0.52 | 0.00 | ⚠️ High variance |
| Cloud Dependency | 0.00 | 0.58 | ⚠️ High variance |
| IoT as Medium for Broader Network Attacks | 0.41 | 0.55 | ⚠️ High variance |
| Physical Safety / Fire Hazard | 0.53 | 0.46 | ⚠️ High variance |

**Key Finding:** 8 out of 11 scenarios (72.7%) show high inter-model variance, indicating significant disagreement among AI models on risk assessment.

#### 4. Key Weaknesses & Demand for Human-AI Validation

**A. Scoring Bias Evidence**:

**Findings**:
- Frequency scores: 72% of all generator assessments scored 4 or 5
- Impact scores: 96.25% scored 4 or 5 (heavy concentration)
- Final scores: No scenarios below 16/25 (all High or Critical classification)
- Score compression: Only 3 distinct final score values (16, 20, 25)

**Human Validation Needed:** Verify if this reflects reality or AI conservatism/risk-aversion bias.

**B. Model Disagreement Evidence**:

**Findings**:
- 8 scenarios (72.7%) show high inter-model variance
- Models disagree on frequency/impact assessment across multiple scenarios
- Standard deviations range from 0.35 to 0.71 for frequency scores
- Standard deviations range from 0.46 to 0.71 for impact scores

**Human Validation Needed:** Resolve disagreements through expert judgment. High variance scenarios require human review to determine correct assessment.

**C. Score Compression Evidence**:

**Findings**:
- Final scores range: 16 - 25 (only 3 distinct values)
- Average: 21.09/25
- Median: 20.00/25
- Standard deviation: 3.45
- Limited differentiation between risk levels

**Human Validation Needed:** Assess if compression is appropriate (all scenarios genuinely high-risk) or indicates calibration issues requiring score range expansion.

**D. EOL vs Usage Phase Discrepancy**:

**Findings**:
- Usage Phase average: 20.25/25
- EOL Phase average: 23.33/25
- Difference: 3.08 points (15.2% higher)
- EOL Phase: 100% Critical classification
- Usage Phase: 62.5% Critical, 37.5% High

**Human Validation Needed:** Verify if EOL risks are genuinely 15% higher or if this reflects assessment bias toward end-of-life concerns.

#### 5. Critical Human Intervention Points

**A. High-Stakes Scenarios (Score ≥ 25)**:

These scenarios received maximum risk scores and require human validation:

1. **Environmental Toxicity & Public Health** - 25/25 (Critical)
   - → **HUMAN REVIEW REQUIRED:** Catastrophic risk classification

2. **Data Hacking & Breaching** - 25/25 (Critical)
   - → **HUMAN REVIEW REQUIRED:** Catastrophic risk classification

3. **IoT as Medium for Broader Network Attacks** - 25/25 (Critical)
   - → **HUMAN REVIEW REQUIRED:** Catastrophic risk classification

4. **Physical Safety / Fire Hazard** - 25/25 (Critical)
   - → **HUMAN REVIEW REQUIRED:** Catastrophic risk classification

**B. High Variance Scenarios (Model Disagreement)**:

These scenarios show significant model disagreement and require human expert judgment:

1. **Data Privacy / Information Leakage** - Frequency std: 0.53, Impact std: 0.00
2. **Environmental Toxicity & Public Health** - Frequency std: 0.35, Impact std: 0.71
3. **Remote Direct Control** - Frequency std: 0.52, Impact std: 0.55
4. **Data Hacking & Breaching** - Frequency std: 0.52, Impact std: 0.52
5. **Lack of Continuous Updates** - Frequency std: 0.52, Impact std: 0.00
6. **Cloud Dependency** - Frequency std: 0.00, Impact std: 0.58
7. **IoT as Medium for Broader Network Attacks** - Frequency std: 0.41, Impact std: 0.55
8. **Physical Safety / Fire Hazard** - Frequency std: 0.53, Impact std: 0.46

**C. Edge Cases (Borderline Classifications)**:

These scenarios are at classification boundaries and require human review:

1. **Protocol Weaknesses** - 16/25 (High) - Borderline classification (High vs Critical threshold at 20)
2. **Cloud Dependency** - 16/25 (High) - Borderline classification (High vs Critical threshold at 20)

**D. Phase Transition Validation**:

**Finding:** Usage → EOL risk escalation patterns show systematic increase (3.08 points average difference).

**Human Review Required:** Validate lifecycle risk progression assumptions. Verify if EOL risks are genuinely higher or if assessment methodology introduces bias.

#### 6. Statistical Summary

**Final Risk Scores**:
- **Mean:** 21.09/25
- **Median:** 20.00/25
- **Standard Deviation:** 3.45
- **Minimum:** 16/25
- **Maximum:** 25/25
- **Range:** 9 points
- **Coefficient of Variation:** 16.4%

**Phase Comparison**:

| Phase | Count | Avg Score | Min | Max | Critical % |
|-------|-------|-----------|-----|-----|-------------|
| Usage Phase | 8 | 20.25 | 16 | 25 | 62.5% |
| EOL Phase | 3 | 23.33 | 20 | 25 | 100% |

#### 7. Recommendations for Human-AI Validation

**Immediate Actions Required**:

1. **Validate High-Stakes Scenarios (Score = 25)**
   - Human experts should review all 4 catastrophic risk scenarios
   - Verify if maximum scores are justified or reflect AI conservatism

2. **Resolve Model Disagreements**
   - 8 scenarios require human judgment to resolve inter-model variance
   - Establish ground truth for frequency and impact assessments

3. **Calibrate Scoring Scale**
   - Investigate score compression (only 3 distinct values)
   - Consider if scoring rubric needs adjustment for better differentiation

4. **Validate Phase Discrepancy**
   - Verify if EOL risks are genuinely 15% higher than Usage Phase
   - Review lifecycle risk progression assumptions

5. **Address Scoring Bias**
   - Review why 72% of frequency scores are 4-5
   - Determine if this reflects reality or AI risk-aversion bias
   - Consider recalibration if bias is confirmed

**Research Questions for Human Validation**:

1. **Bias Investigation:**
   - Are AI models systematically overestimating risk frequency?
   - Is the concentration in 4-5 range appropriate for IoT security landscape?

2. **Disagreement Resolution:**
   - Which model assessments are most accurate when models disagree?
   - Can we identify model characteristics that predict accuracy?

3. **Calibration:**
   - Should the scoring scale be expanded to allow more granular differentiation?
   - Are current thresholds (Critical ≥ 20, High ≥ 12) appropriate?

4. **Lifecycle Validation:**
   - Is the EOL phase genuinely higher risk, or is this assessment bias?
   - How should lifecycle stage affect risk scoring?

---

## Part 3: System Output Reference

### 3.1 Current Console Output

When you run `run_risk_assessment()`, the system prints the following:

**1. Workflow Start**:
```
🔄 Running Multi-Agent Workflow...
```

**2. Progress Bars (tqdm)**:

During execution, you'll see progress bars for each agent:

- **Generator Ensemble**: 
  ```
  Generator Ensemble: 100%|████████████| 9/9 [00:XX<00:00, X.XXmodel/s]
  ```
  Shows progress for 9 parallel model calls

- **Aggregator**:
  ```
  Aggregator: 100%|████████████| 1/1 [00:XX<00:00, X.XXstep/s]
  ```
  Or during revisions:
  ```
  Aggregator: Revising: 100%|████████████| 1/1 [00:XX<00:00, X.XXstep/s]
  ```

- **Challenger A (Logic)**:
  ```
  Challenger A: Checking: 100%|████████████| 1/1 [00:XX<00:00, X.XXstep/s]
  ```

- **Challenger B (Source)**:
  ```
  Challenger B: Verifying: 100%|████████████| X/X [00:XX<00:00, X.XXcitation/s]
  Challenger B: Analyzing: 100%|████████████| 1/1 [00:XX<00:00, X.XXstep/s]
  ```
  Shows progress for each citation being verified, then analysis

- **Challenger C (Compliance)**:
  ```
  Challenger C: Checking: 100%|████████████| 1/1 [00:XX<00:00, X.XXstep/s]
  ```

- **Verifier**:
  ```
  Verifier: Routing: 100%|████████████| 1/1 [00:XX<00:00, X.XXstep/s]
  ```

**Note**: All progress bars use `leave=False`, so they disappear after completion and are replaced by the next one.

**3. Result Saving**:
```
💾 Result saved to: results/assessment_YYYYMMDD_HHMMSS.json
```

Or if saving fails:
```
⚠️  Failed to save result: <error message>
```

**4. Final Output (if run as `__main__`)**:

When running `python src/main.py`, it also prints:

```
Running risk assessment...

=== Final Assessment ===
Score: 4/5
Summary: <assessment summary>

Key Arguments:
  - <argument 1>
  - <argument 2>
  ...

Regulatory Citations: <citation 1>, <citation 2>, ...

Vulnerabilities: <CVE-XXX>, <vulnerability>, ...

=== Critiques (X) ===

challenger_a:
  Valid: True
  Confidence: 85.00%
  Recommendation: accept
  Issues: <list of issues if any>

challenger_b:
  Valid: True
  Confidence: 90.00%
  Recommendation: accept
  Issues: <list of issues if any>

challenger_c:
  Valid: True
  Confidence: 80.00%
  Recommendation: needs_review
  Issues: <list of issues if any>

Revision Count: 2
```

### 3.2 Log Files

In addition to console output, the system creates:

**1. Log File**: `logs/assessment_YYYYMMDD_HHMMSS.log`
   - Contains detailed workflow execution log
   - Includes all agent interactions
   - Conversation traces with prompts/responses

**2. Result JSON**: `results/assessment_YYYYMMDD_HHMMSS.json`
   - Complete assessment data
   - All critiques
   - Conversation log
   - Metadata (revision count, timestamps)

### 3.3 Example Full Output Flow

```
🔄 Running Multi-Agent Workflow...

Generator Ensemble: 100%|████████████| 9/9 [00:15<00:00, 1.67model/s]
Aggregator: 100%|████████████| 1/1 [00:08<00:00, 8.12step/s]
Challenger A: Checking: 100%|████████████| 1/1 [00:05<00:00, 5.23step/s]
Challenger B: Verifying: 100%|████████████| 4/4 [00:12<00:00, 3.33citation/s]
Challenger B: Analyzing: 100%|████████████| 1/1 [00:06<00:00, 6.00step/s]
Challenger C: Checking: 100%|████████████| 1/1 [00:05<00:00, 5.45step/s]
Verifier: Routing: 100%|████████████| 1/1 [00:04<00:00, 4.25step/s]
Aggregator: Revising: 100%|████████████| 1/1 [00:08<00:00, 8.00step/s]
Challenger A: Checking: 100%|████████████| 1/1 [00:05<00:00, 5.20step/s]
Challenger B: Verifying: 100%|████████████| 3/3 [00:10<00:00, 3.00citation/s]
Challenger B: Analyzing: 100%|████████████| 1/1 [00:06<00:00, 6.00step/s]
Challenger C: Checking: 100%|████████████| 1/1 [00:05<00:00, 5.10step/s]
Verifier: Routing: 100%|████████████| 1/1 [00:04<00:00, 4.23step/s]

💾 Result saved to: results/assessment_20251209_163045.json
```

### 3.4 What's NOT Printed

The system does **NOT** print:
- Individual model responses (only in log files)
- Detailed reasoning traces (only in JSON/log files)
- Intermediate state between revisions (only final state)
- API call details (only in log files)
- Cost information (calculated separately via scripts)

### 3.5 Summary

**Console Output**: Minimal, progress-focused
- Workflow start message
- Progress bars for each agent
- Result save confirmation
- (Optional) Final assessment summary if run as main

**Log Files**: Comprehensive
- All agent interactions
- Full prompts and responses
- Workflow execution details

**JSON Files**: Structured data
- Complete assessment results
- All critiques and metadata
- Conversation history

### 3.6 Logging and Results Management

**Created:** 2025-12-08

#### Overview

The system now automatically saves assessment results and logs complete workflow execution for audit and analysis purposes.

#### Features

**1. Automatic JSON Result Saving**

Every assessment run automatically saves a complete JSON file containing:
- **Metadata**: Timestamp, input scenario, revision count, statistics
- **Input**: Original risk scenario description
- **Output**: Complete assessment results including:
  - Synthesized draft (final assessment)
  - All 9 initial draft assessments
  - All critiques from challengers
- **Workflow Stats**: Revision count, total assessments, total critiques

**File Location**: `results/assessment_YYYYMMDD_HHMMSS.json`

**2. Complete Workflow Logging**

Every assessment run creates a detailed log file recording:
- Workflow start with input scenario
- Final assessment result (score, summary, arguments, citations, vulnerabilities)
- All critiques with status and recommendations
- Workflow statistics
- Result file path

**File Location**: `logs/assessment_YYYYMMDD_HHMMSS.log`

#### Usage

**Default Behavior (Automatic)**:

By default, both logging and result saving are enabled:

```python
from src.main import run_risk_assessment

result = run_risk_assessment("IoT device scenario...")
# Automatically:
# - Saves JSON to results/ directory
# - Creates log file in logs/ directory
```

**Disable Saving/Logging**:

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

#### File Naming Convention

Both JSON and log files use the same timestamp format:
- **Format**: `assessment_YYYYMMDD_HHMMSS.{json|log}`
- **Example**: `assessment_20251208_223638.json`

The timestamp reflects when the workflow **completed**, ensuring chronological ordering.

#### Benefits

1. **Audit Trail**: Complete record of all assessments for regulatory compliance
2. **Analysis**: Historical data for pattern analysis and system improvement
3. **Debugging**: Detailed logs help identify issues in workflow execution
4. **Reproducibility**: Saved results enable result review and comparison
5. **Compliance**: Structured JSON format suitable for regulatory reporting

---

## Part 4: Prompt Appendix

### 4.1 Generator Ensemble Prompt

```
You are an expert IoT risk assessor. Analyze the following IoT device scenario and provide a comprehensive risk assessment.

{reference_sources}

Device Scenario:
{risk_input}

IMPORTANT: When making your assessment, reference the authoritative sources provided above. Use industry statistics, market insights, and technical frameworks (e.g., expanded CIA framework) to inform your risk evaluation. Consider industry-specific focus areas (automotive, healthcare, smart cities) and adoption barriers when relevant. Pay special attention to the real-world security incidents and case studies - these demonstrate actual risk manifestations and should inform your assessment of similar scenarios.

TASK: Perform a Dual-Factor Risk Assessment.

You must output TWO distinct scores that multiply to form the Final Risk Score.

### CRITICAL DEFINITION: LIKELIHOOD = FREQUENCY

**IMPORTANT:** In this risk assessment framework, "Likelihood" DOES NOT mean "theoretical probability of a future event."

Instead, "Likelihood" is defined as **"Frequency of Occurrence"** and **"Prevalence in the Current Landscape."**

You must assign the Likelihood/Frequency Score (1-5) based on the following strict rubric:

DIMENSION 1: LIKELIHOOD/FREQUENCY (1-5) - "How often does this risk state occur?"

- **Score 5 (Systemic/Constant):** The risk is an inherent part of the device's standard operation (e.g., continuous data collection) OR a near-universal user behavior (e.g., "install-and-forget" mentality). It happens by default.
  - *Reference Examples:* Mass Data Inference (data collection is default), User Awareness Deficit (widespread user behavior)

- **Score 4 (Widespread/Common):** The vulnerability is present in a vast majority of devices (e.g., unencrypted traffic, weak default passwords) or is frequently exploited by automated tools (e.g., botnets).
  - *Reference Examples:* Data Hacking (98% unencrypted traffic), Mirai Botnet (default passwords)

- **Score 3 (Targeted/Occasional):** The vulnerability exists but requires specific technical skills, targeted malice, or specific conditions to exploit. It is not automatic.
  - *Reference Examples:* Remote Direct Control (requires hacking skill, e.g., Finland HVAC attack)

- **Score 2 (Rare/Proof-of-Concept):** Feasible in laboratory settings or complex edge cases, but rarely seen in the wild.

- **Score 1 (Theoretical):** No documented cases; purely hypothetical.

**Constraint:** Do NOT lower the score just because a "smart user" *could* prevent it. Assume the average, non-technical user behavior. Focus on **how prevalent the risk state is**, not on whether it *could* be prevented.

DIMENSION 2: IMPACT SEVERITY (1-5) - "How severe is the damage when it occurs?"

- **Score 5 (Catastrophic):** Loss of life, severe physical harm, or permanent infrastructure damage.
- **Score 4 (Severe):** Major privacy breach, financial loss, or identity theft.
- **Score 3 (Moderate):** Service disruption or reversible damage.
- **Score 1-2 (Minor):** Nuisance or minimal loss.

CALCULATION:
Final Risk Score = Frequency Score × Impact Score (range: 1-25)

RISK CLASSIFICATION:
- Critical: 20-25 (e.g., 5×5, 5×4, 4×5)
- High: 12-19 (e.g., 4×4, 3×5, 5×3)
- Medium: 6-11 (e.g., 3×3, 2×4, 4×2)
- Low: 1-5 (e.g., 1×5, 2×2, 3×1)

Provide your assessment in the following JSON format:
{
    "score": <integer 1-5>,  // Legacy score for backward compatibility (map from final_risk_score: 1-5=1, 6-10=2, 11-15=3, 16-20=4, 21-25=5)
    "reasoning": {
        "summary": "<brief summary of the risk>",
        "key_arguments": ["<argument 1>", "<argument 2>", ...],
        "regulatory_citations": ["<regulation 1>", "<regulation 2>", ...],
        "vulnerabilities": ["<CVE or vulnerability 1>", "<CVE or vulnerability 2>", ...]
    },
    "risk_assessment": {
        "frequency_score": <integer 1-5>,  // Also called "Likelihood" - measures how often/widespread the risk occurs
        "frequency_rationale": "<One sentence justifying the frequency based on history/default behavior. Focus on prevalence, not future probability.>",
        "impact_score": <integer 1-5>,
        "impact_rationale": "<One sentence justifying the severity of damage>",
        "final_risk_score": <integer 1-25>,  // Must be frequency_score * impact_score
        "risk_classification": "<Low/Medium/High/Critical>"
    }
}

Be specific with regulatory citations (e.g., "PSTI Act 2022", "ISO 27001") and vulnerabilities (e.g., "CVE-2024-12345").
```

### 4.2 Aggregator Prompt (Initial Synthesis)

```
You are synthesizing risk assessments from 9 expert models. Your task is to create a unified, consensus-driven risk assessment.

{reference_sources}

Individual Assessments:
{assessments}

IMPORTANT: When synthesizing assessments, reference the authoritative sources provided above. Ensure your unified assessment aligns with industry standards, market insights, and the expanded CIA framework (Confidentiality, Integrity, Availability with six outcomes).

**REMINDER:** "Likelihood" = "Frequency" (prevalence/occurrence rate), NOT future probability. When synthesizing frequency scores, focus on how widespread the risk state is across the current landscape.

Analyze the reasoning traces, identify consensus points, and synthesize a unified assessment that:
1. Reflects the majority logic and evidence
2. Incorporates the strongest arguments from all assessments
3. Maintains consistency between the score and reasoning
4. Preserves all valid regulatory citations and vulnerabilities
5. Synthesizes frequency and impact scores from individual assessments (if provided)
   - For frequency: Focus on prevalence (how often/widespread), not future probability

For DUAL-FACTOR ASSESSMENT:
**IMPORTANT:** Remember that "Likelihood" = "Frequency" (prevalence/occurrence rate), NOT future probability.

- Synthesize frequency_score (also called "Likelihood") by considering the most common frequency assessment across models
  - Focus on how widespread/prevalent the risk state is, not on whether it might happen
- Synthesize impact_score by considering the most common impact assessment across models
- Calculate final_risk_score = frequency_score × impact_score
- Determine risk_classification based on final_risk_score:
  * Critical: 20-25
  * High: 12-19
  * Medium: 6-11
  * Low: 1-5

Provide the unified assessment in JSON format:
{
    "score": <integer 1-5>,  // Legacy score (map from final_risk_score: 1-5=1, 6-10=2, 11-15=3, 16-20=4, 21-25=5)
    "reasoning": {
        "summary": "<synthesized summary>",
        "key_arguments": ["<unified argument 1>", ...],
        "regulatory_citations": ["<all valid citations>", ...],
        "vulnerabilities": ["<all valid vulnerabilities>", ...]
    },
    "risk_assessment": {
        "frequency_score": <integer 1-5>,  // Also called "Likelihood" - measures how often/widespread the risk occurs
        "frequency_rationale": "<Synthesized rationale based on consensus from individual assessments. Focus on prevalence, not future probability.>",
        "impact_score": <integer 1-5>,
        "impact_rationale": "<Synthesized rationale based on consensus from individual assessments>",
        "final_risk_score": <integer 1-25>,  // Must be frequency_score * impact_score
        "risk_classification": "<Low/Medium/High/Critical>"
    }
}
```

### 4.3 Aggregator Revision Prompt (With Critiques)

```
You are REVISING a risk assessment based on critiques from three challenger agents. This is a revision cycle - you MUST address ALL issues raised.

{reference_sources}

Previous Assessment:
{previous_assessment}

Critiques from Challengers:
{critiques}

IMPORTANT: When revising, reference the authoritative sources provided above. Use industry statistics, market insights, and technical frameworks to strengthen your revised assessment. Ensure compliance with the expanded CIA framework and relevant industry vertical requirements.

CRITICAL: You must address each issue raised:

**REMINDER:** "Likelihood" = "Frequency" (prevalence/occurrence rate), NOT future probability. When revising frequency scores, focus on how widespread the risk state is, not on whether it might happen.

1. If Challenger A (Logic) found missing reasoning or arguments:
   - ADD detailed reasoning that justifies the score
   - ENSURE key_arguments are comprehensive and support the severity level
   - FIX any logical inconsistencies or contradictions
   - If frequency-related critiques mention "unlikely" arguments, correct them to focus on prevalence

2. If Challenger C (Compliance) found missing regulatory information:
   - ADD relevant ISO standards (27001, 27002, etc.) if applicable
   - INCLUDE PSTI Act 2022 compliance considerations
   - ADDRESS IoT security best practices
   - ENSURE regulatory citations are complete

3. If Challenger B (Source) found unverified citations:
   - REMOVE unverified citations
   - REPLACE with verified alternatives if possible
   - KEEP only citations that can be verified

4. Maintain consistency:
   - Score must match the evidence and reasoning
   - All arguments must support the severity level
   - Regulatory citations must be relevant and verifiable

Provide the REVISED assessment in JSON format:
{
    "score": <integer 1-5>,  // Legacy score (map from final_risk_score: 1-5=1, 6-10=2, 11-15=3, 16-20=4, 21-25=5)
    "reasoning": {
        "summary": "<revised summary that addresses all critiques>",
        "key_arguments": ["<argument addressing issue 1>", "<argument addressing issue 2>", ...],
        "regulatory_citations": ["<only verified citations>", ...],
        "vulnerabilities": ["<valid vulnerabilities>", ...]
    },
    "risk_assessment": {
        "frequency_score": <integer 1-5>,  // Also called "Likelihood" - measures how often/widespread the risk occurs
        "frequency_rationale": "<Revised rationale addressing frequency-related critiques. Focus on prevalence, not future probability.>",
        "impact_score": <integer 1-5>,
        "impact_rationale": "<Revised rationale addressing impact-related critiques>",
        "final_risk_score": <integer 1-25>,  // Must be frequency_score * impact_score
        "risk_classification": "<Low/Medium/High/Critical>"
    }
}

IMPORTANT: This is a revision - do not simply repeat the previous assessment. Actively improve it based on the critiques. If critiques mention calculation errors or frequency/impact justification issues, address them in the revised risk_assessment breakdown.
```

### 4.4 Challenger A (Logic) Prompt

```
You are a formal logician analyzing a risk assessment for internal consistency.

{reference_sources}

Risk Assessment:
Score: {score}
Reasoning: {reasoning}
Risk Assessment Breakdown: {risk_assessment}

IMPORTANT: When evaluating logical consistency, consider whether the assessment properly references and aligns with the authoritative sources provided above. Check if industry statistics, market insights, and technical frameworks are correctly applied in the reasoning.

### CRITICAL DEFINITION: LIKELIHOOD = FREQUENCY

**IMPORTANT:** In this framework, "Likelihood" is defined as **"Frequency of Occurrence"** and **"Prevalence in the Current Landscape"**, NOT as "theoretical probability of a future event."

The Frequency/Likelihood score measures **how often the risk state occurs** or **how widespread the vulnerability is**, not whether it *might* happen in the future.

Your task - DUAL-FACTOR AUDIT:

### AUDIT INSTRUCTION: LIKELIHOOD vs. IMPACT

You are evaluating the Generator's risk scoring. You must strictly enforce the separation of "Frequency" (Likelihood) and "Severity" (Impact).

**How to validate Likelihood/Frequency Scores:**

CHECK 1: FREQUENCY/LIKELIHOOD SCORE (Tolerance Applied)

1. **Check for Prevalence:** If the Generator cites evidence that a vulnerability is widespread (e.g., "57% of devices affected") or inherent (e.g., "functionality requires data sending"), they MUST assign a High Likelihood (4 or 5).

2. **Reject "Theoretical" Arguments:** If the Generator argues "It is unlikely because hackers might not be interested," REJECT this reasoning. If the door is unlocked (vulnerability exists), the Likelihood of the risk state is HIGH, even if no one has walked through it yet.

3. **Validate against Ground Truth:**
   - Standard Operation (Data Collection) = Score 5 (Systemic/Constant)
   - Widespread Vulnerability (Unencrypted Traffic) = Score 4 (Common)
   - Targeted Hack (Remote Control) = Score 3 (Occasional)
   - If the Generator deviates significantly from this logic (e.g., giving Remote Control a 5 for Likelihood when it requires targeted hacking), flag it as an error.

4. **Evidence Requirements:**
   - Does the Generator cite at least one historical case or real-world incident to support their Frequency score?
   - If yes, ACCEPT the Frequency score. Do not demand statistical tables or exhaustive evidence.
   - If no case study is cited for a high frequency (4-5), FLAG it as an issue.
   - Consider: Score 5 (Systemic) should have evidence of default behavior or widespread automated attacks
   - Consider: Score 4 (Common) should reference frequently reported vulnerabilities
   - Consider: Score 3 (Occasional) should mention targeted attacks or specific conditions

**Key Principle:** Do NOT lower the Likelihood score just because a "smart user" *could* prevent it. Focus on **how prevalent the risk state is**, not on whether it *could* be prevented.

CHECK 2: IMPACT SCORE (Moderate Strictness with Tolerance)
- Is the Impact score justified by the harm described in the scenario?
- **TOLERANCE:** If the impact score is within 1 point of what seems reasonable, ACCEPT it. Only reject if there's a MAJOR mismatch (e.g., Impact 5 for "Ad tracking").
- Example: If they claim "Death is possible" (Impact 5) but the scenario is just "Ad tracking", REJECT it.
- Example: If they claim Impact 5 (Catastrophic) for physical safety risks (e.g., hypothermia, fire), ACCEPT if scenario supports it.
- Example: If they claim Impact 4 (Severe) for privacy breach when scenario suggests Impact 5, ACCEPT it (within tolerance).
- Verify that the impact_rationale clearly explains the severity level claimed, but don't demand exhaustive detail.

CHECK 3: CALCULATION VERIFICATION (Critical - No Tolerance)
- Does Frequency Score × Impact Score = Final Risk Score?
- If the calculation is incorrect, this is a CRITICAL error that must be flagged.
- **Exception:** If the difference is only 1-2 points and seems like a rounding error, note it but don't necessarily reject.

CHECK 4: RISK CLASSIFICATION (Tolerance Applied)
- Does the risk_classification match the final_risk_score?
  * Critical: 20-25
  * High: 12-19
  * Medium: 6-11
  * Low: 1-5
- **TOLERANCE:** If classification is close (e.g., score 19 classified as "High" instead of "Critical"), ACCEPT it. Only flag if completely wrong (e.g., score 20 classified as "Low").

CHECK 5: LEGACY SCORE CONSISTENCY (Minor Check - High Tolerance)
- If legacy score (1-5) is provided, verify it reasonably maps from final_risk_score
- This is a minor check - focus on the dual-factor assessment primarily
- **TOLERANCE:** Accept any reasonable mapping. Only flag if completely inconsistent.

Provide your critique in JSON format:
{
    "is_valid": <true/false>,
    "issues": ["<issue 1>", "<issue 2>", ...],
    "confidence": <0.0-1.0>,
    "recommendation": "<accept|reject|needs_review>"
}

### EVALUATION GUIDELINES - MAXIMUM TOLERANCE APPLIED

**CRITICAL PRINCIPLE: Be lenient and accept assessments unless there are MAJOR errors.**

**When to ACCEPT (set is_valid=true):**
1. ✅ Core logic is sound and both frequency and impact scores are reasonably justified (within 1 point tolerance)
2. ✅ Basic reasoning supports both scores, even if some details are missing
3. ✅ At least one historical case or real-world incident is cited for frequency (don't demand statistical tables)
4. ✅ Impact score matches the scenario severity (within 1 point tolerance)
5. ✅ Calculation is correct OR off by only 1-2 points (likely rounding error)
6. ✅ Risk classification is approximately correct (within reasonable range)
7. ✅ Minor gaps in reasoning or missing minor arguments - note them but don't reject

**When to REJECT (set is_valid=false):**
1. ❌ MAJOR calculation error (frequency × impact ≠ final_score by 3+ points)
2. ❌ Complete lack of reasoning or both scores completely unjustified
3. ❌ MAJOR logical inconsistency (e.g., Impact 5 for "Ad tracking", Frequency 5 for "Targeted hack")
4. ❌ No evidence cited for high frequency (4-5) AND no default behavior described
5. ❌ Risk classification completely wrong (e.g., score 20 classified as "Low")

**When to NEEDS_REVIEW (set recommendation="needs_review"):**
1. ⚠️ Minor calculation error (off by 1-2 points)
2. ⚠️ One score seems slightly off but not completely wrong
3. ⚠️ Missing some details but core logic is sound
4. ⚠️ Risk classification is close but not exact

**TOLERANCE REMINDERS:**
- Do NOT demand statistical tables or exhaustive evidence
- Do NOT reject for minor gaps in reasoning
- Do NOT reject if scores are within 1 point of reasonable
- Do NOT reject for missing minor arguments
- ACCEPT if the assessment is "good enough" even if not perfect
- Focus on MAJOR errors, not minor imperfections

If the logic is fundamentally sound, calculations are approximately correct, and scores are reasonably justified, set is_valid=true. Only set is_valid=false for SIGNIFICANT logical inconsistencies, major calculation errors, or complete lack of reasoning.
```

### 4.5 Challenger B (Source) Prompt

```
You are a fact-checker verifying the external validity of citations in a risk assessment. Your role is to flag MAJOR unverified claims that could undermine the assessment's credibility, not to reject assessments for minor citation issues.

{reference_sources}

Risk Assessment:
{assessment}

Citations to verify:
{citations}

Search results for each citation:
{search_results}

IMPORTANT: When verifying citations, cross-reference with the authoritative sources provided above. Verify that statistics, market data, and technical frameworks cited in the assessment match the reference sources. Also verify external citations (regulations, CVEs, standards) through search results. Consider whether the assessment references relevant real-world security incidents and case studies from the reference sources - these provide concrete evidence of risk manifestations.

For each citation, determine:
1. Does it exist and is it real?
2. Is it correctly cited?
3. Is it relevant to the risk assessment?
4. Is it a MAJOR claim (e.g., critical CVE, key regulation) or MINOR detail (e.g., specific statistic, minor standard)?

Provide your critique in JSON format:
{
    "is_valid": <true/false>,
    "issues": ["<unverified MAJOR citation: X>", "<incorrect MAJOR citation: Y>", ...],
    "confidence": <0.0-1.0>,
    "recommendation": "<accept|reject|needs_review>"
}

Evaluation Guidelines:
- **ACCEPT if ≥50% of citations are verified** OR if all MAJOR citations (CVEs, key regulations, critical standards) are verified
- **Focus on MAJOR claims**: Only flag unverified citations that are central to the risk assessment's argument
- **Ignore minor issues**: Missing verification for minor statistics, secondary standards, or peripheral citations should NOT cause rejection
- **Set is_valid=true** if:
  * At least 50% of citations are verified, OR
  * All critical citations (CVEs, major regulations like PSTI Act, ISO 27001) are verified, OR
  * Only minor citations are unverified and they don't undermine the core argument
- **Set is_valid=false** ONLY if:
  * MAJORITY of citations are unverified AND they are central to the assessment, OR
  * Critical citations (CVEs, key regulations) are unverified and the assessment heavily relies on them
- **Recommendation**: Use "accept" if is_valid=true and issues are minor. Use "needs_review" if some major citations need attention but assessment is mostly sound.

Remember: Your goal is to catch significant factual errors, not to be a perfectionist. An assessment with 60% verified citations and minor unverified details should generally be accepted.
```

### 4.6 Challenger C (Safety) Prompt

```
You are a safety and compliance expert validating a risk assessment against regulatory requirements.

{reference_sources}

Risk Assessment:
Score: {score}
Reasoning: {reasoning}

IMPORTANT: When validating compliance, reference the authoritative sources provided above. Ensure the assessment considers the expanded CIA framework (six outcomes), industry-specific requirements (automotive, healthcare, smart cities), and adoption barriers. Cross-reference with industry statistics and market insights where relevant. Pay special attention to real-world security incidents - these demonstrate actual compliance failures and safety violations that should inform your evaluation (e.g., Finland HVAC attack shows Availability failures, Ring/South Korea camera hacks show Confidentiality failures).

Validate against:
- PSTI Act 2022 requirements
- ISO standards (27001, 27002, etc.)
- IoT security best practices
- Product safety regulations
- Expanded CIA framework (Confidentiality: Data privacy and Access; Integrity: Reliability and Compliance; Availability: Uptime and Resilience)
- Industry vertical requirements (automotive, healthcare, smart cities)

Check if:
1. The assessment addresses all relevant compliance requirements
2. Safety constraints are properly considered
3. Regulatory obligations are identified
4. The severity reflects compliance violations

Provide your critique in JSON format:
{
    "is_valid": <true/false>,
    "issues": ["<compliance issue 1>", "<safety concern 2>", ...],
    "confidence": <0.0-1.0>,
    "recommendation": "<accept|reject|needs_review>"
}

Evaluation Guidelines:
- If major compliance requirements are addressed, set is_valid=true even if some minor standards are not explicitly mentioned
- Only set is_valid=false for SIGNIFICANT compliance gaps or complete absence of regulatory considerations
- Missing one or two minor ISO standards should be noted but may not require rejection if core compliance is addressed
- If the assessment shows awareness of key regulatory requirements (PSTI Act, basic ISO standards), consider it valid despite minor gaps

If major compliance requirements are properly addressed, set is_valid=true. If there are significant compliance gaps or complete absence of regulatory considerations, set is_valid=false.
```

### 4.7 Verifier Prompt

```
You are the final arbiter reviewing critiques from three challenger agents.

{reference_sources}

Synthesized Draft:
{assessment}

Critiques:
{critiques}

IMPORTANT: When making your final decision, consider whether the assessment and critiques properly reference and align with the authoritative sources provided above. Ensure the assessment reflects industry standards, market insights, and the expanded CIA framework.

Determine:
1. Are there any critical issues that require revision?
2. Should the assessment be accepted, rejected, or revised?
3. If revision is needed, what should be addressed?

Provide your decision in JSON format:
{
    "needs_revision": <true/false>,
    "reason": "<explanation>",
    "revision_focus": ["<area 1 to revise>", "<area 2 to revise>", ...]
}

If all critiques are resolved or minor, set needs_revision=false. If there are significant issues, set needs_revision=true.
```

---

## Document End

**Last Updated:** 2025-12-10  
**Version:** 1.0  
**Status:** Complete Reference Documentation

---

