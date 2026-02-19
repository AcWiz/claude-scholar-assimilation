# Team Coordination Rules

研究团队 9 个 agent 的协调规则，确保高效协作。

## 任务委派规则

### 何时委派给哪个 agent

| 任务类型 | 主 agent | 协作 agent |
|----------|----------|------------|
| 文献搜索与综述 | literature-scout | citation-checker |
| 研究空白分析 | literature-scout | paper-writer |
| 代码架构设计 | code-architect | data-analyst |
| 模型实现 | code-architect | - |
| 实验运行 | code-architect | data-analyst |
| 统计分析 | data-analyst | mock-reviewer |
| 图表绘制 | figure-designer | data-analyst |
| 论文写作 | paper-writer | literature-scout, data-analyst |
| 语言润色 | language-editor | paper-writer |
| 去 AI 化检查 | language-editor | - |
| 中英翻译 | language-editor | - |
| 引用验证 | citation-checker | literature-scout |
| 模拟审稿 | mock-reviewer | data-analyst, literature-scout |
| 投稿准备 | submission-manager | 全体 |
| Rebuttal 撰写 | submission-manager | paper-writer, data-analyst |
| 录用后推广 | submission-manager | figure-designer |

## 并行执行规则

### 可以并行执行的任务组
1. **文献搜索** + **代码架构设计**（研究早期）
2. **统计分析** + **图表绘制**（实验完成后）
3. **语言润色** + **引用验证**（论文初稿完成后）
4. **模拟审稿** + **格式检查**（投稿前）

### 必须串行执行的任务
1. 文献搜索 -> 论文写作（Related Work 依赖文献调研）
2. 实验运行 -> 统计分析 -> 图表绘制 -> 论文写作（Results 依赖数据）
3. 论文写作 -> 语言润色 -> 模拟审稿 -> 投稿准备（依次推进）
4. 审稿意见 -> Rebuttal 策略 -> 补充实验/修改论文（Rebuttal 流程）

## 记忆更新协议

### 每个 agent 的 memory.md 更新时机
- **会话开始**：读取 `team/{name}/memory.md`
- **会话结束**：更新 `team/{name}/memory.md`
- **重大决策**：立即记录到 memory.md

### memory.md 内容规范
```markdown
## 最近工作记录
- [日期] [任务描述] [结果摘要]

## 积累的经验
- [经验描述]

## 待跟进事项
- [ ] [事项描述] [优先级] [截止日期]
```

### 跨 agent 信息传递
- 不直接修改其他 agent 的 memory.md
- 通过 workspace/ 目录下的共享文件传递数据
- 使用 workspace/plan/ 存放协作计划

## 工作区使用规范

### 目录用途
- `workspace/temp/` - 临时文件，任务完成后清理
- `workspace/logs/` - 工作日志，长期保留
- `workspace/plan/` - 协作计划和任务分解

### 文件命名规范
- 共享数据：`{source-agent}_{content}_{date}.{ext}`
- 例如：`data-analyst_ablation-results_20260219.csv`
- 计划文件：`plan_{project}_{date}.md`

## Agent 通信协议

### 请求格式
当一个 agent 需要另一个 agent 的协助时：
1. 在 workspace/plan/ 中创建任务描述文件
2. 明确说明：输入数据、期望输出、截止时间
3. 标注优先级：紧急 / 正常 / 低优先级

### 交付格式
完成任务后：
1. 将结果文件放在约定的输出目录
2. 更新自己的 memory.md
3. 在结果文件中附带质量自检说明

### 冲突解决
- 技术决策冲突：以 code-architect 意见为主
- 写作风格冲突：以 paper-writer 意见为主
- 统计方法冲突：以 data-analyst 意见为主
- 投稿策略冲突：以 submission-manager 意见为主
- 最终决策权：用户（Product Owner）
