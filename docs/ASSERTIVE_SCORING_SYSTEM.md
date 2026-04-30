# Assertive Scoring System — Harness Engineering

> **核心理念**: 断言式评分体系 — 多维度、是非分明、客观评分，控制输出随机性，提高系统稳定性。
> 
> **负责人**: Snowdrop (首席评分官)

---

## 1. 问题陈述

### 当前 Harness 的局限性

```
现状: 单一通过/失败判定
  ┌─────────────┐
  │  Harness    │ → PASS / FAIL
  │  输出       │
  └─────────────┘
  
问题:
- 无法定位失败维度 (是质量差? 还是规范不符?)
- 审查维度重叠、冲突 (Satonus 和 Methode 标准不一致)
- 质量、审美、规范性难以量化 ("感觉不对" → 无法执行)
```

### 目标: 多维度确定性控制

```
目标: 多维度评分 → 加权聚合 → 确定性判定
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  多维度     │ → │  加权聚合   │ → │  确定性     │
  │  评分       │    │  算法       │    │  判定       │
  └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 2. 评分维度设计

### 2.1 通用维度集 (适用于代码任务)

| 维度 | 权重 | 评分标准 | 判定规则 |
|:---|:---:|:---|:---|
| **correctness** | 30% | 功能正确性 | PASS(100)/UNCERTAIN(50)/FAIL(0) |
| **quality** | 25% | 代码质量 (复杂度、可维护性) | A(100)/B(80)/C(60)/D(40)/F(0) |
| **aesthetics** | 15% | 审美/可读性 (命名、格式) | A(100)/B(80)/C(60)/D(40)/F(0) |
| **compliance** | 20% | 规范符合 (项目规则、标准) | PASS(100)/WARNING(50)/FAIL(0) |
| **overlap** | 10% | 重复度 (与现有代码重复) | 0%(100) → 100%(0) 线性递减 |

### 2.2 任务特定维度集

#### Blog 内容生成

| 维度 | 权重 | 评分标准 |
|:---|:---:|:---|
| accuracy | 25% | 事实准确性 |
| readability | 25% | 可读性 (Flesch-Kincaid) |
| engagement | 20% | 吸引力 (标题、开头) |
| seo | 15% | SEO 优化 |
| originality | 15% | 原创度 (查重) |

#### PR 审查

| 维度 | 权重 | 评分标准 |
|:---|:---:|:---|
| correctness | 35% | 功能正确性 |
| security | 25% | 安全性 |
| performance | 20% | 性能影响 |
| compatibility | 20% | 兼容性 |

---

## 3. 评分算法

### 3.1 基础公式

```python
def calculate_score(dimensions: dict, weights: dict) -> dict:
    """
    计算加权总分
    
    dimensions: {维度名: 原始分 (0-100)}
    weights: {维度名: 权重 (0-1)}
    """
    total_weight = sum(weights.values())
    normalized_weights = {k: v/total_weight for k, v in weights.items()}
    
    weighted_scores = {
        dim: score * normalized_weights[dim] 
        for dim, score in dimensions.items()
    }
    
    total_score = sum(weighted_scores.values())
    
    return {
        "total": total_score,
        "breakdown": weighted_scores,
        "dimensions": dimensions,
        "verdict": _verdict(total_score)
    }

def _verdict(score: float) -> str:
    if score >= 80: return "PASS"
    if score >= 60: return "HOLD"
    return "REJECT"
```

### 3.2 对抗性验证

```python
def adversarial_check(scores: dict, threshold: float = 0.3) -> list:
    """
    检测维度冲突和异常
    
    返回需要人工复核的维度对
    """
    anomalies = []
    
    # 检测极端差异
    for dim1, score1 in scores.items():
        for dim2, score2 in scores.items():
            if dim1 >= dim2:
                continue
            diff = abs(score1 - score2)
            if diff > threshold * 100:  # 差异 > 30%
                anomalies.append({
                    "type": "extreme_variance",
                    "dimensions": [dim1, dim2],
                    "scores": [score1, score2],
                    "diff": diff
                })
    
    # 检测重叠 (由专门工具计算)
    overlap_score = calculate_overlap()
    if overlap_score > 50:  # 重复度 > 50%
        anomalies.append({
            "type": "high_overlap",
            "score": overlap_score
        })
    
    return anomalies
```

---

## 4. Snowdrop 角色: 首席评分官

### 4.1 职责

```
Snowdrop (首席评分官)
├── 1. 设计评分维度
│   └── 根据任务类型选择/定义维度集
├── 2. 执行多维度审查
│   └── 对每个维度给出客观评分 (A/B/C/D/F 或 PASS/WARNING/FAIL)
├── 3. 对抗性验证
│   ├── 重叠检测 (与现有代码/内容比较)
│   ├── 冲突识别 (维度间矛盾)
│   └── 异常标记 (需要人工复核)
├── 4. 评分校准
│   ├── 收集历史评分数据
│   ├── 分析评分与实际效果的相关性
│   └── 优化维度权重
└── 5. 评分报告生成
    └── 结构化输出: 总分 + 维度分解 + 改进建议
```

### 4.2 评分流程

```
输入: Harness 输出 (代码/内容/PR)
    │
    ▼
┌─────────────────┐
│ 1. 维度选择     │ ← Snowdrop 根据任务类型选择维度集
│ (Dimension      │
│  Selection)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 多维度评分   │ ← 每个维度独立评分
│ (Multi-Dim      │
│  Scoring)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 对抗性验证   │ ← 重叠检测、冲突识别
│ (Adversarial    │
│  Validation)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 加权聚合     │ ← 计算总分
│ (Weighted       │
│  Aggregation)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. 判定输出     │ ← PASS / HOLD / REJECT
│ (Verdict)       │
└────────┬────────┘
         │
         ▼
输出: 评分报告
  {
    "total": 82.5,
    "verdict": "PASS",
    "breakdown": {
      "correctness": 30.0,
      "quality": 20.0,
      "aesthetics": 12.0,
      "compliance": 18.0,
      "overlap": 2.5
    },
    "anomalies": [],
    "suggestions": ["reduce duplication in utils.py"]
  }
```

---

## 5. 审查对抗机制

### 5.1 对抗流程

```
Satonus (审查员)          Snowdrop (评分官)          Methode (执行员)
     │                          │                          │
     │ 1. 提出异议               │                          │
     │ "这段代码有安全问题"       │                          │
     │─────────────────────────>│                          │
     │                          │                          │
     │                          │ 2. 多维度量化             │
     │                          │ security: FAIL(0)         │
     │                          │ correctness: PASS(100)    │
     │                          │ quality: B(80)            │
     │                          │                           │
     │                          │ 3. 总分计算               │
     │                          │ 0×0.25 + 100×0.30 + 80×0.25 = 55
     │                          │ → REJECT                  │
     │<─────────────────────────│                          │
     │                          │                          │
     │ 4. 要求修复               │                          │
     │─────────────────────────────────────────────────────>│
     │                          │                          │
     │                          │                          │ 5. 根据评分修复
     │                          │                          │ (重点修复 security)
     │                          │                          │
     │                          │                          │ 6. 提交修复
     │<─────────────────────────────────────────────────────│
     │                          │                          │
     │ 7. 再审                   │                          │
     │─────────────────────────>│                          │
     │                          │ 8. 终评                  │
     │                          │ security: PASS(100)       │
     │                          │ 总分: 92.5 → PASS         │
     │<─────────────────────────│                          │
     │                          │                          │
     │ 9. 归档评分               │                          │
     │ (用于权重校准)             │                          │
```

### 5.2 冲突解决

当维度间出现冲突时:

```
场景: correctness = PASS(100), compliance = FAIL(0)
      (代码功能正确，但不符合项目规范)

Snowdrop 决策:
1. 检查规范重要性
   - 如果是安全规范 → compliance 权重临时提升到 40%
   - 如果是风格规范 → 建议 WARNING 而非 FAIL
   
2. 生成折中方案
   "功能正确，但需调整命名规范。
   建议: 先合并，后续 refactor PR 修复风格。"
   
3. 记录冲突模式
   用于后续权重优化
```

---

## 6. 权重自动校准

### 6.1 数据收集

```python
# 每次评分后记录
calibration_log = {
    "task_id": "uuid",
    "task_type": "code_review",
    "dimensions": {...},
    "total_score": 82.5,
    "verdict": "PASS",
    "actual_outcome": "success",  # 后续跟踪实际效果
    "time_to_fix": "2h",          # 发现问题到修复的时间
    "reopen_count": 0             # 问题重新打开次数
}
```

### 6.2 权重优化

```python
def optimize_weights(history: list, target_metric: str = "min_reopen"):
    """
    基于历史数据优化权重
    
    target_metric: "min_reopen" | "min_time_to_fix" | "max_pass_accuracy"
    """
    # 使用网格搜索或贝叶斯优化
    best_weights = None
    best_score = float('-inf')
    
    for weights in generate_weight_combinations():
        score = evaluate_weights(history, weights, target_metric)
        if score > best_score:
            best_score = score
            best_weights = weights
    
    return best_weights
```

---

## 7. 集成到 GSD

### 7.1 新 GSD 命令

```markdown
## /gsd-score — 多维度评分

Usage: /gsd-score <artifact> --dimensions <dim_set>

Example:
/gsd-score pr-123.diff --dimensions code_review

Output:
```json
{
  "total": 82.5,
  "verdict": "PASS",
  "breakdown": {
    "correctness": {"score": 100, "weighted": 30.0, "comment": "功能正确"},
    "quality": {"score": 80, "weighted": 20.0, "comment": "复杂度略高"},
    "aesthetics": {"score": 80, "weighted": 12.0, "comment": "命名规范"},
    "compliance": {"score": 100, "weighted": 20.0, "comment": "符合规范"},
    "overlap": {"score": 25, "weighted": 2.5, "comment": "与 utils.py 有重复"}
  },
  "anomalies": [
    {"type": "high_overlap", "score": 75, "suggestion": "extract common logic"}
  ],
  "suggestions": ["reduce duplication in utils.py"]
}
```
```

### 7.2 集成到现有流程

```
现有: /gsd-verify-work → PASS/FAIL
新增: /gsd-score → 多维度评分报告

组合使用:
1. /gsd-execute-phase (Methode 执行)
2. /gsd-score (Snowdrop 评分)
3. /gsd-verify-work (Satonus 验证评分结果)
4. /gsd-ship (Kouka 交付，基于评分 ≥80)
```

---

## 8. 实施路线图

| 阶段 | 任务 | 负责 | 时间 |
|:---|:---|:---|:---:|
| 1 | 设计通用维度集 | Snowdrop | 1d |
| 2 | 实现评分算法 | Methode | 2d |
| 3 | 集成到 GSD (/gsd-score) | Satonus | 2d |
| 4 | 收集历史数据 | Lacia | 持续 |
| 5 | 权重校准系统 | Snowdrop | 1w |
| 6 | 任务特定维度集 | Snowdrop | 2d |
| 7 | 全链路集成测试 | All | 2d |

---

## 9. 参考

- `archived/Contexture与Harness Engineering调研.md` §多模态控制
- `archived/Regulations.md` §审查规范
- `research/get-shit-done/commands/gsd/verify-work.md`

---

*Assertive Scoring System — Harness Engineering V7.1*
*Designed by Snowdrop | Multi-dimensional | Objective | Deterministic*
