# -*- coding: utf-8 -*-
# Установщик Ульвара на чистую Windows.
# Ставит Python (если нет), создаёт venv и зависимости, ставит Ollama и модели,
# настраивает язык и создаёт ярлык на рабочем столе.
$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path','User')
}
function Have($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }

Write-Host ""
Write-Host "==================================================" -ForegroundColor DarkCyan
Write-Host "   УЛЬВАР — установка / Ulvar - setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor DarkCyan
Write-Host ""

# --- Язык интерфейса ---
Write-Host "Выберите язык / Choose language:"
Write-Host "  [1] Русский"
Write-Host "  [2] English"
$sel = Read-Host "1/2"
$LANG = if ($sel -eq "2") { "en" } else { "ru" }
$RU = ($LANG -eq "ru")
function Say($ru, $en) { if ($RU) { Write-Host $ru } else { Write-Host $en } }

# --- Python ---
Say "`n[1/5] Проверяю Python..." "`n[1/5] Checking Python..."
$PY = $null
foreach ($cand in @("py -3.12","py -3","python")) {
    $exe, $arg = $cand.Split(" ",2)
    if (Have $exe) {
        try {
            $v = & $exe $arg --version 2>&1
            if ($v -match "3\.(1[0-9]|[2-9][0-9])") { $PY = $cand; break }
        } catch {}
    }
}
if (-not $PY) {
    Say "Python не найден — ставлю через winget..." "Python not found - installing via winget..."
    if (Have "winget") {
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
        Refresh-Path
        if (Have "py") { $PY = "py -3" } elseif (Have "python") { $PY = "python" }
    }
}
if (-not $PY) {
    Say "Не удалось поставить Python автоматически. Открою страницу загрузки — установите Python 3.12 (галочка 'Add to PATH') и запустите установку заново." `
        "Could not install Python automatically. Opening the download page - install Python 3.12 (check 'Add to PATH') and run setup again."
    Start-Process "https://www.python.org/downloads/"
    Read-Host "Enter — выход / exit"; exit 1
}
$pyExe, $pyArg = $PY.Split(" ",2)
Say "Python найден: $PY" "Python found: $PY"

# --- venv + зависимости ---
Say "`n[2/5] Создаю окружение и ставлю библиотеки (это займёт пару минут)..." `
    "`n[2/5] Creating environment and installing libraries (a couple of minutes)..."
if (-not (Test-Path "$ROOT\venv")) { & $pyExe $pyArg -m venv "$ROOT\venv" }
& "$ROOT\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
& "$ROOT\venv\Scripts\python.exe" -m pip install -r "$ROOT\requirements.txt"

# --- Ollama ---
Say "`n[3/5] Проверяю Ollama (локальный ИИ-движок)..." "`n[3/5] Checking Ollama (local AI engine)..."
if (-not (Have "ollama")) {
    if (Have "winget") {
        winget install -e --id Ollama.Ollama --accept-package-agreements --accept-source-agreements --silent
        Refresh-Path
    }
}
if (-not (Have "ollama")) {
    Say "Ollama не установлена. Открою страницу — установите и запустите установку заново." `
        "Ollama is not installed. Opening the page - install it and run setup again."
    Start-Process "https://ollama.com/download"
    Read-Host "Enter — выход / exit"; exit 1
}

# --- Модели ---
Say "`n[4/5] Скачиваю ИИ-модели (большая загрузка, ~15 ГБ — можно отойти)..." `
    "`n[4/5] Downloading AI models (large download, ~15 GB - grab a coffee)..."
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
ollama pull qwen2.5:14b-instruct
ollama pull qwen2.5vl:7b

# --- Настройки: язык ---
Say "`n[5/5] Применяю настройки..." "`n[5/5] Applying settings..."
& "$ROOT\venv\Scripts\python.exe" -c "import store; s=store.get_settings(); s['lang']='$LANG'; store.save_settings(s)"

# --- Ярлык на рабочем столе ---
try {
    $desktop = [Environment]::GetFolderPath("Desktop")
    $ws = New-Object -ComObject WScript.Shell
    $sc = $ws.CreateShortcut("$desktop\Ульвар.lnk")
    $sc.TargetPath = "$ROOT\venv\Scripts\pythonw.exe"
    $sc.Arguments = "`"$ROOT\main.py`""
    $sc.WorkingDirectory = $ROOT
    $sc.IconLocation = "$ROOT\venv\Scripts\pythonw.exe,0"
    $sc.Save()
} catch {}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Say "   Готово! Запустите «Ульвар» с рабочего стола." "   Done! Launch 'Ulvar' from the desktop."
Say "   ПИН для входа: 0000" "   Login PIN: 0000"
Write-Host "==================================================" -ForegroundColor Green
Read-Host "Enter — закрыть / close"
