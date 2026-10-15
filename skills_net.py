# -*- coding: utf-8 -*-
"""Навыки Ульвара: сеть и интернет (расширенные)."""
from skills import skill, _ok, _err
import socket
import subprocess
import requests


@skill("Сеть", "Узнать IP-адрес по доменному имени")
def resolve_host(host):
    try:
        return socket.gethostbyname(host)
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Проверить, открыт ли порт на хосте")
def check_port(host, port, timeout=3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(float(timeout))
        r = s.connect_ex((host, int(port)))
        s.close()
        return f"Порт {port} на {host}: {'ОТКРЫТ' if r == 0 else 'закрыт'}"
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Сканировать популярные порты на хосте")
def scan_ports(host="127.0.0.1"):
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 11434]
    open_ports = []
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(0.5)
        if s.connect_ex((host, p)) == 0:
            open_ports.append(str(p))
        s.close()
    return f"Открытые порты на {host}: {', '.join(open_ports) or 'нет'}"


@skill("Сеть", "HTTP-заголовки сайта")
def http_headers(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        r = requests.head(url, timeout=15, allow_redirects=True)
        return "\n".join(f"{k}: {v}" for k, v in r.headers.items())
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Статус-код сайта (жив ли сайт)")
def site_status(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        r = requests.get(url, timeout=15)
        return f"{url} → {r.status_code} ({'OK' if r.ok else 'проблема'})"
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Скорость загрузки (примерный тест)")
def speed_test():
    try:
        import time
        url = "https://speed.hetzner.de/10MB.bin"
        t = time.time()
        size = 0
        with requests.get(url, stream=True, timeout=30) as r:
            for chunk in r.iter_content(65536):
                size += len(chunk)
                if size > 5_000_000:
                    break
        mbps = (size*8/1e6)/(time.time()-t)
        return f"Примерная скорость: {mbps:.1f} Мбит/с"
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Список Wi-Fi сетей вокруг")
def wifi_list():
    try:
        r = subprocess.run("netsh wlan show networks", shell=True, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        nets = [l.split(":", 1)[1].strip() for l in r.stdout.splitlines() if l.strip().startswith("SSID")]
        return "\n".join(nets) or "(не найдено)"
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Показать текущую Wi-Fi сеть и сигнал")
def wifi_current():
    try:
        r = subprocess.run("netsh wlan show interfaces", shell=True, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        keep = [l.strip() for l in r.stdout.splitlines()
                if any(k in l for k in ("SSID", "Сигнал", "Signal", "Канал", "Channel"))]
        return "\n".join(keep) or "(нет данных)"
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Пароль от сохранённой Wi-Fi сети (своей)")
def wifi_password(ssid):
    try:
        r = subprocess.run(f'netsh wlan show profile name="{ssid}" key=clear',
                           shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        for l in r.stdout.splitlines():
            if "Key Content" in l or "Содержимое ключа" in l:
                return l.split(":", 1)[1].strip()
        return "(пароль не найден)"
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Сбросить кэш DNS")
def flush_dns():
    subprocess.run("ipconfig /flushdns", shell=True)
    return _ok("DNS-кэш сброшен")


@skill("Сеть", "IP-конфигурация сетевых адаптеров")
def ipconfig():
    r = subprocess.run("ipconfig", shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout.strip()[:3000]


@skill("Сеть", "Трассировка маршрута до хоста")
def traceroute(host="google.com"):
    r = subprocess.run(f"tracert -h 15 {host}", shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    return r.stdout.strip()[:3000]


@skill("Сеть", "Активные сетевые подключения")
def netstat():
    r = subprocess.run("netstat -n", shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return "\n".join(r.stdout.splitlines()[:40])


@skill("Сеть", "Геолокация по IP-адресу")
def ip_location(ip=""):
    try:
        url = f"http://ip-api.com/json/{ip}?lang=ru"
        d = requests.get(url, timeout=15).json()
        if d.get("status") == "success":
            return f"{d.get('country')}, {d.get('city')} — {d.get('isp')}"
        return "(не удалось определить)"
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Скачать картинку по ссылке")
def download_image(url, out=None):
    try:
        import os
        from skills import downloads_folder
        out = out or os.path.join(downloads_folder(), url.split("/")[-1].split("?")[0] or "image.jpg")
        with requests.get(url, stream=True, timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as r:
            with open(out, "wb") as f:
                for c in r.iter_content(8192):
                    f.write(c)
        return _ok(out)
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "Извлечь все ссылки со страницы")
def extract_page_links(url):
    try:
        import re
        if not url.startswith("http"):
            url = "https://" + url
        html = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
        links = re.findall(r'href=["\'](https?://[^"\']+)', html)
        return "\n".join(sorted(set(links))[:50]) or "(нет ссылок)"
    except Exception as e:
        return _err(str(e))


def _fmt_search(parts, sources):
    text = "\n".join(parts)[:2500]
    srcs = [(t, u) for t, u in sources if u]
    if srcs:
        text += "\n\nИСТОЧНИКИ:\n" + "\n".join(f"{t} | {u}" for t, u in srcs[:8])
    return text


@skill("Интернет", "Поиск в интернете — найти информацию (по многим сайтам, если есть ключ Tavily) и вернуть текст + источники")
def web_search_results(query, count=6):
    import re
    UA = {"User-Agent": "UlvarAssistant/1.0 (personal local AI assistant; +https://localhost)"}
    sources = []
    # ключ Tavily (многосайтовый поиск)
    key = ""
    try:
        import store
        key = store.get_settings().get("tavily_key", "")
    except Exception:
        pass
    if key:
        try:
            d = requests.post("https://api.tavily.com/search",
                              json={"api_key": key, "query": query, "max_results": int(count),
                                    "include_answer": True}, timeout=25).json()
            parts = []
            if d.get("answer"):
                parts.append(d["answer"])
            for r in d.get("results", []):
                parts.append(f"• {r.get('title','')}: {(r.get('content','') or '')[:200]}")
                sources.append((r.get("title", "")[:50], r.get("url", "")))
            if parts:
                return _fmt_search(parts, sources)
        except Exception:
            pass
    # бесплатно: DuckDuckGo Instant Answer
    try:
        d = requests.get("https://api.duckduckgo.com/",
                         params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                         headers=UA, timeout=15).json()
        parts = []
        if d.get("AbstractText"):
            parts.append(d["AbstractText"])
            if d.get("AbstractURL"):
                sources.append((d.get("Heading", "DuckDuckGo"), d["AbstractURL"]))
        if d.get("Answer"):
            parts.append(str(d["Answer"]))
        for t in (d.get("RelatedTopics") or []):
            if isinstance(t, dict) and t.get("Text"):
                parts.append("• " + t["Text"])
                if t.get("FirstURL"):
                    sources.append((t["Text"][:40], t["FirstURL"]))
            if len(parts) >= int(count) + 1:
                break
        if parts:
            return _fmt_search(parts, sources)
    except Exception:
        pass
    # бесплатно: Википедия (рус, затем англ)
    for lang in ("ru", "en"):
        try:
            s = requests.get(f"https://{lang}.wikipedia.org/w/api.php",
                             params={"action": "query", "list": "search", "srsearch": query,
                                     "format": "json", "srlimit": int(count)},
                             headers=UA, timeout=15).json()
            hits = s.get("query", {}).get("search", [])
            if hits:
                parts = []
                for h in hits[:int(count)]:
                    snip = re.sub(r"<[^>]+>", "", h.get("snippet", "")).strip()
                    parts.append(f"{h['title']}: {snip}")
                    sources.append((h["title"],
                                    f"https://{lang}.wikipedia.org/wiki/" + h["title"].replace(" ", "_")))
                return _fmt_search(parts, sources)
        except Exception:
            pass
    return "(ничего не найдено)"


@skill("Сеть", "GET-запрос к API (возвращает JSON)")
def api_get(url, params=None):
    try:
        r = requests.get(url, params=params or {}, timeout=20)
        return r.text[:3000]
    except Exception as e:
        return _err(str(e))


@skill("Сеть", "POST-запрос к API с JSON-телом")
def api_post(url, json_body=None):
    try:
        r = requests.post(url, json=json_body or {}, timeout=20)
        return f"{r.status_code}: {r.text[:2000]}"
    except Exception as e:
        return _err(str(e))
