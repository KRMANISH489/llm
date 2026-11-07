"""LLM configuration — tweak these to scale model size / training."""

from dataclasses import dataclass, asdict
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CHECKPOINT_DIR = ROOT / "checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


@dataclass
class ModelConfig:
    vocab_size: int = 256  # char-level by default; updated after tokenizer build
    block_size: int = 256  # context length
    n_layer: int = 6
    n_head: int = 6
    n_embd: int = 384
    dropout: float = 0.1
    bias: bool = True


@dataclass
class TrainConfig:
    batch_size: int = 32
    learning_rate: float = 3e-4
    max_iters: int = 3000
    eval_interval: int = 250
    eval_iters: int = 50
    warmup_iters: int = 100
    min_lr: float = 3e-5
    weight_decay: float = 0.1
    grad_clip: float = 1.0
    seed: int = 1337
    device: str = "cuda"  # auto-fallback to cpu in train.py
    dtype: str = "float16"  # float16 | bfloat16 | float32
    compile_model: bool = False
    data_path: str = str(DATA_DIR / "corpus.txt")
    checkpoint_path: str = str(CHECKPOINT_DIR / "best.pt")
    tokenizer_path: str = str(CHECKPOINT_DIR / "tokenizer.json")


@dataclass
class GenConfig:
    max_new_tokens: int = 200
    temperature: float = 0.8
    top_k: int = 50
    top_p: float = 0.9


def save_json(obj, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(obj) if hasattr(obj, "__dataclass_fields__") else obj, f, indent=2)


def load_json(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
