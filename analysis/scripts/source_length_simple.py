"""Simple analysis of source description lengths"""
from pathlib import Path
import re

content = Path('src/utils/reference_sources.py').read_text(encoding='utf-8')

# Extract case studies (most detailed)
case_studies_pattern = r'-\s+([^:]+):\s*([^S]+?)(?=Source:\s*[^\n]+)'
matches = list(re.finditer(case_studies_pattern, content, re.DOTALL))

print("=" * 80)
print("SOURCE DESCRIPTION LENGTH ANALYSIS")
print("=" * 80)
print()

entries = []
for match in matches:
    title = match.group(1).strip()
    description = match.group(2).strip()
    length = len(description)
    entries.append((title, description, length))

print(f"Total source entries with descriptions: {len(entries)}")
print()

if entries:
    lengths = [e[2] for e in entries]
    print("STATISTICS:")
    print(f"  • Average length: {sum(lengths)/len(lengths):.0f} characters")
    print(f"  • Median length: {sorted(lengths)[len(lengths)//2]} characters")
    print(f"  • Min length: {min(lengths)} characters")
    print(f"  • Max length: {max(lengths)} characters")
    print()
    
    # Word count (rough estimate: 5 chars per word)
    total_chars = sum(lengths)
    total_words = total_chars // 5
    print(f"  • Total characters: {total_chars:,}")
    print(f"  • Estimated total words: ~{total_words:,}")
    print(f"  • Average words per entry: ~{total_words//len(entries)}")
    print()
    
    print("=" * 80)
    print("DETAILED BREAKDOWN (sorted by length):")
    print("=" * 80)
    print()
    
    for i, (title, desc, length) in enumerate(sorted(entries, key=lambda x: x[2], reverse=True), 1):
        words = length // 5
        print(f"{i:2d}. {title[:60]}")
        print(f"    Length: {length:3d} chars (~{words} words)")
        print(f"    Preview: {desc[:80]}...")
        print()

# Also check the entire knowledge base size
total_kb_size = len(content)
print("=" * 80)
print("KNOWLEDGE BASE OVERALL SIZE:")
print("=" * 80)
print(f"Total file size: {total_kb_size:,} characters")
print(f"Estimated words: ~{total_kb_size // 5:,} words")
print(f"Estimated pages (250 words/page): ~{total_kb_size // 5 // 250} pages")
print("=" * 80)

