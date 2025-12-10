# Analysis Scripts and Documentation

This directory contains all analysis scripts and evaluation-related documentation that are not part of the core MAS (Multi-Agent System) implementation.

## Directory Structure

```
analysis/
├── scripts/          # Analysis and evaluation scripts
└── docs/            # Analysis reports and evaluation summaries
```

## Scripts

All analysis scripts have been moved here from the main `scripts/` directory. These include:

- **Analysis Scripts:**
  - `analyze_challenger_agreement.py` - Analyze agreement patterns among challengers
  - `analyze_challenger_pass_rate.py` - Analyze challenger pass rates
  - `analyze_pass_rate.py` - General pass rate analysis
  - `evaluation_results_summary.py` - Comprehensive evaluation results summary
  - `generate_reflection.py` - Generate reflection report on evaluation results

- **Cost Analysis:**
  - `cost_estimator.py` - Estimate costs for assessments
  - `cost_optimization_analysis.py` - Cost optimization recommendations
  - `calculate_batch_cost.py` - Calculate batch evaluation costs
  - `calculate_last_round_cost.py` - Calculate last round costs

- **Summarization:**
  - `summarize_formal_assessment.py` - Summarize formal assessment results
  - `summarize_scores.py` - Summarize risk scores
  - `print_results_table.py` - Print formatted results table

- **Testing & Verification:**
  - `test_setup.py` - Test system setup
  - `test_challenger_b_isolated.py` - Isolated test for Challenger B
  - `check_json_output.py` - Check JSON output format
  - `quick_test.py`, `quick_test_dual_factor.py`, `quick_verify.py` - Quick test scripts

- **Utilities:**
  - `show_results.py` - Display results
  - `measure_time.py` - Measure execution time
  - `time_analysis.py` - Time analysis
  - `batch_evaluate.py` - Batch evaluation script

## Documentation

All evaluation summaries and analysis reports have been moved here from the main `docs/` directory:

- `EVALUATION_RESULTS_SUMMARY.md` - Main evaluation results summary (Chinese)
- `EVALUATION_RESULTS_SUMMARY_EN.md` - Evaluation results summary (English)
- `EVALUATION_RESULTS_SUMMARY_HUMAN_AI_VALIDATION.md` - Human-AI validation research focus
- `CHALLENGER_AGREEMENT_ANALYSIS.md` - Challenger agreement analysis
- `FORMAL_ASSESSMENT_SUMMARY_CN.md` - Formal assessment summary (Chinese)
- `IMPROVEMENTS_SUMMARY.md` - System improvements summary
- `revision_analysis.md` - Revision pattern analysis

## Note

The core MAS system files remain in:
- `src/` - Core MAS implementation
- `scripts/formal_assessment.py` - Main assessment runner
- `scripts/test_system_health.py` - System health check
- `evaluation_inputs/` - Input scenarios
- `results/` - Assessment results
- `logs/` - System logs

