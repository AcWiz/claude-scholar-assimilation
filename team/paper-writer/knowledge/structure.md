# 论文结构模式

> 来源：claude-scholar ml-paper-writing 知识库

## Introduction 模式

### Contribution Statement 结构
1. 从更广泛的背景或问题开始
2. 缩小到具体的局限性
3. 将你的方法呈现为解决方案
4. 清晰陈述贡献

```
[Context]: Existing approaches struggle with [limitation] due to [reason].
[Our Approach]: We propose [method], which [key innovation].
[Contribution]: This achieves [result] and enables [capability].
```

### 贡献列表模式
- 放在 Introduction 末尾
- 使用 2-4 个 bullet points
- 每条 1-2 行（双栏格式）
- 使用强动词开头（We propose / demonstrate / show）

```
Our contributions are three-fold:
- We propose [method], which achieves [result].
- We demonstrate that [technique] improves [metric].
- We show that [approach] enables [new capability].
```

### Related Work 组织
- 按方法论组织，非时间顺序
- 按方法/假设分组
- 与每组对比你的方法
- "One line of work uses X whereas we use Y because..."

## Methods 模式

### 算法呈现
1. 高层概述
2. 数学公式
3. 算法伪代码（复杂时）
4. 实现细节

### 组件分解
- 先呈现模型架构
- 分解为关键组件
- 解释每个组件的角色
- 展示组件如何交互

## Results 模式

### 定量开头
- 以最强结果开头
- 使用精确数字和指标
- 包含与 baseline 的对比
- 陈述统计显著性

```
Our method achieves [score] on [dataset], improving over the previous
best of [baseline] by [margin] (p<0.001).
```

### Table 集成
- 加粗每列最佳结果
- 包含方向指示器（上下箭头）
- 提供独立完整的 table caption
- 正文中先引用再呈现

## Discussion 模式

### 限制先行
- 第一段清晰陈述限制
- 解释为何限制不削弱核心声明
- 区分限制和未来工作

### Broader Impact
- 从直接影响开始
- 扩展到相关领域
- 考虑社会影响
- 以前瞻性声明结尾

## 过渡模式

- Introduction -> Methods: "We now describe our approach."
- Methods -> Results: "We evaluate our method on [tasks]."
- Results -> Discussion: "These results suggest that [insight]."

## 何凯明风格

### 摘要模式
- 模式 1: 直接陈述贡献 "We introduce [method], a [feature] framework..."
- 模式 2: 问题-解决方案 "[Problem] is difficult. We present [solution]..."

### 三段式引言
1. 问题陈述 (2-3 段)
2. 方法概述 (1-2 段)
3. 主要贡献 (1 段列表)

### "Surprisingly" 三层递进
- Level 1: "Surprisingly, we observe: (i)... and (ii)..."
- Level 2: "More surprisingly, our [method] can compete with..."
- Level 3: "With [condition], our [method] can outperform..."

### 消融写作
- 增量式：baseline -> (a) -> (b) -> (c) ours
- 破坏性："We conduct a destructive comparison..."
- 叙事："We observe... This is consistent with..."
