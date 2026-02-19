# My Claude Scholar 配置

## 项目概述

**My Claude Scholar** - 基于 Claude Code Agent Teams 的个人科研团队系统

**Mission**: 用 9 个专业 Agent 组成虚拟科研团队，覆盖从文献调研到论文投稿的完整学术研究生命周期。每个 Agent 拥有独立职责、专属知识库和持久化记忆，通过协作完成高质量科研产出。

**架构**: Claude Code Agent Teams（多 Agent 协作，非单体 Agent）

---

## 用户背景

### 学术背景
- **学历**: 计算机科学 PhD
- **研究方向**: AI/ML + NLP + CV
- **投稿目标**:
  - ML 顶会: NeurIPS, ICML, ICLR
  - NLP 顶会: ACL, EMNLP, NAACL
  - CV 顶会: CVPR, ICCV, ECCV
- **写作工具**: LaTeX + Overleaf + Word
- **关注点**: 学术写作质量、逻辑连贯性、自然表达、去 AI 痕迹

### 技术栈偏好

**Python 生态**:
- **包管理**: `uv`（推荐）/ `conda`（miniconda/miniforge，兼容老系统）
- **配置管理**: Hydra + OmegaConf（配置组合、覆盖、类型安全）
- **模型训练**: Transformers Trainer / PyTorch Lightning
- **数据处理**: pandas, numpy, scipy
- **可视化**: matplotlib, seaborn, plotly

**Git 规范**:
- **提交规范**: Conventional Commits
  ```
  Type: feat, fix, docs, style, refactor, perf, test, chore
  Scope: data, model, config, trainer, utils, paper, experiment
  ```
- **分支策略**: master / develop / feature / bugfix / hotfix / release
- **合并策略**: 功能分支用 rebase 同步，用 merge --no-ff 合并

---

## 团队架构（9 Agents）

```
                        ┌─────────────────────┐
                        │    用户 (PI / 导师)    │
                        └──────────┬──────────┘
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

### Agent 职责说明

| Agent | 角色 | 核心职责 |
|-------|------|---------|
| **literature-scout** | 文献侦察兵 | 文献搜索、分类、趋势分析、Related Work 草稿、Zotero MCP 集成 |
| **code-architect** | 代码架构师 | ML 项目架构设计、代码审查、重构、TDD、Factory & Registry 模式 |
| **data-analyst** | 数据分析师 | 实验结果分析、统计检验、消融实验、数据可视化、表格生成 |
| **paper-writer** | 论文写手 | 论文各 Section 写作、逻辑连贯性、学术表达、去 AI 痕迹 |
| **language-editor** | 语言编辑 | 英文润色、中英互译、语法检查、学术用语规范、表达优化 |
| **figure-designer** | 图表设计师 | 架构图、实验图表、matplotlib/TikZ、配色方案、Figure caption |
| **citation-checker** | 引文核查员 | 引文格式验证、BibTeX 校验、引文信息核实、重复检测 |
| **mock-reviewer** | 模拟审稿人 | 按顶会标准模拟审稿、生成 Review 报告、Weakness 分析、Rebuttal 建议 |
| **submission-manager** | 投稿管理员 | 投稿清单检查、格式合规、补充材料整理、Camera-ready 准备 |

### Agent 持久化记忆

每个 Agent 在 `team/{name}/memory.md` 维护持久化记忆：
- 每次会话结束后自动更新
- 记录已完成任务、学到的偏好、待跟进事项
- 下次启动时自动加载，保持上下文连续性

---

## 研究生命周期（7 阶段）

```
构思 → ML开发 → 实验分析 → 论文写作 → 自审 → 投稿/Rebuttal → 录用后处理
```

| 阶段 | 核心 Agent | 辅助 Agent | 产出 |
|------|-----------|-----------|------|
| 1. 研究构思 | literature-scout | - | 文献综述、Research Gap、研究问题 |
| 2. ML 项目开发 | code-architect | data-analyst | 代码框架、训练流程、基线实现 |
| 3. 实验分析 | data-analyst | figure-designer | 实验结果、统计分析、图表 |
| 4. 论文写作 | paper-writer | language-editor, figure-designer | 论文初稿、图表、参考文献 |
| 5. 论文自审 | mock-reviewer | citation-checker | Review 报告、修改建议 |
| 6. 投稿与 Rebuttal | submission-manager | paper-writer, mock-reviewer | 投稿包、Rebuttal 文档 |
| 7. 录用后处理 | submission-manager | figure-designer | Camera-ready、演讲、海报 |

---

## 使用模式

### 模式 A：单仓库多项目（推荐日常使用）

在 `projects/` 目录下管理多个研究项目，共享 agent、命令和知识库：

```
my-claude-scholar/
├── projects/
│   ├── _template/              # 项目模板
│   ├── transformer-interp/     # 研究 A：ICLR 投稿
│   ├── llm-reasoning/          # 研究 B：NeurIPS 投稿
│   └── graduation-thesis/      # 毕业论文
├── .claude/                    # 共享 agent 和命令
├── team/                       # 共享 agent 记忆
└── knowledge/                  # 共享知识库
```

**优势**：agent 记忆跨项目积累；知识库和命令统一维护；单一仓库管理。

**使用 `/new-project` 命令**创建新项目。

### 模式 B：Clone 独立仓库（推荐重大研究）

将 my-claude-scholar 作为模板，clone 为独立仓库：

```bash
git clone https://github.com/Gdnaiteab/my-claude-scholar.git my-iclr-paper
cd my-iclr-paper
git remote set-url origin https://github.com/yourname/my-iclr-paper.git
```

**优势**：完全隔离；可针对性定制 agent（如毕业论文需要调整格式规范）；独立 git 历史。

**同步上游改进**：
```bash
git remote add upstream https://github.com/Gdnaiteab/my-claude-scholar.git
git fetch upstream && git merge upstream/master
```

### 何时选择哪种模式

| 场景 | 推荐模式 |
|------|----------|
| 同领域多个实验 | 模式 A（共享知识） |
| 不同领域的独立研究 | 模式 B（完全隔离） |
| 毕业论文（需特殊格式） | 模式 B（定制 agent） |
| 快速探索性实验 | 模式 A（快速启动） |
| 与他人协作的项目 | 模式 B（独立仓库） |

---

## 实验工作流

### 端到端流程

```
初始化 → 开发 → 实验 → 分析 → 写作 → 投稿
  │        │       │       │       │       │
  │     code-    code-   data-   paper-  submis-
  │    architect architect analyst  writer  sion-mgr
  │        │       │       │       │       │
  v        v       v       v       v       v
/new-    /plan    wandb  /analyze /polish /submission
project  /tdd    tracking -results /de-ai  -check
```

### 工具链

| 工具 | 用途 | 配置位置 |
|------|------|----------|
| **uv** / **conda** | Python 包管理 | `pyproject.toml`（uv）或 `environment.yml`（conda） |
| **Hydra** | 实验配置管理 | `projects/{name}/run/conf/` |
| **wandb** | 实验追踪和可视化 | `projects/{name}/run/conf/config.yaml` |
| **Git** | 版本控制 | Conventional Commits |
| **Zotero** | 文献管理 | MCP 集成 |

### 项目目录结构

每个研究项目（`projects/{name}/`）遵循标准结构：

```
projects/{name}/
├── run/conf/          # Hydra 配置（code-architect 维护）
├── run/pipeline/      # 训练/评估脚本
├── src/               # 源代码（Factory & Registry 模式）
├── data/              # 数据（raw/ 和 processed/）
├── outputs/           # 实验输出（experiments/, checkpoints/, figures/, tables/）
├── paper/             # 论文（draft/, figures/, tables/, references.bib）
└── tests/             # 测试
```

详细规范见 `.claude/rules/experiment-workflow.md`。

---

## 全局配置

### 语言设置
- 用中文进行回答和交流
- 专业术语保持英文（如 NeurIPS, RLHF, Transformer, Attention）
- 不翻译特定名词、模型名称或数据集名称
- 代码注释使用中文，命名使用英文

### 工作目录规范

**全局工作区**（跨项目共享）：
- 全局计划: `workspace/plan/` 文件夹
- 临时文件: `workspace/temp/` 文件夹
- 工作日志: `workspace/logs/` 文件夹
- Agent 记忆: `team/{agent-name}/memory.md`
- 知识库: `knowledge/` 文件夹

**项目工作区**（每个研究项目独立）：
- 实验配置: `projects/{name}/run/conf/`
- 源代码: `projects/{name}/src/`
- 实验输出: `projects/{name}/outputs/`
- 论文文件: `projects/{name}/paper/`
- 项目数据: `projects/{name}/data/`

文件夹不存在时自动创建。

### 任务执行原则
- 复杂任务先交流意见，再拆解实施
- 实施后进行示例测试
- 做好备份，不影响现有功能
- 完成后及时删除 `workspace/temp/` 中的临时文件

---

## 工作风格

### 任务管理
- 使用 TodoWrite 跟踪进度
- 复杂任务先规划再执行
- 优先使用已有 Agent 和 knowledge

### 沟通方式
- 不确定时主动询问
- 重要操作前先确认
- 遵循 Hook 强制流程

### 代码风格
- Python 遵循 PEP 8
- 注释使用中文，命名使用英文
- 详见 `.claude/rules/coding-style.md`

---

## 知识库结构

```
knowledge/
├── conference-checklists/    # 各顶会投稿检查清单
└── prompts/                  # 预设 Prompt 模板
    ├── 01-中转英              # 中文转英文
    ├── 02-英转中              # 英文转中文
    ├── 03-中转中              # 中文润色
    ├── 04-缩写               # 文本压缩
    ├── 05-扩写               # 文本扩展
    ├── 06-表达润色-英文        # 英文 polish
    ├── 07-表达润色-中文        # 中文 polish
    ├── 08-逻辑检查            # 逻辑一致性检查
    ├── 09-去AI味             # 去除 AI 写作痕迹
    ├── 10-论文架构图           # Architecture diagram
    ├── 11-实验绘图推荐         # Chart recommendation
    ├── 12-生成图标题           # Figure caption
    ├── 13-生成表标题           # Table caption
    ├── 14-实验分析            # Experiment analysis
    └── 15-审稿人视角           # Reviewer perspective
```

---

## 命令目录（25+ Commands）

### 文献与研究命令

| 命令 | 功能 |
|------|------|
| `/research-init` | 启动 Zotero 集成研究构思工作流 |
| `/zotero-review` | 从 Zotero 集合读取论文，生成结构化文献综述 |
| `/zotero-notes` | 批量阅读 Zotero 论文，生成结构化阅读笔记 |
| `/literature-search` | 按关键词搜索相关文献 |
| `/related-work` | 生成 Related Work 章节草稿 |
| `/new-project` | 从模板创建新研究项目（配置 wandb、git 分支） |

### 实验与分析命令

| 命令 | 功能 |
|------|------|
| `/analyze-results` | 分析实验结果（统计检验、可视化、消融实验） |
| `/plot-results` | 生成实验结果图表 |
| `/ablation` | 设计和分析消融实验 |

### 论文写作命令

| 命令 | 功能 |
|------|------|
| `/write-section` | 撰写论文指定 Section |
| `/polish` | 英文表达润色 |
| `/de-ai` | 去除 AI 写作痕迹 |
| `/translate` | 中英互译 |
| `/check-logic` | 逻辑一致性检查 |
| `/figure-caption` | 生成 Figure/Table caption |

### 审稿与投稿命令

| 命令 | 功能 |
|------|------|
| `/mock-review` | 模拟顶会审稿 |
| `/check-citations` | 引文格式和信息验证 |
| `/rebuttal` | 生成系统化 Rebuttal 文档 |
| `/submission-check` | 投稿前全面检查 |
| `/camera-ready` | Camera-ready 准备 |
| `/presentation` | 创建会议演讲大纲 |
| `/poster` | 生成学术海报设计方案 |

### 开发工作流命令

| 命令 | 功能 |
|------|------|
| `/plan` | 创建实施计划 |
| `/commit` | 提交代码（遵循 Conventional Commits） |
| `/code-review` | 代码审查 |
| `/tdd` | 测试驱动开发工作流 |
| `/update-memory` | 检查并更新 Agent 记忆 |

---

## Agent 目录（9 Agents）

| Agent | 一句话描述 |
|-------|----------|
| `literature-scout` | 文献搜索与综述生成，Zotero MCP 深度集成 |
| `code-architect` | ML 项目代码架构设计与审查，Factory & Registry 模式 |
| `data-analyst` | 自动化实验结果分析、统计检验和数据可视化 |
| `paper-writer` | 学术论文各 Section 写作，符合顶会标准 |
| `language-editor` | 英文润色、中英互译、学术表达规范化 |
| `figure-designer` | 学术图表设计，matplotlib/TikZ/pgfplots 输出 |
| `citation-checker` | 引文格式验证、BibTeX 校验、引文信息核实 |
| `mock-reviewer` | 按 NeurIPS/ICML/ACL 等标准模拟审稿 |
| `submission-manager` | 投稿清单管理、格式合规、Camera-ready 流程 |

---

## 钩子目录（6 Hooks）

跨平台 Node.js 钩子，自动化工作流执行：

| 钩子 | 触发时机 | 功能 |
|------|----------|------|
| `hook-common.js` | - | 跨平台共享工具库 |
| `session-start.js` | SessionStart | 显示 Git 状态、待办事项、可用命令、Agent 状态 |
| `skill-forced-eval.js` | UserPromptSubmit | 强制评估所有可用 Agent，匹配最佳执行者 |
| `session-summary.js` | SessionEnd | 生成工作日志，更新 Agent 记忆，检测 CLAUDE.md 更新 |
| `stop-summary.js` | Stop | 快速状态检查，临时文件检测，未保存更改提醒 |
| `security-guard.js` | PreToolUse | 安全验证（密钥检测、危险命令拦截、敏感文件保护） |

---

## 规则目录（4 Rules）

全局约束，始终生效：

| 规则文件 | 路径 | 作用 |
|---------|------|------|
| `coding-style.md` | `.claude/rules/` | ML 项目代码标准：文件 200-400 行、不可变配置、类型提示、Factory & Registry 模式 |
| `experiment-reproducibility.md` | `.claude/rules/` | 实验可复现性：随机种子、配置记录、环境记录、检查点管理 |
| `security.md` | `.claude/rules/` | 安全规范：密钥管理、敏感文件保护、提交前安全检查 |
| `agents.md` | `.claude/rules/` (待创建) | Agent 编排：自动调用时机、并行执行、多视角分析 |

---

## 任务完成总结

每次任务完成时，主动提供简要总结：

```
本次操作回顾
1. [主要操作]
2. [修改的文件]

当前状态
- [Git / 文件系统 / 运行状态]

下一步建议
1. [针对性建议]

Agent 记忆更新
- [本次涉及的 Agent 及其记忆变更]
```
