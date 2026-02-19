# Experiment Workflow - 端到端实验流程

所有实验项目必须遵循此工作流程，确保可追踪性、可复现性和团队协作效率。

## 项目初始化

### 从模板创建项目

1. 复制 `projects/_template/` 到 `projects/{project-name}/`
2. 更新 `README.md`：填写研究主题、目标会议、关键词
3. 配置环境：
   ```bash
   cd projects/{project-name}
   cp .env.example .env  # 填写 WANDB_API_KEY 等
   uv sync               # 安装依赖（或 conda env create -f environment.yml）
   ```
4. 初始化 git 分支：`git checkout -b project/{project-name}`
5. 配置 wandb：更新 `run/conf/config.yaml` 中的 `wandb.project` 和 `wandb.entity`

### 项目目录规范

| 目录 | 用途 | 负责 Agent | 读写权限 |
|------|------|-----------|----------|
| `run/conf/` | Hydra 配置文件 | code-architect | 读写 |
| `run/pipeline/` | 训练/评估脚本 | code-architect | 读写 |
| `src/` | 源代码 | code-architect | 读写 |
| `data/raw/` | 原始数据 | code-architect | 写入；data-analyst 读取 |
| `data/processed/` | 处理后数据 | code-architect | 读写 |
| `outputs/experiments/` | Hydra 实验输出 | 自动生成 | 所有 agent 只读 |
| `outputs/checkpoints/` | 模型检查点 | code-architect | 写入 |
| `outputs/figures/` | 实验图表（中间版） | data-analyst, figure-designer | 写入 |
| `outputs/tables/` | 实验表格（中间版） | data-analyst | 写入 |
| `outputs/logs/` | wandb 本地日志 | 自动生成 | 只读 |
| `paper/draft/` | 论文草稿 | paper-writer | 读写 |
| `paper/figures/` | 论文最终图表 | figure-designer | 写入；paper-writer 引用 |
| `paper/tables/` | 论文最终表格 | data-analyst | 写入；paper-writer 引用 |
| `paper/references.bib` | 参考文献 | citation-checker | 读写 |
| `tests/` | 测试代码 | code-architect | 读写 |

## 包管理

支持两种包管理方案，根据服务器环境选择：

### 方案 A：uv（推荐，适用于现代系统）

```bash
# 安装依赖
uv sync

# 添加新依赖
uv add <package>

# 添加开发依赖
uv add --dev <package>

# 锁定依赖版本
uv lock

# 在项目环境中运行
uv run python run/pipeline/train.py
```

**配置文件**: `pyproject.toml` + `uv.lock`（必须提交到 git）

### 方案 B：conda（miniconda/miniforge，适用于老系统）

当训练服务器的操作系统版本较低（如 CentOS 7、旧版 Ubuntu）导致 uv 无法使用时，使用 conda：

```bash
# 创建环境（从模板）
conda env create -f environment.yml

# 激活环境
conda activate {project-name}

# 添加 conda 依赖
conda install <package>

# 添加 pip-only 依赖（conda 中没有的包）
pip install <package>

# 导出环境（更新 environment.yml）
conda env export --from-history > environment.yml

# 运行
python run/pipeline/train.py
```

**配置文件**: `environment.yml`（必须提交到 git）

### 如何选择

| 条件 | 推荐方案 |
|------|----------|
| 本地开发（macOS/新版 Linux） | uv |
| 训练服务器（老系统/glibc 版本低） | conda (miniforge) |
| 需要 CUDA 特定版本 | conda（更方便管理 CUDA toolkit） |
| 追求依赖解析速度 | uv |

### 通用规范
- 禁止使用裸 `pip install` 直接安装（破坏依赖一致性）
- `pyproject.toml`（uv）或 `environment.yml`（conda）必须提交到 git
- 虚拟环境 `.venv/` 和 `.conda/` 不提交到 git
- 两份配置文件可以同时存在（同一项目在不同环境使用不同方案）

## 实验追踪（Weights & Biases）

### wandb 配置

在 `run/conf/config.yaml` 中配置：
```yaml
wandb:
  enabled: true
  project: "{project-name}"    # wandb 项目名
  entity: null                 # wandb 团队/用户名
  tags: []                     # 实验标签
  notes: ""                    # 实验说明
```

### wandb 初始化规范

```python
import wandb

def init_wandb(cfg):
    """初始化 wandb 实验追踪。"""
    if not cfg.wandb.enabled:
        wandb.init(mode="disabled")
        return

    wandb.init(
        project=cfg.wandb.project,
        entity=cfg.wandb.entity,
        name=f"{cfg.experiment.name}_{cfg.experiment.seed}",
        config=OmegaConf.to_container(cfg, resolve=True),
        tags=cfg.wandb.tags,
        notes=cfg.wandb.notes,
    )
```

### 必须记录的指标
- **训练指标**: train/loss, train/lr, train/epoch
- **验证指标**: val/loss, val/{主指标}（如 val/accuracy, val/f1）
- **系统指标**: wandb 自动记录（GPU 使用率、内存等）
- **最终结果**: test/{所有评估指标}

### wandb 命名规范
- **Project**: 研究项目名（如 `transformer-interpretability`）
- **Run name**: `{method}_{seed}`（如 `baseline_42`）
- **Tags**: 方法类型、数据集、实验阶段（如 `["ablation", "cifar10", "v2"]`）

## 实验命名规范

### 实验名格式
```
{method}_{dataset}_{variant}_{YYYYMMDD}
```

**示例**：
- `baseline_cifar10_v1_20260219`
- `ablation_no_aug_imagenet_20260220`
- `final_bert_sst2_20260301`

### Hydra 输出目录
Hydra 自动在 `outputs/experiments/` 下生成：
```
outputs/experiments/
└── 2026-02-19/
    └── 14-30-00/
        ├── .hydra/
        │   ├── config.yaml
        │   ├── hydra.yaml
        │   └── overrides.yaml
        └── train.log
```

## Git 分支策略

### 实验分支模型
```
master          ← 稳定版本
  └── develop   ← 开发主线
       ├── project/{name}     ← 项目分支（长期）
       ├── experiment/{name}  ← 实验分支（短期）
       └── feature/{name}     ← 功能分支（短期）
```

### 实验分支生命周期
1. 从 `develop` 创建 `experiment/{实验名}`
2. 在分支上进行实验开发和运行
3. 实验完成后，将代码和配置（不含大文件）合并回 `develop`
4. 保留分支标签用于追溯

### 提交规范（Conventional Commits）
```
feat(model): add attention mechanism for transformer
fix(data): correct data augmentation pipeline
experiment(ablation): run ablation without dropout
docs(paper): update methods section draft
```

新增 scope: `experiment` 用于实验相关提交。

## 数据流转规范

### Agent 间数据传递路径

```
code-architect                      data-analyst
  │                                    │
  ├─ outputs/experiments/ ────────────►├─ 读取实验结果
  ├─ outputs/checkpoints/ ────────────►├─ 读取模型文件（如需）
  │                                    │
  │                                    ├─ outputs/figures/ ──►  figure-designer
  │                                    ├─ outputs/tables/  ──►  paper-writer
  │                                    │
  │                               figure-designer
  │                                    │
  │                                    ├─ paper/figures/ ────►  paper-writer
  │                                    │
  │                               paper-writer
  │                                    │
  │                                    ├─ paper/draft/ ──────►  language-editor
  │                                    ├─ paper/references.bib ► citation-checker
  │                                    │
  │                               mock-reviewer
  │                                    │
  │                                    ├─ 读取 paper/draft/ ──► 生成审稿报告
  │                                    │
  │                               submission-manager
  │                                    │
  │                                    └─ 整合所有 paper/ 内容
```

### 数据交接格式
- 实验结果：CSV 或 JSON（含列名说明）
- 图表：PDF 矢量图（论文用）+ PNG 位图（预览用）
- 表格：LaTeX tabular 格式 + CSV 原始数据
- 论文：LaTeX .tex 文件 或 Word .docx 文件

## 实验记录清单

每次实验运行前必须确认：

- [ ] 配置文件已保存到 `run/conf/`
- [ ] 随机种子已设置（`experiment.seed`）
- [ ] wandb 已配置且 tags 已设置
- [ ] 依赖已锁定（`uv lock`）
- [ ] 代码已提交到 git（`experiment/` 分支）

每次实验运行后必须记录：

- [ ] wandb run URL 已记录到项目 README.md 实验记录表
- [ ] 关键指标已记录（val/test 最佳指标值）
- [ ] 异常现象已记录（如有）
- [ ] 下一步实验计划已记录

## Clone 模式使用指南

当以 clone 方式创建独立研究仓库时：

1. `git clone https://github.com/Gdnaiteab/my-claude-scholar.git {new-project-name}`
2. `cd {new-project-name}`
3. `git remote set-url origin {new-repo-url}`
4. 直接在仓库根目录或 `projects/` 下开展研究
5. 可定期从上游同步改进：
   ```bash
   git remote add upstream https://github.com/Gdnaiteab/my-claude-scholar.git
   git fetch upstream
   git merge upstream/master --allow-unrelated-histories
   ```
