"""
Citation Parser - Extract and normalize citations from reasoning text
Created: 2025-01-XX
"""

import re
from typing import List, Dict


class CitationParser:
    """Extract and normalize citations (CVEs, regulations, standards)"""
    
    # Patterns for different citation types
    CVE_PATTERN = r'CVE[-\s]?(?:\d{4}[-\s]?)?\d{4,7}[-\s]?\d{4,7}'
    UK_ACT_PATTERN = r'(?:UK|United Kingdom)?\s*(?:Act|Regulation)\s+(?:\d{4})?'
    PSTI_PATTERN = r'PSTI\s+(?:Act\s+)?(?:2022)?'
    REGULATION_PATTERN = r'(?:EU|UK|US)\s+(?:Regulation|Directive)\s+(?:\d+/\d+)?'
    ISO_STANDARD_PATTERN = r'ISO[/\s]?\d{4,5}(?:[/-]\d+)?'
    
    def extract_cves(self, text: str) -> List[str]:
        """Extract CVE identifiers from text"""
        matches = re.finditer(self.CVE_PATTERN, text, re.IGNORECASE)
        return [match.group().strip().upper() for match in matches]
    
    def extract_regulations(self, text: str) -> List[str]:
        """Extract regulatory citations from text"""
        regulations = []
        
        # PSTI Act
        psti_matches = re.finditer(self.PSTI_PATTERN, text, re.IGNORECASE)
        for match in psti_matches:
            regulations.append("PSTI Act 2022")
        
        # UK Acts
        uk_act_matches = re.finditer(self.UK_ACT_PATTERN, text, re.IGNORECASE)
        for match in uk_act_matches:
            regulations.append(match.group().strip())
        
        # EU/UK/US Regulations
        reg_matches = re.finditer(self.REGULATION_PATTERN, text, re.IGNORECASE)
        for match in reg_matches:
            regulations.append(match.group().strip())
        
        return list(set(regulations))  # Remove duplicates
    
    def extract_standards(self, text: str) -> List[str]:
        """Extract ISO standards from text"""
        matches = re.finditer(self.ISO_STANDARD_PATTERN, text, re.IGNORECASE)
        return [match.group().strip().upper() for match in matches]
    
    def normalize_citation(self, citation: str, citation_type: str) -> str:
        """Normalize citation format"""
        if citation_type == "cve":
            # Normalize CVE format: CVE-YYYY-NNNNN
            cve_match = re.search(r'CVE[-\s]?(\d{4})[-\s]?(\d{4,7})', citation, re.IGNORECASE)
            if cve_match:
                return f"CVE-{cve_match.group(1)}-{cve_match.group(2)}"
        elif citation_type == "regulation":
            # Normalize regulation names
            if "PSTI" in citation.upper():
                return "PSTI Act 2022"
        elif citation_type == "standard":
            # Normalize ISO standards
            iso_match = re.search(r'ISO[/\s]?(\d{4,5})(?:[/-](\d+))?', citation, re.IGNORECASE)
            if iso_match:
                if iso_match.group(2):
                    return f"ISO {iso_match.group(1)}-{iso_match.group(2)}"
                return f"ISO {iso_match.group(1)}"
        
        return citation.strip()

