"""
Web UI + REST API for the trained LLM.
Usage:
  python app.py
  open http://127.0.0.1:5000
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import GenConfig, TrainConfig
from generate import generate_text, load_model
from train import get_device

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

_state: dict = {"model": None, "tokenizer": None, "device": None, "error": None}


def ensure_loaded() -> None:
    if _state["model"] is not None:
        return
    ckpt = Path(TrainConfig().checkpoint_path)
    tok = Path(TrainConfig().tokenizer_path)
    if not ckpt.exists():
        _state["error"] = "Model not trained yet. Run: python train.py"
        return
    device = get_device("cuda")
    model, tokenizer = load_model(ckpt, tok, device)
    _state.update(model=model, tokenizer=tokenizer, device=device, error=None)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    ensure_loaded()
    return jsonify(
        {
            "ok": _state["error"] is None,
            "error": _state["error"],
            "device": str(_state["device"]) if _state["device"] else None,
        }
    )


@app.post("/api/generate")
def api_generate():
    ensure_loaded()
    if _state["error"]:
        return jsonify({"error": _state["error"]}), 400
    data = request.get_json(force=True) or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "prompt required"}), 400
    text = generate_text(
        _state["model"],
        _state["tokenizer"],
        prompt,
        _state["device"],
        max_new_tokens=int(data.get("max_new_tokens", GenConfig.max_new_tokens)),
        temperature=float(data.get("temperature", GenConfig.temperature)),
        top_k=int(data.get("top_k", GenConfig.top_k)),
        top_p=float(data.get("top_p", GenConfig.top_p)),
    )
    return jsonify({"text": text})


@app.post("/api/chat")
def api_chat():
    ensure_loaded()
    if _state["error"]:
        return jsonify({"error": _state["error"]}), 400
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or ""
    if not message:
        return jsonify({"error": "message required"}), 400
    prompt = history + f"User: {message}\nAssistant:"
    full = generate_text(
        _state["model"],
        _state["tokenizer"],
        prompt,
        _state["device"],
        max_new_tokens=int(data.get("max_new_tokens", GenConfig.max_new_tokens)),
        temperature=float(data.get("temperature", GenConfig.temperature)),
        top_k=int(data.get("top_k", GenConfig.top_k)),
        top_p=float(data.get("top_p", GenConfig.top_p)),
    )
    reply = full[len(prompt) :].split("User:")[0].strip() or full[len(prompt) :].strip()
    new_history = prompt + " " + reply + "\n"
    return jsonify({"reply": reply, "history": new_history})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
