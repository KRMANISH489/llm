"""Generate project documentation PowerPoint."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Colors
BG = RGBColor(0x0C, 0x12, 0x10)
CARD = RGBColor(0x14, 0x20, 0x1A)
ACCENT = RGBColor(0x3E, 0xCF, 0x8E)
GOLD = RGBColor(0xF0, 0xB4, 0x29)
INK = RGBColor(0xE8, 0xF2, 0xEC)
MUTED = RGBColor(0x8A, 0xA3, 0x96)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x04, 0x14, 0x0C)


def set_slide_bg(slide, color):
    fill = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    fill.fill.solid()
    fill.fill.fore_color.rgb = color
    fill.line.fill.background()
    # send to back
    spTree = slide.shapes._spTree
    sp = fill._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def add_textbox(slide, left, top, width, height, text, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Calibri"):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font
    p.alignment = align
    return tf


def add_bullet_block(slide, left, top, width, height, lines, size=16, color=INK, spacing=6):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.name = "Calibri"
        p.space_after = Pt(spacing)
        p.level = 0
    return tf


def accent_bar(slide):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), prs.slide_height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()


def footer(slide, page, total=14):
    add_textbox(slide, 0.5, 7.05, 8, 0.3, "Mini-GPT LLM Project Documentation", size=11, color=MUTED)
    add_textbox(slide, 11.5, 7.05, 1.5, 0.3, f"{page} / {total}", size=11, color=MUTED, align=PP_ALIGN.RIGHT)


def card(slide, left, top, width, height):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD
    shape.line.color.rgb = RGBColor(0x2A, 0x3A, 0x32)
    shape.adjustments[0] = 0.08
    return shape


# ---------- SLIDE 1: Title ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.8, 2.0, 11.5, 1, "Mini-GPT LLM", size=48, bold=True, color=ACCENT)
add_textbox(s, 0.8, 3.0, 11.5, 0.6, "Complete Project Documentation", size=28, color=INK)
add_textbox(
    s, 0.8, 3.8, 11, 1.2,
    "File-by-file explanation • Why each part is needed • How frontend & backend merge",
    size=18, color=MUTED,
)
add_textbox(s, 0.8, 5.5, 11, 0.4, "From-scratch decoder-only Transformer  |  Train • Generate • Chat • Web UI", size=14, color=GOLD)
footer(s, 1)

# ---------- SLIDE 2: Agenda ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "Agenda", size=32, bold=True, color=ACCENT)
items = [
    "1.  Project overview & architecture",
    "2.  Core ML files (model, tokenizer, dataset, config)",
    "3.  Training & inference files (train, generate, evaluate)",
    "4.  Interfaces (CLI chat, Flask API, web frontend)",
    "5.  Why each file is needed",
    "6.  How frontend and backend merge",
    "7.  End-to-end data flow & how to run",
]
add_bullet_block(s, 0.8, 1.2, 11, 5.2, items, size=20, spacing=12)
footer(s, 2)

# ---------- SLIDE 3: Overview ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "1. Project Overview", size=32, bold=True, color=ACCENT)
add_textbox(
    s, 0.6, 1.1, 12, 0.8,
    "A complete mini Large Language Model (LLM) built from scratch in Python/PyTorch, "
    "with training, generation, CLI chat, REST API, and a web chat UI.",
    size=16, color=INK,
)
boxes = [
    (0.6, 2.1, "CORE", "Transformer GPT model\nTokenizer + Dataset\nConfig & checkpoints"),
    (3.7, 2.1, "TRAIN / RUN", "train.py\ngenerate.py\nevaluate.py\nmain.py"),
    (6.8, 2.1, "BACKEND", "Flask app.py\n/api/chat\n/api/generate\n/api/health"),
    (9.9, 2.1, "FRONTEND", "static/index.html\nChat UI\nControls\nFetch API"),
]
for left, top, title, body in boxes:
    card(s, left, top, 2.9, 3.4)
    add_textbox(s, left + 0.2, top + 0.25, 2.5, 0.4, title, size=16, bold=True, color=GOLD)
    add_textbox(s, left + 0.2, top + 0.9, 2.5, 2.2, body, size=14, color=INK)
footer(s, 3)

# ---------- SLIDE 4: Architecture ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "Architecture (High Level)", size=32, bold=True, color=ACCENT)
flow = [
    "corpus.txt  →  tokenizer  →  dataset batches",
    "model.py (GPT)  ← trained by →  train.py  →  checkpoints/best.pt",
    "generate.py / chat.py / app.py  load checkpoint + tokenizer",
    "Browser (index.html)  ↔  HTTP JSON  ↔  Flask (app.py)  ↔  GPT.generate()",
]
add_bullet_block(s, 0.8, 1.3, 11.5, 3.5, [f"•  {x}" for x in flow], size=18, spacing=14)
add_textbox(
    s, 0.8, 5.2, 11.5, 1.2,
    "Key idea: The neural network is shared. Training writes weights. Chat/Web only load weights and call generate(). "
    "The frontend never talks to PyTorch directly — it talks to Flask.",
    size=15, color=MUTED,
)
footer(s, 4)

# ---------- SLIDE 5: Config & requirements ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "2. Foundation Files", size=32, bold=True, color=ACCENT)

card(s, 0.5, 1.15, 6.0, 5.2)
add_textbox(s, 0.75, 1.35, 5.5, 0.4, "config.py", size=22, bold=True, color=GOLD)
add_bullet_block(s, 0.75, 1.9, 5.5, 4.2, [
    "What it does:",
    "• Defines ModelConfig (layers, heads, embed size, context)",
    "• Defines TrainConfig (LR, batch, iters, paths)",
    "• Defines GenConfig (temperature, top-k, top-p)",
    "• Sets DATA_DIR / CHECKPOINT_DIR paths",
    "• Helpers: save_json / load_json",
    "",
    "Why needed:",
    "• Single source of truth — no magic numbers scattered",
    "• Easy to scale model or change training safely",
], size=14, spacing=4)

card(s, 6.8, 1.15, 6.0, 5.2)
add_textbox(s, 7.05, 1.35, 5.5, 0.4, "requirements.txt", size=22, bold=True, color=GOLD)
add_bullet_block(s, 7.05, 1.9, 5.5, 4.2, [
    "What it does:",
    "• Lists Python dependencies:",
    "  torch, numpy, tqdm, tiktoken,",
    "  flask, flask-cors",
    "",
    "Why needed:",
    "• Reproducible installs for any machine",
    "• Separates ML stack (torch) from web stack (flask)",
    "",
    "Install:",
    "  pip install -r requirements.txt",
], size=14, spacing=4)
footer(s, 5)

# ---------- SLIDE 6: Tokenizer & Dataset ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "Tokenizer & Dataset", size=32, bold=True, color=ACCENT)

card(s, 0.5, 1.15, 6.0, 5.2)
add_textbox(s, 0.75, 1.35, 5.5, 0.4, "tokenizer.py", size=22, bold=True, color=GOLD)
add_bullet_block(s, 0.75, 1.9, 5.5, 4.2, [
    "What it does:",
    "• CharTokenizer: maps characters ↔ IDs",
    "• Special tokens: PAD, UNK, BOS, EOS",
    "• encode() / decode() / save() / load()",
    "• Optional TikTokenWrapper (GPT-2 BPE)",
    "",
    "Why needed:",
    "• Neural nets need numbers, not raw text",
    "• Same tokenizer must be used at train & chat time",
    "• Saved to checkpoints/tokenizer.json",
], size=14, spacing=4)

card(s, 6.8, 1.15, 6.0, 5.2)
add_textbox(s, 7.05, 1.35, 5.5, 0.4, "dataset.py + data/corpus.txt", size=20, bold=True, color=GOLD)
add_bullet_block(s, 7.05, 1.9, 5.5, 4.2, [
    "What it does:",
    "• Loads training text from corpus.txt",
    "• Builds tokenizer from corpus characters",
    "• Splits into train (90%) / val (10%)",
    "• get_batch(): random context windows",
    "",
    "Why needed:",
    "• LLMs learn by next-token prediction",
    "• Batches feed (input X, target Y=X shifted)",
    "• Better corpus → better model quality",
], size=14, spacing=4)
footer(s, 6)

# ---------- SLIDE 7: Model ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "model.py — The Brain", size=32, bold=True, color=ACCENT)
add_textbox(
    s, 0.6, 1.05, 12, 0.5,
    "Decoder-only Transformer (mini-GPT). This is the actual LLM.",
    size=16, color=MUTED,
)
parts = [
    ("CausalSelfAttention", "Each token attends only to past tokens (causal mask). Multi-head Q/K/V."),
    ("MLP", "Feed-forward expansion (4×) with GELU — per-token processing."),
    ("Block", "LayerNorm → Attention → residual → LayerNorm → MLP → residual."),
    ("GPT", "Token + position embeddings → N blocks → LayerNorm → lm_head logits."),
    ("generate()", "Autoregressive sampling with temperature, top-k, top-p, EOS stop."),
]
y = 1.6
for title, desc in parts:
    card(s, 0.5, y, 12.3, 0.9)
    add_textbox(s, 0.75, y + 0.12, 3.2, 0.6, title, size=16, bold=True, color=ACCENT)
    add_textbox(s, 4.0, y + 0.18, 8.5, 0.6, desc, size=14, color=INK)
    y += 1.0
footer(s, 7)

# ---------- SLIDE 8: Train / Generate / Evaluate ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "Training & Inference Scripts", size=32, bold=True, color=ACCENT)

cols = [
    (0.45, "train.py", [
        "Builds model + optimizer",
        "Warmup + cosine LR schedule",
        "AMP optional on CUDA",
        "Eval every N steps",
        "Saves best.pt checkpoint",
        "WHY: Turns corpus into learned weights",
    ]),
    (4.55, "generate.py", [
        "Loads checkpoint + tokenizer",
        "Encodes prompt to IDs",
        "Calls model.generate()",
        "Decodes IDs back to text",
        "CLI flags: temp, top-k, tokens",
        "WHY: One-shot text completion",
    ]),
    (8.65, "evaluate.py", [
        "Computes validation loss",
        "Reports perplexity (ppl)",
        "Prints sample generations",
        "Sanity-check quality",
        "",
        "WHY: Measure if training worked",
    ]),
]
for left, title, lines in cols:
    card(s, left, 1.2, 3.9, 5.2)
    add_textbox(s, left + 0.2, 1.4, 3.5, 0.4, title, size=20, bold=True, color=GOLD)
    add_bullet_block(s, left + 0.2, 2.0, 3.5, 4.0, [f"• {x}" if x else "" for x in lines], size=13, spacing=6)
footer(s, 8)

# ---------- SLIDE 9: Chat + main ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "CLI Interfaces", size=32, bold=True, color=ACCENT)

card(s, 0.5, 1.15, 6.0, 5.2)
add_textbox(s, 0.75, 1.35, 5.5, 0.4, "chat.py", size=22, bold=True, color=GOLD)
add_bullet_block(s, 0.75, 1.9, 5.5, 4.2, [
    "What it does:",
    "• Interactive terminal chat loop",
    "• Keeps conversation history string",
    "• Prompt format: User: … / Assistant:",
    "• Runtime commands: /temp /topk /tokens /clear",
    "",
    "Why needed:",
    "• Fast local testing without a browser",
    "• Same generation logic as the web API",
], size=14, spacing=4)

card(s, 6.8, 1.15, 6.0, 5.2)
add_textbox(s, 7.05, 1.35, 5.5, 0.4, "main.py", size=22, bold=True, color=GOLD)
add_bullet_block(s, 7.05, 1.9, 5.5, 4.2, [
    "What it does:",
    "• Single CLI entry point / router",
    "• Subcommands:",
    "    python main.py train",
    "    python main.py generate",
    "    python main.py chat",
    "    python main.py web",
    "",
    "Why needed:",
    "• One place to discover all features",
    "• Cleaner than remembering many scripts",
], size=14, spacing=4)
footer(s, 9)

# ---------- SLIDE 10: Backend ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "Backend — app.py (Flask)", size=32, bold=True, color=ACCENT)
add_textbox(
    s, 0.6, 1.05, 12, 0.45,
    "Flask serves both the HTML page and JSON APIs. It loads the GPT model once into memory.",
    size=15, color=MUTED,
)

apis = [
    ("GET /", "Serves static/index.html (the frontend UI)"),
    ("GET /api/health", "Checks if checkpoint exists & model loaded; returns device"),
    ("POST /api/generate", "Body: {prompt, temperature, top_k, …} → {text}"),
    ("POST /api/chat", "Body: {message, history, …} → {reply, history}"),
]
y = 1.65
for title, desc in apis:
    card(s, 0.5, y, 12.3, 1.0)
    add_textbox(s, 0.75, y + 0.22, 3.5, 0.55, title, size=16, bold=True, color=ACCENT)
    add_textbox(s, 4.3, y + 0.25, 8.2, 0.55, desc, size=14, color=INK)
    y += 1.15
footer(s, 10)

# ---------- SLIDE 11: Frontend ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "Frontend — static/index.html", size=32, bold=True, color=ACCENT)

card(s, 0.5, 1.2, 6.0, 5.1)
add_textbox(s, 0.75, 1.4, 5.5, 0.4, "What it does", size=20, bold=True, color=GOLD)
add_bullet_block(s, 0.75, 2.0, 5.5, 4.0, [
    "• Chat message list (You / Bot bubbles)",
    "• Input form + Send button",
    "• Controls: temperature, top-k, tokens",
    "• On load: fetch /api/health",
    "• On send: POST /api/chat with JSON",
    "• Updates history from API response",
    "• Pure HTML/CSS/JS — no React build step",
], size=14, spacing=6)

card(s, 6.8, 1.2, 6.0, 5.1)
add_textbox(s, 7.05, 1.4, 5.5, 0.4, "Why needed", size=20, bold=True, color=GOLD)
add_bullet_block(s, 7.05, 2.0, 5.5, 4.0, [
    "• Friendly UI for non-terminal users",
    "• Demonstrates real client ↔ server use",
    "• Separates presentation from ML logic",
    "• Easy to restyle without touching PyTorch",
    "",
    "Tech:",
    "• fetch() for HTTP",
    "• JSON request/response",
    "• CORS enabled in Flask for flexibility",
], size=14, spacing=6)
footer(s, 11)

# ---------- SLIDE 12: Merge FE/BE ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "How Frontend & Backend Merge", size=30, bold=True, color=ACCENT)

steps = [
    ("1. Start backend", "python main.py web   →  Flask listens on http://127.0.0.1:5000"),
    ("2. Load UI", "Browser opens /  →  Flask sends static/index.html"),
    ("3. Health check", "JS calls GET /api/health  →  Backend loads best.pt if needed"),
    ("4. User sends chat", "JS POST /api/chat with {message, history, temperature, …}"),
    ("5. Model runs", "app.py builds prompt → generate_text() → GPT sampling on CPU/GPU"),
    ("6. Response", "JSON {reply, history}  →  Frontend appends Bot bubble & stores history"),
]
y = 1.15
for title, desc in steps:
    add_textbox(s, 0.7, y, 2.8, 0.45, title, size=15, bold=True, color=ACCENT)
    add_textbox(s, 3.5, y, 9.2, 0.55, desc, size=14, color=INK)
    y += 0.85
footer(s, 12)

# ---------- SLIDE 13: Merge diagram detail ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "Merge Contract (API Contract)", size=30, bold=True, color=ACCENT)

card(s, 0.5, 1.15, 6.0, 5.2)
add_textbox(s, 0.75, 1.35, 5.5, 0.4, "Request (Frontend → Backend)", size=16, bold=True, color=GOLD)
add_textbox(
    s, 0.75, 1.95, 5.5, 4.0,
    'POST /api/chat\nContent-Type: application/json\n\n{\n  "message": "What is an LLM?",\n  "history": "",\n  "temperature": 0.8,\n  "top_k": 50,\n  "max_new_tokens": 160\n}',
    size=13, color=INK, font="Consolas",
)

card(s, 6.8, 1.15, 6.0, 5.2)
add_textbox(s, 7.05, 1.35, 5.5, 0.4, "Response (Backend → Frontend)", size=16, bold=True, color=GOLD)
add_textbox(
    s, 7.05, 1.95, 5.5, 4.0,
    '{\n  "reply": "An LLM predicts text…",\n  "history": "User: What is an LLM?\\nAssistant: An LLM predicts text…\\n"\n}\n\n• reply → shown in UI\n• history → kept in JS variable\n  for multi-turn chat\n• No PyTorch objects cross the wire\n  — only JSON strings/numbers',
    size=13, color=INK, font="Consolas",
)
footer(s, 13)

# ---------- SLIDE 14: Why needed summary + run ----------
s = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(s, BG)
accent_bar(s)
add_textbox(s, 0.6, 0.35, 12, 0.6, "Why Each Layer Exists + How to Run", size=28, bold=True, color=ACCENT)

add_bullet_block(s, 0.7, 1.15, 12, 3.2, [
    "• Model/Tokenizer/Dataset — Learning engine (no UI needed to train)",
    "• train.py — Produces weights (best.pt); without this, chat has nothing to load",
    "• generate/chat — Local ways to use the model without a server",
    "• app.py — Backend bridge: HTTP ↔ PyTorch; enables browsers & other clients",
    "• index.html — Frontend UX; talks only to JSON APIs (clean separation)",
    "• main.py — Convenience router so users run one command family",
], size=15, spacing=8)

card(s, 0.5, 4.5, 12.3, 2.0)
add_textbox(s, 0.75, 4.65, 11.8, 0.35, "Quick start", size=16, bold=True, color=GOLD)
add_textbox(
    s, 0.75, 5.1, 11.8, 1.2,
    "pip install -r requirements.txt\n"
    "python main.py train --device cpu --max-iters 3000\n"
    "python main.py web          # open http://127.0.0.1:5000",
    size=14, color=INK, font="Consolas",
)
footer(s, 14)

out = r"d:\test\LLM\MiniGPT_LLM_Documentation.pptx"
prs.save(out)
print("Saved:", out)
