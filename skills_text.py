# -*- coding: utf-8 -*-
"""Навыки Ульвара: работа с текстом."""
from skills import skill, _ok, _err
import re
import html as _html
import unicodedata
import random as _rnd


@skill("Текст", "ВЕРХНИЙ регистр")
def to_upper(text): return text.upper()


@skill("Текст", "нижний регистр")
def to_lower(text): return text.lower()


@skill("Текст", "Каждое Слово С Большой Буквы")
def to_title(text): return text.title()


@skill("Текст", "Первая буква заглавная")
def capitalize_text(text): return text.capitalize()


@skill("Текст", "Убрать лишние пробелы")
def trim_spaces(text): return re.sub(r"\s+", " ", text).strip()


@skill("Текст", "Перевернуть текст задом наперёд")
def reverse_text(text): return text[::-1]


@skill("Текст", "Сделать slug для URL (латиница-дефисы)")
def slugify(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


@skill("Текст", "Посчитать, сколько раз встречается подстрока")
def count_occurrences(text, sub): return str(text.lower().count(sub.lower()))


@skill("Текст", "Заменить одну подстроку на другую")
def replace_text(text, old, new): return text.replace(old, new)


@skill("Текст", "Удалить все цифры из текста")
def remove_digits(text): return re.sub(r"\d", "", text)


@skill("Текст", "Оставить только цифры")
def only_digits(text): return re.sub(r"\D", "", text)


@skill("Текст", "Извлечь все e-mail адреса")
def extract_emails(text):
    return "\n".join(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)) or "(нет)"


@skill("Текст", "Извлечь все ссылки (URL)")
def extract_urls(text):
    return "\n".join(re.findall(r"https?://[^\s]+", text)) or "(нет)"


@skill("Текст", "Извлечь все телефонные номера")
def extract_phones(text):
    return "\n".join(re.findall(r"\+?\d[\d\s()-]{7,}\d", text)) or "(нет)"


@skill("Текст", "Сосчитать строки, слова, символы")
def text_stats(text):
    return f"Строк: {text.count(chr(10))+1}, слов: {len(text.split())}, символов: {len(text)}"


@skill("Текст", "Отсортировать строки по алфавиту")
def sort_lines(text):
    return "\n".join(sorted(text.splitlines()))


@skill("Текст", "Убрать повторяющиеся строки")
def unique_lines(text):
    seen, out = set(), []
    for l in text.splitlines():
        if l not in seen:
            seen.add(l); out.append(l)
    return "\n".join(out)


@skill("Текст", "Пронумеровать строки")
def number_lines(text):
    return "\n".join(f"{i}. {l}" for i, l in enumerate(text.splitlines(), 1))


@skill("Текст", "Обрезать текст до N символов")
def truncate(text, n=100):
    n = int(n)
    return text[:n] + ("…" if len(text) > n else "")


@skill("Текст", "Экранировать HTML-символы")
def html_escape(text): return _html.escape(text)


@skill("Текст", "Раскодировать HTML-символы")
def html_unescape(text): return _html.unescape(text)


@skill("Текст", "Сгенерировать текст-рыбу (lorem ipsum)")
def lorem(words=50):
    base = ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
            "tempor incididunt ut labore et dolore magna aliqua").split()
    return " ".join(_rnd.choice(base) for _ in range(int(words)))


@skill("Текст", "Разница между двумя текстами (построчно)")
def text_diff(a, b):
    import difflib
    return "\n".join(difflib.unified_diff(a.splitlines(), b.splitlines(),
                                          lineterm="", n=1)) or "(тексты одинаковы)"


@skill("Текст", "Похожесть двух текстов в процентах")
def text_similarity(a, b):
    import difflib
    return f"{difflib.SequenceMatcher(None, a, b).ratio()*100:.0f}% схожести"


@skill("Текст", "Markdown → HTML (базовый)")
def md_to_html(text):
    t = _html.escape(text)
    t = re.sub(r"^### (.*)$", r"<h3>\1</h3>", t, flags=re.M)
    t = re.sub(r"^## (.*)$", r"<h2>\1</h2>", t, flags=re.M)
    t = re.sub(r"^# (.*)$", r"<h1>\1</h1>", t, flags=re.M)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    return t.replace("\n", "<br>\n")


@skill("Текст", "Убрать знаки препинания")
def remove_punctuation(text):
    return re.sub(r"[^\w\s]", "", text)


@skill("Текст", "Частота слов (топ)")
def word_frequency(text, top=10):
    import collections
    words = re.findall(r"\w+", text.lower())
    c = collections.Counter(words).most_common(int(top))
    return "\n".join(f"{w}: {n}" for w, n in c)


@skill("Текст", "Транслитерация кириллицы в латиницу")
def translit(text):
    m = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
         "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
         "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts",
         "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya"}
    return "".join(m.get(c, m.get(c.lower(), c)).upper() if c.isupper() else m.get(c, c) for c in text)


@skill("Текст", "Обернуть текст по ширине (перенос строк)")
def wrap_text(text, width=80):
    import textwrap
    return "\n".join(textwrap.wrap(text, int(width)))


@skill("Текст", "Вынуть текст между двумя метками")
def extract_between(text, start, end):
    res = re.findall(re.escape(start) + r"(.*?)" + re.escape(end), text, re.S)
    return "\n".join(res) or "(не найдено)"
