"""
Interactive CLI chat with the trained LLM.
Usage:
  python chat.py
  python chat.py --temperature 0.7
"""

from __future__ import annotations

import argparse
from pathlib import Path

from config import GenConfig, TrainConfig
from generate import generate_text, load_model
from train import get_device


def chat_loop(args: argparse.Namespace) -> None:
    if not Path(args.checkpoint).exists():
        raise SystemExit(
            f"Checkpoint not found: {args.checkpoint}\n"
            "Pehle train karein: python train.py"
        )

    device = get_device(args.device)
    model, tokenizer = load_model(args.checkpoint, args.tokenizer, device)
    print("=" * 50)
    print("Mini-GPT Chat  |  type 'exit' / 'quit' to leave")
    print("Commands: /temp 0.8  /topk 40  /tokens 150  /clear")
    print("=" * 50)

    history = ""
    temperature = args.temperature
    top_k = args.top_k
    top_p = args.top_p
    max_new_tokens = args.max_new_tokens

    while True:
        try:
            user = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user:
            continue
        if user.lower() in {"exit", "quit", "q"}:
            print("Bye!")
            break
        if user.startswith("/temp "):
            temperature = float(user.split(maxsplit=1)[1])
            print(f"temperature = {temperature}")
            continue
        if user.startswith("/topk "):
            top_k = int(user.split(maxsplit=1)[1])
            print(f"top_k = {top_k}")
            continue
        if user.startswith("/tokens "):
            max_new_tokens = int(user.split(maxsplit=1)[1])
            print(f"max_new_tokens = {max_new_tokens}")
            continue
        if user == "/clear":
            history = ""
            print("history cleared")
            continue

        prompt = history + f"User: {user}\nAssistant:"
        full = generate_text(
            model,
            tokenizer,
            prompt,
            device,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )
        # take only the new assistant continuation
        reply = full[len(prompt) :].split("User:")[0].strip()
        if not reply:
            reply = full[len(prompt) :].strip() or "(empty)"
        print(f"Bot> {reply}")
        history = prompt + " " + reply + "\n"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Chat with mini-GPT")
    p.add_argument("--checkpoint", default=str(TrainConfig().checkpoint_path))
    p.add_argument("--tokenizer", default=str(TrainConfig().tokenizer_path))
    p.add_argument("--device", default="cuda")
    p.add_argument("--temperature", type=float, default=GenConfig.temperature)
    p.add_argument("--top-k", type=int, default=GenConfig.top_k)
    p.add_argument("--top-p", type=float, default=GenConfig.top_p)
    p.add_argument("--max-new-tokens", type=int, default=GenConfig.max_new_tokens)
    return p.parse_args()


if __name__ == "__main__":
    chat_loop(parse_args())
