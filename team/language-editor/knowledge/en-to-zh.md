# 英转中翻译参考

> 来源：awesome-ai-research-writing prompt 02

## 核心规则

### 1. 语法清洗
- **忽略引用与标签**：直接删除所有 `\cite{...}`、`\ref{...}`、`\label{...}`
- **提取格式内容**：`\textbf{text}` -> 仅翻译 text 内容
- **数学公式转化**：`$\alpha$` -> alpha，`\frac{a}{b}` -> a/b

### 2. 翻译原则
- **严格对应原文**：直译，不润色、不重写、不逻辑优化
- **保持句式结构**：中文语序尽量与英文原句一致
- **如实反映**：原文有语法错误或表达生硬，翻译中如实体现，不自动纠正
- **不增减词汇**：不为通顺而随意添加或删除

### 3. 输出格式
- 只输出翻译后的纯中文文本段落
- 不包含任何 LaTeX 代码

## 翻译注意事项

### 术语处理
- 常见 ML/AI 术语保持英文：Transformer, attention, embedding, loss, epoch
- 首次出现可添加中文注释：self-attention（自注意力）
- 后续使用英文原文

### 数学符号处理
| LaTeX | 中文 |
|-------|------|
| `$x \in \mathbb{R}^n$` | x 属于 n 维实数空间 |
| `$\sum_{i=1}^{N}$` | 对 i 从 1 到 N 求和 |
| `$\arg\min$` | 取使...最小化的值 |
| `$\mathcal{L}$` | 损失函数 L |
| `$\nabla$` | 梯度 |

### 句式对应
- "We propose X that..." -> "我们提出了 X，它..."
- "As shown in Table 1" -> "如表 1 所示"
- "Our method achieves..." -> "我们的方法达到了..."
- "Compared to [baseline]" -> "与 [baseline] 相比"
