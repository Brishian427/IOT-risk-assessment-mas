"""Check JSON output for completeness"""
import json
from pathlib import Path

result_file = Path('results/assessment_iot_risk_20251209_234050.json')
data = json.loads(result_file.read_text(encoding='utf-8'))

print('='*80)
print('📋 JSON 文件内容检查')
print('='*80)

print(f'\n✅ Metadata:')
print(f'   Assessment Type: {data["metadata"]["assessment_type"]}')
print(f'   Revision Count: {data["metadata"]["revision_count"]}')
print(f'   Total Assessments: {data["metadata"]["total_assessments"]}')

print(f'\n✅ Synthesized Draft:')
draft = data['output']['synthesized_draft']
print(f'   Legacy Score: {draft["score"]}')
print(f'   Has risk_assessment: {"risk_assessment" in draft}')

if 'risk_assessment' in draft:
    ra = draft['risk_assessment']
    print(f'   Frequency Score: {ra["frequency_score"]}')
    print(f'   Impact Score: {ra["impact_score"]}')
    print(f'   Final Risk Score: {ra["final_risk_score"]}')
    print(f'   Classification: {ra["risk_classification"]}')
    print(f'   Calculation: {ra["frequency_score"]} × {ra["impact_score"]} = {ra["final_risk_score"]}')
    print(f'   Frequency Rationale Length: {len(ra["frequency_rationale"])} chars')
    print(f'   Impact Rationale Length: {len(ra["impact_rationale"])} chars')

print(f'\n✅ Reasoning:')
print(f'   Summary Length: {len(draft["reasoning"]["summary"])} chars')
print(f'   Key Arguments: {len(draft["reasoning"]["key_arguments"])}')
print(f'   Citations: {len(draft["reasoning"]["regulatory_citations"])}')
print(f'   Vulnerabilities: {len(draft["reasoning"]["vulnerabilities"])}')

print(f'\n✅ Critiques: {len(data["output"]["critiques"])}')
challenger_counts = {}
for c in data["output"]["critiques"]:
    name = c["challenger_name"]
    challenger_counts[name] = challenger_counts.get(name, 0) + 1
for name, count in challenger_counts.items():
    print(f'   {name}: {count}')

print(f'\n✅ Conversation Log: {len(data.get("conversation_log", []))} entries')
if data.get("conversation_log"):
    stages = {}
    for entry in data["conversation_log"]:
        stage = entry.get("stage", "unknown")
        stages[stage] = stages.get(stage, 0) + 1
    print('   Stages:')
    for stage, count in stages.items():
        print(f'     {stage}: {count}')

print('\n✅ 所有重要内容都已保存！')

