# -*- coding: utf-8 -*-
"""
Навыки Ульвара («руки») — 100 реально полезных умений.
Каждый навык — функция, возвращает строку-результат (для отчёта пользователю/модели).
Реестр SKILLS используется для вызова по имени и для tool-calling.
GUI-навыки (мышь/клавиатура/экран) требуют pyautogui (ставится отдельно).
"""
import os
import sys
import re
import json
import time
import shutil
import socket
import hashlib
import base64
import uuid
import random
import subprocess
import threading
import datetime as _dt
import glob as _glob

import requests

try:
    import psutil
except Exception:
    psutil = None
try:
    import pyperclip
except Exception:
    pyperclip = None

SKILLS = {}


def skill(category, desc):
    def deco(fn):
        SKILLS[fn.__name__] = {"func": fn, "category": category, "desc": desc}
        return fn
    return deco


def _gui():
    """Ленивая загрузка pyautogui (GUI-автоматизация)."""
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    return pyautogui


def _ok(msg):
    return f"✓ {msg}"


def _err(msg):
    return f"✗ {msg}"


# ======================================================================
#  ФАЙЛЫ И ПАПКИ (1–18)
# ======================================================================
@skill("Файлы", "Прочитать текстовый файл")
def read_file(path, max_chars=20000):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            t = f.read(max_chars)
        return t if t else "(файл пуст)"
    except Exception as e:
        return _err(f"чтение: {e}")


@skill("Файлы", "Записать текст в файл (перезапись)")
def write_file(path, text):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return _ok(f"записано: {path}")
    except Exception as e:
        return _err(f"запись: {e}")


@skill("Файлы", "Дописать текст в конец файла")
def append_file(path, text):
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
        return _ok(f"дописано: {path}")
    except Exception as e:
        return _err(f"дозапись: {e}")


@skill("Файлы", "Удалить файл")
def delete_file(path):
    try:
        os.remove(path)
        return _ok(f"удалён: {path}")
    except Exception as e:
        return _err(f"удаление: {e}")


@skill("Файлы", "Скопировать файл")
def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        return _ok(f"скопировано: {src} → {dst}")
    except Exception as e:
        return _err(f"копирование: {e}")


@skill("Файлы", "Переместить файл или папку")
def move_path(src, dst):
    try:
        shutil.move(src, dst)
        return _ok(f"перемещено: {src} → {dst}")
    except Exception as e:
        return _err(f"перемещение: {e}")


@skill("Файлы", "Переименовать файл/папку")
def rename_path(path, new_name):
    try:
        new = os.path.join(os.path.dirname(path), new_name)
        os.rename(path, new)
        return _ok(f"переименовано: {new}")
    except Exception as e:
        return _err(f"переименование: {e}")


@skill("Файлы", "Список файлов и папок в директории")
def list_dir(path="."):
    try:
        items = os.listdir(path)
        rows = []
        for it in sorted(items):
            full = os.path.join(path, it)
            tag = "[папка]" if os.path.isdir(full) else "      "
            rows.append(f"{tag} {it}")
        return "\n".join(rows) or "(пусто)"
    except Exception as e:
        return _err(f"список: {e}")


@skill("Файлы", "Создать папку")
def make_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return _ok(f"папка: {path}")
    except Exception as e:
        return _err(f"создание папки: {e}")


@skill("Файлы", "Удалить папку со всем содержимым")
def delete_dir(path):
    try:
        shutil.rmtree(path)
        return _ok(f"папка удалена: {path}")
    except Exception as e:
        return _err(f"удаление папки: {e}")


@skill("Файлы", "Информация о файле (размер, дата)")
def file_info(path):
    try:
        st = os.stat(path)
        return (f"Путь: {path}\nРазмер: {st.st_size/1024:.1f} КБ\n"
                f"Изменён: {_dt.datetime.fromtimestamp(st.st_mtime):%d.%m.%Y %H:%M}")
    except Exception as e:
        return _err(f"инфо: {e}")


@skill("Файлы", "Найти файлы по маске имени в папке (рекурсивно)")
def search_files(folder, pattern="*", recursive=True):
    try:
        p = os.path.join(folder, "**", pattern) if recursive else os.path.join(folder, pattern)
        res = _glob.glob(p, recursive=recursive)[:200]
        return "\n".join(res) or "(ничего не найдено)"
    except Exception as e:
        return _err(f"поиск файлов: {e}")


@skill("Файлы", "Найти текст внутри файлов папки")
def search_in_files(folder, text, exts=(".txt", ".py", ".md", ".json", ".js", ".html", ".csv", ".log")):
    try:
        hits = []
        for root, _, files in os.walk(folder):
            for fn in files:
                if fn.lower().endswith(tuple(exts)):
                    fp = os.path.join(root, fn)
                    try:
                        with open(fp, encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if text.lower() in line.lower():
                                    hits.append(f"{fp}:{i}: {line.strip()[:120]}")
                                    if len(hits) >= 100:
                                        return "\n".join(hits)
                    except Exception:
                        pass
        return "\n".join(hits) or "(не найдено)"
    except Exception as e:
        return _err(f"поиск в файлах: {e}")


@skill("Файлы", "Упаковать файлы/папку в zip")
def zip_path(src, zip_path):
    try:
        base = zip_path[:-4] if zip_path.endswith(".zip") else zip_path
        if os.path.isdir(src):
            shutil.make_archive(base, "zip", src)
        else:
            import zipfile
            with zipfile.ZipFile(base + ".zip", "w", zipfile.ZIP_DEFLATED) as z:
                z.write(src, os.path.basename(src))
        return _ok(f"архив: {base}.zip")
    except Exception as e:
        return _err(f"zip: {e}")


@skill("Файлы", "Распаковать zip-архив")
def unzip(zip_path, dest):
    try:
        shutil.unpack_archive(zip_path, dest)
        return _ok(f"распаковано в {dest}")
    except Exception as e:
        return _err(f"unzip: {e}")


@skill("Файлы", "Открыть файл в программе по умолчанию")
def open_file(path):
    try:
        os.startfile(path)
        return _ok(f"открыт: {path}")
    except Exception as e:
        return _err(f"открытие: {e}")


@skill("Файлы", "Путь к папке Загрузки")
def downloads_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")


@skill("Файлы", "Хеш файла (sha256)")
def file_hash(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return _err(f"хеш: {e}")


# ======================================================================
#  СИСТЕМА И ПК (19–40)
# ======================================================================
@skill("Система", "Сводка о системе (ОС, CPU, RAM)")
def system_info():
    import platform
    info = [f"ОС: {platform.system()} {platform.release()}",
            f"Процессор: {platform.processor()[:60]}"]
    if psutil:
        info.append(f"Ядер: {psutil.cpu_count()}")
        info.append(f"ОЗУ: {psutil.virtual_memory().total/1e9:.1f} ГБ")
    return "\n".join(info)


@skill("Система", "Текущая загрузка процессора, %")
def cpu_usage():
    if not psutil:
        return _err("psutil не установлен")
    return f"CPU: {psutil.cpu_percent(interval=0.5)}%"


@skill("Система", "Использование оперативной памяти")
def ram_usage():
    if not psutil:
        return _err("psutil не установлен")
    m = psutil.virtual_memory()
    return f"ОЗУ: {m.used/1e9:.1f}/{m.total/1e9:.1f} ГБ ({m.percent}%)"


@skill("Система", "Свободное место на дисках")
def disk_usage():
    if not psutil:
        return _err("psutil не установлен")
    out = []
    for p in psutil.disk_partitions():
        try:
            u = psutil.disk_usage(p.mountpoint)
            out.append(f"{p.device} {u.free/1e9:.0f} ГБ своб. из {u.total/1e9:.0f}")
        except Exception:
            pass
    return "\n".join(out)


@skill("Система", "Состояние батареи")
def battery_status():
    if not psutil or not hasattr(psutil, "sensors_battery"):
        return _err("нет данных о батарее")
    b = psutil.sensors_battery()
    if not b:
        return "Батарея не обнаружена (стационарный ПК?)"
    return f"Батарея: {b.percent}% {'(заряжается)' if b.power_plugged else ''}"


@skill("Система", "Время работы системы с момента включения")
def uptime():
    if not psutil:
        return _err("psutil не установлен")
    s = time.time() - psutil.boot_time()
    return f"Аптайм: {int(s//3600)} ч {int((s%3600)//60)} мин"


@skill("Система", "Список запущенных процессов (топ по памяти)")
def list_processes(top=15):
    if not psutil:
        return _err("psutil не установлен")
    procs = []
    for p in psutil.process_iter(["name", "memory_info"]):
        try:
            procs.append((p.info["name"], p.info["memory_info"].rss))
        except Exception:
            pass
    procs.sort(key=lambda x: x[1], reverse=True)
    return "\n".join(f"{n}: {m/1e6:.0f} МБ" for n, m in procs[:top])


@skill("Система", "Найти процесс по имени")
def find_process(name):
    if not psutil:
        return _err("psutil не установлен")
    found = [f"PID {p.pid}: {p.info['name']}" for p in psutil.process_iter(["name"])
             if name.lower() in (p.info["name"] or "").lower()]
    return "\n".join(found) or "(не найден)"


@skill("Система", "Завершить процесс по имени или PID")
def kill_process(name_or_pid):
    if not psutil:
        return _err("psutil не установлен")
    killed = 0
    for p in psutil.process_iter(["name", "pid"]):
        try:
            if str(name_or_pid) == str(p.pid) or str(name_or_pid).lower() in (p.info["name"] or "").lower():
                p.kill(); killed += 1
        except Exception:
            pass
    return _ok(f"завершено процессов: {killed}")


@skill("Система", "Запустить программу/приложение по имени")
def open_app(name):
    try:
        os.startfile(name)
        return _ok(f"запущено: {name}")
    except Exception:
        try:
            subprocess.Popen(name, shell=True)
            return _ok(f"запущено: {name}")
        except Exception as e:
            return _err(f"запуск: {e}")


@skill("Система", "Выполнить команду в терминале и вернуть вывод")
def run_command(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return (r.stdout + r.stderr).strip()[:8000] or "(нет вывода)"
    except Exception as e:
        return _err(f"команда: {e}")


@skill("Разработка", "Выполнить код Python и вернуть вывод")
def run_python(code, timeout=60):
    try:
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return (r.stdout + r.stderr).strip()[:8000] or "(нет вывода)"
    except Exception as e:
        return _err(f"python: {e}")


@skill("Система", "Увеличить громкость (шагов)")
def volume_up(steps=5):
    g = _gui()
    for _ in range(steps):
        g.press("volumeup")
    return _ok(f"громкость +{steps}")


@skill("Система", "Уменьшить громкость (шагов)")
def volume_down(steps=5):
    g = _gui()
    for _ in range(steps):
        g.press("volumedown")
    return _ok(f"громкость -{steps}")


@skill("Система", "Включить/выключить звук (mute)")
def mute_toggle():
    _gui().press("volumemute")
    return _ok("mute переключён")


@skill("Система", "Яркость экрана в процентах (0-100)")
def set_brightness(percent):
    try:
        subprocess.run(["powershell", "-Command",
                        f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)."
                        f"WmiSetBrightness(1,{int(percent)})"], timeout=15)
        return _ok(f"яркость {percent}%")
    except Exception as e:
        return _err(f"яркость: {e}")


@skill("Система", "Заблокировать компьютер")
def lock_pc():
    try:
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return _ok("ПК заблокирован")
    except Exception as e:
        return _err(f"блокировка: {e}")


@skill("Система", "Перевести ПК в спящий режим")
def sleep_pc():
    try:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return _ok("спящий режим")
    except Exception as e:
        return _err(f"сон: {e}")


@skill("Система", "Выключить ПК через N секунд")
def shutdown_pc(delay=30):
    try:
        subprocess.run(f"shutdown /s /t {int(delay)}", shell=True)
        return _ok(f"выключение через {delay}с (отмена: shutdown /a)")
    except Exception as e:
        return _err(f"выключение: {e}")


@skill("Система", "Перезагрузить ПК через N секунд")
def restart_pc(delay=30):
    try:
        subprocess.run(f"shutdown /r /t {int(delay)}", shell=True)
        return _ok(f"перезагрузка через {delay}с (отмена: shutdown /a)")
    except Exception as e:
        return _err(f"перезагрузка: {e}")


@skill("Система", "Отменить запланированное выключение/перезагрузку")
def cancel_shutdown():
    subprocess.run("shutdown /a", shell=True)
    return _ok("выключение отменено")


# ======================================================================
#  БУФЕР ОБМЕНА И ЭКРАН / GUI-АВТОМАТИЗАЦИЯ (41–62)
# ======================================================================
@skill("Буфер", "Прочитать текст из буфера обмена")
def clipboard_get():
    if not pyperclip:
        return _err("pyperclip не установлен")
    return pyperclip.paste() or "(буфер пуст)"


@skill("Буфер", "Положить текст в буфер обмена")
def clipboard_set(text):
    if not pyperclip:
        return _err("pyperclip не установлен")
    pyperclip.copy(text)
    return _ok("скопировано в буфер")


@skill("Экран", "Снять скриншот всего экрана в файл")
def screenshot(path=None):
    g = _gui()
    path = path or os.path.join(downloads_folder(), f"screenshot_{int(time.time())}.png")
    g.screenshot(path)
    return _ok(f"скриншот: {path}")


@skill("Экран", "Снять скриншот области (x, y, ширина, высота)")
def screenshot_region(x, y, w, h, path=None):
    g = _gui()
    path = path or os.path.join(downloads_folder(), f"region_{int(time.time())}.png")
    g.screenshot(path, region=(int(x), int(y), int(w), int(h)))
    return _ok(f"скриншот области: {path}")


@skill("Экран", "Размер экрана в пикселях")
def screen_size():
    g = _gui()
    w, h = g.size()
    return f"Экран: {w}x{h}"


@skill("Экран", "Текущие координаты мыши")
def mouse_position():
    g = _gui()
    x, y = g.position()
    return f"Мышь: x={x}, y={y}"


@skill("Экран", "Переместить мышь в точку (x, y)")
def mouse_move(x, y, duration=0.3):
    _gui().moveTo(int(x), int(y), duration=duration)
    return _ok(f"мышь → ({x}, {y})")


@skill("Экран", "Клик левой кнопкой в точке (x, y)")
def mouse_click(x=None, y=None):
    g = _gui()
    if x is None:
        g.click()
    else:
        g.click(int(x), int(y))
    return _ok(f"клик {('('+str(x)+','+str(y)+')') if x is not None else ''}")


@skill("Экран", "Двойной клик в точке (x, y)")
def mouse_double_click(x=None, y=None):
    g = _gui()
    g.doubleClick(int(x), int(y)) if x is not None else g.doubleClick()
    return _ok("двойной клик")


@skill("Экран", "Правый клик в точке (x, y)")
def mouse_right_click(x=None, y=None):
    g = _gui()
    g.rightClick(int(x), int(y)) if x is not None else g.rightClick()
    return _ok("правый клик")


@skill("Экран", "Перетащить мышь из точки в точку")
def mouse_drag(x1, y1, x2, y2, duration=0.5):
    g = _gui()
    g.moveTo(int(x1), int(y1))
    g.dragTo(int(x2), int(y2), duration=duration, button="left")
    return _ok(f"перетащено ({x1},{y1})→({x2},{y2})")


@skill("Экран", "Прокрутить колесо (вверх +, вниз -)")
def scroll(amount=300):
    _gui().scroll(int(amount))
    return _ok(f"прокрутка {amount}")


@skill("Экран", "Напечатать текст (ввод с клавиатуры)")
def type_text(text, interval=0.01):
    _gui().write(text, interval=interval)
    return _ok("текст введён")


@skill("Экран", "Нажать клавишу (например enter, esc, f5)")
def press_key(key):
    _gui().press(key)
    return _ok(f"нажато: {key}")


@skill("Экран", "Горячая комбинация (например ctrl c, alt tab)")
def hotkey(*keys):
    _gui().hotkey(*keys)
    return _ok(f"комбинация: {'+'.join(keys)}")


@skill("Экран", "Цвет пикселя в точке (x, y)")
def pixel_color(x, y):
    g = _gui()
    c = g.pixel(int(x), int(y))
    return f"Пиксель ({x},{y}): RGB{c}"


@skill("Экран", "Найти картинку на экране и вернуть координаты")
def locate_on_screen(image_path, confidence=0.8):
    g = _gui()
    try:
        box = g.locateCenterOnScreen(image_path, confidence=confidence)
        return f"Найдено в ({box.x}, {box.y})" if box else "(не найдено на экране)"
    except Exception as e:
        return _err(f"поиск картинки: {e}")


@skill("Экран", "Найти картинку на экране и кликнуть по ней")
def click_image(image_path, confidence=0.8):
    g = _gui()
    try:
        box = g.locateCenterOnScreen(image_path, confidence=confidence)
        if not box:
            return "(картинка не найдена)"
        g.click(box)
        return _ok(f"клик по картинке в ({box.x}, {box.y})")
    except Exception as e:
        return _err(f"клик по картинке: {e}")


@skill("Окна", "Заголовок активного окна")
def active_window_title():
    try:
        import pygetwindow as gw
        w = gw.getActiveWindow()
        return w.title if w else "(нет активного окна)"
    except Exception as e:
        return _err(f"окно: {e}")


@skill("Окна", "Список открытых окон")
def list_windows():
    try:
        import pygetwindow as gw
        titles = [t for t in gw.getAllTitles() if t.strip()]
        return "\n".join(titles) or "(нет окон)"
    except Exception as e:
        return _err(f"окна: {e}")


@skill("Окна", "Активировать (вывести на передний план) окно по заголовку")
def focus_window(title):
    try:
        import pygetwindow as gw
        ws = gw.getWindowsWithTitle(title)
        if not ws:
            return "(окно не найдено)"
        ws[0].activate()
        return _ok(f"активировано: {ws[0].title}")
    except Exception as e:
        return _err(f"фокус: {e}")


@skill("Окна", "Показать рабочий стол (свернуть всё)")
def show_desktop():
    _gui().hotkey("win", "d")
    return _ok("рабочий стол")


# ======================================================================
#  ОКНА, УВЕДОМЛЕНИЯ, ВИД (63–70)
# ======================================================================
@skill("Окна", "Развернуть окно по заголовку")
def maximize_window(title):
    try:
        import pygetwindow as gw
        ws = gw.getWindowsWithTitle(title)
        if ws:
            ws[0].maximize(); return _ok("развёрнуто")
        return "(окно не найдено)"
    except Exception as e:
        return _err(str(e))


@skill("Окна", "Свернуть окно по заголовку")
def minimize_window(title):
    try:
        import pygetwindow as gw
        ws = gw.getWindowsWithTitle(title)
        if ws:
            ws[0].minimize(); return _ok("свёрнуто")
        return "(окно не найдено)"
    except Exception as e:
        return _err(str(e))


@skill("Окна", "Закрыть окно по заголовку")
def close_window(title):
    try:
        import pygetwindow as gw
        ws = gw.getWindowsWithTitle(title)
        if ws:
            ws[0].close(); return _ok("закрыто")
        return "(окно не найдено)"
    except Exception as e:
        return _err(str(e))


@skill("Уведомления", "Показать всплывающее уведомление Windows")
def notify(title, message):
    try:
        from plyer import notification as _n
        _n.notify(title=title, message=message, timeout=6)
        return _ok("уведомление показано")
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
            return _ok("показано (окно)")
        except Exception as e:
            return _err(f"уведомление: {e}")


@skill("Уведомления", "Показать окно с сообщением")
def message_box(text, title="Ульвар"):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)
        return _ok("показано")
    except Exception as e:
        return _err(str(e))


@skill("Вид", "Поставить картинку обоями рабочего стола")
def set_wallpaper(image_path):
    try:
        import ctypes
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(image_path), 3)
        return _ok("обои установлены")
    except Exception as e:
        return _err(f"обои: {e}")


@skill("Система", "Открыть страницу настроек Windows (напр. ms-settings:bluetooth)")
def open_settings(page="ms-settings:"):
    try:
        os.startfile(page)
        return _ok(f"настройки: {page}")
    except Exception as e:
        return _err(str(e))


@skill("Интернет", "Открыть ссылку в браузере")
def open_url(url):
    import webbrowser
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return _ok(f"открыто: {url}")


# ======================================================================
#  ИНТЕРНЕТ И СЕТЬ (71–82)
# ======================================================================
@skill("Интернет", "Поиск в Google (откроет браузер)")
def web_search(query):
    import webbrowser
    webbrowser.open("https://www.google.com/search?q=" + requests.utils.quote(query))
    return _ok(f"поиск: {query}")


@skill("Интернет", "Скачать файл по ссылке")
def download_file(url, path=None):
    try:
        path = path or os.path.join(downloads_folder(), url.split("/")[-1].split("?")[0] or "file")
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
        return _ok(f"скачано: {path}")
    except Exception as e:
        return _err(f"скачивание: {e}")


@skill("Интернет", "Внешний (публичный) IP-адрес")
def public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=10).text
    except Exception as e:
        return _err(str(e))


@skill("Интернет", "Локальный IP-адрес ПК")
def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
        return ip
    except Exception as e:
        return _err(str(e))


@skill("Интернет", "Проверить доступность хоста (ping)")
def ping(host="8.8.8.8"):
    r = subprocess.run(f"ping -n 2 {host}", shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout.strip()[:1500]


@skill("Интернет", "Есть ли интернет")
def is_online():
    try:
        requests.get("https://www.google.com", timeout=5)
        return "✓ интернет есть"
    except Exception:
        return "✗ интернета нет"


@skill("Интернет", "Получить текст веб-страницы (без тегов)")
def get_webpage_text(url, max_chars=4000):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        html = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
        text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except Exception as e:
        return _err(f"страница: {e}")


@skill("Интернет", "Погода в городе (через wttr.in, без ключа)")
def weather(city="Berlin"):
    try:
        return requests.get(f"https://wttr.in/{requests.utils.quote(city)}?format=3&lang=ru",
                            timeout=15).text.strip()
    except Exception as e:
        return _err(f"погода: {e}")


@skill("Интернет", "Открыть поиск на YouTube")
def youtube_search(query):
    import webbrowser
    webbrowser.open("https://www.youtube.com/results?search_query=" + requests.utils.quote(query))
    return _ok(f"YouTube: {query}")


@skill("Интернет", "Открыть место на картах")
def open_maps(place):
    import webbrowser
    webbrowser.open("https://www.google.com/maps/search/" + requests.utils.quote(place))
    return _ok(f"карты: {place}")


@skill("Интернет", "HTTP GET — код ответа и начало тела")
def http_get(url):
    try:
        r = requests.get(url, timeout=20)
        return f"{r.status_code}\n{r.text[:1000]}"
    except Exception as e:
        return _err(str(e))


@skill("Интернет", "Курсы валют к рублю/доллару (exchangerate, без ключа)")
def currency(base="USD"):
    try:
        d = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=15).json()
        rates = d.get("rates", {})
        pick = {k: rates[k] for k in ("EUR", "RUB", "UAH", "USD", "GBP", "PLN") if k in rates}
        return f"1 {base} = " + ", ".join(f"{v} {k}" for k, v in pick.items())
    except Exception as e:
        return _err(str(e))


# ======================================================================
#  ТЕКСТ, РАСЧЁТЫ, УТИЛИТЫ (83–95)
# ======================================================================
@skill("Утилиты", "Посчитать математическое выражение")
def calculate(expr):
    try:
        allowed = set("0123456789+-*/().,%^ eπ")
        e = expr.replace("^", "**").replace("π", "3.141592653589793")
        if not set(e) <= allowed | set("*."):
            pass
        return str(eval(e, {"__builtins__": {}}, {}))
    except Exception as ex:
        return _err(f"вычисление: {ex}")


@skill("Утилиты", "Посчитать слова и символы в тексте")
def word_count(text):
    return f"Слов: {len(text.split())}, символов: {len(text)}, строк: {text.count(chr(10))+1}"


@skill("Утилиты", "Сгенерировать надёжный пароль")
def generate_password(length=16):
    import string
    chars = string.ascii_letters + string.digits + "!@#$%^&*-_"
    return "".join(random.choice(chars) for _ in range(int(length)))


@skill("Утилиты", "Сгенерировать уникальный идентификатор (UUID)")
def make_uuid():
    return str(uuid.uuid4())


@skill("Утилиты", "Хеш текста (sha256/md5)")
def hash_text(text, algo="sha256"):
    try:
        return hashlib.new(algo, text.encode("utf-8")).hexdigest()
    except Exception as e:
        return _err(str(e))


@skill("Утилиты", "Закодировать текст в base64")
def b64_encode(text):
    return base64.b64encode(text.encode("utf-8")).decode()


@skill("Утилиты", "Раскодировать base64 в текст")
def b64_decode(data):
    try:
        return base64.b64decode(data).decode("utf-8", "replace")
    except Exception as e:
        return _err(str(e))


@skill("Утилиты", "Текущие дата и время")
def now():
    return _dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")


@skill("Утилиты", "Случайное число в диапазоне")
def random_number(a=1, b=100):
    return str(random.randint(int(a), int(b)))


@skill("Утилиты", "Красиво отформатировать JSON")
def json_pretty(text):
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except Exception as e:
        return _err(f"json: {e}")


@skill("Утилиты", "Найти совпадения по регулярному выражению")
def regex_find(pattern, text):
    try:
        res = re.findall(pattern, text)
        return "\n".join(map(str, res)) or "(нет совпадений)"
    except Exception as e:
        return _err(str(e))


@skill("Утилиты", "Напомнить через N секунд (уведомление)")
def remind_me(seconds, text="Напоминание"):
    def _later():
        time.sleep(float(seconds))
        notify("Напоминание Ульвара", text)
    threading.Thread(target=_later, daemon=True).start()
    return _ok(f"напомню через {seconds}с: {text}")


@skill("Утилиты", "Перевести текст (через бесплатный переводчик)")
def translate(text, to="ru"):
    try:
        r = requests.get("https://api.mymemory.translated.net/get",
                         params={"q": text, "langpair": f"auto|{to}"}, timeout=15).json()
        return r.get("responseData", {}).get("translatedText", "(нет перевода)")
    except Exception as e:
        return _err(f"перевод: {e}")


# ======================================================================
#  МЕДИА, ИЗОБРАЖЕНИЯ, РАЗНОЕ (96–100+)
# ======================================================================
@skill("Медиа", "Проиграть системный звук (бип)")
def beep(freq=800, ms=300):
    try:
        import winsound
        winsound.Beep(int(freq), int(ms))
        return _ok("бип")
    except Exception as e:
        return _err(str(e))


@skill("Медиа", "Озвучить текст голосом (TTS)")
def speak(text):
    try:
        import pyttsx3
        e = pyttsx3.init()
        e.say(text); e.runAndWait()
        return _ok("озвучено")
    except Exception as e:
        return _err(f"озвучка: {e}")


@skill("Медиа", "Управление музыкой: play/pause/next/prev")
def media_control(action="play_pause"):
    key = {"play_pause": "playpause", "next": "nexttrack", "prev": "prevtrack"}.get(action, "playpause")
    _gui().press(key)
    return _ok(f"музыка: {action}")


@skill("Изображения", "Изменить размер картинки")
def resize_image(path, width, height, out=None):
    try:
        from PIL import Image
        im = Image.open(path)
        im = im.resize((int(width), int(height)))
        out = out or path.rsplit(".", 1)[0] + f"_{width}x{height}.png"
        im.save(out)
        return _ok(f"сохранено: {out}")
    except Exception as e:
        return _err(f"ресайз: {e}")


@skill("Изображения", "Конвертировать картинку в другой формат")
def convert_image(path, to_format="png"):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        out = path.rsplit(".", 1)[0] + "." + to_format
        im.save(out)
        return _ok(f"сохранено: {out}")
    except Exception as e:
        return _err(f"конвертация: {e}")


@skill("Система", "Создать ярлык на рабочем столе")
def create_shortcut(target, name=None):
    try:
        import pythoncom
        from win32com.client import Dispatch
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        name = name or os.path.splitext(os.path.basename(target))[0]
        lnk = os.path.join(desktop, name + ".lnk")
        sh = Dispatch("WScript.Shell")
        sc = sh.CreateShortcut(lnk)
        sc.TargetPath = target
        sc.Save()
        return _ok(f"ярлык: {lnk}")
    except Exception:
        # запасной путь через PowerShell
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            name = name or os.path.splitext(os.path.basename(target))[0]
            lnk = os.path.join(desktop, name + ".lnk")
            ps = (f"$s=(New-Object -COM WScript.Shell).CreateShortcut('{lnk}');"
                  f"$s.TargetPath='{target}';$s.Save()")
            subprocess.run(["powershell", "-Command", ps], timeout=15)
            return _ok(f"ярлык: {lnk}")
        except Exception as e:
            return _err(f"ярлык: {e}")


# ======================================================================
#  Вспомогательное: вызов навыка по имени + каталог
# ======================================================================
def run_skill(name, *args, **kwargs):
    """Вызвать навык по имени."""
    s = SKILLS.get(name)
    if not s:
        return _err(f"навык не найден: {name}")
    try:
        return s["func"](*args, **kwargs)
    except Exception as e:
        return _err(f"{name}: {e}")


def catalog():
    """Список всех навыков по категориям."""
    by_cat = {}
    for name, meta in SKILLS.items():
        by_cat.setdefault(meta["category"], []).append((name, meta["desc"]))
    out = [f"Всего навыков: {len(SKILLS)}\n"]
    for cat in sorted(by_cat):
        out.append(f"### {cat}")
        for name, desc in sorted(by_cat[cat]):
            out.append(f"  • {name} — {desc}")
        out.append("")
    return "\n".join(out)


@skill("Мета", "Список всех навыков (имя и описание)")
def list_skills():
    return catalog()


@skill("Мета", "Сколько всего навыков")
def skills_count():
    return f"Навыков: {len(SKILLS)}"


@skill("Мета", "Найти навык по ключевому слову")
def find_skill(keyword):
    kw = keyword.lower()
    hits = [f"{n} — {m['desc']}" for n, m in SKILLS.items()
            if kw in n.lower() or kw in m["desc"].lower()]
    return "\n".join(hits) or "(не найдено)"


# ======================================================================
#  Подключение модулей-расширений (статические файлы, которые пишем сами)
# ======================================================================
_EXT = ("skills_text", "skills_data", "skills_image", "skills_docs",
        "skills_net", "skills_win", "skills_dev", "skills_media", "skills_auto",
        "skills_present")
for _m in _EXT:
    try:
        __import__(_m)
    except Exception as _e:
        print(f"[skills] модуль {_m} не загружен: {_e}")


if __name__ == "__main__":
    print(catalog())
