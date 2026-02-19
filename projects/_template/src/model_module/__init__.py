"""模型模块：模型定义与注册。"""
from typing import Dict, Type
from torch import nn

MODEL_FACTORY: Dict[str, Type[nn.Module]] = {}

def register_model(name: str):
    """模型注册装饰器。"""
    def decorator(cls):
        MODEL_FACTORY[name] = cls
        return cls
    return decorator

def ModelFactory(name: str) -> Type[nn.Module]:
    """模型工厂。"""
    return MODEL_FACTORY.get(name)

__all__ = ["MODEL_FACTORY", "register_model", "ModelFactory"]
