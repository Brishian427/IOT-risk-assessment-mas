# IoT Risk Assessment Multi-Agent System

Created: 2025-12-02

A Reasoning-First Multi-Agent System for IoT Risk Assessment using LangGraph, implementing a "Heterogeneous Sequential Debate" architecture.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Meta-Context

This project was developed as part of the **PPE Capstone - IoT Group** (November 2025) and serves as a strategic advisory document for the **Centre for Strategy & Evaluation Services (CSES)**. 

### The Problem: The "Expert Gap"

Traditional risk assessment frameworks (e.g., Djemame et al., 2011) rely on structured judgement from diverse human subject matter experts (SMEs)—engineers, lawyers, and ethicists—to interpret qualitative hazards and map them onto quantitative risk scales. However, in resource-constrained environments, access to such expert panels is often unavailable, creating an "Expert Gap" that undermines the validity of risk assessments.

**Without expert calibration**, risk scoring becomes highly susceptible to subjectivity and bias, rendering assessments methodologically invalid for regulatory purposes.

### Our Solution: Synthetic Expert Judgment

This Multi-Agent System (MAS) addresses the Expert Gap by implementing a **Reasoning-First approach to Synthetic Expert Judgment**. Unlike standard voting systems that aggregate raw numerical scores, our architecture aggregates and critiques the **Reasoning Trace** (the "Why") alongside the numerical score, enabling automated reasoning to augment regulatory capacity where human expertise is limited.

### Key Innovation

The system replaces the missing human expert panel with a heterogeneous ensemble of LLM agents that:
- Generate diverse risk assessments with explicit reasoning traces
- Cross-examine each other's reasoning through specialised challenger agents
- Synthesise consensus through iterative refinement
- Provide human-validatable reasoning trails for regulatory review

## Architecture

The system implements a sequential debate pipeline:

1. **Generator Ensemble** - 8 parallel models generate initial risk assessments
2. **Aggregator** - Synthesises unified draft from 8 assessments
3. **Challenger A (Logic)** - Checks internal consistency
4. **Challenger B (Source)** - Verifies external validity (regulations/CVEs)
5. **Challenger C (Safety)** - Validates compliance constraints
6. **Verifier** - Routes workflow (loop or end) based on critiques

## Key Challenges & Solutions

Implementing MAS for risk assessment introduces specific failure modes. Our design proactively mitigates these challenges:

| Challenge | The Risk | Our Solution |
|-----------|----------|--------------|
| **Hallucinated Reasoning** | Models giving the "right" score but for "wrong" reasons (invented facts or regulations) | Challenger B (Source) uses Tavily Search API to verify citations against real regulatory databases |
| **Logical Inconsistency** | High severity score justified by weak or irrelevant arguments | Challenger A (Logic) checks internal consistency and score-argument alignment |
| **Echo Chambers** | All agents agreeing due to shared underlying training data | Explicit use of distinct model families (Claude vs. GPT vs. Llama) for Generator vs. Challenger roles |
| **Quality vs. Quantity** | Raw vote counting ignores argument quality | Aggregator prioritises quality of argument over raw count of votes, synthesising reasoning traces |
| **Infinite Loops** | Revision cycles continuing indefinitely | Verifier enforces MAX_REVISIONS=3 with graceful degradation (accepts if ≥2/3 challengers pass) |

### System Workflow Diagram

```mermaid
graph TD
    Start([Risk Input]) --> GenEnsemble[Generator Ensemble<br/>9 Parallel Models]
    
    GenEnsemble --> |8 Assessments| Aggregator[Aggregator<br/>Synthesise Unified Draft]
    
    Aggregator --> |Synthesised Draft| ChallengerA[Challenger A<br/>Logic Check]
    Aggregator --> |Synthesised Draft| ChallengerB[Challenger B<br/>Source Verification]
    Aggregator --> |Synthesised Draft| ChallengerC[Challenger C<br/>Compliance Check]
    
    ChallengerA --> |Critique| Verifier[Verifier<br/>Route Decision]
    ChallengerB --> |Critique| Verifier
    ChallengerC --> |Critique| Verifier
    
    Verifier --> |All Pass| End([Final Assessment])
    Verifier --> |Issues Found<br/>Revision Needed| RevisionCheck{Max Revisions<br/>Reached?}
    
    RevisionCheck --> |No| Aggregator
    RevisionCheck --> |Yes| GracefulCheck{2/3 Challengers<br/>Pass?}
    
    GracefulCheck --> |Yes| End
    GracefulCheck --> |No| End
    
    style GenEnsemble fill:#e1f5ff
    style Aggregator fill:#fff4e1
    style ChallengerA fill:#ffe1f5
    style ChallengerB fill:#ffe1f5
    style ChallengerC fill:#ffe1f5
    style Verifier fill:#e1ffe1
    style End fill:#f0f0f0
```

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant GenEnsemble as Generator Ensemble<br/>(8 Models)
    participant Aggregator
    participant ChallengerA as Challenger A<br/>(Logic)
    participant ChallengerB as Challenger B<br/>(Source)
    participant ChallengerC as Challenger C<br/>(Compliance)
    participant Verifier
    
    User->>GenEnsemble: Risk Input
    par Parallel Generation
        GenEnsemble->>GenEnsemble: GPT-4o
        GenEnsemble->>GenEnsemble: Claude 3.5 Sonnet
        GenEnsemble->>GenEnsemble: Gemini Pro
        GenEnsemble->>GenEnsemble: ... (5 more models)
    end
    GenEnsemble->>Aggregator: 8 Assessments
    
    Aggregator->>Aggregator: Synthesise Unified Draft
    Aggregator->>ChallengerA: Synthesised Draft
    Aggregator->>ChallengerB: Synthesised Draft
    Aggregator->>ChallengerC: Synthesised Draft
    
    par Parallel Validation
        ChallengerA->>ChallengerA: Check Logic
        ChallengerB->>ChallengerB: Verify Sources
        ChallengerC->>ChallengerC: Check Compliance
    end
    
    ChallengerA->>Verifier: Critique A
    ChallengerB->>Verifier: Critique B
    ChallengerC->>Verifier: Critique C
    
    Verifier->>Verifier: Evaluate Critiques
    
    alt All Pass or Good Enough
        Verifier->>User: Final Assessment
    else Revision Needed
        Verifier->>Aggregator: Revision Request
        Note over Aggregator: Revise based on critiques
        Aggregator->>ChallengerA: Revised Draft
        Aggregator->>ChallengerB: Revised Draft
        Aggregator->>ChallengerC: Revised Draft
    end
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

3. Configure API keys in `.env`:
   - OpenAI API key (for GPT-4o, o1 models)
   - Anthropic API key (for Claude models)
   - Google API key (for Gemini)
   - Tavily API key (for Challenger B search)
   - DeepSeek API key and base URL (for DeepSeek V3)
   - Groq API key (optional, for Llama models)
   - Mistral API key (optional, for Mistral models)

## Usage

```python
from src.main import run_risk_assessment

result = run_risk_assessment(
    risk_input="IoT device description and scenario..."
)
```

## Project Structure

```
.
├── src/                     # Source code
│   ├── schemas.py          # Pydantic models
│   ├── config.py            # Configuration and API keys
│   ├── graph.py             # LangGraph workflow
│   ├── main.py              # Entry point
│   ├── agents/              # Agent implementations
│   │   ├── generator_ensemble.py
│   │   ├── aggregator.py
│   │   ├── challenger_a.py
│   │   ├── challenger_b.py
│   │   ├── challenger_c.py
│   │   └── verifier.py
│   └── utils/               # Utility functions
│       ├── citation_parser.py
│       ├── search_helpers.py
│       └── prompt_templates.py
├── scripts/                 # Utility scripts
│   ├── show_results.py      # Run assessment and show results
│   ├── cost_estimator.py    # Estimate operation costs
│   ├── measure_time.py      # Measure execution time
│   └── ...
├── examples/                # Example test scripts
│   ├── test_full_workflow.py
│   └── test_individual_agents.py
├── docs/                    # Documentation
│   ├── API_KEYS.md         # API key documentation
│   ├── IMPROVEMENTS_SUMMARY.md
│   └── revision_analysis.md
└── requirements.txt
```

## Testing

Run the test scripts:
```bash
# Full workflow test
python examples/test_full_workflow.py

# Show results with formatted output
python scripts/show_results.py

# Measure execution time
python scripts/measure_time.py

# Cost estimation
python scripts/cost_estimator.py
```

## Models Used

- **Generator Ensemble**: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, claude-3-opus, deepseek-chat, llama-3.3-70b, mistral-large, o1-mini (8 models - Gemini temporarily disabled due to API compatibility)
- **Aggregator**: claude-3-5-sonnet-latest
- **Challenger A**: gpt-4o (logic consistency checking)
- **Challenger B**: deepseek-chat (source verification with search)
- **Challenger C**: gpt-4o (compliance validation)
- **Verifier**: claude-3-5-sonnet-latest

---

## Technical Design Decisions

### Core Architecture Choices

**Orchestration Framework**: LangGraph provides stateful workflows with conditional routing, enabling natural implementation of revision loops and parallel execution.

**State Management**: `TypedDict` with `Annotated[List[Critique], operator.add]` handles concurrent updates from parallel challengers safely.

**Generator Ensemble**: 8 heterogeneous models (GPT-4o, Claude Opus, DeepSeek, Llama, Mistral, O1-mini) run in parallel to generate diverse assessments with reasoning traces. Temperature set to `0.0` for deterministic output. (Gemini temporarily disabled due to API compatibility)

**Aggregator**: Dual-mode operation—initial synthesis combines 9 assessments; revision mode actively addresses challenger critiques. Uses Claude 3.5 Sonnet for synthesis quality.

**Challenger Architecture**: Three specialised validators run in parallel:
- **Challenger A (Logic)**: GPT-4o checks internal consistency and score-argument alignment
- **Challenger B (Source)**: DeepSeek Chat with Tavily Search API verifies external citations
- **Challenger C (Compliance)**: GPT-4o validates regulatory compliance

**Verifier**: Claude 3.5 Sonnet routes workflow with graceful degradation—accepts if ≥2/3 challengers pass when max revisions reached.

**Data Validation**: Pydantic V2 ensures type safety with strict validation (scores 1-5, confidence 0.0-1.0).

**Execution Model**: Hybrid async/sync—async LLM calls within synchronous LangGraph nodes using `asyncio.run()` and `asyncio.gather()` for parallel execution.

**Revision Strategy**: Aggregator-centric revision (not generator re-run) for efficiency and targeted improvement.

---

## Performance & Cost

### Execution Time
- **One-time pass**: ~2-3 minutes
- **With 3 revisions**: ~2-4 minutes (typical: ~2 minutes)
- **Bottleneck**: Generator Ensemble (8 models in parallel, limited by slowest)

### Cost per Operation
- **Typical (3 revisions)**: ~$0.80 USD (~¥5.79 CNY)
- **Optimised (1 revision)**: ~$0.52 USD (~¥3.78 CNY)
- **Perfect (no revisions)**: ~$0.38 USD (~¥2.78 CNY)

See `scripts/cost_estimator.py` for detailed cost breakdown.

---

## Human-in-the-Loop Validation

While the MAS automates the generation of arguments, the human acts as the **"Final Arbiter of Logic"**:

- **Reasoning Audit**: The Human Validator reviews the Synthesised Reasoning Trace (e.g., "Critical because of unpatched firmware vulnerability CVE-2025-XYZ") and validates alignment with real-world context.

- **Edge Case Resolution**: If Challengers identify conflicts (e.g., Safety vs. Privacy trade-offs) causing infinite loops (detected after 3 cycles), the system triggers an Escalation Path requiring human ethical judgment.

---

## Future Improvements

Potential enhancements based on usage patterns:

1. **Dynamic Model Selection**: Adjust generator ensemble based on input complexity
2. **Adaptive Revision Limits**: Increase MAX_REVISIONS for complex scenarios
3. **Caching**: Cache verified citations to reduce Tavily API calls
4. **Streaming**: Stream intermediate results for better UX
5. **Model Fine-tuning**: Fine-tune models on domain-specific risk assessments

