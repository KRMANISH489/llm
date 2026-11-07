"""
Character-level tokenizer with optional byte-fallback.
Simple, fast, and enough to train a working mini-LLM from scratch.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


class CharTokenizer:
    PAD = "<PAD>"
    UNK = "<UNK>"
    BOS = "<BOS>"
    EOS = "<EOS>"
    SPECIAL = [PAD, UNK, BOS, EOS]

    def __init__(self, chars: Iterable[str] | None = None):
        chars = list(chars or [])
        # Stable order: special tokens first, then sorted unique chars
        vocab = list(self.SPECIAL)
        for c in sorted(set(chars)):
            if c not in vocab:
                vocab.append(c)
        self.itos = {i: c for i, c in enumerate(vocab)}
        self.stoi = {c: i for i, c in self.itos.items()}

    @property
    def vocab_size(self) -> int:
        return len(self.itos)

    @property
    def pad_id(self) -> int:
        return self.stoi[self.PAD]

    @property
    def unk_id(self) -> int:
        return self.stoi[self.UNK]

    @property
    def bos_id(self) -> int:
        return self.stoi[self.BOS]

    @property
    def eos_id(self) -> int:
        return self.stoi[self.EOS]

    def encode(self, text: str, add_bos: bool = False, add_eos: bool = False) -> list[int]:
        ids: list[int] = []
        if add_bos:
            ids.append(self.bos_id)
        ids.extend(self.stoi.get(c, self.unk_id) for c in text)
        if add_eos:
            ids.append(self.eos_id)
        return ids

    def decode(self, ids: Iterable[int], skip_special: bool = True) -> str:
        out = []
        for i in ids:
            tok = self.itos.get(int(i), self.UNK)
            if skip_special and tok in self.SPECIAL:
                continue
            out.append(tok)
        return "".join(out)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"itos": {str(k): v for k, v in self.itos.items()}}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "CharTokenizer":
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        itos = {int(k): v for k, v in payload["itos"].items()}
        tok = cls.__new__(cls)
        tok.itos = itos
        tok.stoi = {v: k for k, v in itos.items()}
        return tok

    @classmethod
    def from_text(cls, text: str) -> "CharTokenizer":
        return cls(chars=list(text))


class TikTokenWrapper:
    """Optional OpenAI tiktoken wrapper for larger pretrained-style vocab use."""

    def __init__(self, encoding_name: str = "gpt2"):
        import tiktoken

        self.enc = tiktoken.get_encoding(encoding_name)
        self.encoding_name = encoding_name

    @property
    def vocab_size(self) -> int:
        return self.enc.n_vocab

    def encode(self, text: str, add_bos: bool = False, add_eos: bool = False) -> list[int]:
        ids = self.enc.encode(text)
        # gpt2 has no dedicated bos/eos; keep API compatible
        return ids

    def decode(self, ids: Iterable[int], skip_special: bool = True) -> str:
        return self.enc.decode(list(ids))

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"type": "tiktoken", "encoding": self.encoding_name}, f)

    @classmethod
    def load(cls, path: str | Path) -> "TikTokenWrapper":
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        return cls(payload.get("encoding", "gpt2"))
