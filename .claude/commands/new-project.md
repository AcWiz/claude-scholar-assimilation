---
description: "Create a new research project from template"
arguments:
  - name: "name"
    description: "Project name (lowercase, hyphens, e.g. transformer-interpretability)"
    required: true
  - name: "venue"
    description: "Target venue (e.g. ICLR, NeurIPS, ICML, ACL, CVPR, thesis)"
    required: false
---

# /new-project - 创建新研究项目

从 `projects/_template/` 模板创建新研究项目。

## 执行步骤

1. **验证项目名**：
   - 必须是小写字母、数字和连字符组成
   - 不能与已有项目重名
   - 检查 `projects/` 目录下是否已存在同名目录

2. **复制模板**：
   ```bash
   cp -r projects/_template projects/$name
   ```

3. **初始化项目**：
   - 更新 `projects/$name/README.md`：填入项目名、目标会议/期刊
   - 更新 `projects/$name/pyproject.toml`：将 `name` 字段改为项目名
   - 更新 `projects/$name/run/conf/config.yaml`：将 `wandb.project` 改为项目名
   - 创建 `projects/$name/.env`（从 `.env.example` 复制）

4. **Git 操作**：
   - 创建项目分支：`git checkout -b project/$name`
   - 暂存新文件：`git add projects/$name/`
   - 提交：`git commit -m "feat(project): initialize $name research project"`

5. **输出确认**：
   显示项目结构和下一步操作指南：
   - 配置 wandb API key
   - 安装依赖：`cd projects/$name && uv sync`（或 `conda env create -f environment.yml`）
   - 开始研究

## 注意事项
- 如果用户指定了 venue（如 ICLR），在 README.md 中自动填入目标会议信息
- 如果用户没有指定 venue，在 README.md 中留空供后续填写
