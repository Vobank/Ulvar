# -*- coding: utf-8 -*-
"""Навыки Ульвара: данные (CSV, JSON, числа)."""
from skills import skill, _ok, _err
import json as _json
import csv as _csv
import io
import statistics as _st


@skill("Данные", "Прочитать CSV и показать первые строки")
def csv_preview(path, rows=10):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            r = list(_csv.reader(f))
        return "\n".join(", ".join(row) for row in r[:int(rows)+1])
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Сколько строк и колонок в CSV")
def csv_shape(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            r = list(_csv.reader(f))
        cols = len(r[0]) if r else 0
        return f"Строк: {len(r)}, колонок: {cols}"
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Заголовки колонок CSV")
def csv_headers(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return ", ".join(next(_csv.reader(f)))
    except Exception as e:
        return _err(str(e))


@skill("Данные", "CSV → JSON")
def csv_to_json(path, out=None):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            data = list(_csv.DictReader(f))
        out = out or path.rsplit(".", 1)[0] + ".json"
        with open(out, "w", encoding="utf-8") as f:
            _json.dump(data, f, ensure_ascii=False, indent=2)
        return _ok(f"сохранено: {out} ({len(data)} записей)")
    except Exception as e:
        return _err(str(e))


@skill("Данные", "JSON → CSV")
def json_to_csv(path, out=None):
    try:
        with open(path, encoding="utf-8") as f:
            data = _json.load(f)
        if isinstance(data, dict):
            data = [data]
        out = out or path.rsplit(".", 1)[0] + ".csv"
        keys = list({k for row in data for k in row})
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = _csv.DictWriter(f, fieldnames=keys)
            w.writeheader(); w.writerows(data)
        return _ok(f"сохранено: {out}")
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Проверить, корректен ли JSON")
def json_validate(text):
    try:
        _json.loads(text)
        return "✓ JSON корректен"
    except Exception as e:
        return f"✗ ошибка: {e}"


@skill("Данные", "Минимизировать JSON (в одну строку)")
def json_minify(text):
    try:
        return _json.dumps(_json.loads(text), ensure_ascii=False, separators=(",", ":"))
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Достать значение из JSON по ключу (точечный путь a.b.c)")
def json_get(text, path):
    try:
        obj = _json.loads(text)
        for part in path.split("."):
            obj = obj[int(part)] if part.isdigit() else obj[part]
        return _json.dumps(obj, ensure_ascii=False)
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Среднее, медиана, сумма чисел (через запятую/пробел)")
def number_stats(numbers):
    try:
        nums = [float(x) for x in numbers.replace(",", " ").split()]
        return (f"Кол-во: {len(nums)}, сумма: {sum(nums):g}, среднее: {_st.mean(nums):g}, "
                f"медиана: {_st.median(nums):g}, мин: {min(nums):g}, макс: {max(nums):g}")
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Отсортировать числа")
def sort_numbers(numbers, desc=False):
    try:
        nums = sorted((float(x) for x in numbers.replace(",", " ").split()), reverse=bool(desc))
        return ", ".join(f"{n:g}" for n in nums)
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Сумма чисел")
def sum_numbers(numbers):
    try:
        return str(sum(float(x) for x in numbers.replace(",", " ").split()))
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Процент: сколько X% от Y")
def percent_of(x, y):
    try:
        return f"{float(x)}% от {float(y)} = {float(x)*float(y)/100:g}"
    except Exception as e:
        return _err(str(e))


@skill("Данные", "На сколько % X больше/меньше Y")
def percent_change(old, new):
    try:
        old, new = float(old), float(new)
        return f"{(new-old)/old*100:+.1f}%"
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Перевести единицы (км↔миль, кг↔фунт, °C↔°F)")
def convert_units(value, frm, to):
    try:
        v = float(value)
        table = {("km", "mi"): v*0.621371, ("mi", "km"): v*1.60934,
                 ("kg", "lb"): v*2.20462, ("lb", "kg"): v/2.20462,
                 ("c", "f"): v*9/5+32, ("f", "c"): (v-32)*5/9,
                 ("m", "ft"): v*3.28084, ("ft", "m"): v/3.28084}
        key = (frm.lower(), to.lower())
        return f"{v} {frm} = {table[key]:g} {to}" if key in table else _err("не знаю такой перевод")
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Римские цифры из числа")
def to_roman(num):
    try:
        num = int(num)
        vals = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),
                (50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
        res = ""
        for v, s in vals:
            while num >= v:
                res += s; num -= v
        return res
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Число в двоичный/шестнадцатеричный вид")
def number_base(num, base=2):
    try:
        n = int(num)
        return {2: bin(n), 8: oct(n), 16: hex(n)}.get(int(base), str(n))
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Факториал числа")
def factorial(n):
    try:
        import math
        return str(math.factorial(int(n)))
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Простое ли число")
def is_prime(n):
    try:
        n = int(n)
        if n < 2:
            return "нет"
        for i in range(2, int(n**0.5)+1):
            if n % i == 0:
                return f"нет (делится на {i})"
        return "да, простое"
    except Exception as e:
        return _err(str(e))


@skill("Данные", "Среднее нескольких CSV-колонок по числам (имя колонки)")
def csv_column_sum(path, column):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            rows = list(_csv.DictReader(f))
        vals = [float(r[column]) for r in rows if r.get(column, "").strip().replace(".", "").replace("-", "").isdigit()]
        return f"Сумма '{column}': {sum(vals):g}, среднее: {sum(vals)/len(vals):g}" if vals else "(нет чисел)"
    except Exception as e:
        return _err(str(e))
