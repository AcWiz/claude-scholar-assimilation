# [研究项目名称]

## 基本信息

| 项目 | 内容 |
|------|------|
| **研究主题** | [简要描述研究问题和方法] |
| **目标会议/期刊** | [例如：NeurIPS 2026 / ACL 2026 / CVPR 2026] |
| **关键词** | [关键词1, 关键词2, 关键词3] |
| **PI** | [负责人姓名] |

## 项目结构

```
├── run/                  # 运行配置与入口脚本
│   ├── conf/             # Hydra 配置文件（model / dataset / trainer）
│   └── pipeline/         # 训练、评估等入口脚本
├── src/                  # 核心源代码
│   ├── data_module/      # 数据集加载、预处理、增强
│   ├── model_module/     # 模型定义与注册
│   ├── trainer_module/   # 训练器定义与注册
│   └── utils/            # 共享工具函数
├── data/                 # 数据目录
│   ├── raw/              # 原始数据（gitignored）
│   └── processed/        # 预处理后的数据
├── outputs/              # 实验输出
│   ├── experiments/      # 实验结果
│   ├── checkpoints/      # 模型检查点（gitignored）
│   ├── figures/          # 生成的图表
│   ├── tables/           # 生成的表格
│   └── logs/             # 运行日志（gitignored）
├── paper/                # 论文相关
│   ├── draft/            # 论文草稿
│   ├── figures/          # 论文用图
│   ├── tables/           # 论文用表
│   └── references.bib    # 参考文献
└── tests/                # 单元测试
```

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv 安装项目依赖
uv sync
```

### 2. 配置环境变量

```bash
# 复制环境变量模板并填写
cp .env.example .env
# 编辑 .env，填入 WANDB_API_KEY 等信息
```

### 3. 配置 Weights & Biases

```bash
wandb login
```

### 4. 运行实验

```bash
# 使用默认配置运行
python run/pipeline/train.py

# 覆盖配置参数
python run/pipeline/train.py model=default dataset=default experiment.name=my_exp experiment.seed=123

# 多次运行（不同种子）
python run/pipeline/train.py --multirun experiment.seed=42,123,456
```

## 实验记录

| 实验名称 | 日期 | 配置 | W&B 链接 | 结果摘要 | 备注 |
|----------|------|------|----------|----------|------|
| baseline | YYYY-MM-DD | `model=default` | [link]() | acc=0.XX | 初始基线 |
| | | | | | |
| | | | | | |
