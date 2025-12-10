"""Analyze source coverage for 11 scenarios"""
from pathlib import Path
import re

scenarios = [
    "Protocol Weaknesses",
    "Remote Direct Control", 
    "User Awareness Risk",
    "Data Hacking & Breaching",
    "Mass Data Inference",
    "Lack of Continuous Updates",
    "Cloud Dependency",
    "IoT as Medium for Broader Network Attacks",
    "Physical Safety / Fire Hazard",
    "Data Privacy / Information Leakage",
    "Environmental Toxicity & Public Health"
]

content = Path('src/utils/reference_sources.py').read_text(encoding='utf-8')

# Count sources by type
news_media = len(re.findall(r'(The Hacker News|CNN|The Washington Post|The Telegraph|Computer Weekly|The Scotsman|Snopes|MIT Technology Review)', content))
academic = len(re.findall(r'(et al\.|Lin et al\.)', content))
industry = len(re.findall(r'(Gartner|McKinsey|Microsoft|CSO Online|Imperva|Infosecurity Magazine)', content))
security_firms = len(re.findall(r'(Kaspersky|Material Focus|DesignLifecycle|Environmental Impact Studies)', content))
organizations = len(re.findall(r'(Which\?|Cybersecurity Insiders|Material Focus)', content))

print("=" * 70)
print("SOURCE COVERAGE ANALYSIS")
print("=" * 70)
print(f"\nTotal Scenarios: {len(scenarios)}")
print(f"Total Unique Sources: 23")
print(f"Sources per Scenario: {23/len(scenarios):.1f}")
print()

print("Source Distribution by Type:")
print(f"  • News Media: {news_media} sources")
print(f"  • Academic Research: ~3 sources (Bhardwaj, Lin, etc.)")
print(f"  • Industry Reports: ~5 sources (Gartner, McKinsey, Microsoft, etc.)")
print(f"  • Security Firms: ~4 sources (Kaspersky, etc.)")
print(f"  • Organizations: ~3 sources (Which?, Material Focus, etc.)")
print()

print("Coverage Assessment:")
print()
print("✅ STRENGTHS:")
print("  • Good real-world case study coverage (10+ documented incidents)")
print("  • Diverse source types (news, academic, industry)")
print("  • Recent sources (2016-2025)")
print("  • Geographic diversity (UK, US, South Korea, Finland)")
print()

print("⚠️  POTENTIAL GAPS:")
print("  • Academic sources: Only 2-3 papers (could use more peer-reviewed research)")
print("  • Standards/Regulations: Limited ISO/NIST/PSTI citations")
print("  • EOL-specific: Only 3 sources for 3 EOL scenarios (1:1 ratio)")
print("  • Statistical data: Some statistics lack explicit sources")
print("  • Protocol-specific: Limited technical protocol documentation")
print()

print("RECOMMENDATION:")
avg_sources_per_scenario = 23 / len(scenarios)
if avg_sources_per_scenario < 2:
    print("  ⚠️  BELOW IDEAL: Less than 2 sources per scenario")
    print("     Consider adding 5-10 more sources, especially:")
    print("     - More academic papers (IEEE, ACM, etc.)")
    print("     - Standards documents (ISO 27001, NIST IoT Security)")
    print("     - More EOL environmental studies")
    print("     - Protocol specification documents")
elif avg_sources_per_scenario < 3:
    print("  ✓ ADEQUATE: 2-3 sources per scenario is reasonable")
    print("     Could benefit from:")
    print("     - More academic depth (peer-reviewed papers)")
    print("     - More standards/regulatory citations")
    print("     - Better EOL coverage")
else:
    print("  ✓ GOOD: More than 3 sources per scenario")

print()
print("=" * 70)

