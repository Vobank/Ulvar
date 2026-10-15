# -*- coding: utf-8 -*-
"""Навыки Ульвара: системное администрирование Windows."""
from skills import skill, _ok, _err
import subprocess
import os


def _ps(cmd, timeout=60):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return (r.stdout + r.stderr).strip()


def _cmd(cmd, timeout=60):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return (r.stdout + r.stderr).strip()


@skill("Windows", "Список установленных программ")
def installed_programs():
    out = _ps("Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
              "Select-Object -ExpandProperty DisplayName -ErrorAction SilentlyContinue | Sort-Object")
    return out[:4000] or "(пусто)"


@skill("Windows", "Программы в автозагрузке")
def startup_programs():
    return _ps("Get-CimInstance Win32_StartupCommand | Select-Object Name,Command | Format-Table -AutoSize | Out-String")[:3000]


@skill("Windows", "Список служб Windows (запущенные)")
def list_services():
    return _ps("Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object -ExpandProperty Name")[:3000]


@skill("Windows", "Запустить службу")
def start_service(name):
    _ps(f"Start-Service -Name '{name}'")
    return _ok(f"служба {name} запущена")


@skill("Windows", "Остановить службу")
def stop_service(name):
    _ps(f"Stop-Service -Name '{name}' -Force")
    return _ok(f"служба {name} остановлена")


@skill("Windows", "Статус конкретной службы")
def service_status(name):
    return _ps(f"(Get-Service -Name '{name}').Status")


@skill("Windows", "Прочитать значение из реестра")
def registry_read(path, name):
    return _ps(f"(Get-ItemProperty -Path '{path}' -Name '{name}').'{name}'")


@skill("Windows", "Список задач планировщика")
def scheduled_tasks():
    return _ps("Get-ScheduledTask | Where-Object {$_.State -ne 'Disabled'} | "
               "Select-Object -ExpandProperty TaskName | Select-Object -First 50")[:3000]


@skill("Windows", "Создать задачу в планировщике (запуск программы в HH:MM)")
def create_task(name, program, time_hhmm="09:00"):
    out = _cmd(f'schtasks /create /tn "{name}" /tr "{program}" /sc daily /st {time_hhmm} /f')
    return out or _ok(f"задача {name} создана")


@skill("Windows", "Удалить задачу планировщика")
def delete_task(name):
    return _cmd(f'schtasks /delete /tn "{name}" /f')


@skill("Windows", "Переменные окружения")
def env_vars():
    return "\n".join(f"{k}={v}" for k, v in sorted(os.environ.items()))[:3000]


@skill("Windows", "Значение переменной окружения")
def get_env(name):
    return os.environ.get(name, "(не задана)")


@skill("Windows", "Задать переменную окружения (для пользователя)")
def set_env(name, value):
    _cmd(f'setx {name} "{value}"')
    return _ok(f"{name} задана (нужен перезапуск программ)")


@skill("Windows", "Список принтеров")
def list_printers():
    return _ps("Get-Printer | Select-Object -ExpandProperty Name")


@skill("Windows", "Напечатать файл на принтере по умолчанию")
def print_file(path):
    try:
        os.startfile(path, "print")
        return _ok(f"отправлено на печать: {path}")
    except Exception as e:
        return _err(str(e))


@skill("Windows", "Очистить временные файлы (%TEMP%)")
def clear_temp():
    import shutil, glob
    temp = os.environ.get("TEMP", "")
    cnt = 0
    for p in glob.glob(os.path.join(temp, "*")):
        try:
            if os.path.isfile(p):
                os.remove(p); cnt += 1
            else:
                shutil.rmtree(p, ignore_errors=True); cnt += 1
        except Exception:
            pass
    return _ok(f"очищено объектов: {cnt}")


@skill("Windows", "Очистить корзину")
def empty_recycle_bin():
    return _ps("Clear-RecycleBin -Force -ErrorAction SilentlyContinue; 'готово'")


@skill("Windows", "Информация о видеокарте")
def gpu_info():
    return _ps("Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,"
               "@{n='VRAM_MB';e={[math]::Round($_.AdapterRAM/1MB)}} | Format-List | Out-String")[:2000]


@skill("Windows", "Загрузка видеокарты NVIDIA (nvidia-smi)")
def gpu_usage():
    return _cmd("nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu "
                "--format=csv,noheader") or "(nvidia-smi недоступна)"


@skill("Windows", "Температура и состояние системы (кратко)")
def system_health():
    cpu = _ps("(Get-CimInstance Win32_Processor).LoadPercentage")
    ram = _ps("$m=Get-CimInstance Win32_OperatingSystem; "
              "[math]::Round(($m.TotalVisibleMemorySize-$m.FreePhysicalMemory)/$m.TotalVisibleMemorySize*100)")
    return f"Загрузка CPU: {cpu}%, ОЗУ занято: {ram}%"


@skill("Windows", "Информация о материнской плате и BIOS")
def motherboard_info():
    return _ps("Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer,Product | Format-List | Out-String")


@skill("Windows", "Серийный номер и модель ПК")
def pc_model():
    return _ps("Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model | Format-List | Out-String")


@skill("Windows", "Список USB-устройств")
def usb_devices():
    return _ps("Get-PnpDevice -Class USB -Status OK | Select-Object -ExpandProperty FriendlyName")[:2000]


@skill("Windows", "Разрешение и количество мониторов")
def monitors_info():
    return _ps("Get-CimInstance Win32_VideoController | Select-Object "
               "CurrentHorizontalResolution,CurrentVerticalResolution | Format-List | Out-String")


@skill("Windows", "Сколько времени работает ПК (последняя загрузка)")
def last_boot():
    return _ps("(Get-CimInstance Win32_OperatingSystem).LastBootUpTime")


@skill("Windows", "Открыть диспетчер задач")
def open_task_manager():
    subprocess.Popen("taskmgr")
    return _ok("диспетчер задач открыт")


@skill("Windows", "Открыть панель управления")
def open_control_panel():
    subprocess.Popen("control")
    return _ok("панель управления открыта")


@skill("Windows", "Открыть проводник в папке")
def open_explorer(path="."):
    subprocess.Popen(f'explorer "{os.path.abspath(path)}"')
    return _ok(f"проводник: {path}")


@skill("Windows", "Включить/выключить ночной свет будет вручную — открыть настройки")
def open_night_light():
    os.startfile("ms-settings:nightlight")
    return _ok("настройки ночного света")


@skill("Windows", "Сменить тему (светлая/тёмная) — открыть настройки")
def open_theme_settings():
    os.startfile("ms-settings:personalization-colors")
    return _ok("настройки темы")


@skill("Windows", "Проверить диск на ошибки (chkdsk, только чтение)")
def check_disk(drive="C:"):
    return _cmd(f"chkdsk {drive}", timeout=120)[:2000]
