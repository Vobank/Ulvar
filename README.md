# Ульвар · Ulvar

**[Русский](#русский) · [English](#english)**

Личный локальный ИИ-ассистент для Windows — как настольное приложение Claude, но полностью на вашем компьютере. Общается, пишет код, управляет ПК (300+ навыков), ищет в интернете, делает документы и презентации. Все диалоги шифруются и не покидают ваш ПК.

A personal, local AI assistant for Windows — like a desktop Claude app, but running entirely on your machine. Chats, writes code, controls your PC (300+ skills), searches the web, creates documents and presentations. All conversations are encrypted and never leave your computer.

<img width="1" height="1" alt="" src="#"/>

---

## Русский

### Что это
Ульвар — настольное приложение (отдельное окно, не вкладка браузера), которое работает на локальной модели через [Ollama](https://ollama.com). Ничего не отправляется в облако (кроме интернет-поиска, если вы его включите).

### Возможности
- 💬 Общение и помощь с кодом, как у больших ИИ-ассистентов
- 🛠 Режим агента: 300+ «навыков» — управление файлами, окнами, мышью/клавиатурой, системой, медиа
- 🔎 Авто-поиск в интернете по многим сайтам (с источниками)
- 🖼 Зрение: понимает присланные картинки и скриншоты
- 📄 Создаёт документы Word/Excel/PDF и простые презентации
- 🗂 Проекты: отдельные пространства с общим контекстом
- 🎨 Темы (системная/светлая/тёмная) и языки (русский/English)
- 🔒 Переписка и память шифруются (AES), вход по ПИН

### Требования
- Windows 10/11
- Видеокарта с 8+ ГБ видеопамяти — для комфортной работы локальной модели
  (слабый ПК? в настройках можно переключиться на облачный API)
- ~20 ГБ свободного места (модели)

### Установка
1. Скачайте и распакуйте проект.
2. Запустите **`Установить.bat`** — он сам поставит Python, библиотеки, Ollama и модели, спросит язык.
3. На рабочем столе появится ярлык **«Ульвар»** — запускайте им.
4. ПИН для входа: **`0000`** (меняется в коде/настройках).

### Настройки
Всё внутри приложения (⚙ Настройки): модель, тема, язык, «отвечать на языке сообщения», опасные действия агента, ключ поиска Tavily, имя, характер ассистента.

### Приватность
Диалоги и память лежат зашифрованными в папке `data` только на вашем ПК. ПИН `0000` — это удобный замок на вход, а не криптозащита от эксперта с доступом к диску.

---

## English

### What it is
Ulvar is a desktop app (its own window, not a browser tab) powered by a local model via [Ollama](https://ollama.com). Nothing goes to the cloud (except web search, if you enable it).

### Features
- 💬 Chat and coding help, like the big AI assistants
- 🛠 Agent mode: 300+ "skills" — control files, windows, mouse/keyboard, system, media
- 🔎 Auto web search across many sites (with sources)
- 🖼 Vision: understands images and screenshots you send
- 📄 Creates Word/Excel/PDF documents and simple presentations
- 🗂 Projects: separate spaces with shared context
- 🎨 Themes (system/light/dark) and languages (Russian/English)
- 🔒 Conversations and memory are encrypted (AES), PIN login

### Requirements
- Windows 10/11
- A GPU with 8+ GB VRAM for a smooth local model
  (weak PC? switch to a cloud API in settings)
- ~20 GB free space (models)

### Install
1. Download and unzip the project.
2. Run **`Установить.bat`** (the installer) — it installs Python, libraries, Ollama and the models, and asks for your language.
3. A **"Ulvar"** shortcut appears on your desktop — launch it from there.
4. Login PIN: **`0000`** (change it in the code/settings).

### Settings
Everything is in-app (⚙ Settings): model, theme, language, "reply in the message's language", agent's dangerous actions, Tavily search key, your name, assistant persona.

### Privacy
Conversations and memory are stored encrypted in the `data` folder on your PC only. The `0000` PIN is a convenient lock, not expert-grade protection against someone with disk access.

---

### Технологии / Tech
Python · Flask · pywebview · Ollama (qwen2.5) · cryptography (Fernet/AES) · reportlab · Tavily (optional)

### Лицензия / License
MIT — see [LICENSE](LICENSE).
