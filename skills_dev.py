# -*- coding: utf-8 -*-
"""Навыки Ульвара: разработка (git, pip, код)."""
from skills import skill, _ok, _err
import subprocess
import sys
import os


def _run(cmd, cwd=None, timeout=120):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=cwd, timeout=timeout)
    return (r.stdout + r.stderr).strip()


# ---------- git ----------
@skill("Git", "Статус git-репозитория")
def git_status(path="."):
    return _run("git status", cwd=path) or "(не git-репозиторий?)"


@skill("Git", "История коммитов (последние)")
def git_log(path=".", n=10):
    return _run(f"git log --oneline -n {int(n)}", cwd=path)


@skill("Git", "Изменения (diff)")
def git_diff(path="."):
    return _run("git diff", cwd=path)[:4000] or "(нет изменений)"


@skill("Git", "Текущая ветка")
def git_branch(path="."):
    return _run("git branch --show-current", cwd=path)


@skill("Git", "Склонировать репозиторий")
def git_clone(url, dest=""):
    return _run(f"git clone {url} {dest}", timeout=300)


@skill("Git", "Добавить все файлы и закоммитить")
def git_commit(message, path="."):
    _run("git add -A", cwd=path)
    return _run(f'git commit -m "{message}"', cwd=path)


@skill("Git", "Отправить изменения (push)")
def git_push(path="."):
    return _run("git push", cwd=path, timeout=120)


@skill("Git", "Забрать изменения (pull)")
def git_pull(path="."):
    return _run("git pull", cwd=path, timeout=120)


# ---------- pip / python ----------
@skill("Python", "Установить пакет pip")
def pip_install(package):
    return _run(f'"{sys.executable}" -m pip install {package}', timeout=300)[-2000:]


@skill("Python", "Удалить пакет pip")
def pip_uninstall(package):
    return _run(f'"{sys.executable}" -m pip uninstall -y {package}')[-1500:]


@skill("Python", "Список установленных пакетов")
def pip_list():
    return _run(f'"{sys.executable}" -m pip list')[:3000]


@skill("Python", "Версия пакета")
def pip_version(package):
    return _run(f'"{sys.executable}" -m pip show {package}')[:1000]


@skill("Python", "Создать виртуальное окружение")
def create_venv(path="venv"):
    return _run(f'"{sys.executable}" -m venv {path}') or _ok(f"venv создан: {path}")


@skill("Python", "Проверить синтаксис Python-файла")
def python_check(path):
    r = _run(f'"{sys.executable}" -m py_compile "{path}"')
    return r or _ok("синтаксис OK")


@skill("Разработка", "Форматировать JSON-файл красиво")
def format_json_file(path):
    try:
        import json
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return _ok("отформатирован")
    except Exception as e:
        return _err(str(e))


@skill("Разработка", "Посчитать строки кода в проекте")
def count_lines_of_code(folder=".", exts=(".py", ".js", ".html", ".css", ".c", ".cpp", ".java")):
    total, files = 0, 0
    for root, _, fs in os.walk(folder):
        if any(skip in root for skip in ("venv", "node_modules", ".git", "__pycache__")):
            continue
        for fn in fs:
            if fn.endswith(tuple(exts)):
                try:
                    with open(os.path.join(root, fn), encoding="utf-8", errors="ignore") as f:
                        total += sum(1 for _ in f); files += 1
                except Exception:
                    pass
    return f"Файлов кода: {files}, строк: {total}"


@skill("Разработка", "Запустить локальный веб-сервер в папке")
def start_web_server(folder=".", port=8000):
    try:
        subprocess.Popen(f'"{sys.executable}" -m http.server {port}', shell=True, cwd=folder)
        return _ok(f"сервер на http://localhost:{port} (папка {folder})")
    except Exception as e:
        return _err(str(e))


@skill("Разработка", "Открыть папку/файл в VS Code")
def open_in_vscode(path="."):
    try:
        subprocess.Popen(f'code "{path}"', shell=True)
        return _ok("открыто в VS Code")
    except Exception as e:
        return _err(str(e))


@skill("Разработка", "Структура папок проекта (дерево)")
def project_tree(folder=".", max_depth=2):
    out = []
    folder = os.path.abspath(folder)
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in ("venv", "node_modules", ".git", "__pycache__")]
        depth = root[len(folder):].count(os.sep)
        if depth > int(max_depth):
            dirs[:] = []
            continue
        indent = "  " * depth
        out.append(f"{indent}{os.path.basename(root)}/")
        for f in files[:20]:
            out.append(f"{indent}  {f}")
    return "\n".join(out[:150])


@skill("Разработка", "Прогнать тесты (pytest), если есть")
def run_tests(path="."):
    return _run(f'"{sys.executable}" -m pytest -q', cwd=path, timeout=300)[-2500:]


@skill("Разработка", "Сгенерировать requirements.txt из окружения")
def freeze_requirements(out="requirements.txt"):
    txt = _run(f'"{sys.executable}" -m pip freeze')
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(txt)
        return _ok(f"сохранено: {out}")
    except Exception as e:
        return _err(str(e))


@skill("Разработка", "Красиво показать содержимое файла с номерами строк")
def show_file_numbered(path, start=1, end=60):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(f"{i+1}: {lines[i]}" for i in range(int(start)-1, min(int(end), len(lines))))
    except Exception as e:
        return _err(str(e))
