"""Count actual sources in reference_sources.py"""
import re
from pathlib import Path

content = Path('src/utils/reference_sources.py').read_text(encoding='utf-8')

# Find all Source: mentions
sources = re.findall(r'Source:\s*([^\n]+)', content)

print(f"Total 'Source:' mentions: {len(sources)}")
print("\nAll sources found:")
for i, s in enumerate(sources, 1):
    print(f"{i:2d}. {s}")

# Extract unique sources (split by / and clean)
unique_sources = set()
for s in sources:
    # Split by / to handle multiple sources
    parts = s.split('/')
    for part in parts:
        # Clean up and add
        cleaned = part.strip()
        if cleaned:
            unique_sources.add(cleaned)

print(f"\n{'='*60}")
print(f"Unique sources: {len(unique_sources)}")
print(f"{'='*60}")
for source in sorted(unique_sources):
    print(f"  • {source}")

# Also check for implicit sources (mentioned but not in Source: format)
implicit = []
if 'McKinsey' in content:
    implicit.append('McKinsey B2B IoT Survey')
if 'Microsoft survey' in content:
    implicit.append('Microsoft survey')

if implicit:
    print(f"\nImplicit sources (mentioned but not in 'Source:' format): {len(implicit)}")
    for imp in implicit:
        print(f"  • {imp}")

print(f"\n{'='*60}")
print(f"TOTAL: {len(unique_sources) + len(implicit)} unique sources")
print(f"{'='*60}")

