# 修订通过情况分析

## 当前系统状态

### 修订逻辑
- **MAX_REVISIONS = 3** (最多允许3次修订)
- **revision_count 从 0 开始计数**
- 实际会运行 **4 轮** (0, 1, 2, 3)

### 通过条件
系统在以下情况会结束：
1. **所有 Challenger 都通过** (`is_valid=True` 且 `recommendation="accept"`)
2. **达到最大修订次数** (`revision_count >= MAX_REVISIONS`)

### 当前问题

从测试结果看，系统**确实会达到最大修订次数**，主要原因：

#### 1. Challenger A (逻辑检查) 持续不通过
- **问题**: 评估缺少 reasoning 或 arguments
- **原因**: 
  - Generator 生成失败（连接错误）
  - Aggregator 没有真正改进评估
  - Challenger A 标准过于严格

#### 2. Challenger C (合规检查) 持续不通过  
- **问题**: 缺少 ISO 标准引用、PSTI Act 合规信息
- **原因**:
  - 初始评估质量不足
  - Aggregator 修订时没有补充合规信息

#### 3. Challenger B (源验证) 通常通过
- **表现较好**: 大部分情况下能验证引用

## 风险分析

### ⚠️ 高风险：无法在三轮内完成

**问题根源**:
1. **Aggregator 修订策略不足**
   - 当前 Aggregator 只是重新合成，没有根据 critiques 主动改进
   - 缺少"根据 critiques 修订评估"的明确指令

2. **Challenger 标准可能过严**
   - Challenger A: 要求完整的 reasoning，但评估可能确实缺少
   - Challenger C: 要求所有合规标准，但初始评估可能不完整

3. **没有"graceful degradation"机制**
   - 达到最大修订次数后，系统强制结束
   - 没有"接受当前最佳评估"的选项

## 解决方案

### 方案 1: 改进 Aggregator 修订策略 (推荐)

修改 `AGGREGATOR_PROMPT`，在修订时明确要求根据 critiques 改进：

```python
AGGREGATOR_REVISION_PROMPT = """
You are revising a risk assessment based on critiques from three challenger agents.

Previous Assessment:
{previous_assessment}

Critiques from Challengers:
{critiques}

Your task:
1. Address ALL issues raised by the challengers
2. If Challenger A found missing reasoning, ADD detailed reasoning
3. If Challenger C found missing compliance info, ADD regulatory citations
4. If Challenger B found unverified citations, REMOVE or REPLACE them
5. Maintain consistency between score and reasoning

Provide the REVISED assessment in JSON format:
{{
    "score": <integer 1-5>,
    "reasoning": {{
        "summary": "<revised summary addressing critiques>",
        "key_arguments": ["<argument addressing issue 1>", ...],
        "regulatory_citations": ["<verified citations only>", ...],
        "vulnerabilities": ["<valid vulnerabilities>", ...]
    }}
}}
"""
```

### 方案 2: 放宽 Challenger 标准

修改 Challenger prompts，允许"minor issues"：

```python
# Challenger A: 允许缺少部分 reasoning，只要核心逻辑正确
"If the core logic is sound despite minor gaps, set is_valid=true"

# Challenger C: 允许缺少部分合规信息，只要主要合规点覆盖
"If major compliance requirements are addressed, set is_valid=true"
```

### 方案 3: 添加 Graceful Degradation

修改 `should_continue`，在达到最大修订次数时：
- 检查是否有"good enough"的评估（至少 2/3 Challenger 通过）
- 如果有，接受并结束
- 如果没有，返回当前最佳评估

### 方案 4: 增加 MAX_REVISIONS

简单但增加成本：
```python
MAX_REVISIONS: int = 5  # 从 3 增加到 5
```

## 成本影响

- **当前**: 约 ¥5.79/次（3轮修订）
- **如果增加到5轮**: 约 ¥7.79/次（+¥2.00）
- **如果改进修订策略**: 可能减少到 1-2 轮，约 ¥3.78-¥4.02/次

## 推荐行动

1. **立即实施**: 方案 1（改进 Aggregator 修订策略）
2. **短期优化**: 方案 3（添加 graceful degradation）
3. **长期优化**: 方案 2（调整 Challenger 标准，基于实际使用数据）

