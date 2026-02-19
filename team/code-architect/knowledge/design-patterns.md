# ML 项目设计模式

## Factory & Registry 模式

所有模型、数据集、训练器必须使用工厂和注册模式，实现配置驱动的模块切换。

### Registry 实现

```python
from typing import Dict, Type

DATASET_FACTORY: Dict[str, Type[Dataset]] = {}

def register_dataset(name: str):
    """数据集注册装饰器"""
    def decorator(cls):
        DATASET_FACTORY[name] = cls
        return cls
    return decorator

def DatasetFactory(name: str) -> Type[Dataset]:
    """数据集工厂"""
    return DATASET_FACTORY.get(name, SimpleDataset)
```

### 模型注册示例

```python
MODEL_FACTORY: Dict[str, Type[nn.Module]] = {}

def register_model(name: str):
    def decorator(cls):
        MODEL_FACTORY[name] = cls
        return cls
    return decorator

@register_model('TransformerDecoder')
class TransformerDecoder(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.hidden_dim = cfg.model.hidden_dim
        self.num_layers = cfg.model.num_layers
```

## Config-Driven 设计

### 不可变配置

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelConfig:
    hidden_dim: int
    num_layers: int
    dropout: float = 0.1
    activation: str = "gelu"

@dataclass(frozen=True)
class TrainingConfig:
    batch_size: int
    learning_rate: float
    num_epochs: int
    seed: int = 42
```

### Hydra 配置组合

```yaml
# conf/config.yaml
defaults:
  - model: transformer
  - dataset: custom
  - trainer: default

experiment:
  name: baseline
  seed: 42
```

```yaml
# conf/model/transformer.yaml
hidden_dim: 768
num_layers: 12
num_heads: 12
dropout: 0.1
```

### 模型只接受 cfg 参数

```python
@register_model('MyModel')
class MyModel(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        # 所有超参数从 cfg 获取
        self.hidden_dim = cfg.model.hidden_dim
        self.encoder = TransformerEncoder(cfg)
```

## 目录结构规范

```
project/
├── run/
│   ├── conf/                    # Hydra 配置
│   │   ├── config.yaml
│   │   ├── model/
│   │   ├── dataset/
│   │   └── trainer/
│   ├── pipeline/                # 工作流脚本
│   └── outputs/                 # 实验输出
├── src/
│   ├── data_module/             # 数据模块
│   │   ├── __init__.py          # Factory & Registry
│   │   ├── dataset/
│   │   ├── augmentation/
│   │   └── utils.py
│   ├── model_module/            # 模型模块
│   │   ├── __init__.py          # Factory & Registry
│   │   ├── base_model.py        # 基类 (~200 行)
│   │   ├── transformer.py       # 具体实现 (~300 行)
│   │   └── cnn.py
│   ├── trainer_module/          # 训练模块
│   └── utils/                   # 共享工具
└── tests/                       # 测试
```

## 小文件原则

- 单文件 200-400 行，超出则拆分
- `__init__.py` 只包含 Factory、Registry 和 `__all__`
- 相关功能放同一目录下

## 类型提示和文档

```python
from typing import Dict, List, Optional, Tuple

def train_model(
    cfg: TrainingConfig,
    model: nn.Module,
    train_loader: DataLoader,
) -> Tuple[nn.Module, Dict[str, float]]:
    """训练模型。

    Args:
        cfg: 训练配置对象。
        model: 待训练的模型。
        train_loader: 训练数据加载器。

    Returns:
        训练后的模型和指标字典。

    Raises:
        ValueError: 配置无效时。
    """
    ...
```

## 日志规范

```python
import logging
logger = logging.getLogger(__name__)

# 正确使用
logger.info(f"Epoch {epoch}: loss={loss:.4f}, acc={acc:.2%}")
logger.warning(f"Learning rate {lr} is unusually high")
logger.error(f"Failed to load checkpoint: {path}")

# 禁止使用
print(f"loss: {loss}")  # 禁止 print 调试
```

## 禁止模式

- 文件超过 800 行
- 嵌套超过 4 层
- 可变默认参数: `def foo(a=[])`
- 全局变量（用 config 代替）
- 裸 except: `except:`
- 硬编码超参数（用 cfg 代替）
- 未使用的 import
- print() 调试语句（用 logger 代替）
