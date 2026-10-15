# -*- coding: utf-8 -*-
"""Запуск Ульвара как настольного приложения (отдельное окно)."""
import os
import threading
import time
import sys
import subprocess

import requests
import webview

import server
import llm

PORT = 5099


def ensure_ollama():
    """Если Ollama не запущена — пробуем поднять её."""
    if llm.ensure_ollama():
        return
    env = dict(os.environ)
    env.setdefault("OLLAMA_MODELS", r"D:\Ollama\models")
    try:
        subprocess.Popen(["ollama", "serve"], env=env,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception:
        try:
            subprocess.Popen(
                [os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama app.exe")],
                env=env)
        except Exception:
            pass
    for _ in range(30):
        if llm.ensure_ollama():
            return
        time.sleep(0.5)


def start_server():
    server.run(PORT)


def wait_server():
    for _ in range(60):
        try:
            requests.get(f"http://127.0.0.1:{PORT}/api/status", timeout=1)
            return True
        except Exception:
            time.sleep(0.2)
    return False


WIN_W, WIN_H = 1200, 840


def _find_hwnd(timeout=4.0):
    import ctypes
    import time as _t
    u = ctypes.windll.user32
    end = _t.time() + timeout
    while _t.time() < end:
        hwnd = u.FindWindowW(None, "Ульвар")
        if hwnd:
            return hwnd
        _t.sleep(0.15)
    return 0


def _fit_workarea():
    """Разворачиваем окно во весь монитор, вплотную к краям.
    Координаты берём теми же метриками, в каком масштабе работает SetWindowPos,
    поэтому зазора из-за DPI не возникает.
    - Автоскрытый таскбар: заполняем весь экран минус 1px снизу (чтобы панель
      задач всплывала и окно не считалось полноэкранным).
    - Обычный таскбар: занимаем рабочую область (панель задач остаётся видимой)."""
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32

        class RECT(ctypes.Structure):
            _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                        ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

        hwnd = _find_hwnd()
        if not hwnd:
            return False

        u.ShowWindow(hwnd, 3)  # SW_MAXIMIZE — заполнить монитор целиком, без зазоров

        # автоскрытый ли таскбар?
        autohide = False
        try:
            class APPBARDATA(ctypes.Structure):
                _fields_ = [("cbSize", wintypes.DWORD), ("hWnd", wintypes.HWND),
                            ("uCallbackMessage", wintypes.UINT), ("uEdge", wintypes.UINT),
                            ("rc", RECT), ("lParam", wintypes.LPARAM)]
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(APPBARDATA)
            autohide = bool(ctypes.windll.shell32.SHAppBarMessage(4, ctypes.byref(abd)) & 1)
        except Exception:
            pass

        # Автоскрытый таскбар: оставляем НАСТОЯЩИЙ maximized-режим (окно во весь
        # монитор, вплотную к низу). В этом режиме Windows сам даёт автоскрытому
        # таскбару всплывать поверх окна при наведении — трогать размер НЕ нужно.
        if autohide:
            return True

        # Обычный видимый таскбар: SW_MAXIMIZE у безрамочного окна накрывает панель
        # задач — подрезаем окно ровно до верхнего края таскбара, чтобы он был виден.
        win = RECT()
        u.GetWindowRect(hwnd, ctypes.byref(win))
        x, y = win.left, win.top
        w, h = win.right - win.left, win.bottom - win.top
        tray = u.FindWindowW("Shell_TrayWnd", None)
        if tray and w > 0 and h > 0:
            tr = RECT()
            u.GetWindowRect(tray, ctypes.byref(tr))
            th = tr.bottom - tr.top
            if 0 < th < h // 2 and tr.top > y and win.bottom > tr.top:
                SWP = 0x0004 | 0x0010 | 0x0020  # NOZORDER|NOACTIVATE|FRAMECHANGED
                u.SetWindowPos(hwnd, 0, x, y, w, tr.top - y, SWP)
        return True
    except Exception:
        return False


class WinApi:
    """Кнопки заголовка (свернуть / развернуть-в-окно / закрыть) + изменение размера."""
    def __init__(self):
        self._max = False  # открывается окном по центру

    def minimize(self):
        webview.windows[0].minimize()

    def _screen(self):
        try:
            s = webview.screens[0]
            return s.width, s.height
        except Exception:
            return 1920, 1080

    def maximize_gap(self):
        """Развернуть в рабочую область (не поверх таскбара, без рамки)."""
        if _fit_workarea():
            self._max = True
            return
        w = webview.windows[0]
        try:
            w.maximize()
            self._max = True
        except Exception:
            pass

    def restore_win(self):
        w = webview.windows[0]
        try:
            w.restore()
        except Exception:
            pass
        try:
            sw, sh = self._screen()
            w.resize(WIN_W, WIN_H)
            w.move((sw - WIN_W) // 2, max(0, (sh - WIN_H) // 2))
            self._max = False
        except Exception:
            pass

    def toggle_max(self):
        if self._max:
            self.restore_win()
        else:
            self.maximize_gap()
        return self._max

    def set_size(self, width, height):
        try:
            webview.windows[0].resize(max(600, int(width)), max(400, int(height)))
            self._max = False
        except Exception:
            pass

    def close(self):
        webview.windows[0].destroy()


if __name__ == "__main__":
    threading.Thread(target=ensure_ollama, daemon=True).start()
    threading.Thread(target=start_server, daemon=True).start()
    if not wait_server():
        print("Сервер не поднялся", file=sys.stderr)
    _winapi = WinApi()
    webview.create_window(
        "Ульвар",
        f"http://127.0.0.1:{PORT}",
        width=WIN_W, height=WIN_H, min_size=(900, 620),
        background_color="#101016",
        frameless=True,
        easy_drag=False,
        js_api=_winapi,
    )

    def _ensure_taskbar_button():
        """Гарантируем кнопку окна на панели задач (для frameless-окна
        добавляем стиль WS_EX_APPWINDOW). Без рамки и без чёрной полосы."""
        try:
            import ctypes
            u = ctypes.windll.user32
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd = _find_hwnd()
            if hwnd:
                ex = u.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ex |= WS_EX_APPWINDOW
                ex &= ~WS_EX_TOOLWINDOW
                u.SetWindowLongW(hwnd, GWL_EXSTYLE, ex)
        except Exception:
            pass

    def _onstart():
        import time as _t
        _t.sleep(0.3)
        _ensure_taskbar_button()
        _winapi.maximize_gap()   # развернуть в рабочую область

    webview.start(_onstart)
