const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
let currentId = null, streaming = false, count = 0;
let pendImages = [], pendFiles = [], allConvs = [];
let lastBotBody = null, delId = null;

function win(a) { try { window.pywebview.api[a](); } catch (e) { } }

/* ======== Тема и язык (i18n) ======== */
let lang = "ru", theme = "system", savedTheme = "system", savedLang = "ru";
const I18N = {
  ru: {
    settings: "Настройки", g_look: "Вид", theme: "Тема", theme_sys: "Система",
    theme_light: "Светлая", theme_dark: "Тёмная", language: "Язык",
    g_engine: "Движок", engine: "Где работает модель",
    engine_s: "Локально — через Ollama. По API — облако (для слабых ПК).",
    engine_local: "Локально", engine_api: "По API", api_base: "Адрес API",
    api_key: "Ключ API", api_model: "Модель в облаке", g_model: "Модель",
    model_main: "Основная модель", model_vision: "Для картинок (зрение)",
    auto_model: "Авто-выбор модели", auto_model_s: "Простое — быстрой, сложное — умной.",
    temp: "Креативность", g_agent: "Агент", danger: "Опасные действия без подтверждения",
    danger_s: "Удаление, выключение и т.п.", g_search: "Поиск", tavily: "Ключ Tavily",
    tavily_s: "Поиск сразу по многим сайтам. Бесплатно на tavily.com.",
    g_personal: "Личное", your_name: "Как к тебе обращаться", persona: "Характер Ульвара",
    persona_s: "Пусто = стандартный.", g_data: "Данные",
    export: "⬇ Выгрузить текущий диалог в файл", clear_all: "🗑 Очистить все диалоги",
    cancel: "Отмена", save: "Сохранить", new_chat: "Новый диалог", earlier: "Ранее",
    mi_attach: "📎 Прикрепить файлы или фото", mi_skills: "🧩 Навыки",
    mi_agent: "🛠 Режим агента", mi_web: "🔎 Поиск в интернете",
    search_ph: "Поиск по диалогам", composer_ph: "Чем помочь сегодня?",
    greet_night: "Доброй ночи", greet_morning: "Доброе утро",
    greet_day: "Добрый день", greet_evening: "Добрый вечер",
    enter_pin: "Введи ПИН", wrong_pin: "Неверный ПИН",
    reply_match: "Отвечать на языке сообщения", reply_match_s: "Иначе — всегда на языке интерфейса.",
    brand: "Ульвар",
    status_online: "🟢 Онлайн · работает локально", status_offline: "🔴 Модель не запущена (запусти Ollama)",
    status_api: "☁ Онлайн · облачный API", status_model: "Модель", status_skills: "Навыков", status_convs: "Диалогов",
    skills_title: "Навыки Ульвара", skills_search_ph: "Поиск навыка…", close: "Закрыть",
    del_title: "Удалить диалог?", del_text: "Это действие нельзя отменить.", delete: "Удалить",
    agent_on: "вкл", agent_off: "выкл", today: "сегодня", yesterday: "вчера",
    copy: "Копировать", copied: "Скопировано ✓",
    confirm_clear: "Удалить ВСЕ диалоги? Это нельзя отменить.", all_cleared: "Все диалоги удалены.",
    no_open_dialog: "Нет открытого диалога.", done: "(готово)",
    agent_ph: "Дай задание — Ульвар сделает на ПК…",
    projects: "Проекты", project_new: "＋ Новый проект", project_create: "Новый проект",
    project_edit: "Изменить проект", project_name: "Название",
    project_instr: "Инструкции — контекст для всех чатов проекта",
    no_projects: "Пока нет проектов. Создай первый — и чаты в нём будут помнить общий контекст.",
    created: "Создан", chats_n: "чатов", regen: "↻ Переписать", image: "изображение",
    confirm_del_project: "Удалить проект? Чаты останутся, но выйдут из проекта.",
    searching: "🔎 ищу по смыслу…", nothing_found: "Ничего не найдено", search_err: "Ошибка поиска",
    sk_total: "всего", sk_in: "в проекте",
    recent_opened: "Недавно открытые", no_recent: "Пока пусто", remove_recent: "Убрать из недавних",
  },
  en: {
    settings: "Settings", g_look: "Appearance", theme: "Theme", theme_sys: "System",
    theme_light: "Light", theme_dark: "Dark", language: "Language",
    g_engine: "Engine", engine: "Where the model runs",
    engine_s: "Local — via Ollama. API — cloud (for weak PCs).",
    engine_local: "Local", engine_api: "API", api_base: "API URL",
    api_key: "API key", api_model: "Cloud model", g_model: "Model",
    model_main: "Main model", model_vision: "For images (vision)",
    auto_model: "Auto model choice", auto_model_s: "Simple → fast, complex → smart.",
    temp: "Creativity", g_agent: "Agent", danger: "Dangerous actions without confirmation",
    danger_s: "Deleting, shutting down, etc.", g_search: "Search", tavily: "Tavily key",
    tavily_s: "Search across many sites at once. Free at tavily.com.",
    g_personal: "Personal", your_name: "How to address you", persona: "Ulvar's character",
    persona_s: "Empty = default.", g_data: "Data",
    export: "⬇ Export current chat to file", clear_all: "🗑 Clear all chats",
    cancel: "Cancel", save: "Save", new_chat: "New chat", earlier: "Earlier",
    mi_attach: "📎 Attach files or photos", mi_skills: "🧩 Skills",
    mi_agent: "🛠 Agent mode", mi_web: "🔎 Web search",
    search_ph: "Search chats", composer_ph: "How can I help today?",
    greet_night: "Good night", greet_morning: "Good morning",
    greet_day: "Good afternoon", greet_evening: "Good evening",
    enter_pin: "Enter PIN", wrong_pin: "Wrong PIN",
    reply_match: "Reply in the message's language", reply_match_s: "Otherwise — always in the interface language.",
    brand: "Ulvar",
    status_online: "🟢 Online · running locally", status_offline: "🔴 Model not running (start Ollama)",
    status_api: "☁ Online · cloud API", status_model: "Model", status_skills: "Skills", status_convs: "Chats",
    skills_title: "Ulvar skills", skills_search_ph: "Search skill…", close: "Close",
    del_title: "Delete chat?", del_text: "This action cannot be undone.", delete: "Delete",
    agent_on: "on", agent_off: "off", today: "today", yesterday: "yesterday",
    copy: "Copy", copied: "Copied ✓",
    confirm_clear: "Delete ALL chats? This cannot be undone.", all_cleared: "All chats deleted.",
    no_open_dialog: "No open chat.", done: "(done)",
    agent_ph: "Give a task — Ulvar will do it on the PC…",
    projects: "Projects", project_new: "＋ New project", project_create: "New project",
    project_edit: "Edit project", project_name: "Name",
    project_instr: "Instructions — context for all chats in the project",
    no_projects: "No projects yet. Create one — chats inside it will share a common context.",
    created: "Created", chats_n: "chats", regen: "↻ Regenerate", image: "image",
    confirm_del_project: "Delete project? Chats stay but leave the project.",
    searching: "🔎 searching by meaning…", nothing_found: "Nothing found", search_err: "Search error",
    sk_total: "total", sk_in: "in project",
    recent_opened: "Recently opened", no_recent: "Nothing yet", remove_recent: "Remove from recent",
  },
};
function t(key) { return (I18N[lang] && I18N[lang][key] !== undefined) ? I18N[lang][key] : (I18N.ru[key] !== undefined ? I18N.ru[key] : key); }
const CATS_EN = {
  "Excel": "Excel", "Git": "Git", "PDF": "PDF", "Python": "Python", "Windows": "Windows",
  "Word": "Word", "Автоматизация": "Automation", "Буфер": "Clipboard", "Вид": "Appearance",
  "Данные": "Data", "Документы": "Documents", "Изображения": "Images", "Интернет": "Internet",
  "Медиа": "Media", "Мета": "Meta", "Окна": "App windows", "Презентации": "Presentations",
  "Разработка": "Development", "Сеть": "Network", "Система": "System", "Текст": "Text",
  "Уведомления": "Notifications", "Утилиты": "Utilities", "Файлы": "Files", "Экран": "Screen",
};
function catName(c) { return lang === "en" ? (CATS_EN[c] || c) : c; }
let skillsEn = null;
async function loadSkillsEn() {
  if (skillsEn) return;
  try { skillsEn = await (await fetch("/ui/skills_en.json")).json(); } catch (e) { skillsEn = {}; }
}
function skillDesc(s) { return (lang === "en" && skillsEn && skillsEn[s.name]) ? skillsEn[s.name] : s.desc; }
function applyTheme(v) { theme = v || "system"; document.documentElement.dataset.theme = theme; }
function applyLang(v) {
  lang = (v === "en") ? "en" : "ru";
  document.documentElement.lang = lang;
  $$("[data-i18n]").forEach(e => { const k = e.getAttribute("data-i18n"); if (I18N[lang][k] !== undefined) e.textContent = I18N[lang][k]; });
  $$("[data-i18n-ph]").forEach(e => { const k = e.getAttribute("data-i18n-ph"); if (I18N[lang][k] !== undefined) e.setAttribute("placeholder", I18N[lang][k]); });
  if (typeof setGreet === "function") setGreet();
  if (typeof agentMode !== "undefined" && typeof setAgentMode === "function") setAgentMode(agentMode, false);
  if (typeof renderConvs === "function") try { renderConvs(); } catch (e) {}
  if (typeof refreshStatus === "function") try { refreshStatus(); } catch (e) {}
}
function segSelect(seg, v) { $$("#" + seg + " button").forEach(b => b.classList.toggle("on", b.dataset.v === v)); }
function segValue(seg) { const b = $("#" + seg + " button.on"); return b ? b.dataset.v : null; }
function wireSegs() {
  const bind = (seg, fn) => $$("#" + seg + " button").forEach(b => b.onclick = () => { segSelect(seg, b.dataset.v); if (fn) fn(b.dataset.v); });
  bind("segTheme", v => applyTheme(v));         // живой предпросмотр темы
  bind("segLang", v => applyLang(v));           // живой предпросмотр языка
  bind("segEngine", v => $("#apiBox").classList.toggle("show", v === "api"));
}

/* ======== ПИН ======== */
let pin = "";
function renderDots() { $$(".dots .d").forEach((d, i) => d.classList.toggle("on", i < pin.length)); }
function pinKey(k) {
  if (k === "c") pin = ""; else if (k === "x") pin = pin.slice(0, -1); else if (pin.length < 4) pin += k;
  renderDots(); if (pin.length === 4) tryUnlock();
}
async function tryUnlock() {
  const d = await (await fetch("/api/unlock", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pin }) })).json();
  if (d.ok) { $("#lock").style.display = "none"; $("#app").classList.add("show"); init(); }
  else { $("#lockerr").textContent = t("wrong_pin"); pin = ""; renderDots(); setTimeout(() => $("#lockerr").textContent = "", 1400); }
}
$$(".pad button").forEach(b => b.onclick = () => pinKey(b.dataset.k));
document.addEventListener("keydown", e => {
  if ($("#app").classList.contains("show")) return;
  if (/^[0-9]$/.test(e.key)) pinKey(e.key); else if (e.key === "Backspace") pinKey("x");
});

/* ======== Markdown ======== */
function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
function inl(t) {
  const c = []; t = t.replace(/`([^`]+)`/g, (m, x) => { c.push(x); return `\u0001${c.length - 1}\u0001`; });
  t = esc(t).replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    .replace(/\u0001(\d+)\u0001/g, (m, i) => `<code class="inline">${esc(c[i])}</code>`);
  return t;
}
function codeBlock(lang, code) {
  return `<div class="codewrap"><div class="bar"><span>${esc(lang || "код")}</span><button class="copy" data-code="${encodeURIComponent(code)}">${t("copy")}</button></div><pre><code>${esc(code)}</code></pre></div>`;
}
function md(src) {
  const b = []; src = src.replace(/```(\w*)\n?([\s\S]*?)```/g, (m, l, c) => { b.push(codeBlock(l, c.replace(/\n$/, ""))); return `\u0000${b.length - 1}\u0000`; });
  let h = "", p = [], list = null, li = [];
  const fp = () => { if (p.length) { h += `<p>${p.map(inl).join("<br>")}</p>`; p = []; } };
  const fl = () => { if (list) { h += `<${list}>` + li.map(t => `<li>${inl(t)}</li>`).join("") + `</${list}>`; list = null; li = []; } };
  for (let line of src.split("\n")) {
    let m;
    if (m = line.match(/^\u0000(\d+)\u0000$/)) { fp(); fl(); h += b[+m[1]]; }
    else if (m = line.match(/^(#{1,3})\s+(.*)/)) { fp(); fl(); h += `<h${m[1].length}>${inl(m[2])}</h${m[1].length}>`; }
    else if (m = line.match(/^\s*[-*•]\s+(.*)/)) { fp(); if (list !== "ul") fl(); list = "ul"; li.push(m[1]); }
    else if (m = line.match(/^\s*\d+[.)]\s+(.*)/)) { fp(); if (list !== "ol") fl(); list = "ol"; li.push(m[1]); }
    else if (line.trim() === "") { fp(); fl(); }
    else { fl(); p.push(line); }
  }
  fp(); fl(); return h;
}

/* ======== Сообщения ======== */
function el(t, c, h) { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; }
function attChips(atts) {
  if (!atts || !atts.length) return "";
  return `<div class="atts">` + atts.map(a =>
    `<span class="att">${a.kind === "image" ? "🖼" : "📄"} ${esc(a.name)}</span>`).join("") + `</div>`;
}
function addUser(content, atts) {
  const m = el("div", "msg user");
  m.innerHTML = `<div>${attChips(atts)}<div class="bubble">${esc(content)}</div></div>`;
  $("#msgs").appendChild(m); scrollDown();
}
function srcBlock(sources) {
  if (!sources || !sources.length) return "";
  return `<details class="sources"><summary>🔗 Источники (${sources.length})</summary>` +
    sources.map(s => `<a href="${s.url}" target="_blank">${esc(s.title || s.url)}</a>`).join("") + "</details>";
}
function addBot(content, sources) {
  const m = el("div", "msg bot");
  const body = el("div", "body", srcBlock(sources) + (content ? md(content) : ""));
  m.appendChild(body); $("#msgs").appendChild(m); scrollDown();
  return { m, body };
}
function scrollDown() { const s = $("#scroll"); s.scrollTop = s.scrollHeight; }

/* ======== Композер: центр <-> низ ======== */
function place(empty) {
  const comp = $("#composer");
  if (empty) { $("#hero").style.display = "flex"; $("#msgs").style.display = "none"; $("#dock").style.display = "none"; $("#heroslot").appendChild(comp); }
  else { $("#hero").style.display = "none"; $("#msgs").style.display = "block"; $("#dock").style.display = "block"; $("#dockwrap").appendChild(comp); }
}

/* ======== Отправка / стрим ======== */
function setStreaming(on) {
  streaming = on;
  $("#sendArea").innerHTML = on ? '<button class="stopbtn" id="stopBtn">■ Стоп</button>' : '<button class="send" id="send">➤</button>';
  if (on) $("#stopBtn").onclick = stopGen; else $("#send").onclick = send;
}
async function stopGen() { try { await fetch("/api/stop", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: currentId }) }); } catch (e) { } }

async function streamInto(url, payload, body) {
  let full = "", raf = null, srcHtml = "";
  const paint = () => { body.innerHTML = srcHtml + md(full) + '<span class="cursor"></span>'; scrollDown(); raf = null; };
  try {
    const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const rd = r.body.getReader(), dec = new TextDecoder(); let buf = "";
    while (true) {
      const { done, value } = await rd.read(); if (done) break;
      buf += dec.decode(value, { stream: true }); let i;
      while ((i = buf.indexOf("\n\n")) >= 0) {
        const ln = buf.slice(0, i).trim(); buf = buf.slice(i + 2);
        if (!ln.startsWith("data:")) continue;
        const o = JSON.parse(ln.slice(5).trim());
        if (o.sources && o.sources.length) {
          srcHtml = srcBlock(o.sources);
          if (!raf) raf = requestAnimationFrame(paint);
        }
        if (o.delta) { full += o.delta; if (!raf) raf = requestAnimationFrame(paint); }
        if (o.done) currentId = o.id;
      }
    }
  } catch (e) { full += "\n\n⚠️ Ошибка связи: " + e; }
  body.innerHTML = srcHtml + md(full);
  return full;
}

async function runAgentTask(text) {
  if ($("#hero").style.display !== "none") place(false);
  addUser(text, []);
  $("#input").value = ""; autosize();
  setStreaming(true);
  const { body } = addBot("");
  body.innerHTML = '<span class="status">Думаю<span class="sdots"></span></span>';
  let answer = "", sources = [];
  try {
    const r = await fetch("/api/agent", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: currentId, message: text, project: activeProject ? activeProject.id : null }) });
    const rd = r.body.getReader(), dec = new TextDecoder(); let buf = "";
    while (true) {
      const { done, value } = await rd.read(); if (done) break;
      buf += dec.decode(value, { stream: true }); let i;
      while ((i = buf.indexOf("\n\n")) >= 0) {
        const ln = buf.slice(0, i).trim(); buf = buf.slice(i + 2);
        if (!ln.startsWith("data:")) continue;
        const o = JSON.parse(ln.slice(5).trim());
        if (o.status) { body.innerHTML = `<span class="status">${esc(o.status)}<span class="sdots"></span></span>`; scrollDown(); }
        if (o.answer !== undefined) { answer = o.answer; sources = o.sources || []; currentId = o.id || currentId; }
      }
    }
  } catch (e) { answer = "⚠️ Ошибка агента: " + e; }
  body.innerHTML = srcBlock(sources) + md(answer || t("done"));
  setStreaming(false); count += 2; scrollDown(); refreshConvs();
}

async function send() {
  const inp = $("#input"); const text = inp.value.trim();
  if ((!text && !pendImages.length && !pendFiles.length) || streaming) return;
  if (agentMode) { runAgentTask(text); return; }
  const first = count === 0;
  if ($("#hero").style.display !== "none") place(false);

  const atts = [...pendFiles.map(f => ({ name: f.name, kind: "file" })), ...pendImages.map(() => ({ name: t("image"), kind: "image" }))];
  addUser(text, atts);
  const payload = { id: currentId, message: text, images: pendImages.map(x => x.data), files: pendFiles.map(f => ({ name: f.name, text: f.text })), project: activeProject ? activeProject.id : null };
  inp.value = ""; autosize(); clearPend();

  setStreaming(true);
  const { body } = addBot("");
  body.innerHTML = '<span class="cursor"></span>';
  await streamInto("/api/chat", payload, body);
  lastBotBody = body; addRegen(body);
  setStreaming(false); count += 2;
  refreshConvs();
  if (first) { try { await fetch("/api/title", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: currentId }) }); refreshConvs(); } catch (e) { } }
  inp.focus();
}

function addRegen(body) {
  const row = el("div", "msgactions", `<button>${t("regen")}</button>`);
  row.querySelector("button").onclick = async () => {
    if (streaming) return; row.remove(); setStreaming(true);
    body.innerHTML = '<span class="cursor"></span>';
    await streamInto("/api/regenerate", { id: currentId }, body);
    setStreaming(false); addRegen(body);
  };
  body.parentElement.appendChild(row);
}

/* ======== Вложения ======== */
function renderPend() {
  const box = $("#pend"); box.innerHTML = "";
  pendImages.forEach((im, i) => { const c = el("div", "pend", `<img src="${im.data}"><span>картинка</span><button class="x">✕</button>`); c.querySelector(".x").onclick = () => { pendImages.splice(i, 1); renderPend(); }; box.appendChild(c); });
  pendFiles.forEach((f, i) => { const c = el("div", "pend", `📄 <span>${esc(f.name)}</span><button class="x">✕</button>`); c.querySelector(".x").onclick = () => { pendFiles.splice(i, 1); renderPend(); }; box.appendChild(c); });
}
function clearPend() { pendImages = []; pendFiles = []; renderPend(); }
function addFiles(files) {
  [...files].forEach(f => {
    if (f.type.startsWith("image/")) { const r = new FileReader(); r.onload = () => { pendImages.push({ name: f.name, data: r.result }); renderPend(); }; r.readAsDataURL(f); }
    else { const r = new FileReader(); r.onload = () => { pendFiles.push({ name: f.name, text: r.result }); renderPend(); }; r.readAsText(f); }
  });
}
/* ===== Меню «+» ===== */
let agentMode = false, allSkills = [], userName = "Вова";
let activeProject = null, allProjects = [], editingProject = null;
function togglePlus(e) {
  if (e) e.stopPropagation();
  const m = $("#plusMenu");
  if (!m.classList.contains("hidden")) { m.classList.add("hidden"); return; }
  const r = $("#attachBtn").getBoundingClientRect();
  m.style.left = r.left + "px";
  m.classList.remove("hidden");
  m.style.top = (r.top - m.offsetHeight - 8) + "px";
}
$("#attachBtn").onclick = togglePlus;
$("#fileInput").onchange = e => { addFiles(e.target.files); e.target.value = ""; };
$("#miAttach").onclick = () => { $("#plusMenu").classList.add("hidden"); $("#fileInput").click(); };
$("#miSkills").onclick = () => { $("#plusMenu").classList.add("hidden"); openSkills(); };
$("#miWeb").onclick = () => {
  $("#plusMenu").classList.add("hidden");
  setAgentMode(true);
  $("#input").value = "Найди в интернете и ответь: ";
  autosize(); $("#input").focus();
};
function setAgentMode(v, save = true) {
  agentMode = v;
  $("#agentState").textContent = v ? t("agent_on") : t("agent_off");
  $("#input").placeholder = v ? t("agent_ph") : t("composer_ph");
  if (save) fetch("/api/settings", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ agent_mode: v }) });
}
$("#miAgent").onclick = () => { setAgentMode(!agentMode); $("#plusMenu").classList.add("hidden"); };
document.addEventListener("click", e => {
  if (!e.target.closest("#plusMenu") && !e.target.closest("#attachBtn")) $("#plusMenu").classList.add("hidden");
});

/* ===== Панель навыков ===== */
async function openSkills() {
  await loadSkillsEn();
  if (!allSkills.length) {
    const d = await (await fetch("/api/skills")).json();
    allSkills = d.skills || [];
    $("#skCount").textContent = d.count || allSkills.length;
    $("#skTotal").textContent = `— ${t("sk_total")} ${allSkills.length}`;
  }
  renderSkills("");
  $("#skillsOverlay").classList.add("show");
  $("#skSearch").focus();
}
function closeSkills() { $("#skillsOverlay").classList.remove("show"); }
function renderSkills(q) {
  q = (q || "").toLowerCase();
  const box = $("#skList"); box.innerHTML = "";
  allSkills.filter(s => !q || s.name.toLowerCase().includes(q) || s.desc.toLowerCase().includes(q) || skillDesc(s).toLowerCase().includes(q) || s.category.toLowerCase().includes(q) || catName(s.category).toLowerCase().includes(q))
    .slice(0, 200).forEach(s => {
      const dsc = skillDesc(s);
      const el = el2("div", "skrow", `<div class="n">${s.name} <span>${esc(catName(s.category))}</span></div><div class="d">${esc(dsc)}</div>`);
      el.onclick = () => {
        setAgentMode(true);
        $("#input").value = dsc + " ";
        closeSkills(); autosize(); $("#input").focus();
      };
      box.appendChild(el);
    });
}
function el2(t, c, h) { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; }
$("#skSearch")?.addEventListener("input", e => renderSkills(e.target.value));

/* ===== Ручки изменения размера окна ===== */
function initResize() {
  const start = (dir) => (e) => {
    e.preventDefault();
    const sx = e.screenX, sy = e.screenY, sw = window.innerWidth, sh = window.innerHeight;
    let raf = null, tw = sw, th = sh;
    const mv = (ev) => {
      if (dir.includes("r")) tw = Math.max(600, sw + (ev.screenX - sx));
      if (dir.includes("b")) th = Math.max(400, sh + (ev.screenY - sy));
      if (!raf) raf = requestAnimationFrame(() => { try { window.pywebview.api.set_size(tw, th); } catch (e) {} raf = null; });
    };
    const up = () => { document.removeEventListener("mousemove", mv); document.removeEventListener("mouseup", up); };
    document.addEventListener("mousemove", mv); document.addEventListener("mouseup", up);
  };
  $(".r-r").addEventListener("mousedown", start("r"));
  $(".r-b").addEventListener("mousedown", start("b"));
  $(".r-br").addEventListener("mousedown", start("rb"));
}
initResize();
document.addEventListener("paste", e => {
  if (!$("#app").classList.contains("show")) return;
  const items = e.clipboardData?.items || [];
  for (const it of items) if (it.type.startsWith("image/")) { const f = it.getAsFile(); if (f) addFiles([f]); }
});
document.addEventListener("dragover", e => e.preventDefault());
document.addEventListener("drop", e => { e.preventDefault(); if (e.dataTransfer?.files?.length) addFiles(e.dataTransfer.files); });

/* ======== Диалоги ======== */
async function refreshConvs() {
  allConvs = await (await fetch("/api/conversations")).json();
  renderConvs();
}
function fmtDate(ts) {
  if (!ts) return "";
  const loc = lang === "en" ? "en" : "ru";
  const d = new Date(ts * 1000), now = new Date(), day = 86400000;
  const hm = d.toLocaleTimeString(loc, { hour: "2-digit", minute: "2-digit" });
  if (d.toDateString() === now.toDateString()) return t("today") + " " + hm;
  if (new Date(now - day).toDateString() === d.toDateString()) return t("yesterday") + " " + hm;
  return d.toLocaleDateString(loc, { day: "2-digit", month: "2-digit", year: "2-digit" }) + " · " + hm;
}
function convRow(c, snippet) {
  const d = el("div", "conv" + (c.id === currentId ? " active" : ""));
  const nm = el("div", "nm",
    `<div class="ct">${esc(c.title)}</div>` +
    (snippet ? `<div class="csnip">${esc(snippet)}</div>` : "") +
    `<div class="cdate">${fmtDate(c.updated)}</div>`);
  d.appendChild(nm);
  const del = el("button", "del", "🗑"); del.onclick = e => { e.stopPropagation(); askDel(c.id, c.title); };
  d.appendChild(del);
  d.onclick = () => openConv(c.id);
  return d;
}
function renderConvs() {
  const box = $("#convs"); box.innerHTML = "";
  let list = allConvs;
  if (activeProject) list = allConvs.filter(c => c.project === activeProject.id);
  list.forEach(c => box.appendChild(convRow(c)));
}

/* ======== Проекты ======== */
async function refreshProjects() {
  try { allProjects = await (await fetch("/api/projects")).json(); } catch (e) { allProjects = []; }
}
function projChatCount(pid) { return allConvs.filter(c => c.project === pid).length; }
async function openProjects() {
  await refreshProjects(); renderProjects();
  $("#projOverlay").classList.add("show");
}
function closeProjects() { $("#projOverlay").classList.remove("show"); }
function renderProjects() {
  const box = $("#projList"); box.innerHTML = "";
  if (!allProjects.length) { box.innerHTML = `<div class="projempty">${t("no_projects")}</div>`; return; }
  allProjects.forEach(p => {
    const card = el("div", "projcard");
    card.innerHTML = `<div class="pn">🗂 ${esc(p.name)}</div>` +
      `<div class="pmeta">${t("created")}: ${fmtDate(p.created)} · ${projChatCount(p.id)} ${t("chats_n")}</div>` +
      (p.instructions ? `<div class="pins">${esc(p.instructions)}</div>` : "") +
      `<button class="pedit" title="${t("project_edit")}">✎</button>` +
      `<button class="pdel" title="${t("delete")}">🗑</button>`;
    card.querySelector(".pedit").onclick = e => { e.stopPropagation(); openProjForm(p); };
    card.querySelector(".pdel").onclick = async e => {
      e.stopPropagation();
      if (!confirm(t("confirm_del_project"))) return;
      await fetch("/api/projects/" + p.id, { method: "DELETE" });
      await refreshProjects();
      if (activeProject && activeProject.id === p.id) exitProject();
      renderProjects(); await refreshConvs();
    };
    card.onclick = () => enterProject(p);
    box.appendChild(card);
  });
}
function openProjForm(p) {
  editingProject = p || null;
  $("#projFormTitle").textContent = p ? t("project_edit") : t("project_create");
  $("#projName").value = p ? p.name : "";
  $("#projInstr").value = p ? (p.instructions || "") : "";
  $("#projFormOverlay").classList.add("show");
  setTimeout(() => $("#projName").focus(), 50);
}
function closeProjForm() { $("#projFormOverlay").classList.remove("show"); editingProject = null; }
async function saveProjForm() {
  const name = $("#projName").value.trim(); if (!name) { $("#projName").focus(); return; }
  const instructions = $("#projInstr").value;
  if (editingProject) {
    await fetch("/api/projects/" + editingProject.id, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, instructions }) });
    if (activeProject && activeProject.id === editingProject.id) {
      activeProject.name = name; activeProject.instructions = instructions;
      $("#projBanner .pbname").textContent = "🗂 " + name;
    }
  } else {
    await fetch("/api/projects", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, instructions }) });
  }
  closeProjForm(); await refreshProjects(); renderProjects();
}
function enterProject(p) {
  activeProject = p;
  $("#projBanner .pbname").textContent = "🗂 " + p.name;
  $("#projBanner").style.display = "flex";
  closeProjects(); newChat(); renderConvs();
}
function exitProject() {
  activeProject = null;
  $("#projBanner").style.display = "none";
  newChat(); renderConvs();
}
$("#navProjects").onclick = openProjects;
$("#projNewBtn").onclick = () => openProjForm(null);
$("#projSaveBtn").onclick = saveProjForm;
$("#pbExit").onclick = exitProject;
$("#pbEdit").onclick = () => { if (activeProject) openProjForm(activeProject); };
let searchTimer = null;
async function doSearch(q) {
  if (!q.trim()) { renderConvs(); return; }
  const box = $("#convs");
  box.innerHTML = `<div style="padding:10px;color:var(--mut);font-size:12.5px">${t("searching")}</div>`;
  try {
    const d = await (await fetch("/api/search", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ q }) })).json();
    box.innerHTML = "";
    if (!d.results || !d.results.length) { box.innerHTML = `<div style="padding:10px;color:var(--mut);font-size:12.5px">${t("nothing_found")}</div>`; return; }
    d.results.forEach(c => box.appendChild(convRow(c, c.snippet)));
  } catch (e) { box.innerHTML = `<div style="padding:10px;color:var(--bad)">${t("search_err")}</div>`; }
}
async function showRecent() {
  const box = $("#convs");
  box.innerHTML = `<div class="seclabel" style="padding-top:4px">${t("recent_opened")}</div>`;
  let list = [];
  try { list = await (await fetch("/api/recent")).json(); } catch (e) {}
  if (activeProject) list = list.filter(c => c.project === activeProject.id);
  if (!list.length) { box.innerHTML += `<div style="padding:10px;color:var(--mut);font-size:12.5px">${t("no_recent")}</div>`; return; }
  list.forEach(c => {
    const row = convRow(c);
    const del = row.querySelector(".del");
    if (del) {
      del.textContent = "✕"; del.title = t("remove_recent");
      del.onclick = async e => { e.stopPropagation(); await fetch("/api/recent/" + c.id, { method: "DELETE" }); showRecent(); };
    }
    box.appendChild(row);
  });
}
async function openConv(id) {
  const c = await (await fetch("/api/conversations/" + id)).json();
  try { fetch("/api/recent", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id }) }); } catch (e) {}
  currentId = id; count = c.messages.length;
  $("#msgs").innerHTML = "";
  if (!c.messages.length) { place(true); setGreet(); }
  else {
    place(false);
    c.messages.forEach(m => { if (m.role === "user") addUser(m.content, m.attachments); else { const { body } = addBot(m.content, m.sources); lastBotBody = body; } });
    if (lastBotBody) addRegen(lastBotBody);
  }
  renderConvs();
}
async function newChat() {
  // не создаём пустой диалог на сервере — он появится после первого сообщения
  currentId = null; count = 0; $("#msgs").innerHTML = ""; place(true); setGreet(); renderConvs();
}
function askDel(id, title) { delId = id; $("#delName").textContent = `«${title}» — ${t("del_text")}`; $("#delOverlay").classList.add("show"); }
function closeDel() { $("#delOverlay").classList.remove("show"); delId = null; }
$("#delConfirm").onclick = async () => {
  if (!delId) return; await fetch("/api/conversations/" + delId, { method: "DELETE" });
  if (delId === currentId) newChat(); else refreshConvs(); closeDel();
};

/* ======== Приветствие ======== */
function setGreet() {
  const h = new Date().getHours();
  const key = h < 6 ? "greet_night" : h < 12 ? "greet_morning" : h < 18 ? "greet_day" : "greet_evening";
  $("#greetText").textContent = `${t(key)}, ${userName}`;
}

/* ======== Настройки ======== */
async function openSettings() {
  const s = await (await fetch("/api/settings")).json();
  const ms = (await (await fetch("/api/models")).json()).models || [];
  const fill = (sel, val) => { sel.innerHTML = ""; ms.forEach(m => { const o = el("option", null, m); o.value = m; if (m === val) o.selected = true; sel.appendChild(o); }); };
  fill($("#setModel"), s.model); fill($("#setVision"), s.vision_model);
  $("#setTemp").value = s.temperature; $("#tempVal").textContent = s.temperature;
  $("#setAuto").checked = !!s.auto_model;
  $("#setDanger").checked = !!s.allow_dangerous;
  $("#setTavily").value = s.tavily_key || "";
  $("#setName").value = s.user_name || "Вова";
  $("#setPersona").value = s.system_prompt || "";
  // вид / язык / движок
  segSelect("segTheme", s.theme || "system");
  segSelect("segLang", s.lang || "ru");
  $("#setReplyMatch").checked = s.reply_match !== false;
  segSelect("segEngine", s.engine || "local");
  $("#setApiBase").value = s.api_base || "";
  $("#setApiKey").value = s.api_key || "";
  $("#setApiModel").value = s.api_model || "";
  $("#apiBox").classList.toggle("show", (s.engine || "local") === "api");
  refreshStatus();
  $("#setOverlay").classList.add("show");
}
function closeSettings() {
  // откат непринятых превью темы/языка к сохранённым
  applyTheme(savedTheme); applyLang(savedLang);
  $("#setOverlay").classList.remove("show");
}
async function saveSettings() {
  const payload = {
    model: $("#setModel").value, vision_model: $("#setVision").value,
    temperature: parseFloat($("#setTemp").value), system_prompt: $("#setPersona").value,
    auto_model: $("#setAuto").checked, allow_dangerous: $("#setDanger").checked,
    tavily_key: $("#setTavily").value, user_name: $("#setName").value.trim() || "Вова",
    theme: segValue("segTheme") || "system", lang: segValue("segLang") || "ru",
    reply_match: $("#setReplyMatch").checked,
    engine: segValue("segEngine") || "local", api_base: $("#setApiBase").value.trim(),
    api_key: $("#setApiKey").value.trim(), api_model: $("#setApiModel").value.trim(),
  };
  await fetch("/api/settings", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  userName = payload.user_name; savedTheme = payload.theme; savedLang = payload.lang;
  applyTheme(savedTheme); applyLang(savedLang); setGreet();
  $("#setOverlay").classList.remove("show"); refreshStatus();
}
async function clearAllDialogs() {
  if (!confirm(t("confirm_clear"))) return;
  await fetch("/api/conversations/clear", { method: "POST" });
  currentId = null; await refreshConvs(); newChat();
  alert(t("all_cleared"));
}
function exportDialog() {
  if (!currentId) { alert(t("no_open_dialog")); return; }
  fetch("/api/conversations/" + currentId).then(r => r.json()).then(c => {
    const txt = c.messages.map(m => (m.role === "user" ? "Вы: " : "Ульвар: ") + m.content).join("\n\n");
    const blob = new Blob([txt], { type: "text/plain;charset=utf-8" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = (c.title || "диалог") + ".txt"; a.click();
  });
}
$("#setTemp").oninput = e => $("#tempVal").textContent = e.target.value;
$("#navSettings").onclick = openSettings;

/* ======== Статус ======== */
async function refreshStatus() {
  try {
    const d = await (await fetch("/api/status")).json();
    const el = $("#setStatus");
    const line = d.engine === "api" ? t("status_api") : (d.ollama ? t("status_online") : t("status_offline"));
    if (el) el.textContent =
      line +
      `\n${t("status_model")}: ${d.model || "—"}` +
      `\n${t("status_skills")}: ${allSkills.length || "…"}  ·  ${t("status_convs")}: ${allConvs.length}`;
  } catch (e) { }
}

/* ======== Ввод ======== */
function autosize() { const t = $("#input"); t.style.height = "auto"; t.style.height = Math.min(t.scrollHeight, 220) + "px"; }
$("#input").addEventListener("input", autosize);
$("#input").addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
$("#send").onclick = send;
$("#navNew").onclick = newChat;
$("#search").addEventListener("input", e => {
  clearTimeout(searchTimer);
  const q = e.target.value;
  if (!q.trim()) { showRecent(); return; }
  searchTimer = setTimeout(() => doSearch(q), 350);
});
$("#search").addEventListener("focus", () => { if (!$("#search").value.trim()) showRecent(); });
$("#search").addEventListener("blur", () => { setTimeout(() => { if (!$("#search").value.trim()) renderConvs(); }, 200); });
document.addEventListener("click", e => {
  const b = e.target.closest(".copy");
  if (b) { const code = decodeURIComponent(b.dataset.code); (navigator.clipboard?.writeText(code) || Promise.reject()).then(() => { b.textContent = t("copied"); setTimeout(() => b.textContent = t("copy"), 1200); }).catch(() => { }); }
});
$$(".overlay").forEach(o => o.addEventListener("click", e => {
  if (e.target !== o) return;
  if (o.id === "setOverlay") closeSettings(); else o.classList.remove("show");
}));

/* ======== Старт ======== */
async function init() {
  wireSegs();
  try {
    const s = await (await fetch("/api/settings")).json();
    userName = s.user_name || "Вова";
    savedTheme = s.theme || "system"; savedLang = s.lang || "ru";
    applyTheme(savedTheme); applyLang(savedLang);
    setAgentMode(!!s.agent_mode, false);
  } catch (e) {}
  setGreet();
  try { const d = await (await fetch("/api/skills")).json(); allSkills = d.skills || []; const sc = $("#skCount"); if (sc) sc.textContent = d.count || allSkills.length; } catch (e) {}
  await refreshConvs();
  await refreshProjects();
  await refreshStatus(); await newChat(); setInterval(refreshStatus, 5000);
}

/* Применяем тему и язык ещё до входа — чтобы экран ПИН был на нужном языке */
(async function preboot() {
  try {
    const s = await (await fetch("/api/settings")).json();
    savedTheme = s.theme || "system"; savedLang = s.lang || "ru";
    applyTheme(savedTheme); applyLang(savedLang);
  } catch (e) {}
})();
