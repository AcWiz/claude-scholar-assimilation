"""训练入口脚本。

使用 Hydra 管理配置，W&B 记录实验。
运行示例：
    python run/pipeline/train.py
    python run/pipeline/train.py experiment.name=my_exp experiment.seed=123
"""

import logging
import os
import platform
import random

import hydra
import numpy as np
import torch
import wandb
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)


def set_seed(seed: int = 42) -> None:
    """设置随机种子，确保实验可复现。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    logger.info("随机种子已设置: %d", seed)


def log_environment() -> dict:
    """记录运行环境信息，用于可复现性追踪。"""
    env_info = {
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else "N/A",
        "gpu_model": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
        "gpu_count": torch.cuda.device_count(),
        "platform": platform.platform(),
    }
    for key, value in env_info.items():
        logger.info("  %s: %s", key, value)
    return env_info


def init_wandb(cfg: DictConfig) -> None:
    """初始化 Weights & Biases 实验追踪。"""
    if not cfg.wandb.enabled:
        logger.info("W&B 已禁用，跳过初始化。")
        wandb.init(mode="disabled")
        return

    wandb.init(
        project=cfg.wandb.project,
        entity=cfg.wandb.entity,
        name=cfg.experiment.name,
        tags=list(cfg.wandb.tags),
        notes=cfg.wandb.notes,
        config=OmegaConf.to_container(cfg, resolve=True),
    )
    logger.info("W&B 初始化完成: project=%s, name=%s", cfg.wandb.project, cfg.experiment.name)


@hydra.main(version_base=None, config_path="../conf", config_name="config")
def main(cfg: DictConfig) -> None:
    """训练主函数。"""
    # --- 基础设置 ---
    logger.info("实验配置:\n%s", OmegaConf.to_yaml(cfg))
    set_seed(cfg.experiment.seed)

    logger.info("运行环境:")
    env_info = log_environment()

    # --- 初始化 W&B ---
    init_wandb(cfg)
    if cfg.wandb.enabled:
        wandb.log({"env": env_info})

    # --- TODO: 加载数据集 ---
    # 使用 DatasetFactory 加载数据集
    # from src.data_module import DatasetFactory
    # dataset_cls = DatasetFactory(cfg.dataset.name)
    # train_dataset = dataset_cls(cfg, split="train")
    # val_dataset = dataset_cls(cfg, split="val")
    logger.info("TODO: 加载数据集")

    # --- TODO: 构建模型 ---
    # 使用 ModelFactory 构建模型
    # from src.model_module import ModelFactory
    # model_cls = ModelFactory(cfg.model.name)
    # model = model_cls(cfg)
    logger.info("TODO: 构建模型")

    # --- TODO: 训练循环 ---
    # 使用 TrainerFactory 或自定义训练循环
    # from src.trainer_module import TrainerFactory
    # trainer_cls = TrainerFactory(cfg.trainer.name)
    # trainer = trainer_cls(cfg, model, train_dataset, val_dataset)
    # trainer.train()
    logger.info("TODO: 实现训练循环")

    # --- TODO: 评估与保存 ---
    # results = trainer.evaluate()
    # wandb.log(results)
    # torch.save(model.state_dict(), os.path.join(cfg.paths.checkpoint_dir, "best_model.pt"))
    logger.info("TODO: 实现评估与模型保存")

    # --- 清理 ---
    wandb.finish()
    logger.info("实验完成: %s", cfg.experiment.name)


if __name__ == "__main__":
    main()
