"""
分析系统通过率和修订情况
Created: 2025-01-XX
"""

import json
from src.main import run_risk_assessment

def analyze_revision_pattern():
    """分析修订模式和通过情况"""
    
    test_scenario = """
    IoT Smart Door Lock Device:
    - Bluetooth and WiFi connectivity
    - Mobile app control
    - No encryption on Bluetooth communication
    - Firmware updates over unencrypted HTTP
    - Default PIN code (0000)
    - Stores user access logs in plaintext
    - No PSTI Act 2022 compliance documentation
    - Potential CVE-2024-12345 vulnerability (unpatched)
    """
    
    print("=" * 80)
    print("分析修订模式和通过情况")
    print("=" * 80)
    print()
    
    result = run_risk_assessment(test_scenario)
    
    revision_count = result.get("revision_count", 0)
    critiques = result.get("critiques", [])
    synthesized_draft = result.get("synthesized_draft")
    
    print(f"📊 修订统计")
    print(f"  总修订次数: {revision_count}")
    print(f"  最大允许修订: 3")
    print(f"  是否达到最大修订: {'是' if revision_count >= 3 else '否'}")
    print()
    
    # 分析 critiques
    print(f"📋 挑战者反馈分析")
    print(f"  总反馈数: {len(critiques)}")
    
    # 按挑战者分组
    challenger_stats = {}
    for critique in critiques:
        name = critique.challenger_name
        if name not in challenger_stats:
            challenger_stats[name] = {
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "accept": 0,
                "reject": 0,
                "needs_review": 0,
            }
        
        challenger_stats[name]["total"] += 1
        if critique.is_valid:
            challenger_stats[name]["valid"] += 1
        else:
            challenger_stats[name]["invalid"] += 1
        
        rec = critique.recommendation.lower()
        if "accept" in rec:
            challenger_stats[name]["accept"] += 1
        elif "reject" in rec:
            challenger_stats[name]["reject"] += 1
        else:
            challenger_stats[name]["needs_review"] += 1
    
    for name, stats in challenger_stats.items():
        print(f"\n  {name.upper()}:")
        print(f"    总反馈数: {stats['total']}")
        print(f"    通过 (valid): {stats['valid']} ({stats['valid']/stats['total']*100:.1f}%)")
        print(f"    不通过 (invalid): {stats['invalid']} ({stats['invalid']/stats['total']*100:.1f}%)")
        print(f"    建议接受: {stats['accept']}")
        print(f"    建议拒绝: {stats['reject']}")
        print(f"    需要审查: {stats['needs_review']}")
    
    # 分析每轮修订的情况
    print()
    print("=" * 80)
    print("🔄 每轮修订分析")
    print("=" * 80)
    
    # 假设每轮有3个挑战者（A, B, C）
    rounds = len(critiques) // 3 if len(critiques) % 3 == 0 else (len(critiques) // 3) + 1
    
    for round_num in range(min(rounds, revision_count + 1)):
        round_critiques = critiques[round_num * 3:(round_num + 1) * 3]
        if not round_critiques:
            break
            
        print(f"\n修订轮次 {round_num}:")
        all_valid = all(c.is_valid for c in round_critiques)
        all_accept = all("accept" in c.recommendation.lower() for c in round_critiques)
        
        print(f"  状态: {'✅ 全部通过' if all_valid and all_accept else '❌ 需要修订'}")
        
        for critique in round_critiques:
            status = "✅" if critique.is_valid else "❌"
            print(f"    {status} {critique.challenger_name}: "
                  f"valid={critique.is_valid}, "
                  f"recommendation={critique.recommendation}, "
                  f"confidence={critique.confidence:.1%}")
            if critique.issues:
                print(f"      问题: {critique.issues[0][:60]}...")
    
    # 问题诊断
    print()
    print("=" * 80)
    print("🔍 问题诊断")
    print("=" * 80)
    
    if revision_count >= 3:
        print("⚠️  达到最大修订次数，系统强制结束")
        print()
        print("可能的原因:")
        print("  1. Challenger 标准过于严格")
        print("  2. Aggregator 在修订时没有真正改进评估")
        print("  3. 评估本身存在根本性问题（如连接错误）")
        print("  4. 需要调整 Challenger 的评判标准")
    else:
        print("✅ 系统在最大修订次数内完成")
    
    # 检查是否有持续不通过的模式
    if len(critiques) >= 6:
        recent_critiques = critiques[-6:]  # 最后两轮
        challenger_a_recent = [c for c in recent_critiques if c.challenger_name == "challenger_a"]
        challenger_c_recent = [c for c in recent_critiques if c.challenger_name == "challenger_c"]
        
        if challenger_a_recent and all(not c.is_valid for c in challenger_a_recent):
            print()
            print("⚠️  Challenger A 持续不通过，可能原因:")
            print("  - 逻辑检查标准过于严格")
            print("  - 评估质量确实存在问题")
        
        if challenger_c_recent and all(not c.is_valid for c in challenger_c_recent):
            print()
            print("⚠️  Challenger C 持续不通过，可能原因:")
            print("  - 合规性检查标准过于严格")
            print("  - 评估缺少必要的合规性信息")
    
    print()
    print("=" * 80)
    print("💡 优化建议")
    print("=" * 80)
    print()
    print("1. 如果 Challenger 持续不通过:")
    print("   - 检查 Aggregator 的修订提示词，确保它真正根据 critiques 改进")
    print("   - 考虑放宽 Challenger 的评判标准（降低 confidence 阈值）")
    print("   - 增加 'minor issues' 的容忍度")
    print()
    print("2. 如果达到最大修订次数:")
    print("   - 增加 MAX_REVISIONS（但会增加成本）")
    print("   - 改进 Aggregator 的修订策略")
    print("   - 在 Verifier 中添加 'graceful degradation' 逻辑")
    print()
    print("3. 成本优化:")
    print("   - 如果经常达到最大修订次数，考虑:")
    print("     * 提高初始评估质量（改进 Generator prompts）")
    print("     * 使用更智能的 Aggregator 修订策略")
    print("     * 允许 Verifier 在达到最大修订时接受 'good enough' 的评估")


if __name__ == "__main__":
    analyze_revision_pattern()

