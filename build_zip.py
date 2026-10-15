# -*- coding: utf-8 -*-
"""Собирает чистую раздачу Ульвара в ZIP с паролем (AES).
Включает только код и интерфейс; НЕ включает venv, личные данные, модели, мусор.
Готовый архив кладётся в Загрузки. Пароль архива: 0000.
Распаковывать архив удобнее 7-Zip (встроенный проводник Windows AES-архивы не открывает).
"""
import os
import sys

import pyzipper

ROOT = os.path.dirname(os.path.abspath(__file__))
PASSWORD = b"0000"
ARCH_NAME = "Ulvar.zip"

# Что кладём в архив (папки и отдельные файлы)
INCLUDE_DIRS = ["ui"]
INCLUDE_FILES = [
    "main.py", "server.py", "llm.py", "store.py", "persona.py", "smartsearch.py",
    "agent.py",
    "skills.py", "skills_auto.py", "skills_data.py", "skills_dev.py", "skills_docs.py",
    "skills_image.py", "skills_media.py", "skills_net.py", "skills_present.py",
    "skills_text.py", "skills_win.py",
    "requirements.txt", "README.md", "LICENSE", ".gitignore",
    "install.ps1", "Установить.bat", "Ульвар.bat", "НАВЫКИ.txt",
]
# В ui берём только нужное
UI_ALLOW = {"index.html", "style.css", "app.js", "skills_en.json"}


def _downloads():
    import ctypes.wintypes
    CSIDL_PERSONAL = 0x0005  # не то; используем профиль
    p = os.path.join(os.path.expanduser("~"), "Downloads")
    return p if os.path.isdir(p) else os.path.expanduser("~")


def collect():
    files = []  # (абсолютный путь, путь в архиве)
    for f in INCLUDE_FILES:
        src = os.path.join(ROOT, f)
        if os.path.isfile(src):
            files.append((src, os.path.join("Ulvar", f)))
    for d in INCLUDE_DIRS:
        base = os.path.join(ROOT, d)
        for dp, _, fns in os.walk(base):
            if "__pycache__" in dp:
                continue
            for fn in fns:
                if d == "ui" and fn not in UI_ALLOW:
                    continue
                src = os.path.join(dp, fn)
                rel = os.path.relpath(src, ROOT)
                files.append((src, os.path.join("Ulvar", rel)))
    return files


def main():
    out = os.path.join(_downloads(), ARCH_NAME)
    files = collect()
    with pyzipper.AESZipFile(out, "w", compression=pyzipper.ZIP_DEFLATED,
                             encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(PASSWORD)
        for src, arc in files:
            zf.write(src, arc)
    size = os.path.getsize(out) / 1024
    print(f"OK: {out}  ({len(files)} файлов, {size:.0f} КБ, пароль 0000)")


if __name__ == "__main__":
    main()
