"""数据模块：数据集加载、预处理、增强。"""
from typing import Dict, Type
from torch.utils.data import Dataset

DATASET_FACTORY: Dict[str, Type[Dataset]] = {}

def register_dataset(name: str):
    """数据集注册装饰器。"""
    def decorator(cls):
        DATASET_FACTORY[name] = cls
        return cls
    return decorator

def DatasetFactory(name: str) -> Type[Dataset]:
    """数据集工厂。"""
    return DATASET_FACTORY.get(name)

__all__ = ["DATASET_FACTORY", "register_dataset", "DatasetFactory"]
