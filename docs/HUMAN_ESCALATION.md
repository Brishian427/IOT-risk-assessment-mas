# Human Escalation Mechanism

**Created:** 2025-01-XX  
**Purpose:** Route failed consensus scenarios to human operators for review

---

## Overview

The Human-in-the-Loop escalation mechanism automatically routes assessments to human operators when:

1. **Max revisions reached without consensus** - System cannot achieve 2/3 challenger approval after maximum revision attempts
2. **Critical risk classification** - Assessment indicates Critical risk (20-25/25 score)
3. **All challengers reject** - All three challengers reject the assessment

---

## How It Works

### 1. Escalation Detection

The `should_escalate()` function in `src/utils/escalation_handler.py` checks for escalation conditions:

```python
def should_escalate(state: StateSchema) -> Tuple[bool, str]:
    """
    Determine if escalation to human is needed.
    
    Returns:
        Tuple of (should_escalate, reason)
    """
```

### 2. Escalation File Creation

When escalation is triggered, the system:

1. Creates a JSON file in `escalations/` directory
2. Includes complete assessment state:
   - Current synthesized draft
   - All 9 initial assessments
   - All critiques from challengers
   - Revision history
   - Escalation reason

**File Format:** `escalations/escalation_YYYYMMDD_HHMMSS.json`

### 3. Workflow Routing

The workflow routes to `escalation_node` when escalation is needed:

```
Verifier → should_continue() → "escalate" → Escalation Node → END
```

### 4. Logging and Notification

- **Console Output:** Clear escalation notice with file path
- **Log Files:** Escalation event logged in assessment log
- **JSON Results:** Escalation info included in result JSON

---

## Escalation File Structure

```json
{
  "metadata": {
    "escalation_type": "Human Review Required",
    "timestamp": "2025-01-XXT...",
    "reason": "Max revisions (3) reached without 2/3 challenger consensus...",
    "status": "PENDING_HUMAN_REVIEW"
  },
  "escalation_reason": "...",
  "workflow_state": {
    "revision_count": 3,
    "total_assessments": 9,
    "total_critiques": 12
  },
  "current_assessment": {
    "model_name": "aggregated",
    "score": 5,
    "reasoning": {...},
    "risk_assessment": {...}
  },
  "all_assessments": [...],
  "critiques": [...],
  "human_review_required": {
    "action": "Review this assessment and provide final decision",
    "priority": "HIGH"
  }
}
```

---

## Escalation Triggers

### Trigger 1: Max Revisions Without Consensus

**Condition:** `revision_count >= MAX_REVISIONS` AND less than 2/3 challengers approve

**Example Reason:**
```
"Max revisions (3) reached without 2/3 challenger consensus. Only 1/3 challengers approved."
```

### Trigger 2: Critical Risk Classification

**Condition:** `risk_classification == "Critical"` (score 20-25/25)

**Example Reason:**
```
"Critical risk classification (25/25) requires human validation"
```

### Trigger 3: All Challengers Reject

**Condition:** All three challengers return `is_valid=False` or `recommendation="reject"`

**Example Reason:**
```
"All challengers rejected the assessment. Human review required to resolve conflicts."
```

---

## Usage

### Automatic Escalation

Escalation happens automatically during workflow execution. No configuration needed.

### Checking Escalation Status

After running an assessment:

```python
from src.main import run_risk_assessment

result = run_risk_assessment("IoT device scenario...")

# Check if escalation occurred
escalation = result.get("escalation")
if escalation and escalation.escalated:
    print(f"Escalation file: {escalation.escalation_file}")
    print(f"Reason: {escalation.reason}")
```

### Escalation File Location

Escalation files are saved in:
- **Default:** `escalations/escalation_YYYYMMDD_HHMMSS.json`
- **Custom:** `{output_dir}/escalations/escalation_YYYYMMDD_HHMMSS.json`

---

## Human Review Process

1. **Review Escalation File**
   - Open the escalation JSON file
   - Review current assessment and all critiques
   - Understand why consensus failed

2. **Make Decision**
   - Accept assessment as-is
   - Request revision with specific guidance
   - Reject assessment entirely

3. **Update System** (Future Enhancement)
   - API endpoint for human decisions
   - UI for reviewing escalations
   - Integration with external workflow systems

---

## Configuration

### Escalation Thresholds

In `src/config.py`:

```python
MAX_REVISIONS: int = 3  # Maximum revision attempts before escalation
ESCALATION_CONFIDENCE_THRESHOLD: float = 0.7  # Future use
```

### Custom Escalation Directory

Set via `output_dir` parameter:

```python
result = run_risk_assessment(
    "IoT device scenario...",
    output_dir="./custom_output"
)
# Escalation file: ./custom_output/escalations/escalation_...json
```

---

## Integration with External Workflow Systems

### Current Implementation

- ✅ Escalation detection
- ✅ Escalation file creation
- ✅ Logging and notification
- ⚠️ Human review interface (manual file review)

### Future Enhancements

1. **API Endpoint**
   - REST API for listing pending escalations
   - Endpoint for submitting human decisions
   - Status tracking

2. **UI Dashboard**
   - Web interface for reviewing escalations
   - Decision submission form
   - Historical escalation tracking

3. **Notification System**
   - Email alerts for escalations
   - Slack/Teams integration
   - Priority-based routing

4. **Workflow Integration**
   - Automatic routing to assigned reviewers
   - SLA tracking (time to review)
   - Escalation escalation (if not reviewed in time)

---

## Example Escalation Scenario

### Scenario: Max Revisions Reached

1. **Initial Assessment:** Generator ensemble produces 9 assessments
2. **Aggregation:** Aggregator synthesizes unified draft
3. **Critique Round 1:** Challenger A rejects (logic error), B accepts, C rejects
4. **Revision 1:** Aggregator revises based on critiques
5. **Critique Round 2:** Challenger A rejects (still has issues), B accepts, C rejects
6. **Revision 2:** Aggregator revises again
7. **Critique Round 3:** Challenger A rejects, B accepts, C rejects
8. **Revision 3:** Aggregator revises again
9. **Critique Round 4:** Still only 1/3 approval
10. **Escalation:** System detects max revisions reached, creates escalation file
11. **Human Review:** Operator reviews escalation file and makes final decision

---

## Troubleshooting

### Escalation File Not Created

- Check that escalation conditions are met
- Verify `escalations/` directory is writable
- Check logs for errors

### Escalation Triggered Unexpectedly

- Review escalation reason in file
- Check challenger critiques
- Verify revision count

### Missing Escalation Info in Results

- Ensure escalation node executed
- Check state includes escalation field
- Verify result saver includes escalation metadata

---

## Related Files

- `src/utils/escalation_handler.py` - Escalation detection and file creation
- `src/agents/escalation_node.py` - Escalation workflow node
- `src/agents/verifier.py` - Escalation trigger logic
- `src/schemas.py` - EscalationInfo schema
- `src/graph.py` - Workflow routing

---

**Note:** This is a production-ready implementation of human escalation. The system now properly routes failed consensus scenarios to human operators with complete audit trails.

