"""
Search Helpers - Query construction for Tavily search
Created: 2025-01-XX
"""

from typing import List, Dict


class SearchQueryBuilder:
    """Build search queries for citation verification"""
    
    def build_cve_query(self, cve_id: str) -> str:
        """Build search query for CVE verification"""
        return f'"{cve_id}" CVE vulnerability security'
    
    def build_regulation_query(self, regulation: str) -> str:
        """Build search query for regulation verification"""
        if "PSTI" in regulation.upper():
            return "PSTI Act 2022 Product Security Telecommunications Infrastructure UK legislation"
        elif "UK" in regulation or "United Kingdom" in regulation:
            return f'"{regulation}" UK regulation legislation gov.uk'
        elif "EU" in regulation:
            return f'"{regulation}" EU regulation directive'
        else:
            return f'"{regulation}" regulation legislation'
    
    def build_standard_query(self, standard: str) -> str:
        """Build search query for ISO standard verification"""
        return f'"{standard}" ISO standard certification'
    
    def analyze_search_results(self, citation: str, citation_type: str, results: List[Dict]) -> Dict:
        """
        Analyze search results for citation verification
        
        Returns:
            Dict with 'verified', 'confidence', 'relevant_urls'
        """
        if not results:
            return {
                "verified": False,
                "confidence": 0.0,
                "relevant_urls": []
            }
        
        citation_lower = citation.lower()
        relevant_urls = []
        confidence_scores = []
        
        # Official domains that boost confidence
        official_domains = [
            "gov.uk",
            "legislation.gov.uk",
            "cve.org",
            "nvd.nist.gov",
            "iso.org",
            "bsi-group.com",
            "europa.eu"
        ]
        
        for result in results:
            title = result.get("title", "").lower()
            content = result.get("content", "").lower()
            url = result.get("url", "").lower()
            
            combined_text = f"{title} {content}"
            
            # Check for exact match
            if citation_lower in combined_text:
                score = 0.9
            else:
                # Partial match scoring
                key_terms = citation_lower.split()
                matches = sum(1 for term in key_terms if term in combined_text)
                score = (matches / len(key_terms)) * 0.6 if key_terms else 0.0
            
            # Boost for official domains
            if any(domain in url for domain in official_domains):
                score += 0.3
            
            confidence_scores.append(min(score, 1.0))
            
            if score >= 0.5:
                relevant_urls.append(result.get("url", ""))
        
        max_confidence = max(confidence_scores) if confidence_scores else 0.0
        verified = max_confidence >= 0.7
        
        return {
            "verified": verified,
            "confidence": max_confidence,
            "relevant_urls": relevant_urls[:3]  # Top 3 relevant URLs
        }

