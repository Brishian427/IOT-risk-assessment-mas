"""
Challenger B - Source Verification (Fact Checker)
Created: 2025-01-XX
"""

import json
from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
# Node functions don't need explicit Node import in LangGraph

from src.schemas import StateSchema, Critique
from src.config import Config
from src.utils.prompt_templates import CHALLENGER_B_PROMPT
from src.utils.reference_sources import get_reference_sources
from src.utils.citation_parser import CitationParser
from src.utils.search_helpers import SearchQueryBuilder
from src.utils.conversation_recorder import record


def challenger_b_node(state: StateSchema) -> StateSchema:
    """LangGraph node: Verify external validity of citations"""
    synthesized_draft = state.get("synthesized_draft")
    
    if not synthesized_draft:
        critique = Critique(
            challenger_name="challenger_b",
            is_valid=False,
            issues=["No synthesized draft available for review"],
            confidence=1.0,
            recommendation="reject"
        )
        critiques = state.get("critiques", [])
        return {
            "critiques": critiques + [critique]
        }
    
    # Extract citations from reasoning
    parser = CitationParser()
    reasoning = synthesized_draft.reasoning
    
    all_citations = []
    all_citations.extend(reasoning.regulatory_citations)
    all_citations.extend(reasoning.vulnerabilities)
    
    # Also extract from summary and arguments text
    full_text = f"{reasoning.summary} {' '.join(reasoning.key_arguments)}"
    all_citations.extend(parser.extract_cves(full_text))
    all_citations.extend(parser.extract_regulations(full_text))
    all_citations.extend(parser.extract_standards(full_text))
    
    # Remove duplicates
    all_citations = list(set(all_citations))
    
    if not all_citations:
        # No citations to verify - accept
        critique = Critique(
            challenger_name="challenger_b",
            is_valid=True,
            issues=[],
            confidence=1.0,
            recommendation="accept"
        )
        critiques = state.get("critiques", [])
        return {
            "critiques": critiques + [critique]
        }
    
    # Initialize Tavily search tool
    search_tool = TavilySearch(
        api_key=Config.TAVILY_API_KEY,
        max_results=5
    )
    
    # Initialize LLM for analysis (OpenAI)
    llm = ChatOpenAI(
        model=Config.CHALLENGER_B_MODEL,
        temperature=Config.CHALLENGER_TEMPERATURE,
        api_key=Config.OPENAI_API_KEY
    )
    
    # Bind search tool to LLM
    llm_with_tools = llm.bind_tools([search_tool])
    
    # Search for each citation and collect results
    search_results_summary = []
    query_builder = SearchQueryBuilder()
    
    with tqdm(total=len(all_citations), desc="Challenger B: Verifying", unit="citation", ncols=80, leave=False) as pbar:
        for citation in all_citations:
            pbar.set_postfix_str(f"{citation[:20]:20s}")
        try:
            # Determine citation type and build query
            if citation.upper().startswith("CVE"):
                query = query_builder.build_cve_query(citation)
                citation_type = "CVE"
            elif any(term in citation.upper() for term in ["ISO", "27001", "27002"]):
                query = query_builder.build_standard_query(citation)
                citation_type = "Standard"
            else:
                query = query_builder.build_regulation_query(citation)
                citation_type = "Regulation"
            
            # Perform search
            results = search_tool.invoke(query)
            
            # Analyze results
            analysis = query_builder.analyze_search_results(citation, citation_type.lower(), results)
            
            search_results_summary.append({
                "citation": citation,
                "type": citation_type,
                "verified": analysis["verified"],
                "confidence": analysis["confidence"],
                "urls": analysis["relevant_urls"]
            })
        except Exception as e:
            search_results_summary.append({
                "citation": citation,
                "type": "Unknown",
                "verified": False,
                "confidence": 0.0,
                "urls": [],
                "error": str(e)
            })
    
    # Format for LLM analysis
    with tqdm(total=1, desc="Challenger B: Analyzing", unit="step", ncols=80, leave=False) as pbar2:
        citations_text = "\n".join([f"- {c}" for c in all_citations])
        results_text = json.dumps(search_results_summary, indent=2)
        
        assessment_text = f"""
Score: {synthesized_draft.score}
Summary: {reasoning.summary}
Arguments: {', '.join(reasoning.key_arguments)}
"""
        
        prompt = CHALLENGER_B_PROMPT.format(
            assessment=assessment_text,
            citations=citations_text,
            search_results=results_text,
            reference_sources=get_reference_sources()
        )
        
        try:
            response = llm.invoke(prompt)
            pbar2.update(1)
            
            content = response.content if hasattr(response, 'content') else str(response)
            record(
                stage="challenger_b",
                role="challenger",
                model=Config.CHALLENGER_B_MODEL,
                prompt=prompt,
                response=content,
                revision=state.get("revision_count", 0),
                extra={"citations_checked": len(all_citations)},
            )
            
            # Parse JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            data = json.loads(content)
            
            critique = Critique(
                challenger_name="challenger_b",
                is_valid=data.get("is_valid", True),
                issues=data.get("issues", []),
                confidence=data.get("confidence", 0.5),
                recommendation=data.get("recommendation", "needs_review")
        )
        except Exception as e:
            # Record the error for audit completeness
            record(
                stage="challenger_b",
                role="challenger",
                model=Config.CHALLENGER_B_MODEL,
                prompt=prompt,
                response=f"ERROR: {str(e)}",
                revision=state.get("revision_count", 0),
                extra={"citations_checked": len(all_citations)},
            )
            # On error, check if any citations failed verification
            unverified = [r for r in search_results_summary if not r.get("verified", False)]
            if unverified:
                issues = [f"Unverified citation: {r['citation']}" for r in unverified]
                critique = Critique(
                    challenger_name="challenger_b",
                    is_valid=False,
                    issues=issues,
                    confidence=0.5,
                    recommendation="needs_review"
                )
            else:
                critique = Critique(
                    challenger_name="challenger_b",
                    is_valid=True,
                    issues=[],
                    confidence=0.8,
                    recommendation="accept"
                )
    
    critiques = state.get("critiques", [])
    return {
        "critiques": critiques + [critique]
    }

