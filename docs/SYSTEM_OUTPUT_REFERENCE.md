# System Output Reference
Created: 2025-12-09

## Current Console Output

When you run `run_risk_assessment()`, the system prints the following:

### 1. Workflow Start
```
🔄 Running Multi-Agent Workflow...
```

### 2. Progress Bars (tqdm)
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

### 3. Result Saving
```
💾 Result saved to: results/assessment_YYYYMMDD_HHMMSS.json
```

Or if saving fails:
```
⚠️  Failed to save result: <error message>
```

### 4. Final Output (if run as `__main__`)
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

## Log Files

In addition to console output, the system creates:

1. **Log File**: `logs/assessment_YYYYMMDD_HHMMSS.log`
   - Contains detailed workflow execution log
   - Includes all agent interactions
   - Conversation traces with prompts/responses

2. **Result JSON**: `results/assessment_YYYYMMDD_HHMMSS.json`
   - Complete assessment data
   - All critiques
   - Conversation log
   - Metadata (revision count, timestamps)

## Example Full Output Flow

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

## What's NOT Printed

The system does **NOT** print:
- Individual model responses (only in log files)
- Detailed reasoning traces (only in JSON/log files)
- Intermediate state between revisions (only final state)
- API call details (only in log files)
- Cost information (calculated separately via scripts)

## Summary

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

