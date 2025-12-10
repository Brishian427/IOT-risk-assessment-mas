# Likelihood = Frequency Alignment Update
Created: 2025-12-09

## Overview

Updated the system to ensure **Likelihood** and **Frequency** are treated as **synonyms**, with Likelihood explicitly redefined as "Frequency of Occurrence" and "Prevalence in the Current Landscape", NOT as "theoretical probability of a future event."

## Problem Statement

LLMs are trained with "Likelihood" typically meaning "future probability prediction." Without explicit redefinition, agents might confuse:
- "Theoretically possible" (Possibility) 
- "Actually frequently occurring" (Frequency)

This misalignment could cause agents to score risks incorrectly (e.g., lowering frequency scores because "smart users could prevent it").

## Solution: Explicit Redefinition

### 1. Generator Prompt Updates (`src/utils/prompt_templates.py`)

**Added CRITICAL DEFINITION section:**

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

### 2. Challenger A Prompt Updates (`src/utils/prompt_templates.py`)

**Added AUDIT INSTRUCTION section:**

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

### 3. Aggregator Prompt Updates (`src/utils/prompt_templates.py`)

**Added REMINDER sections:**

- Initial Synthesis: Reminder that "Likelihood" = "Frequency" when synthesizing
- Revision: Reminder when addressing frequency-related critiques
- JSON Format: Comments clarifying frequency_score = Likelihood

### 4. Scenario File Updates (`evaluation_inputs/scenario_*.txt`)

**Updated all 11 scenario Task descriptions:**

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

## Key Changes Summary

| Component | Change |
|-----------|--------|
| **Generator Prompt** | Added CRITICAL DEFINITION section explicitly redefining Likelihood = Frequency |
| **Challenger A Prompt** | Added AUDIT INSTRUCTION with prevalence-based validation rules |
| **Aggregator Prompts** | Added REMINDER sections in synthesis and revision prompts |
| **JSON Format Comments** | Added "Also called 'Likelihood'" comments to frequency_score fields |
| **All 11 Scenarios** | Updated Task descriptions to use "Frequency x Impact" with explicit guidance |

## Expected Behavior

### Example 1: Mass Data Inference
- **Before (confused)**: "Likelihood = 3 (could be prevented with privacy settings)"
- **After (correct)**: "Frequency = 5 (data collection is default operation)"

### Example 2: Remote Direct Control
- **Before (confused)**: "Likelihood = 5 (could happen to anyone)"
- **After (correct)**: "Frequency = 3 (requires targeted hacking, occasional)"

### Example 3: User Awareness
- **Before (confused)**: "Likelihood = 2 (smart users would prevent it)"
- **After (correct)**: "Frequency = 5 (widespread user behavior, systemic)"

## Validation

The system now ensures:
1. ✅ Likelihood is explicitly defined as Frequency (prevalence)
2. ✅ Agents focus on "how widespread" not "might happen"
3. ✅ Challenger rejects "theoretical" arguments for frequency
4. ✅ All prompts consistently use Likelihood = Frequency
5. ✅ Scenario tasks guide agents with explicit frequency assessment

## Files Modified

1. `src/utils/prompt_templates.py` - All prompt updates
2. `evaluation_inputs/scenario_1_mass_data_inference.txt`
3. `evaluation_inputs/scenario_2_remote_direct_control.txt`
4. `evaluation_inputs/scenario_3_data_hacking_breaching.txt`
5. `evaluation_inputs/scenario_4_user_awareness_deficit.txt`
6. `evaluation_inputs/scenario_5_lack_of_continuous_updates.txt`
7. `evaluation_inputs/scenario_6_cloud_dependence.txt`
8. `evaluation_inputs/scenario_7_user_awareness_legal_compliance.txt`
9. `evaluation_inputs/scenario_8_protocol_weaknesses.txt`
10. `evaluation_inputs/scenario_9_physical_safety_fire_hazards.txt`
11. `evaluation_inputs/scenario_10_data_security_secondhand_market.txt`
12. `evaluation_inputs/scenario_11_environmental_toxicity.txt`

## Testing

The system is now ready to test with the updated prompts. Expected outcomes:
- Mass Data Inference: Frequency = 5 (systemic), Impact = 4 (severe) → Final = 20 (Critical)
- Remote Direct Control: Frequency = 3 (occasional), Impact = 5 (catastrophic) → Final = 15 (High)

