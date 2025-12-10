"""Analyze the length of each source description"""
import re
from pathlib import Path

content = Path('src/utils/reference_sources.py').read_text(encoding='utf-8')

# Extract all source entries (everything between "Source:" and the next line or end)
# We'll look at the case studies section which has the most detailed sources
case_studies_section = content.split("10. REAL-WORLD SECURITY INCIDENTS")[1].split("11. FIRMWARE")[0]

# Extract individual case study entries
case_studies = re.findall(r'   [a-f]\)[^a-f\)]+?Source: [^\n]+', case_studies_section, re.DOTALL)

print("=" * 80)
print("SOURCE DESCRIPTION LENGTH ANALYSIS")
print("=" * 80)
print()

# Analyze case studies (most detailed sources)
print("CASE STUDIES (Real-World Incidents) - Detailed Analysis:")
print("-" * 80)

case_study_lengths = []
for i, study in enumerate(case_studies, 1):
    # Split by Source: to get description and source
    parts = study.split('Source:')
    if len(parts) == 2:
        description = parts[0].strip()
        source = parts[1].strip()
        desc_length = len(description)
        case_study_lengths.append(desc_length)
        
        # Extract the incident name (first line after category)
        lines = description.split('\n')
        incident_name = ""
        for line in lines:
            if line.strip().startswith('-') and ':' in line:
                incident_name = line.strip().split(':')[0].replace('-', '').strip()
                break
        
        print(f"{i}. {incident_name[:50]}")
        print(f"   Description length: {desc_length} characters")
        print(f"   Source: {source}")
        print()

if case_study_lengths:
    print(f"Case Study Statistics:")
    print(f"  • Average length: {sum(case_study_lengths)/len(case_study_lengths):.0f} characters")
    print(f"  • Min length: {min(case_study_lengths)} characters")
    print(f"  • Max length: {max(case_study_lengths)} characters")
    print(f"  • Total characters: {sum(case_study_lengths)}")
    print()

# Analyze all source entries in the file
print("=" * 80)
print("ALL SOURCE ENTRIES - Length Analysis:")
print("-" * 80)

# Find all sections with Source: mentions
all_source_entries = []
sections = content.split('\n\n')

for section in sections:
    if 'Source:' in section:
        # Split by Source: to get the entry
        parts = section.split('Source:')
        if len(parts) >= 2:
            description = parts[0].strip()
            source_info = parts[1].split('\n')[0].strip()
            
            # Get the main point (first bullet or line)
            lines = description.split('\n')
            main_point = ""
            for line in lines:
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    main_point = line.strip().replace('-', '').replace('*', '').strip()
                    break
            
            entry_length = len(description)
            all_source_entries.append({
                'point': main_point[:60],
                'description_length': entry_length,
                'source': source_info
            })

# Sort by length
all_source_entries.sort(key=lambda x: x['description_length'], reverse=True)

print(f"\nTotal source entries: {len(all_source_entries)}")
print()

print("Top 5 Longest Entries:")
for i, entry in enumerate(all_source_entries[:5], 1):
    print(f"{i}. {entry['point']}")
    print(f"   Length: {entry['description_length']} chars")
    print(f"   Source: {entry['source']}")
    print()

print("Top 5 Shortest Entries:")
for i, entry in enumerate(all_source_entries[-5:], 1):
    print(f"{i}. {entry['point']}")
    print(f"   Length: {entry['description_length']} chars")
    print(f"   Source: {entry['source']}")
    print()

# Overall statistics
all_lengths = [e['description_length'] for e in all_source_entries]
print("=" * 80)
print("OVERALL STATISTICS:")
print("-" * 80)
print(f"Total entries: {len(all_source_entries)}")
print(f"Average length: {sum(all_lengths)/len(all_lengths):.0f} characters")
print(f"Median length: {sorted(all_lengths)[len(all_lengths)//2]} characters")
print(f"Min length: {min(all_lengths)} characters")
print(f"Max length: {max(all_lengths)} characters")
print(f"Total content: {sum(all_lengths):,} characters")
print()

# Word count estimate
total_words = sum(e['description_length'] // 5 for e in all_source_entries)  # Rough estimate: 5 chars per word
print(f"Estimated total words: ~{total_words:,} words")
print(f"Average words per entry: ~{total_words//len(all_source_entries)} words")
print("=" * 80)

