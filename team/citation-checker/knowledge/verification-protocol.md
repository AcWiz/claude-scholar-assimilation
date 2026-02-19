# 多层引用验证协议

> 来源：claude-scholar citation-verification 知识库

## 四层验证架构

```
Layer 1: Format Validation (格式验证)
  -> Layer 2: Existence Verification (存在性验证)
    -> Layer 3: Information Matching (信息匹配)
      -> Layer 4: Content Validation (内容验证)
```

## Layer 1: 格式验证

### BibTeX 必填字段

| 类型 | 必填字段 | 可选字段 |
|------|----------|----------|
| @article | author, title, journal, year | volume, number, pages, doi |
| @inproceedings | author, title, booktitle, year | pages, organization, doi |
| @book | author/editor, title, publisher, year | volume, series, address |
| @misc | title | author, howpublished, year, note |

### 字段格式检查
- **年份**：4 位数字，范围 1900-2030
- **DOI**：以 `10.` 开头，包含 `/` 分隔符
- **条目结构**：必须有 ENTRYTYPE 和 ID

### LaTeX 引用一致性检查
- 解析 `.tex` 文件中所有 `\cite{}` 命令
- 解析 `.bib` 文件中所有条目 key
- 交叉对比：
  - **未定义引用**：tex 中引用但 bib 中不存在
  - **未使用引用**：bib 中存在但 tex 中未引用

## Layer 2: 存在性验证

### API 验证优先级
1. **DOI** -> CrossRef API
2. **arXiv ID** -> arXiv API
3. **标题** -> Semantic Scholar API

### 验证结果
- `exists` - 论文存在
- `not_found` - 论文不存在
- `api_error` - API 调用失败，需人工验证

## Layer 3: 信息匹配

### 标题匹配
- 标准化：小写、去除标点
- 模糊匹配算法：SequenceMatcher
- 相似度阈值：0.85

### 作者匹配
- 处理 "Last, First" 和 "First Last" 格式差异
- 计算交集比例（Jaccard 相似度）
- 相似度阈值：0.70

### 年份匹配
- 允许 +-1 年容差
- 原因：预印本和正式发表的时间差

### 期刊/会议匹配
- 考虑缩写和全称的差异
- 如 "NeurIPS" vs "Advances in Neural Information Processing Systems"

## Layer 4: 内容验证

### 综合匹配评分

| 维度 | 权重 |
|------|------|
| 标题 | 0.4 |
| 作者 | 0.3 |
| 年份 | 0.2 |
| 期刊 | 0.1 |

### 置信度分级

| 分数范围 | 置信度 | 状态 | 含义 |
|----------|--------|------|------|
| >= 0.9 | 高 | verified | 信息完全匹配 |
| >= 0.7 | 中 | partial_match | 信息有轻微差异，建议人工确认 |
| >= 0.5 | 低 | low_match | 信息差异较大，需要人工验证 |
| < 0.5 | 无 | failed | 信息严重不匹配或论文不存在 |

## 阈值配置

### 严格模式（正式投稿）
- title_similarity: 0.90
- author_similarity: 0.80
- high_confidence: 0.95

### 宽松模式（初稿）
- title_similarity: 0.80
- author_similarity: 0.60
- high_confidence: 0.85

## 完整验证流程

```
输入：.bib 和 .tex 文件

1. 解析 BibTeX 文件，提取所有条目
2. 对每个条目执行 Layer 1 格式验证
3. 通过 Layer 2 API 验证存在性
4. 如果存在，执行 Layer 3 信息匹配
5. 计算 Layer 4 综合匹配分数
6. 判定验证结果
7. 生成验证报告

输出：每条引用的验证状态、置信度、问题描述、修复建议
```

## 验证报告模板

```
## 引用验证报告

### 统计摘要
- 总引用数：N
- 验证通过：X (Y%)
- 部分匹配：A (B%)
- 需人工验证：C (D%)
- 验证失败：E (F%)

### 问题引用
[citation_key]: [问题描述] -> [修复建议]

### LaTeX 一致性
- 未定义引用：[列表]
- 未使用引用：[列表]
```
