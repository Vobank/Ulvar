# -*- coding: utf-8 -*-
"""Агентный режим Ульвара: модель вызывает НАВЫКИ как именованные инструменты.
Использует tool-calling Ollama. Опасные навыки — только с подтверждением."""
import json
import inspect
import requests

import skills
import store

OLLAMA = "http://127.0.0.1:11434"

# Навыки, которые что-то меняют/необратимы — выполняем только с разрешения
DANGEROUS = {
    "delete_file", "delete_dir", "move_path", "rename_path", "kill_process",
    "shutdown_pc", "restart_pc", "sleep_pc", "lock_pc", "set_wallpaper",
    "run_command", "run_python", "empty_recycle_bin", "clear_temp", "clean_downloads",
    "set_brightness", "stop_service", "registry_read", "git_push",
}

# Именованные инструменты для агента (самые полезные навыки)
CURATED = [
    "now", "system_info", "cpu_usage", "ram_usage", "disk_usage", "battery_status", "uptime",
    "gpu_usage", "calculate", "weather", "currency", "web_search", "open_url", "youtube_search",
    "open_app", "run_command", "run_python", "list_dir", "read_file", "write_file", "make_dir",
    "search_files", "search_in_files", "file_info", "downloads_folder",
    "screenshot", "screen_size", "mouse_click", "mouse_move", "type_text", "press_key", "hotkey",
    "scroll", "clipboard_get", "clipboard_set", "notify", "speak", "volume_up", "volume_down",
    "mute_toggle", "media_control", "find_process", "kill_process", "list_windows", "focus_window",
    "open_explorer", "translate", "generate_password", "make_qr", "read_qr", "ping", "public_ip",
    "is_online", "list_processes", "largest_files", "folder_size", "weather", "pdf_text",
    "excel_preview", "git_status", "list_printers", "installed_programs", "wifi_current",
    "make_slides", "make_presentation", "make_presentation_pdf", "make_word", "make_excel", "text_to_pdf",
    "word_to_pdf", "images_to_pdf", "pdf_text", "download_file", "open_file",
    "web_search_results", "get_webpage_text",
]

SYSTEM_AGENT = """Ты — Ульвар, личный ИИ-агент Вовы на его компьютере. У тебя есть РУКИ: инструменты, которыми ты реально управляешь ПК.

Правила:
- Если Вова просит что-то СДЕЛАТЬ или УЗНАТЬ с компьютера — ОБЯЗАТЕЛЬНО вызови подходящий инструмент, не придумывай ответ из головы.
- После того как инструмент вернул результат — дай короткий понятный ответ по-русски на основе этого результата.
- Если задача требует нескольких шагов — вызывай инструменты по очереди.
- Если Вова спрашивает про факты/новости из интернета — вызови web_search_results, прочитай результаты и ответь на их основе (не выдумывай).
- Из результатов поиска бери ТОЛЬКО то, что прямо отвечает на вопрос. Отвечай КРАТКО и по делу, не пересказывай всё подряд и не перечисляй лишнее.
- НЕ вставляй ссылки, URL и слова «Ссылка» в свой ответ — источники показываются Вове отдельно, над ответом. Просто дай чистый текстовый ответ.
- Если у параметра инструмента есть значение по умолчанию — используй его, НЕ переспрашивай (например, скриншот просто сохрани в Загрузки).
- Не проси уточнений без крайней необходимости — действуй разумными значениями по умолчанию.
- Презентации: ВСЕГДА используй make_slides(topic, slides, language, pdf, author) — она сама придумает полное содержание и заголовок. Передай topic (тема), slides (6-10), language (язык и уровень, напр. «немецкий A2» или «русский»), pdf=true (PDF) или pdf=false (PowerPoint), author — кого указать автором на титульном слайде (напр. «Вова Бабайкин»). Весь текст презентации будет на указанном языке. НЕ придумывай outline сам.
- Если Вова просит изменить уже сделанную презентацию (другой автор, язык, тема, число слайдов) — просто вызови make_slides ЗАНОВО с нужными параметрами, не пытайся «редактировать» старый файл.
- Если это просто беседа — отвечай текстом без инструментов."""


def _schema(name):
    fn = skills.SKILLS[name]["func"]
    props, req = {}, []
    for pn, p in inspect.signature(fn).parameters.items():
        if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        typ = "string"
        if p.default is not inspect.Parameter.empty and isinstance(p.default, (int, float)) and not isinstance(p.default, bool):
            typ = "number"
        props[pn] = {"type": typ}
        if p.default is inspect.Parameter.empty:
            req.append(pn)
    return {"type": "object", "properties": props, "required": req}


def _tools():
    seen, out = set(), []
    for name in CURATED:
        if name in skills.SKILLS and name not in seen:
            seen.add(name)
            out.append({"type": "function", "function": {
                "name": name, "description": skills.SKILLS[name]["desc"], "parameters": _schema(name)}})
    return out


_STATUS = {
    "web_search_results": "Ищу в интернете", "get_webpage_text": "Читаю страницу",
    "screenshot": "Делаю скриншот", "make_presentation": "Создаю презентацию",
    "make_slides": "Готовлю презентацию", "make_presentation_pdf": "Создаю презентацию (PDF)", "text_to_pdf": "Создаю PDF",
    "word_to_pdf": "Конвертирую в PDF", "images_to_pdf": "Собираю PDF из картинок",
    "make_word": "Создаю документ", "make_excel": "Создаю таблицу", "pdf_text": "Читаю PDF",
    "run_command": "Выполняю команду", "run_python": "Выполняю код", "open_app": "Открываю программу",
    "mouse_click": "Кликаю мышкой", "type_text": "Печатаю", "open_file": "Открываю файл",
    "list_windows": "Смотрю окна", "find_process": "Ищу процесс", "download_file": "Скачиваю",
    "weather": "Узнаю погоду", "calculate": "Считаю", "now": "Смотрю время",
    "cpu_usage": "Проверяю систему", "disk_usage": "Проверяю диски", "list_dir": "Смотрю папку",
    "read_file": "Читаю файл", "write_file": "Пишу файл", "search_files": "Ищу файлы",
}


def _status_for(name):
    return _STATUS.get(name, "Работаю")


def _lang_instr(s):
    if s.get("reply_match", True):
        return ("Отвечай на том же языке, на котором написано последнее сообщение пользователя "
                "(Reply in the same language as the user's last message).")
    return "Always answer in English." if s.get("lang") == "en" else "Всегда отвечай по-русски."


def _collect_sources(actions):
    out = []
    for a in actions:
        res = a.get("result", "")
        if "ИСТОЧНИКИ:" in res:
            for line in res.split("ИСТОЧНИКИ:", 1)[1].strip().splitlines():
                if "|" in line:
                    t, u = line.split("|", 1)
                    if u.strip().startswith("http"):
                        out.append({"title": t.strip(), "url": u.strip()})
    return out


def run_agent_stream(history, allow_dangerous=False, max_steps=8):
    """Потоковый агент: отдаёт события {status:...} по ходу и финальное {answer, sources}."""
    import llm
    s = store.get_settings()
    last_user = next((m.get("content", "") for m in reversed(history) if m.get("role") == "user"), "")
    model = llm.pick_model(last_user, s)
    msgs = [{"role": "system", "content": SYSTEM_AGENT},
            {"role": "system", "content": _lang_instr(s)}] + history
    tools = _tools()
    actions = []
    for _ in range(max_steps):
        yield {"status": "Думаю"}
        try:
            r = requests.post(f"{OLLAMA}/api/chat",
                              json={"model": model, "messages": msgs, "tools": tools, "stream": False},
                              timeout=300).json()
        except Exception as e:
            yield {"answer": f"⚠️ Ошибка модели: {e}", "actions": actions, "sources": []}
            return
        m = r.get("message", {})
        tcs = m.get("tool_calls") or []
        if not tcs:
            answer = (m.get("content") or "").strip() or "(готово)"
            yield {"answer": answer, "actions": actions, "sources": _collect_sources(actions)}
            return
        msgs.append(m)
        for tc in tcs:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}
            yield {"status": _status_for(name)}
            if name in DANGEROUS and not allow_dangerous:
                res = f"⚠️ «{name}» требует подтверждения (включи «разрешить действия»). Пропущено."
            elif name in skills.SKILLS:
                res = skills.run_skill(name, **args)
            else:
                res = f"навык {name} не найден"
            actions.append({"skill": name, "args": args, "result": str(res)[:2500]})
            msgs.append({"role": "tool", "content": str(res).split("ИСТОЧНИКИ:")[0].strip()})
    yield {"answer": "Достигнут предел шагов агента.", "actions": actions, "sources": _collect_sources(actions)}


def run_agent(history, allow_dangerous=False, max_steps=8):
    import llm
    s = store.get_settings()
    last_user = next((m.get("content", "") for m in reversed(history) if m.get("role") == "user"), "")
    model = llm.pick_model(last_user, s)
    msgs = [{"role": "system", "content": SYSTEM_AGENT}] + history
    tools = _tools()
    actions = []
    for _ in range(max_steps):
        try:
            r = requests.post(f"{OLLAMA}/api/chat",
                              json={"model": model, "messages": msgs, "tools": tools, "stream": False},
                              timeout=300).json()
        except Exception as e:
            return f"⚠️ Ошибка модели: {e}", actions
        m = r.get("message", {})
        tcs = m.get("tool_calls") or []
        if not tcs:
            return (m.get("content") or "").strip() or "(готово)", actions
        msgs.append(m)
        for tc in tcs:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}
            if name in DANGEROUS and not allow_dangerous:
                res = f"⚠️ «{name}» требует подтверждения (включи «разрешить действия»). Пропущено."
            elif name in skills.SKILLS:
                res = skills.run_skill(name, **args)
            else:
                res = f"навык {name} не найден"
            actions.append({"skill": name, "args": args, "result": str(res)[:2500]})
            # модели отдаём результат БЕЗ блока ссылок (чтобы не вставляла URL в ответ)
            model_res = str(res).split("ИСТОЧНИКИ:")[0].strip()
            msgs.append({"role": "tool", "content": model_res})
    return "Достигнут предел шагов агента.", actions
