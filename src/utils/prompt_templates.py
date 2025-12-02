"""
Prompt Templates for Multi-Agent System
Created: 2025-01-XX
"""


# Generator Ensemble Prompt
GENERATOR_PROMPT = """You are an expert IoT risk assessor. Analyze the following IoT device scenario and provide a comprehensive risk assessment.

Device Scenario:
{risk_input}

Provide your assessment in the following JSON format:
{{
    "score": <integer 1-5>,
    "reasoning": {{
        "summary": "<brief summary of the risk>",
        "key_arguments": ["<argument 1>", "<argument 2>", ...],
        "regulatory_citations": ["<regulation 1>", "<regulation 2>", ...],
        "vulnerabilities": ["<CVE or vulnerability 1>", "<CVE or vulnerability 2>", ...]
    }}
}}

Be specific with regulatory citations (e.g., "PSTI Act 2022", "ISO 27001") and vulnerabilities (e.g., "CVE-2024-12345")."""


# Aggregator Prompt (Initial Synthesis)
AGGREGATOR_PROMPT = """You are synthesizing risk assessments from 9 expert models. Your task is to create a unified, consensus-driven risk assessment.

Individual Assessments:
{assessments}

Analyze the reasoning traces, identify consensus points, and synthesize a unified assessment that:
1. Reflects the majority logic and evidence
2. Incorporates the strongest arguments from all assessments
3. Maintains consistency between the score and reasoning
4. Preserves all valid regulatory citations and vulnerabilities

Provide the unified assessment in JSON format:
{{
    "score": <integer 1-5>,
    "reasoning": {{
        "summary": "<synthesized summary>",
        "key_arguments": ["<unified argument 1>", ...],
        "regulatory_citations": ["<all valid citations>", ...],
        "vulnerabilities": ["<all valid vulnerabilities>", ...]
    }}
}}"""


# Aggregator Revision Prompt (With Critiques)
AGGREGATOR_REVISION_PROMPT = """You are REVISING a risk assessment based on critiques from three challenger agents. This is a revision cycle - you MUST address ALL issues raised.

Previous Assessment:
{previous_assessment}

Critiques from Challengers:
{critiques}

CRITICAL: You must address each issue raised:
1. If Challenger A (Logic) found missing reasoning or arguments:
   - ADD detailed reasoning that justifies the score
   - ENSURE key_arguments are comprehensive and support the severity level
   - FIX any logical inconsistencies or contradictions

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
    "score": <integer 1-5>,
    "reasoning": {{
        "summary": "<revised summary that addresses all critiques>",
        "key_arguments": ["<argument addressing issue 1>", "<argument addressing issue 2>", ...],
        "regulatory_citations": ["<only verified citations>", ...],
        "vulnerabilities": ["<valid vulnerabilities>", ...]
    }}
}}

IMPORTANT: This is a revision - do not simply repeat the previous assessment. Actively improve it based on the critiques."""


# Challenger A (Logic) Prompt
CHALLENGER_A_PROMPT = """You are a formal logician analyzing a risk assessment for internal consistency.

Risk Assessment:
Score: {score}
Reasoning: {reasoning}

Your task:
1. Check if the score (1-5) is justified by the evidence in the reasoning
2. Identify any non-sequiturs or logical fallacies
3. Verify that the key arguments support the severity level
4. Check for contradictions within the reasoning

Provide your critique in JSON format:
{{
    "is_valid": <true/false>,
    "issues": ["<issue 1>", "<issue 2>", ...],
    "confidence": <0.0-1.0>,
    "recommendation": "<accept|reject|needs_review>"
}}

Evaluation Guidelines:
- If the core logic is sound and the score is reasonably justified, set is_valid=true even if some details are missing
- Only set is_valid=false for SIGNIFICANT logical inconsistencies or when reasoning is completely missing
- Minor gaps in reasoning or missing minor arguments should be noted but may not require rejection
- If the assessment has basic reasoning that supports the score, consider it valid despite minor issues

If the logic is fundamentally sound, set is_valid=true. If there are major logical inconsistencies or complete lack of reasoning, set is_valid=false and list the issues."""


# Challenger B (Source) Prompt
CHALLENGER_B_PROMPT = """You are a fact-checker verifying the external validity of citations in a risk assessment.

Risk Assessment:
{assessment}

Citations to verify:
{citations}

Search results for each citation:
{search_results}

For each citation, determine:
1. Does it exist and is it real?
2. Is it correctly cited?
3. Is it relevant to the risk assessment?

Provide your critique in JSON format:
{{
    "is_valid": <true/false>,
    "issues": ["<unverified citation: X>", "<incorrect citation: Y>", ...],
    "confidence": <0.0-1.0>,
    "recommendation": "<accept|reject|needs_review>"
}}

If all citations are verified, set is_valid=true. If any citations are unverified or incorrect, set is_valid=false."""


# Challenger C (Safety) Prompt
CHALLENGER_C_PROMPT = """You are a safety and compliance expert validating a risk assessment against regulatory requirements.

Risk Assessment:
Score: {score}
Reasoning: {reasoning}

Validate against:
- PSTI Act 2022 requirements
- ISO standards (27001, 27002, etc.)
- IoT security best practices
- Product safety regulations

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

Synthesized Draft:
{assessment}

Critiques:
{critiques}

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

