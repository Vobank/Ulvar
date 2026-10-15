# -*- coding: utf-8 -*-
"""Умный поиск по диалогам: ключевые слова + смысловой поиск через эмбеддинги (bge-m3)."""
import os
import json
import math
import hashlib
import requests

import store

OLLAMA = "http://127.0.0.1:11434"
EMB_MODEL = "bge-m3"
CACHE = os.path.join(store.DATA, "emb_cache.json")


def _embed(text):
    try:
        r = requests.post(f"{OLLAMA}/api/embeddings",
                          json={"model": EMB_MODEL, "prompt": text[:4000]}, timeout=60)
        return r.json().get("embedding")
    except Exception:
        return None


def _cos(a, b):
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _load_cache():
    try:
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(c):
    try:
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(c, f)
    except Exception:
        pass


def search(q, top=20):
    q = (q or "").strip()
    if not q:
        return []
    metas = store.list_convs()
    cache = _load_cache()
    qv = _embed(q)
    ql = q.lower()
    results = []
    for meta in metas:
        conv = store.get_conv(meta["id"])
        if not conv:
            continue
        msgs = conv.get("messages", [])
        text = " ".join(m.get("content", "") for m in msgs)
        tl = text.lower()
        # ключевое совпадение
        kw = ql in tl or ql in meta["title"].lower()
        score = 0.0
        # смысловое совпадение
        if qv:
            h = hashlib.md5(text.encode("utf-8")).hexdigest()
            ent = cache.get(meta["id"])
            if ent and ent.get("h") == h:
                v = ent.get("v")
            else:
                v = _embed(text)
                if v:
                    cache[meta["id"]] = {"h": h, "v": v}
            score = _cos(qv, v) if v else 0.0
        if kw:
            score = max(score, 0.55) + 0.25
        # сниппет: сообщение с ключевым словом, иначе первое пользовательское
        snippet = ""
        for m in msgs:
            c = m.get("content", "")
            if ql in c.lower():
                i = c.lower().find(ql)
                snippet = ("…" if i > 20 else "") + c[max(0, i - 20):i + 80]
                break
        if not snippet:
            snippet = next((m.get("content", "") for m in msgs if m.get("role") == "user"), "")[:90]
        results.append({"id": meta["id"], "title": meta["title"], "updated": meta["updated"],
                        "score": round(score, 3), "snippet": snippet.strip()})
    _save_cache(cache)
    results = [r for r in results if r["score"] > 0.25]
    results.sort(key=lambda x: -x["score"])
    return results[:top]
