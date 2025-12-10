"""
测量系统运行时间
Created: 2025-01-XX
"""

import time
from src.main import run_risk_assessment

def measure_execution_time():
    """测量一次完整评估的运行时间"""
    
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
    print("测量系统运行时间")
    print("=" * 80)
    print()
    print("开始运行评估...")
    print()
    
    start_time = time.time()
    
    try:
        result = run_risk_assessment(test_scenario)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time % 1) * 1000)
        
        print()
        print("=" * 80)
        print("⏱️  运行时间统计")
        print("=" * 80)
        print(f"总运行时间: {elapsed_time:.2f} 秒")
        print(f"            {minutes} 分 {seconds} 秒 {milliseconds} 毫秒")
        print()
        
        # 分析时间分布
        revision_count = result.get("revision_count", 0)
        total_critiques = len(result.get("critiques", []))
        
        print("📊 执行统计:")
        print(f"  修订轮次: {revision_count}")
        print(f"  总反馈数: {total_critiques}")
        print()
        
        # 估算各阶段时间（基于经验值）
        print("⏱️  时间分布估算:")
        print("  Generator Ensemble (9 models): ~60-90 秒")
        print("  Aggregator: ~10-15 秒")
        print("  Challengers (3 parallel): ~15-25 秒")
        print("  Verifier: ~5-10 秒")
        print(f"  每轮修订循环: ~30-50 秒")
        print()
        
        if revision_count > 0:
            avg_revision_time = elapsed_time / (revision_count + 1)  # +1 for initial cycle
            print(f"  平均每轮时间: ~{avg_revision_time:.1f} 秒")
        
        print()
        print("💡 优化建议:")
        if elapsed_time > 180:  # 超过3分钟
            print("  ⚠️  运行时间较长，考虑:")
            print("     - 减少 Generator 模型数量")
            print("     - 优化 API 调用（并行优化）")
            print("     - 使用更快的模型")
        elif elapsed_time > 120:  # 超过2分钟
            print("  ⚠️  运行时间适中，可以进一步优化")
        else:
            print("  ✅ 运行时间合理")
        
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\n❌ 运行出错 (已运行 {elapsed_time:.2f} 秒)")
        print(f"错误: {str(e)}")
        raise


if __name__ == "__main__":
    measure_execution_time()

