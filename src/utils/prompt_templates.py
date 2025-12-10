"""
Prompt Templates for Multi-Agent System
Created: 2025-01-XX
"""

from src.utils.reference_sources import get_reference_sources


# Generator Ensemble Prompt
GENERATOR_PROMPT = """You are an expert IoT risk assessor. Analyze the following IoT device scenario and provide a comprehensive risk assessment.

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
{{
    "score": <integer 1-5>,  // Legacy score for backward compatibility (map from final_risk_score: 1-5=1, 6-10=2, 11-15=3, 16-20=4, 21-25=5)
    "reasoning": {{
        "summary": "<brief summary of the risk>",
        "key_arguments": ["<argument 1>", "<argument 2>", ...],
        "regulatory_citations": ["<regulation 1>", "<regulation 2>", ...],
        "vulnerabilities": ["<CVE or vulnerability 1>", "<CVE or vulnerability 2>", ...]
    }},
    "risk_assessment": {{
        "frequency_score": <integer 1-5>,  // Also called "Likelihood" - measures how often/widespread the risk occurs
        "frequency_rationale": "<One sentence justifying the frequency based on history/default behavior. Focus on prevalence, not future probability.>",
        "impact_score": <integer 1-5>,
        "impact_rationale": "<One sentence justifying the severity of damage>",
        "final_risk_score": <integer 1-25>,  // Must be frequency_score * impact_score
        "risk_classification": "<Low/Medium/High/Critical>"
    }}
}}

Be specific with regulatory citations (e.g., "PSTI Act 2022", "ISO 27001") and vulnerabilities (e.g., "CVE-2024-12345")."""


# Aggregator Prompt (Initial Synthesis)
AGGREGATOR_PROMPT = """You are synthesizing risk assessments from 9 expert models. Your task is to create a unified, consensus-driven risk assessment.

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
{{
    "score": <integer 1-5>,  // Legacy score (map from final_risk_score: 1-5=1, 6-10=2, 11-15=3, 16-20=4, 21-25=5)
    "reasoning": {{
        "summary": "<synthesized summary>",
        "key_arguments": ["<unified argument 1>", ...],
        "regulatory_citations": ["<all valid citations>", ...],
        "vulnerabilities": ["<all valid vulnerabilities>", ...]
    }},
    "risk_assessment": {{
        "frequency_score": <integer 1-5>,  // Also called "Likelihood" - measures how often/widespread the risk occurs
        "frequency_rationale": "<Synthesized rationale based on consensus from individual assessments. Focus on prevalence, not future probability.>",
        "impact_score": <integer 1-5>,
        "impact_rationale": "<Synthesized rationale based on consensus from individual assessments>",
        "final_risk_score": <integer 1-25>,  // Must be frequency_score * impact_score
        "risk_classification": "<Low/Medium/High/Critical>"
    }}
}}"""


# Aggregator Revision Prompt (With Critiques)
AGGREGATOR_REVISION_PROMPT = """You are REVISING a risk assessment based on critiques from three challenger agents. This is a revision cycle - you MUST address ALL issues raised.

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
{{
    "score": <integer 1-5>,  // Legacy score (map from final_risk_score: 1-5=1, 6-10=2, 11-15=3, 16-20=4, 21-25=5)
    "reasoning": {{
        "summary": "<revised summary that addresses all critiques>",
        "key_arguments": ["<argument addressing issue 1>", "<argument addressing issue 2>", ...],
        "regulatory_citations": ["<only verified citations>", ...],
        "vulnerabilities": ["<valid vulnerabilities>", ...]
    }},
    "risk_assessment": {{
        "frequency_score": <integer 1-5>,  // Also called "Likelihood" - measures how often/widespread the risk occurs
        "frequency_rationale": "<Revised rationale addressing frequency-related critiques. Focus on prevalence, not future probability.>",
        "impact_score": <integer 1-5>,
        "impact_rationale": "<Revised rationale addressing impact-related critiques>",
        "final_risk_score": <integer 1-25>,  // Must be frequency_score * impact_score
        "risk_classification": "<Low/Medium/High/Critical>"
    }}
}}

IMPORTANT: This is a revision - do not simply repeat the previous assessment. Actively improve it based on the critiques. If critiques mention calculation errors or frequency/impact justification issues, address them in the revised risk_assessment breakdown."""


# Challenger A (Logic) Prompt
CHALLENGER_A_PROMPT = """You are a formal logician analyzing a risk assessment for internal consistency.

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
{{
    "is_valid": <true/false>,
    "issues": ["<issue 1>", "<issue 2>", ...],
    "confidence": <0.0-1.0>,
    "recommendation": "<accept|reject|needs_review>"
}}

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

If the logic is fundamentally sound, calculations are approximately correct, and scores are reasonably justified, set is_valid=true. Only set is_valid=false for SIGNIFICANT logical inconsistencies, major calculation errors, or complete lack of reasoning."""


# Challenger B (Source) Prompt
CHALLENGER_B_PROMPT = """You are a fact-checker verifying the external validity of citations in a risk assessment. Your role is to flag MAJOR unverified claims that could undermine the assessment's credibility, not to reject assessments for minor citation issues.

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
{{
    "is_valid": <true/false>,
    "issues": ["<unverified MAJOR citation: X>", "<incorrect MAJOR citation: Y>", ...],
    "confidence": <0.0-1.0>,
    "recommendation": "<accept|reject|needs_review>"
}}

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

Remember: Your goal is to catch significant factual errors, not to be a perfectionist. An assessment with 60% verified citations and minor unverified details should generally be accepted."""


# Challenger C (Safety) Prompt
CHALLENGER_C_PROMPT = """You are a safety and compliance expert validating a risk assessment against regulatory requirements.

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
{{
    "is_valid": <true/false>,
    "issues": ["<compliance issue 1>", "<safety concern 2>", ...],
    "confidence": <0.0-1.0>,
    "recommendation": "<accept|reject|needs_review>"
}}

Evaluation Guidelines:
- If major compliance requirements are addressed, set is_valid=true even if some minor standards are not explicitly mentioned
- Only set is_valid=false for SIGNIFICANT compliance gaps or complete absence of regulatory considerations
- Missing one or two minor ISO standards should be noted but may not require rejection if core compliance is addressed
- If the assessment shows awareness of key regulatory requirements (PSTI Act, basic ISO standards), consider it valid despite minor gaps

If major compliance requirements are properly addressed, set is_valid=true. If there are significant compliance gaps or complete absence of regulatory considerations, set is_valid=false."""


# Verifier Prompt
VERIFIER_PROMPT = """You are the final arbiter reviewing critiques from three challenger agents.

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
{{
    "needs_revision": <true/false>,
    "reason": "<explanation>",
    "revision_focus": ["<area 1 to revise>", "<area 2 to revise>", ...]
}}

If all critiques are resolved or minor, set needs_revision=false. If there are significant issues, set needs_revision=true."""

