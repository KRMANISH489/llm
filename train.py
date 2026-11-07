"""
Train the mini-GPT on a local text corpus.
Usage:
  python train.py
  python train.py --data data/corpus.txt --max-iters 2000
"""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import torch

from config import ModelConfig, TrainConfig, save_json, CHECKPOINT_DIR
from dataset import build_tokenizer_and_data, get_batch, load_text
from model import GPT


def get_device(prefer: str) -> torch.device:
    if prefer == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if prefer == "mps" and getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_lr(it: int, cfg: TrainConfig) -> float:
    if it < cfg.warmup_iters:
        return cfg.learning_rate * (it + 1) / max(1, cfg.warmup_iters)
    if it >= cfg.max_iters:
        return cfg.min_lr
    decay_ratio = (it - cfg.warmup_iters) / max(1, cfg.max_iters - cfg.warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return cfg.min_lr + coeff * (cfg.learning_rate - cfg.min_lr)


@torch.no_grad()
def estimate_loss(
    model: GPT,
    train_ids: torch.Tensor,
    val_ids: torch.Tensor,
    cfg: TrainConfig,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    out = {}
    for split, data in (("train", train_ids), ("val", val_ids)):
        losses = torch.zeros(cfg.eval_iters, device=device)
        for k in range(cfg.eval_iters):
            xb, yb = get_batch(data, cfg.batch_size, model.config.block_size, device)
            _, loss = model(xb, yb)
            losses[k] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out


def train(args: argparse.Namespace) -> None:
    tcfg = TrainConfig(
        batch_size=args.batch_size,
        learning_rate=args.lr,
        max_iters=args.max_iters,
        eval_interval=args.eval_interval,
        data_path=args.data,
        checkpoint_path=args.checkpoint,
        tokenizer_path=args.tokenizer,
        device=args.device,
    )
    mcfg = ModelConfig(
        block_size=args.block_size,
        n_layer=args.n_layer,
        n_head=args.n_head,
        n_embd=args.n_embd,
        dropout=args.dropout,
    )

    torch.manual_seed(tcfg.seed)
    device = get_device(tcfg.device)
    print(f"Device: {device}")

    text = load_text(tcfg.data_path)
    tokenizer, train_ids, val_ids = build_tokenizer_and_data(
        text, mcfg.block_size, tcfg.tokenizer_path
    )
    mcfg.vocab_size = tokenizer.vocab_size
    print(f"Vocab size: {mcfg.vocab_size} | train tokens: {len(train_ids)} | val: {len(val_ids)}")

    model = GPT(mcfg).to(device)
    print(f"Parameters: {model.get_num_params()/1e6:.2f}M")

    if tcfg.compile_model and hasattr(torch, "compile"):
        model = torch.compile(model)  # type: ignore

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=tcfg.learning_rate,
        betas=(0.9, 0.99),
        weight_decay=tcfg.weight_decay,
    )

    scaler = None
    use_amp = device.type == "cuda" and tcfg.dtype in ("float16", "bfloat16")
    amp_dtype = torch.float16 if tcfg.dtype == "float16" else torch.bfloat16
    if use_amp and tcfg.dtype == "float16":
        scaler = torch.cuda.amp.GradScaler()

    best_val = float("inf")
    t0 = time.time()
    for it in range(tcfg.max_iters):
        lr = get_lr(it, tcfg)
        for pg in optimizer.param_groups:
            pg["lr"] = lr

        xb, yb = get_batch(train_ids, tcfg.batch_size, mcfg.block_size, device)

        optimizer.zero_grad(set_to_none=True)
        if use_amp:
            with torch.autocast(device_type=device.type, dtype=amp_dtype):
                _, loss = model(xb, yb)
            if scaler is not None:
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), tcfg.grad_clip)
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), tcfg.grad_clip)
                optimizer.step()
        else:
            _, loss = model(xb, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), tcfg.grad_clip)
            optimizer.step()

        if it % 50 == 0:
            dt = time.time() - t0
            t0 = time.time()
            print(f"iter {it:5d} | loss {loss.item():.4f} | lr {lr:.2e} | {dt*1000:.0f}ms")

        if it % tcfg.eval_interval == 0 or it == tcfg.max_iters - 1:
            losses = estimate_loss(model, train_ids, val_ids, tcfg, device)
            print(
                f"eval {it:5d} | train {losses['train']:.4f} | val {losses['val']:.4f}"
            )
            if losses["val"] < best_val:
                best_val = losses["val"]
                raw = model._orig_mod if hasattr(model, "_orig_mod") else model
                ckpt = {
                    "model_state": raw.state_dict(),
                    "model_config": mcfg.__dict__,
                    "optimizer_state": optimizer.state_dict(),
                    "iter_num": it,
                    "best_val_loss": best_val,
                    "meta": {"tokenizer": str(tcfg.tokenizer_path)},
                }
                Path(tcfg.checkpoint_path).parent.mkdir(parents=True, exist_ok=True)
                torch.save(ckpt, tcfg.checkpoint_path)
                save_json(mcfg, CHECKPOINT_DIR / "model_config.json")
                print(f"  saved checkpoint -> {tcfg.checkpoint_path}")

    print("Training complete.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train mini-GPT LLM")
    p.add_argument("--data", default=str(TrainConfig().data_path))
    p.add_argument("--checkpoint", default=str(TrainConfig().checkpoint_path))
    p.add_argument("--tokenizer", default=str(TrainConfig().tokenizer_path))
    p.add_argument("--device", default="cuda")
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--max-iters", type=int, default=3000)
    p.add_argument("--eval-interval", type=int, default=250)
    p.add_argument("--block-size", type=int, default=256)
    p.add_argument("--n-layer", type=int, default=6)
    p.add_argument("--n-head", type=int, default=6)
    p.add_argument("--n-embd", type=int, default=384)
    p.add_argument("--dropout", type=float, default=0.1)
    return p.parse_args()


if __name__ == "__main__":
    train(parse_args())
