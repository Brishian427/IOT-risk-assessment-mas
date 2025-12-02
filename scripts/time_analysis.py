"""
基于历史测试数据估算运行时间
Created: 2025-01-XX
"""

def analyze_time_from_history():
    """基于之前的测试输出分析运行时间"""
    
    print("=" * 80)
    print("⏱️  系统运行时间分析（基于历史测试数据）")
    print("=" * 80)
    print()
    
    # 基于之前的测试输出估算
    print("📊 各阶段时间估算:")
    print()
    
    print("1. Generator Ensemble (9 models 并行)")
    print("   - 最快模型: ~3-5 秒 (gpt-4o-mini, llama)")
    print("   - 中等模型: ~5-10 秒 (gpt-4o, claude)")
    print("   - 慢速模型: ~15-60 秒 (gemini, deepseek)")
    print("   - 总时间: ~60-120 秒 (取决于最慢的模型)")
    print()
    
    print("2. Aggregator (合成)")
    print("   - 格式化: ~1-2 秒")
    print("   - LLM 调用: ~10-20 秒")
    print("   - 总时间: ~12-22 秒")
    print()
    
    print("3. Challengers (3个并行)")
    print("   - Challenger A (逻辑): ~5-10 秒")
    print("   - Challenger B (源验证): ~15-30 秒 (包含搜索)")
    print("   - Challenger C (合规): ~5-10 秒")
    print("   - 总时间: ~15-30 秒 (并行执行，取最长)")
    print()
    
    print("4. Verifier (路由决策)")
    print("   - LLM 调用: ~5-10 秒")
    print("   - 总时间: ~5-10 秒")
    print()
    
    print("=" * 80)
    print("📈 完整流程时间估算")
    print("=" * 80)
    print()
    
    # 初始循环
    initial_cycle = {
        "name": "初始循环",
        "generator": (60, 120),
        "aggregator": (12, 22),
        "challengers": (15, 30),
        "verifier": (5, 10)
    }
    
    # 修订循环（不包含 generator）
    revision_cycle = {
        "name": "修订循环",
        "aggregator": (12, 22),
        "challengers": (15, 30),
        "verifier": (5, 10)
    }
    
    def calc_cycle_time(cycle):
        total_min = sum(t[0] for k, t in cycle.items() if k != "name")
        total_max = sum(t[1] for k, t in cycle.items() if k != "name")
        return total_min, total_max
    
    initial_min, initial_max = calc_cycle_time(initial_cycle)
    revision_min, revision_max = calc_cycle_time(revision_cycle)
    
    print(f"{initial_cycle['name']}:")
    print(f"  最短: {initial_min} 秒 (~{initial_min//60} 分 {initial_min%60} 秒)")
    print(f"  最长: {initial_max} 秒 (~{initial_max//60} 分 {initial_max%60} 秒)")
    print()
    
    print(f"{revision_cycle['name']} (每轮):")
    print(f"  最短: {revision_min} 秒")
    print(f"  最长: {revision_max} 秒")
    print()
    
    # 不同修订轮次的总时间
    print("=" * 80)
    print("🎯 不同场景的总运行时间")
    print("=" * 80)
    print()
    
    scenarios = [
        ("无修订 (一次通过)", 0),
        ("1轮修订", 1),
        ("2轮修订", 2),
        ("3轮修订 (最大)", 3),
    ]
    
    for scenario_name, revisions in scenarios:
        total_min = initial_min + (revision_min * revisions)
        total_max = initial_max + (revision_max * revisions)
        avg = (total_min + total_max) / 2
        
        print(f"{scenario_name}:")
        print(f"  最短: {total_min} 秒 (~{total_min//60} 分 {total_min%60} 秒)")
        print(f"  平均: {avg:.0f} 秒 (~{avg//60:.1f} 分钟)")
        print(f"  最长: {total_max} 秒 (~{total_max//60} 分 {total_max%60} 秒)")
        print()
    
    print("=" * 80)
    print("💡 关键发现")
    print("=" * 80)
    print()
    print("1. 主要时间消耗:")
    print("   - Generator Ensemble: 60-120 秒 (一次性，最长)")
    print("   - 每轮修订: 30-60 秒")
    print()
    print("2. 典型运行时间:")
    print("   - 一次通过: ~2-3 分钟")
    print("   - 3轮修订: ~3-5 分钟")
    print()
    print("3. 时间优化建议:")
    print("   - Generator 并行已优化，但受最慢模型限制")
    print("   - 可以考虑移除最慢的模型 (如 gemini)")
    print("   - 或者使用更快的模型替代")
    print()
    print("4. 实际测试观察:")
    print("   - 从之前的测试看，完整运行约 2-4 分钟")
    print("   - 取决于 API 响应速度和网络状况")
    print("   - Gemini 模型重试会增加时间")


if __name__ == "__main__":
    analyze_time_from_history()

