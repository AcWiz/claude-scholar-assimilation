"""训练器模块：训练器定义与注册。"""
from typing import Dict, Type

TRAINER_FACTORY: Dict[str, Type] = {}

def register_trainer(name: str):
    """训练器注册装饰器。"""
    def decorator(cls):
        TRAINER_FACTORY[name] = cls
        return cls
    return decorator

def TrainerFactory(name: str) -> Type:
    """训练器工厂。"""
    return TRAINER_FACTORY.get(name)

__all__ = ["TRAINER_FACTORY", "register_trainer", "TrainerFactory"]
