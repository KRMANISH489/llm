"""
Mini-GPT LLM — single entry point.
Examples:
  python main.py train
  python main.py generate --prompt "Once upon a time"
  python main.py chat
  python main.py web
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_module(script: str, extra: list[str]) -> int:
    cmd = [sys.executable, str(ROOT / script), *extra]
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mini-GPT: train / generate / chat / web"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("train", help="Train the model", add_help=False)
    sub.add_parser("generate", help="Generate text", add_help=False)
    sub.add_parser("chat", help="CLI chat", add_help=False)
    sub.add_parser("web", help="Start web UI", add_help=False)

    # parse only the subcommand; forward the rest
    args, rest = parser.parse_known_args()
    mapping = {
        "train": "train.py",
        "generate": "generate.py",
        "chat": "chat.py",
        "web": "app.py",
    }
    raise SystemExit(run_module(mapping[args.cmd], rest))


if __name__ == "__main__":
    main()
