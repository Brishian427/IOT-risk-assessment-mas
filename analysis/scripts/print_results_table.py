"""Print results table in chat"""
import json
from pathlib import Path

formal_dir = Path('results/formal_assessment_20251210')
files = sorted(formal_dir.glob('*.json'))

scenarios = []
for f in files:
    data = json.loads(f.read_text(encoding='utf-8'))
    risk_input = data['metadata']['risk_input']
    draft = data['output']['synthesized_draft']
    
    # Extract scenario name
    scenario_name = "Unknown"
    if 'Risk Category:' in risk_input:
        scenario_name = risk_input.split('Risk Category:')[1].split('\n')[0].strip()
    
    # Extract lifecycle
    lifecycle = "Unknown"
    if 'Usage Phase' in risk_input:
        lifecycle = "Usage Phase"
    elif 'End-of-Life' in risk_input or 'EOL' in risk_input:
        lifecycle = "EOL"
    
    # Extract scores
    legacy = draft['score']
    ra = draft.get('risk_assessment', {})
    freq = ra.get('frequency_score', 'N/A')
    imp = ra.get('impact_score', 'N/A')
    final = ra.get('final_risk_score', 'N/A')
    cls = ra.get('risk_classification', 'N/A')
    
    scenarios.append({
        'name': scenario_name,
        'lifecycle': lifecycle,
        'freq': freq,
        'imp': imp,
        'final': final,
        'class': cls
    })

# Separate by phase
usage_phase = [s for s in scenarios if s['lifecycle'] == 'Usage Phase']
eol_phase = [s for s in scenarios if s['lifecycle'] == 'EOL']

# Define custom order for Usage Phase scenarios
usage_order = [
    "Protocol Weaknesses",
    "Remote Direct Control",
    "User Awareness Risk",
    "Data Hacking & Breaching",
    "Mass Data Inference",
    "Lack of Continuous Updates",
    "Cloud Dependency",
    "IoT as Medium for Broader Network Attacks"
]

# Sort Usage Phase by custom order
def get_usage_order_index(scenario):
    name = scenario['name']
    for idx, order_name in enumerate(usage_order):
        if order_name in name or name in order_name:
            return idx
    return 999  # Put unknown scenarios at the end

usage_phase.sort(key=get_usage_order_index)

# Sort EOL Phase by final score (descending)
eol_phase.sort(key=lambda x: int(x['final']) if x['final'] != 'N/A' else 0, reverse=True)

# Print table
print('=' * 110)
print('📋 FORMAL ASSESSMENT RESULTS TABLE'.center(110))
print('=' * 110)
print()

# Usage Phase
print('📱 USAGE PHASE (8 scenarios)')
print('-' * 110)
print(f'{"#":<3} {"Scenario":<50} {"Freq":<6} {"Imp":<6} {"Final":<7} {"Class":<10}')
print('-' * 110)

for idx, s in enumerate(usage_phase, 1):
    name = s['name'][:48] if len(s['name']) > 48 else s['name']
    freq = str(s['freq'])
    imp = str(s['imp'])
    final = str(s['final'])
    cls = str(s['class'])
    
    print(f'{idx:<3} {name:<50} {freq:<6} {imp:<6} {final:<7} {cls:<10}')

print('-' * 110)

# Calculate Usage Phase stats
usage_final = [int(s['final']) for s in usage_phase if s['final'] != 'N/A']
usage_freq = [int(s['freq']) for s in usage_phase if s['freq'] != 'N/A']
usage_imp = [int(s['imp']) for s in usage_phase if s['imp'] != 'N/A']
usage_critical = sum(1 for s in usage_phase if s['class'] == 'Critical')

if usage_final:
    print(f'\n   Usage Phase Statistics:')
    print(f'     Average Final Score: {sum(usage_final)/len(usage_final):.2f}/25')
    print(f'     Average Frequency: {sum(usage_freq)/len(usage_freq):.2f}/5')
    print(f'     Average Impact: {sum(usage_imp)/len(usage_imp):.2f}/5')
    print(f'     Critical: {usage_critical}/{len(usage_phase)} ({usage_critical*100//len(usage_phase)}%)')

print()
print('=' * 110)
print()

# EOL Phase
print('♻️  END-OF-LIFE (EOL) PHASE (3 scenarios)')
print('-' * 110)
print(f'{"#":<3} {"Scenario":<50} {"Freq":<6} {"Imp":<6} {"Final":<7} {"Class":<10}')
print('-' * 110)

for idx, s in enumerate(eol_phase, 1):
    name = s['name'][:48] if len(s['name']) > 48 else s['name']
    freq = str(s['freq'])
    imp = str(s['imp'])
    final = str(s['final'])
    cls = str(s['class'])
    
    print(f'{idx:<3} {name:<50} {freq:<6} {imp:<6} {final:<7} {cls:<10}')

print('-' * 110)

# Calculate EOL Phase stats
eol_final = [int(s['final']) for s in eol_phase if s['final'] != 'N/A']
eol_freq = [int(s['freq']) for s in eol_phase if s['freq'] != 'N/A']
eol_imp = [int(s['imp']) for s in eol_phase if s['imp'] != 'N/A']
eol_critical = sum(1 for s in eol_phase if s['class'] == 'Critical')

if eol_final:
    print(f'\n   EOL Phase Statistics:')
    print(f'     Average Final Score: {sum(eol_final)/len(eol_final):.2f}/25')
    print(f'     Average Frequency: {sum(eol_freq)/len(eol_freq):.2f}/5')
    print(f'     Average Impact: {sum(eol_imp)/len(eol_imp):.2f}/5')
    print(f'     Critical: {eol_critical}/{len(eol_phase)} ({eol_critical*100//len(eol_phase)}%)')

print()
print('=' * 110)

# Print summary
usage_phase = [s for s in scenarios if s['lifecycle'] == 'Usage Phase']
eol_phase = [s for s in scenarios if s['lifecycle'] == 'EOL']

print(f'\n📊 Summary:')
print(f'   Total Scenarios: {len(scenarios)}')
print(f'   Usage Phase: {len(usage_phase)} scenarios')
print(f'   EOL Phase: {len(eol_phase)} scenarios')

critical = sum(1 for s in scenarios if s['class'] == 'Critical')
high = sum(1 for s in scenarios if s['class'] == 'High')

print(f'\n   Risk Classification:')
print(f'     Critical: {critical} ({critical*100//len(scenarios)}%)')
print(f'     High: {high} ({high*100//len(scenarios)}%)')

if scenarios:
    final_scores = [int(s['final']) for s in scenarios if s['final'] != 'N/A']
    if final_scores:
        print(f'\n   Final Risk Scores:')
        print(f'     Average: {sum(final_scores)/len(final_scores):.2f}/25')
        print(f'     Range: {min(final_scores)} - {max(final_scores)}')

print('=' * 110)

