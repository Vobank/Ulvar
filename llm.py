# -*- coding: utf-8 -*-
"""Связь с моделью: локально через Ollama или по облачному API (OpenAI-совместимый).
Движок выбирается в настройках: engine = 'local' | 'api'. Режим API нужен для
слабых ПК, где большую модель локально не потянуть."""
import json
import requests

OLLAMA = "http://127.0.0.1:11434"
DEFAULT_API_BASE = "https://openrouter.ai/api/v1"


def _use_api(settings):
    return bool(settings and settings.get("engine") == "api" and settings.get("api_key"))


def _api_cfg(settings):
    base = (settings.get("api_base") or DEFAULT_API_BASE).rstrip("/")
    key = settings.get("api_key", "")
    model = settings.get("api_model") or "meta-llama/llama-3.1-8b-instruct"
    return base, key, model


def _clean_msgs(messages):
    """Для облачного API оставляем только текстовые поля (без картинок/служебных)."""
    out = []
    for m in messages:
        out.append({"role": m.get("role", "user"), "content": m.get("content", "") or ""})
    return out


def _api_stream(messages, settings, temperature, should_stop):
    base, key, model = _api_cfg(settings)
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": _clean_msgs(messages),
               "stream": True, "temperature": temperature}
    try:
        with requests.post(f"{base}/chat/completions", json=payload, headers=headers,
                           stream=True, timeout=600) as r:
            if r.status_code >= 400:
                yield f"\n\n⚠️ API ответил ошибкой {r.status_code}. Проверь ключ и модель в настройках."
                return
            for line in r.iter_lines():
                if should_stop and should_stop():
                    break
                if not line:
                    continue
                s = line.decode("utf-8").strip()
                if not s.startswith("data:"):
                    continue
                s = s[5:].strip()
                if s == "[DONE]":
                    break
                try:
                    obj = json.loads(s)
                    chunk = obj["choices"][0]["delta"].get("content", "")
                except Exception:
                    continue
                if chunk:
                    yield chunk
    except Exception as e:
        yield f"\n\n⚠️ Ошибка облачного API: {e}"


def _api_complete(messages, settings, temperature):
    base, key, model = _api_cfg(settings)
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": _clean_msgs(messages),
               "stream": False, "temperature": temperature}
    try:
        r = requests.post(f"{base}/chat/completions", json=payload, headers=headers, timeout=120)
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


def list_models():
    try:
        r = requests.get(f"{OLLAMA}/api/tags", timeout=10)
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


def stream_chat(messages, model, temperature=0.7, should_stop=None, settings=None):
    """Генератор: отдаёт куски текста ответа по мере генерации.
    should_stop() -> True прерывает генерацию. settings.engine='api' → облако."""
    if _use_api(settings):
        yield from _api_stream(messages, settings, temperature, should_stop)
        return
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature},
    }
    try:
        with requests.post(f"{OLLAMA}/api/chat", json=payload, stream=True, timeout=600) as r:
            for line in r.iter_lines():
                if should_stop and should_stop():
                    break
                if not line:
                    continue
                try:
                    obj = json.loads(line.decode("utf-8"))
                except Exception:
                    continue
                chunk = obj.get("message", {}).get("content", "")
                if chunk:
                    yield chunk
                if obj.get("done"):
                    break
    except requests.exceptions.ConnectionError:
        yield "\n\n⚠️ Не вижу локальную модель (Ollama не запущена). Запусти Ollama и повтори."
    except Exception as e:
        yield f"\n\n⚠️ Ошибка модели: {e}"


def complete(messages, model, temperature=0.3, settings=None, num_predict=None):
    """Короткий ответ без стриминга (для авто-названий и т.п.).
    num_predict — макс. длина ответа в токенах (для длинных ответов вроде JSON-плана)."""
    if _use_api(settings):
        return _api_complete(messages, settings, temperature)
    opts = {"temperature": temperature}
    if num_predict:
        opts["num_predict"] = int(num_predict)
    payload = {"model": model, "messages": messages, "stream": False,
               "options": opts}
    try:
        r = requests.post(f"{OLLAMA}/api/chat", json=payload, timeout=120)
        return r.json().get("message", {}).get("content", "").strip()
    except Exception:
        return ""


def ensure_ollama():
    """Проверяет, поднят ли Ollama."""
    try:
        requests.get(f"{OLLAMA}/api/tags", timeout=3)
        return True
    except Exception:
        return False


# слова-признаки «сложной» задачи → берём умную модель
_HARD_KW = [
    "код", "программ", "функци", "алгоритм", "скрипт", "напиши прог", "sql", "регуляр",
    "проанализир", "разбери", "рефактор", "оптимизир", "докажи", "составь план",
    "объясни подробно", "пошагов", "уравнени", "математ", "реши задач", "переведи код",
    "architecture", "debug", "почему не работает", "исправь ошибк", "спроектир",
]


def pick_model(text, settings):
    """Выбор модели: если auto_model — лёгкая для простого, умная для сложного."""
    if not settings.get("auto_model"):
        return settings.get("model")
    t = (text or "").lower()
    hard = len(t) > 220 or any(k in t for k in _HARD_KW)
    return settings.get("model_heavy") if hard else settings.get("model_light")
