"""Dataset helpers: load corpus, build tokenizer, create train/val tensors."""

from __future__ import annotations

from pathlib import Path

import torch

from tokenizer import CharTokenizer


def load_text(path: str | Path) -> str:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Corpus not found: {path}\n"
            "Put training text in data/corpus.txt or pass --data"
        )
    return path.read_text(encoding="utf-8")


def build_tokenizer_and_data(
    text: str, block_size: int, tokenizer_path: str | Path
) -> tuple[CharTokenizer, torch.Tensor, torch.Tensor]:
    tokenizer = CharTokenizer.from_text(text)
    tokenizer.save(tokenizer_path)
    ids = torch.tensor(tokenizer.encode(text), dtype=torch.long)
    n = int(0.9 * len(ids))
    train_ids = ids[:n]
    val_ids = ids[n:]
    if len(train_ids) < block_size + 1 or len(val_ids) < block_size + 1:
        # tiny corpus fallback: reuse full data for both
        train_ids = ids
        val_ids = ids
    return tokenizer, train_ids, val_ids


def get_batch(
    split_ids: torch.Tensor,
    batch_size: int,
    block_size: int,
    device: torch.device,
) -> tuple[torch.Tensor, torch.Tensor]:
    # random windows
    max_start = len(split_ids) - block_size - 1
    if max_start < 1:
        raise ValueError("Corpus too small for chosen block_size. Add more text.")
    ix = torch.randint(0, max_start, (batch_size,))
    x = torch.stack([split_ids[i : i + block_size] for i in ix])
    y = torch.stack([split_ids[i + 1 : i + 1 + block_size] for i in ix])
    return x.to(device), y.to(device)
