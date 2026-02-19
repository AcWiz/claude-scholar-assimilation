# 写作技巧与句式模板

> 来源：claude-scholar ml-paper-writing 知识库

## 过渡短语

### 文献综述过渡
- 引出问题："However, these methods suffer from [limitation]."
- 呈现解决方案："To address this, we propose..."
- 连接相关工作："Building on [prior work], we extend..."

### 方法部分过渡
- 描述组件："Our model consists of two main components: [A] and [B]."
- 解释理由："We choose this architecture because..."
- 设计动机："Motivated by [intuition], we design..."

### 结果部分过渡
- 呈现发现："Our method achieves [result], outperforming baselines by [margin]."
- 分析结果："These results suggest that [insight]."
- 关注亮点："Notably, we observe that..."

### 讨论过渡
- 解释发现："These findings reveal that..."
- 连接更广泛上下文："Beyond the specific task, our results imply..."
- 承认限制："It is important to note that our study is limited to..."

## 句式模板

### 声明表达
- 强声明："We show that [approach] achieves [result]."
- 温和声明："Our results suggest that [factor] contributes to..."
- 观察声明："We observe that [phenomenon] emerges when..."

### 技术描述
- 算法描述："Formally, we optimize [objective] using [method]."
- 实现细节："In practice, we implement [feature] as..."
- 效率近似："For computational efficiency, we approximate..."

### 结果呈现
- 定量结果："Our model achieves [score] (+-[std]), improving over..."
- 统计报告："Results are averaged over N runs with different seeds."
- 显著性："The improvement is statistically significant (p<0.01)."

## 清晰性技巧

### 主动语态优先
- 避免："The model was trained using..."
- 推荐："We trained the model using..."

### 精确而非模糊
- 避免："This approach improves performance."
- 推荐："This approach improves accuracy by 15%."

### 路标指引（Signposting）
- 章节开头："We now describe our model architecture."
- 内部结构："First, we [action]. Next, we [action]. Finally, we [action]."
- 列举："Our approach has three stages: [A], [B], and [C]."

## 常用短语模板

### 摘要开头
- 推荐："We introduce [method], a novel approach for [task]."
- 推荐："We propose [framework] to address [challenge]."
- 避免："In this paper, we study..." (太泛)

### 引入相关工作
- "Recent work has shown promise in [area] [refs]."
- "Several approaches have been proposed for [task] [refs]."

### 描述实验
- "We evaluate on [datasets], comparing against [baselines]."
- "We conduct ablation studies to validate [component]."

### 呈现结果
- "Table 1 shows that our method outperforms all baselines."
- "Our method achieves state-of-the-art on [task/metric]."

### 讨论限制
- "Our approach has limitations: [constraint]."
- "A key limitation is [issue], which we leave for future work."

## 何凯明风格关键词

### 自然性关键词
- "naturally leads to...", "intrinsic relation", "well-defined problem"
- "principled basis", "from first principles", "solely originated from"

### 独立性关键词
- "does not depend on", "independent of", "self-contained"
- "from scratch", "without any X"

### 差异化关键词
- "in contrast to", "unlike", "prior works typically rely on"

### 设计简化关键词
- "minimal adaptations", "sufficient" (not "optimal")
- "simple", "plain", "decouple"

### 谨慎声明关键词
- "under some circumstances", "can compete with"
- "more prominent for", "is sufficient"

## 写作原则

1. **清晰优先**：让审稿人容易理解你的贡献
2. **严谨呈现**：提供足够的细节以供复现
3. **讲故事**：问题 -> 方法 -> 解决方案 -> 影响
4. **诚实**：明确承认限制，不过度声称
