"""
Text generation from a trained checkpoint.
Usage:
  python generate.py --prompt "Once upon a time"
  python generate.py --prompt "Hello" --temperature 0.7 --top-k 40
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from config import GenConfig, ModelConfig, TrainConfig
from model import GPT
from tokenizer import CharTokenizer
from train import get_device


def load_model(
    checkpoint: str | Path,
    tokenizer_path: str | Path,
    device: torch.device,
) -> tuple[GPT, CharTokenizer]:
    ckpt = torch.load(checkpoint, map_location=device, weights_only=False)
    mcfg = ModelConfig(**ckpt["model_config"])
    model = GPT(mcfg).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    tokenizer = CharTokenizer.load(tokenizer_path)
    return model, tokenizer


@torch.no_grad()
def generate_text(
    model: GPT,
    tokenizer: CharTokenizer,
    prompt: str,
    device: torch.device,
    max_new_tokens: int = 200,
    temperature: float = 0.8,
    top_k: int = 50,
    top_p: float = 0.9,
) -> str:
    ids = tokenizer.encode(prompt, add_bos=True)
    idx = torch.tensor([ids], dtype=torch.long, device=device)
    out = model.generate(
        idx,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_k=top_k if top_k > 0 else None,
        top_p=top_p,
        eos_id=tokenizer.eos_id,
    )
    return tokenizer.decode(out[0].tolist())


def main() -> None:
    p = argparse.ArgumentParser(description="Generate text with mini-GPT")
    p.add_argument("--checkpoint", default=str(TrainConfig().checkpoint_path))
    p.add_argument("--tokenizer", default=str(TrainConfig().tokenizer_path))
    p.add_argument("--prompt", default="Once upon a time")
    p.add_argument("--max-new-tokens", type=int, default=GenConfig.max_new_tokens)
    p.add_argument("--temperature", type=float, default=GenConfig.temperature)
    p.add_argument("--top-k", type=int, default=GenConfig.top_k)
    p.add_argument("--top-p", type=float, default=GenConfig.top_p)
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    if not Path(args.checkpoint).exists():
        raise SystemExit(
            f"Checkpoint not found: {args.checkpoint}\nRun: python train.py"
        )

    device = get_device(args.device)
    model, tokenizer = load_model(args.checkpoint, args.tokenizer, device)
    text = generate_text(
        model,
        tokenizer,
        args.prompt,
        device,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
    )
    print(text)


if __name__ == "__main__":
    main()
