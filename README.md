# My Claude Scholar

基于 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Agent Teams 的个人科研团队系统。

9 个专业 Agent 组成虚拟科研团队，覆盖从文献调研到论文投稿的完整学术研究生命周期。每个 Agent 拥有独立职责、专属知识库和持久化记忆，通过协作完成高质量科研产出。

## 特性

- **9 个专业 Agent**：文献侦察、代码架构、数据分析、论文写作、语言编辑、图表设计、引文核查、模拟审稿、投稿管理
- **30+ 斜杠命令**：覆盖研究全流程，从 `/research-init` 到 `/camera-ready`
- **15 套 Prompt 模板**：中英互译、润色、去 AI 味、实验分析、审稿视角等
- **5 大顶会审稿标准**：NeurIPS / ICML / ICLR / ACL / CVPR 评审 checklist
- **持久化记忆**：Agent 记忆跨会话保持，积累你的写作偏好和研究习惯
- **标准化实验模板**：Hydra 配置 + wandb 追踪 + Factory & Registry 模式
- **双包管理支持**：uv（推荐）/ conda（miniconda/miniforge，兼容老系统）
- **Zotero 深度集成**：语义搜索、全文读取、PDF 标注提取、笔记写入（54yyyu/zotero-mcp）
- **安全钩子**：自动拦截密钥泄漏、危险命令

## 前置要求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI（需要 Anthropic API 访问权限）
- Git
- Python >= 3.10
- 包管理器：[uv](https://docs.astral.sh/uv/)（推荐）或 [miniforge](https://github.com/conda-forge/miniforge) / [miniconda](https://docs.anaconda.com/miniconda/)
- [Zotero](https://www.zotero.org/) 账号 + API Key（可选，用于文献管理集成）

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Gdnaiteab/my-claude-scholar.git
cd my-claude-scholar
```

### 2. 启动 Claude Code

```bash
claude
```

Claude Code 会自动加载 `CLAUDE.md`、9 个 Agent、所有命令和规则。

### 3. 创建研究项目

```
/new-project transformer-interpretability --venue ICLR
```

这会从 `projects/_template/` 复制标准化项目结构，配置 wandb 和 git 分支。

### 4. 开始研究

```
/research-init        # 文献调研 + 研究构思
/plan                 # 制定实验计划
/tdd                  # 测试驱动开发
/analyze-results      # 分析实验结果
/write-section        # 撰写论文
/mock-review          # 模拟审稿
/submission-check     # 投稿前检查
```

## 使用模式

### 模式 A：单仓库多项目（推荐日常使用）

在 `projects/` 下管理多个研究，共享 Agent 记忆和知识库：

```
my-claude-scholar/
├── projects/
│   ├── transformer-interp/     # 研究 A
│   ├── llm-reasoning/          # 研究 B
│   └── graduation-thesis/      # 毕业论文
├── .claude/                    # 共享 agent + 命令
├── team/                       # 共享 agent 记忆
└── knowledge/                  # 共享知识库
```

### 模式 B：Clone 独立仓库（推荐重大研究）

```bash
git clone https://github.com/Gdnaiteab/my-claude-scholar.git my-iclr-paper
cd my-iclr-paper
git remote set-url origin https://github.com/yourname/my-iclr-paper.git
```

适用于需要完全隔离、针对性定制 Agent 的场景（如毕业论文的特殊格式要求）。

## 项目结构

```
my-claude-scholar/
├── .claude/
│   ├── agents/                 # 9 个 Agent 定义
│   │   ├── literature-scout.md
│   │   ├── code-architect.md
│   │   ├── data-analyst.md
│   │   ├── paper-writer.md
│   │   ├── language-editor.md
│   │   ├── figure-designer.md
│   │   ├── citation-checker.md
│   │   ├── mock-reviewer.md
│   │   └── submission-manager.md
│   ├── commands/               # 30+ 斜杠命令
│   └── rules/                  # 全局规则
│       ├── coding-style.md
│       ├── experiment-workflow.md
│       ├── experiment-reproducibility.md
│       ├── security.md
│       └── team-coordination.md
├── team/                       # Agent 运行时（记忆 + 知识库）
│   ├── {agent-name}/
│   │   ├── claude.md           # Agent 系统提示
│   │   ├── memory.md           # 持久化记忆
│   │   └── knowledge/          # 专属知识库
│   └── ...
├── knowledge/                  # 全局共享知识库
│   ├── conference-checklists/  # 顶会投稿 checklist
│   └── prompts/                # 15 套 Prompt 模板
├── hooks/                      # 自动化钩子（6 个）
├── projects/                   # 研究项目
│   └── _template/              # 项目模板
├── workspace/                  # 全局工作区
├── CLAUDE.md                   # 主配置文件
└── README.md
```

### 项目模板结构

每个研究项目（`projects/{name}/`）遵循标准结构：

```
projects/{name}/
├── run/
│   ├── conf/                   # Hydra 配置
│   │   ├── config.yaml         # 主配置（含 wandb）
│   │   ├── model/              # 模型配置组
│   │   ├── dataset/            # 数据集配置组
│   │   └── trainer/            # 训练器配置组
│   └── pipeline/
│       └── train.py            # 训练入口
├── src/                        # 源代码（Factory & Registry 模式）
│   ├── data_module/
│   ├── model_module/
│   ├── trainer_module/
│   └── utils/
├── data/                       # 数据
│   ├── raw/                    # 原始数据（gitignored）
│   └── processed/              # 处理后数据
├── outputs/                    # 实验输出
│   ├── experiments/            # Hydra 自动输出
│   ├── checkpoints/            # 模型检查点
│   ├── figures/                # 中间图表
│   └── tables/                 # 中间表格
├── paper/                      # 论文
│   ├── draft/                  # 草稿
│   ├── figures/                # 最终图表
│   ├── tables/                 # 最终表格
│   └── references.bib          # 参考文献
├── tests/                      # 测试
├── pyproject.toml              # uv 包管理
└── environment.yml             # conda 环境（备选）
```

## Agent 团队

```
                     ┌──────────────────┐
                     │   用户 (PI / 导师) │
                     └────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌────────▼────────┐  ┌───────▼───────┐  ┌────────▼────────┐
│ literature-scout │  │ code-architect│  │  data-analyst   │
│   文献侦察兵      │  │   代码架构师   │  │   数据分析师     │
└────────┬────────┘  └───────┬───────┘  └────────┬────────┘
         │                    │                    │
┌────────▼────────┐  ┌───────▼───────┐  ┌────────▼────────┐
│  paper-writer   │  │figure-designer│  │ language-editor  │
│    论文写手      │  │   图表设计师   │  │   语言编辑       │
└────────┬────────┘  └───────┬───────┘  └────────┬────────┘
         │                    │                    │
┌────────▼────────┐  ┌───────▼───────┐  ┌────────▼────────┐
│citation-checker │  │ mock-reviewer  │  │submission-mgr   │
│   引文核查员     │  │   模拟审稿人   │  │   投稿管理员     │
└─────────────────┘  └───────────────┘  └─────────────────┘
```

| Agent | 角色 | 核心职责 |
|-------|------|---------|
| **literature-scout** | 文献侦察兵 | 文献搜索、分类、趋势分析、Research Gap、Related Work 草稿 |
| **code-architect** | 代码架构师 | ML 项目架构、代码审查、TDD、Factory & Registry 模式 |
| **data-analyst** | 数据分析师 | 实验分析、统计检验、消融实验、数据可视化 |
| **paper-writer** | 论文写手 | 论文各 Section 写作、逻辑连贯性、学术表达 |
| **language-editor** | 语言编辑 | 英文润色、中英互译、去 AI 痕迹、学术用语规范 |
| **figure-designer** | 图表设计师 | 架构图、实验图表、matplotlib/TikZ、配色方案 |
| **citation-checker** | 引文核查员 | BibTeX 校验、引文信息核实、格式验证 |
| **mock-reviewer** | 模拟审稿人 | 按顶会标准模拟审稿、Weakness 分析、Rebuttal 建议 |
| **submission-manager** | 投稿管理员 | 投稿清单、格式合规、Camera-ready、Rebuttal 撰写 |

## 研究生命周期

```
构思 ──→ ML开发 ──→ 实验分析 ──→ 论文写作 ──→ 自审 ──→ 投稿/Rebuttal ──→ 录用后处理
 │         │          │           │          │          │                │
 scout   architect  analyst    writer    reviewer   submission-mgr   submission-mgr
```

| 阶段 | 核心命令 | 产出 |
|------|---------|------|
| 研究构思 | `/research-init` `/zotero-review` | 文献综述、Research Gap |
| ML 开发 | `/plan` `/tdd` `/code-review` | 代码框架、基线实现 |
| 实验分析 | `/analyze-results` `/plot-results` `/ablation` | 统计分析、图表 |
| 论文写作 | `/write-section` `/polish` `/de-ai` | 论文各章节 |
| 论文自审 | `/mock-review` `/check-citations` `/logic-check` | Review 报告 |
| 投稿 | `/submission-check` `/rebuttal` `/camera-ready` | 投稿包、Rebuttal |
| 录用后 | `/presentation` `/poster` `/promote` | 演讲、海报、推广 |

## 命令速查

### 文献与研究

| 命令 | 说明 |
|------|------|
| `/research-init` | 启动 Zotero 集成研究构思工作流 |
| `/zotero-review` | 从 Zotero 生成结构化文献综述 |
| `/zotero-notes` | 批量生成结构化阅读笔记 |
| `/new-project` | 从模板创建新研究项目 |

### 实验与分析

| 命令 | 说明 |
|------|------|
| `/analyze-results` | 实验结果分析（统计检验 + 可视化） |
| `/plot-results` | 生成实验图表 |
| `/ablation` | 消融实验设计与分析 |

### 论文写作

| 命令 | 说明 |
|------|------|
| `/write-section` | 撰写论文指定章节 |
| `/polish` | 英文表达润色 |
| `/de-ai` | 去除 AI 写作痕迹 |
| `/translate` | 中英互译 |
| `/logic-check` | 逻辑一致性检查 |
| `/figure-caption` | 生成图/表标题 |
| `/compress` | 文本压缩 |
| `/expand` | 文本扩展 |

### 审稿与投稿

| 命令 | 说明 |
|------|------|
| `/mock-review` | 模拟顶会审稿 |
| `/check-citations` | 引文验证 |
| `/rebuttal` | 生成 Rebuttal 文档 |
| `/submission-check` | 投稿前全面检查 |
| `/camera-ready` | Camera-ready 准备 |
| `/presentation` | 会议演讲大纲 |
| `/poster` | 学术海报方案 |

### 开发工作流

| 命令 | 说明 |
|------|------|
| `/plan` | 创建实施计划 |
| `/commit` | 提交代码（Conventional Commits） |
| `/code-review` | 代码审查 |
| `/tdd` | 测试驱动开发 |
| `/spawn-team` | 启动多 Agent 团队协作 |
| `/update-memory` | 更新 Agent 记忆 |

## 工具链

| 工具 | 用途 | 备注 |
|------|------|------|
| **uv** | Python 包管理 | 推荐，速度快 |
| **conda** | Python 包管理 | miniforge/miniconda，兼容老系统 |
| **Hydra** | 实验配置管理 | YAML 配置组合 + CLI 覆盖 |
| **wandb** | 实验追踪 | 自动记录指标、超参、系统信息 |
| **Git** | 版本控制 | Conventional Commits 规范 |
| **Zotero** | 文献管理 | [54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp)，语义搜索 + 全文 + 标注 |

## 自定义

### 调整 Agent 行为

编辑 `.claude/agents/{name}.md` 或 `team/{name}/claude.md` 修改 Agent 的系统提示、工作流程和质量标准。

### 添加新命令

在 `.claude/commands/` 下创建 `.md` 文件，遵循 frontmatter 格式：

```yaml
---
description: "命令描述"
arguments:
  - name: "arg1"
    description: "参数说明"
    required: true
---
```

### 添加知识库

- 顶会 checklist：`knowledge/conference-checklists/`
- Prompt 模板：`knowledge/prompts/`
- Agent 专属知识：`team/{name}/knowledge/`

### 适配毕业论文

Clone 为独立仓库后，修改以下内容：

1. `team/paper-writer/claude.md` — 调整章节结构（绪论、相关工作、方法、实验、总结）
2. `team/submission-manager/claude.md` — 调整格式要求（学校模板）
3. `knowledge/conference-checklists/` — 添加学校的论文格式规范

## 许可证

MIT

## 致谢

基于 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 的 Agent Teams 架构构建。
