# -*- coding: utf-8 -*-
"""Шифрованное хранилище: переписка, память, настройки.
Переписка и память шифруются (AES через Fernet). Ключ лежит локально.
ПИН — только замок на вход (простой 0000), шифрование — отдельно, на уровне файлов."""
import os
import json
import time
import uuid

from cryptography.fernet import Fernet

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
CONV_DIR = os.path.join(DATA, "conversations")
KEY_FILE = os.path.join(DATA, ".key")
MEM_FILE = os.path.join(DATA, "memory.enc")
SETTINGS = os.path.join(DATA, "settings.json")
PROJECTS = os.path.join(DATA, "projects.enc")
RECENT = os.path.join(DATA, "recent.json")

DEFAULT_SETTINGS = {
    "model": "qwen2.5:14b-instruct",
    "vision_model": "qwen2.5vl:7b",
    "pin": "0000",
    "temperature": 0.7,
    "system_prompt": "",  # пусто = характер по умолчанию из persona.py
    "auto_model": False,                    # сам выбирать модель под задачу
    "model_light": "qwen2.5:14b-instruct",  # быстрая (простые задачи)
    "model_heavy": "qwen2.5:32b-instruct",  # умная (сложные задачи)
    "agent_mode": False,                    # режим агента (помнить состояние)
    "allow_dangerous": False,               # разрешить опасные действия без подтверждения
    "tavily_key": "",                       # ключ поискового API Tavily (опционально)
    "user_name": "Вова",                    # как обращаться к пользователю
    "theme": "system",                      # тема: system | light | dark
    "lang": "ru",                           # язык интерфейса: ru | en
    "reply_match": True,                     # отвечать на языке сообщения (иначе — на языке интерфейса)
    "engine": "local",                      # движок: local (Ollama) | api (облако)
    "api_base": "https://openrouter.ai/api/v1",  # базовый URL OpenAI-совместимого API
    "api_key": "",                          # ключ облачного API (для слабых ПК)
    "api_model": "meta-llama/llama-3.1-8b-instruct",  # модель в облаке
}


def clear_all_convs():
    _ensure()
    n = 0
    for name in os.listdir(CONV_DIR):
        if name.endswith(".enc"):
            try:
                os.remove(os.path.join(CONV_DIR, name)); n += 1
            except Exception:
                pass
    return n


def _ensure():
    os.makedirs(CONV_DIR, exist_ok=True)


def _fernet():
    _ensure()
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, "wb") as f:
            f.write(Fernet.generate_key())
    with open(KEY_FILE, "rb") as f:
        return Fernet(f.read())


def _enc(obj):
    return _fernet().encrypt(json.dumps(obj, ensure_ascii=False).encode("utf-8"))


def _dec(blob):
    return json.loads(_fernet().decrypt(blob).decode("utf-8"))


# ---------- Настройки ----------
def get_settings():
    _ensure()
    if os.path.exists(SETTINGS):
        try:
            with open(SETTINGS, encoding="utf-8") as f:
                s = json.load(f)
            return {**DEFAULT_SETTINGS, **s}
        except Exception:
            pass
    save_settings(DEFAULT_SETTINGS)
    return dict(DEFAULT_SETTINGS)


def save_settings(s):
    _ensure()
    with open(SETTINGS, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


# ---------- Переписка ----------
def _conv_path(cid):
    return os.path.join(CONV_DIR, f"{cid}.enc")


def new_conv():
    cid = uuid.uuid4().hex[:12]
    obj = {"id": cid, "title": "Новый диалог", "created": time.time(),
           "updated": time.time(), "messages": []}
    save_conv(obj)
    return obj


def save_conv(obj):
    obj["updated"] = time.time()
    with open(_conv_path(obj["id"]), "wb") as f:
        f.write(_enc(obj))


def get_conv(cid):
    p = _conv_path(cid)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "rb") as f:
            return _dec(f.read())
    except Exception:
        return None


def list_convs():
    _ensure()
    out = []
    for name in os.listdir(CONV_DIR):
        if name.endswith(".enc"):
            obj = get_conv(name[:-4])
            if obj:
                # пустые диалоги (без сообщений) авто-удаляем, чтобы не копились
                if not obj.get("messages"):
                    try:
                        os.remove(_conv_path(obj["id"]))
                    except Exception:
                        pass
                    continue
                out.append({"id": obj["id"], "title": obj.get("title", "Диалог"),
                            "updated": obj.get("updated", 0), "project": obj.get("project")})
    out.sort(key=lambda x: x["updated"], reverse=True)
    return out


# ---------- Проекты ----------
def list_projects():
    if not os.path.exists(PROJECTS):
        return []
    try:
        with open(PROJECTS, "rb") as f:
            lst = _dec(f.read())
        lst.sort(key=lambda x: x.get("updated", 0), reverse=True)
        return lst
    except Exception:
        return []


def save_projects(lst):
    _ensure()
    with open(PROJECTS, "wb") as f:
        f.write(_enc(lst))


def new_project(name, instructions=""):
    p = {"id": uuid.uuid4().hex[:12], "name": (name or "Проект").strip()[:60],
         "instructions": instructions or "", "created": time.time(), "updated": time.time()}
    lst = list_projects()
    lst.append(p)
    save_projects(lst)
    return p


def get_project(pid):
    for p in list_projects():
        if p["id"] == pid:
            return p
    return None


def update_project(pid, fields):
    lst = list_projects()
    for p in lst:
        if p["id"] == pid:
            if "name" in fields:
                p["name"] = (fields["name"] or p["name"]).strip()[:60]
            if "instructions" in fields:
                p["instructions"] = fields["instructions"] or ""
            p["updated"] = time.time()
            save_projects(lst)
            return p
    return None


def delete_project(pid):
    lst = list_projects()
    new = [p for p in lst if p["id"] != pid]
    save_projects(new)
    # отвязываем диалоги проекта (не удаляем их)
    for name in os.listdir(CONV_DIR):
        if name.endswith(".enc"):
            c = get_conv(name[:-4])
            if c and c.get("project") == pid:
                c["project"] = None
                save_conv(c)
    return len(new) != len(lst)


def delete_conv(cid):
    p = _conv_path(cid)
    if os.path.exists(p):
        os.remove(p)
        return True
    return False


# ---------- Недавно открытые (просмотренные) ----------
def _recent_ids():
    if not os.path.exists(RECENT):
        return []
    try:
        with open(RECENT, encoding="utf-8") as f:
            v = json.load(f)
        return v if isinstance(v, list) else []
    except Exception:
        return []


def _save_recent_ids(ids):
    _ensure()
    with open(RECENT, "w", encoding="utf-8") as f:
        json.dump(ids, f)


def push_recent(cid, cap=20):
    if not cid:
        return
    ids = [i for i in _recent_ids() if i != cid]
    ids.insert(0, cid)
    _save_recent_ids(ids[:cap])


def remove_recent(cid):
    _save_recent_ids([i for i in _recent_ids() if i != cid])


def list_recent():
    """Метаданные недавно открытых чатов (в порядке просмотра), только живые."""
    out, alive = [], []
    for cid in _recent_ids():
        c = get_conv(cid)
        if c and c.get("messages"):
            alive.append(cid)
            out.append({"id": c["id"], "title": c.get("title", "Диалог"),
                        "updated": c.get("updated", 0), "project": c.get("project")})
    if alive != _recent_ids():
        _save_recent_ids(alive)  # подчищаем удалённые
    return out


# ---------- Память ----------
def get_memory():
    if not os.path.exists(MEM_FILE):
        return []
    try:
        with open(MEM_FILE, "rb") as f:
            return _dec(f.read())
    except Exception:
        return []


def save_memory(facts):
    with open(MEM_FILE, "wb") as f:
        f.write(_enc(facts))


def add_memory(fact):
    facts = get_memory()
    if fact and fact not in facts:
        facts.append(fact)
        save_memory(facts)
