# -*- coding: utf-8 -*-
"""Backend Ульвара: API + отдача интерфейса. Стриминг, стоп, переписать,
картинки (зрение), файлы, авто-название, настройки."""
import os
import json
import threading

from flask import Flask, request, jsonify, Response, send_from_directory

import llm
import store
from persona import build_messages

BASE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.join(BASE, "ui")

app = Flask(__name__)
_stops = {}  # id диалога -> threading.Event


@app.after_request
def _no_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp


@app.route("/")
def index():
    return send_from_directory(UI, "index.html")


@app.route("/ui/<path:fname>")
def ui_files(fname):
    return send_from_directory(UI, fname)


@app.post("/api/unlock")
def unlock():
    pin = (request.get_json(force=True) or {}).get("pin", "")
    return jsonify(ok=(pin == store.get_settings().get("pin", "0000")))


@app.get("/api/status")
def status():
    s = store.get_settings()
    eng = s.get("engine", "local")
    model = s.get("api_model") if eng == "api" else s.get("model")
    return jsonify(ollama=llm.ensure_ollama(), model=model, engine=eng)


@app.get("/api/settings")
def settings_get():
    return jsonify(store.get_settings())


@app.post("/api/settings")
def settings_post():
    s = store.get_settings()
    data = request.get_json(force=True) or {}
    for k in ("model", "vision_model", "temperature", "system_prompt",
              "auto_model", "model_light", "model_heavy",
              "agent_mode", "allow_dangerous", "tavily_key", "user_name",
              "theme", "lang", "engine", "api_base", "api_key", "api_model",
              "reply_match"):
        if k in data:
            s[k] = data[k]
    store.save_settings(s)
    return jsonify(ok=True, settings=s)


@app.get("/api/models")
def models():
    s = store.get_settings()
    return jsonify(models=llm.list_models(), current=s.get("model"))


@app.post("/api/search")
def search():
    q = (request.get_json(force=True) or {}).get("q", "")
    try:
        import smartsearch
        return jsonify(results=smartsearch.search(q))
    except Exception as e:
        return jsonify(results=[], error=str(e))


@app.get("/api/skills")
def skills_list():
    try:
        import skills
        items = [{"name": n, "desc": m["desc"], "category": m["category"]}
                 for n, m in sorted(skills.SKILLS.items())]
        return jsonify(count=len(items), skills=items)
    except Exception as e:
        return jsonify(count=0, skills=[], error=str(e))


@app.get("/api/conversations")
def conversations():
    return jsonify(store.list_convs())


@app.post("/api/conversations")
def conv_new():
    return jsonify(store.new_conv())


@app.get("/api/conversations/<cid>")
def conv_get(cid):
    c = store.get_conv(cid)
    return (jsonify(c) if c else (jsonify(error="not found"), 404))


@app.delete("/api/conversations/<cid>")
def conv_del(cid):
    return jsonify(ok=store.delete_conv(cid))


@app.post("/api/conversations/clear")
def conv_clear():
    return jsonify(ok=True, removed=store.clear_all_convs())


# ---------- Проекты ----------
@app.get("/api/projects")
def projects_list():
    return jsonify(store.list_projects())


@app.post("/api/projects")
def project_new():
    d = request.get_json(force=True) or {}
    return jsonify(store.new_project(d.get("name", ""), d.get("instructions", "")))


@app.get("/api/projects/<pid>")
def project_get(pid):
    p = store.get_project(pid)
    return (jsonify(p) if p else (jsonify(error="not found"), 404))


@app.put("/api/projects/<pid>")
def project_update(pid):
    d = request.get_json(force=True) or {}
    p = store.update_project(pid, d)
    return (jsonify(p) if p else (jsonify(error="not found"), 404))


@app.delete("/api/projects/<pid>")
def project_del(pid):
    return jsonify(ok=store.delete_project(pid))


@app.post("/api/recent")
def recent_push():
    cid = (request.get_json(force=True) or {}).get("id")
    store.push_recent(cid)
    return jsonify(ok=True)


@app.get("/api/recent")
def recent_list():
    return jsonify(store.list_recent())


@app.delete("/api/recent/<cid>")
def recent_del(cid):
    store.remove_recent(cid)
    return jsonify(ok=True)


@app.post("/api/stop")
def stop():
    cid = (request.get_json(force=True) or {}).get("id")
    ev = _stops.get(cid)
    if ev:
        ev.set()
    return jsonify(ok=True)


def _clean_b64(img):
    if "," in img and img.strip().startswith("data:"):
        return img.split(",", 1)[1]
    return img


_WEB_KW = [
    "сколько", "какой", "какая", "каков", "когда ", "кто так", "что так", "курс",
    "погод", "новост", "цена", "стоит", "населени", "на данный момент", "сейчас",
    "последн", "в этом году", "2024", "2025", "2026", "результат", "президент",
    "ввп", "сколько стоит", "в каком году", "where", "who is", "how much",
]


def _needs_web(text):
    t = (text or "").lower()
    if len(t) < 8:
        return False
    return any(k in t for k in _WEB_KW)


def _parse_sources(text):
    out = []
    if "ИСТОЧНИКИ:" in text:
        for line in text.split("ИСТОЧНИКИ:", 1)[1].strip().splitlines():
            if "|" in line:
                t, u = line.split("|", 1)
                if u.strip().startswith("http"):
                    out.append({"title": t.strip(), "url": u.strip()})
    return out


def lang_instruction(s):
    """Как Ульвару выбирать язык ответа (общее для чата и агента)."""
    if s.get("reply_match", True):
        return ("Отвечай на том же языке, на котором написано последнее сообщение пользователя "
                "(Reply in the same language as the user's last message).")
    return "Always answer in English." if s.get("lang") == "en" else "Всегда отвечай по-русски."


def _flatten(history):
    """Приводит историю к чистому виду для модели (склеивает контекст файлов)."""
    out = []
    for m in history:
        if m["role"] == "user" and m.get("context"):
            out.append({"role": "user", "content": m["context"] + "\n\n" + m.get("content", "")})
        else:
            out.append({"role": m["role"], "content": m.get("content", "")})
    return out


def _stream(conv, images=None, web_context=None, sources=None):
    """Общий генератор ответа: строит сообщения, стримит, сохраняет."""
    s = store.get_settings()
    mem = list(store.get_memory())
    nm = s.get("user_name", "").strip()
    if nm:
        mem.append(f"Пользователя зовут {nm}. Обращайся к нему по имени.")
    msgs = build_messages(_flatten(conv["messages"]), mem, s.get("system_prompt", ""))
    msgs.insert(1, {"role": "system", "content": lang_instruction(s)})
    # инструкции проекта, если диалог принадлежит проекту
    pid = conv.get("project")
    if pid:
        pr = store.get_project(pid)
        if pr and (pr.get("instructions") or "").strip():
            msgs.insert(2, {"role": "system",
                            "content": "Контекст проекта «" + pr.get("name", "") + "»:\n"
                                       + pr["instructions"].strip()})
    if web_context:
        msgs.insert(1, {"role": "system",
                        "content": "Свежие результаты поиска в интернете по вопросу пользователя:\n"
                                   + web_context + "\n\nОтветь на вопрос КРАТКО на их основе. "
                                   "Не выдумывай. НЕ вставляй ссылки и URL в ответ."})
    last_user = next((m.get("content", "") for m in reversed(conv["messages"]) if m.get("role") == "user"), "")
    model = llm.pick_model(last_user, s)
    if images:
        model = s.get("vision_model") or model
        last = dict(msgs[-1]); last["images"] = [_clean_b64(x) for x in images]
        msgs = msgs[:-1] + [last]

    ev = threading.Event()
    _stops[conv["id"]] = ev

    def gen():
        if sources:
            yield f"data: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"
        full = ""
        for chunk in llm.stream_chat(msgs, model, s.get("temperature", 0.7), ev.is_set, settings=s):
            full += chunk
            yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
        amsg = {"role": "assistant", "content": full}
        if sources:
            amsg["sources"] = sources
        conv["messages"].append(amsg)
        store.save_conv(conv)
        _stops.pop(conv["id"], None)
        yield f"data: {json.dumps({'done': True, 'id': conv['id']}, ensure_ascii=False)}\n\n"

    return Response(gen(), mimetype="text/event-stream")


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True) or {}
    cid = data.get("id")
    text = (data.get("message") or "").strip()
    images = data.get("images") or []
    files = data.get("files") or []  # [{name, text}]

    conv = store.get_conv(cid) if cid else None
    if conv is None:
        conv = store.new_conv()
        proj = data.get("project")
        if proj:
            conv["project"] = proj

    # Контекст из файлов (виден модели, но не засоряет пузырь)
    ctx = "\n\n".join(
        f"Содержимое файла «{f.get('name','файл')}»:\n```\n{f.get('text','')}\n```"
        for f in files
    )
    atts = [{"name": f.get("name", "файл"), "kind": "file"} for f in files]
    atts += [{"name": "изображение", "kind": "image"} for _ in images]

    conv["messages"].append({
        "role": "user", "content": text,
        "context": ctx, "attachments": atts, "has_image": bool(images),
    })
    store.save_conv(conv)
    # обычный чат сам ищет в интернете, если вопрос про свежие факты
    web_context, sources = None, None
    if not images and _needs_web(text):
        try:
            import skills
            raw = skills.run_skill("web_search_results", text, 5)
            if raw and "не найдено" not in raw:
                web_context = raw.split("ИСТОЧНИКИ:", 1)[0].strip()
                sources = _parse_sources(raw)
        except Exception:
            pass
    return _stream(conv, images=images, web_context=web_context, sources=sources)


@app.post("/api/agent")
def agent_run():
    """Агентный режим: модель выполняет действия на ПК через навыки."""
    import agent
    data = request.get_json(force=True) or {}
    cid = data.get("id")
    text = (data.get("message") or "").strip()
    allow = bool(store.get_settings().get("allow_dangerous", False))
    conv = store.get_conv(cid) if cid else None
    if conv is None:
        conv = store.new_conv()
        proj = data.get("project")
        if proj:
            conv["project"] = proj
    conv["messages"].append({"role": "user", "content": text})
    if conv.get("title") in (None, "", "Новый диалог"):
        conv["title"] = (text[:40] + ("…" if len(text) > 40 else "")) or "Задача"
    store.save_conv(conv)

    hist = _flatten(conv["messages"])
    pid = conv.get("project")
    if pid:
        pr = store.get_project(pid)
        if pr and (pr.get("instructions") or "").strip():
            hist = [{"role": "system", "content": "Контекст проекта «" + pr.get("name", "")
                     + "»:\n" + pr["instructions"].strip()}] + hist

    def gen():
        for ev in agent.run_agent_stream(hist, allow_dangerous=allow):
            if "status" in ev:
                yield f"data: {json.dumps({'status': ev['status']}, ensure_ascii=False)}\n\n"
            if "answer" in ev:
                src = ev.get("sources") or []
                amsg = {"role": "assistant", "content": ev["answer"], "actions": ev.get("actions")}
                if src:
                    amsg["sources"] = src
                conv["messages"].append(amsg)
                store.save_conv(conv)
                yield f"data: {json.dumps({'answer': ev['answer'], 'sources': src, 'id': conv['id']}, ensure_ascii=False)}\n\n"

    return Response(gen(), mimetype="text/event-stream")


@app.post("/api/regenerate")
def regenerate():
    cid = (request.get_json(force=True) or {}).get("id")
    conv = store.get_conv(cid)
    if not conv or not conv["messages"]:
        return jsonify(error="empty"), 400
    if conv["messages"][-1]["role"] == "assistant":
        conv["messages"].pop()
        store.save_conv(conv)
    return _stream(conv)


@app.post("/api/title")
def title():
    cid = (request.get_json(force=True) or {}).get("id")
    conv = store.get_conv(cid)
    if not conv or not conv["messages"]:
        return jsonify(title="")
    s = store.get_settings()
    convo = "\n".join(f"{m['role']}: {m['content'][:400]}" for m in conv["messages"][:4])
    prompt = [
        {"role": "system", "content": "Ты придумываешь короткие понятные названия для диалогов на русском."},
        {"role": "user", "content": f"Вот начало диалога:\n{convo}\n\nПридумай название из 2-4 слов (слова ОБЯЗАТЕЛЬНО через пробелы). Ответь только названием, без кавычек и точки."},
    ]
    raw = llm.complete(prompt, s.get("model"), settings=s) or ""
    t = raw.strip().strip('"\'«».').split("\n")[0]
    first_user = next((m["content"] for m in conv["messages"] if m.get("role") == "user"), "")
    # если модель слепила слова без пробелов, пусто или слишком длинно — берём начало сообщения
    if (not t) or len(t) > 42 or (" " not in t and len(t) > 16):
        t = first_user.strip()[:40] or "Диалог"
    conv["title"] = t[:42]
    store.save_conv(conv)
    return jsonify(title=conv["title"])


def run(port=5099):
    app.run(host="127.0.0.1", port=port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    run()
