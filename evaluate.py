"""
Evaluate a checkpoint: validation loss + sample generations.
Usage:
  python evaluate.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from config import ModelConfig, TrainConfig
from dataset import get_batch, load_text
from generate import generate_text, load_model
from tokenizer import CharTokenizer
from train import get_device


@torch.no_grad()
def val_loss(model, ids, batch_size, device, iters=50):
    model.eval()
    losses = []
    for _ in range(iters):
        xb, yb = get_batch(ids, batch_size, model.config.block_size, device)
        _, loss = model(xb, yb)
        losses.append(loss.item())
    return sum(losses) / len(losses)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default=str(TrainConfig().checkpoint_path))
    p.add_argument("--tokenizer", default=str(TrainConfig().tokenizer_path))
    p.add_argument("--data", default=str(TrainConfig().data_path))
    p.add_argument("--device", default="cuda")
    p.add_argument("--batch-size", type=int, default=16)
    args = p.parse_args()

    if not Path(args.checkpoint).exists():
        raise SystemExit("No checkpoint. Run python train.py first.")

    device = get_device(args.device)
    model, tokenizer = load_model(args.checkpoint, args.tokenizer, device)

    text = load_text(args.data)
    ids = torch.tensor(tokenizer.encode(text), dtype=torch.long)
    n = int(0.9 * len(ids))
    val_ids = ids[n:] if len(ids) - n > model.config.block_size + 1 else ids
    loss = val_loss(model, val_ids, args.batch_size, device)
    print(f"val loss: {loss:.4f} | ppl ≈ {torch.exp(torch.tensor(loss)).item():.2f}")
    print("-" * 40)
    for prompt in ["Once upon a time", "User: What is an LLM?\nAssistant:", "Hello"]:
        out = generate_text(model, tokenizer, prompt, device, max_new_tokens=120)
        print(f"PROMPT: {prompt!r}")
        print(out)
        print("-" * 40)


if __name__ == "__main__":
    main()
