#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g2p_v1.py — BẢN G2P v1 (fail-closed): text → chuỗi profile kokoro178.

Cùng đường với bản gốc dùng trong dự án: t0 chuẩn hóa (luật thuần) → g2p_stream
→ ghép profile kiểu misaki (space giữa từ, dấu câu dính sát từ trước).
Trả (profile, errs) — errs ≠ rỗng nghĩa là câu có token cấm phát âm.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "01_g2p"))

from t0.pipeline import normalize as t1_normalize  # noqa: E402
import g2p as G  # noqa: E402
from profiles import load_vocab178  # noqa: E402

PUNCT_EMIT = {",", ".", "!", "?", ";", ":"}   # dấu câu giữ lại cho prosody


def text_to_profile(text: str):
    """text thô → (chuỗi profile kokoro178, errs)."""
    ir = t1_normalize(text)
    out = G.g2p_stream(ir)
    parts, errs = [], []
    if out.get("contract_errors"):
        errs.extend(out["contract_errors"])
    for rec in out.get("records", []):
        pd = rec.get("profile_debug") or {}
        rec_errs = (rec.get("contract_errors") or []) + \
            (rec.get("validation") or []) + (pd.get("errors") or [])
        control = rec.get("status") == "control"
        hard = [e for e in rec_errs if not control]
        if hard:
            errs.append(f"tok[{rec.get('i')}:{rec.get('surface','')[:20]}] {hard[0]}")
            continue
        if control:
            surf = rec.get("surface", "")
            if surf in PUNCT_EMIT and all(c in _vocab178() for c in surf):
                parts.append(("punct", surf))
            continue
        txt = pd.get("text", "")
        if txt:
            parts.append(("word", txt))
    pieces = []
    for kind, t in parts:
        if not pieces:
            pieces.append(t)
        elif kind == "punct":
            pieces.append(t)
        else:
            pieces.append(" " + t)
    return "".join(pieces), errs


_VOCAB178 = None


def _vocab178() -> set:
    global _VOCAB178
    if _VOCAB178 is None:
        chars, _n = load_vocab178()
        _VOCAB178 = chars
    return _VOCAB178
