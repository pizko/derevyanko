/* Качественные цели Метрики для Директа (18.09.2026).
   Цель уходит только от живого, вовлечённого посетителя — боты и скликивание её не зажигают.
   Живой: нет признаков автоматизации + есть «человеческий» ввод (кривая траектория мыши,
   касания экрана, увеличение пальцами, клавиатура). Вовлечённый: активное время, глубина
   прокрутки, открытые объекты. Сигналы визита пишутся в параметры визита (q) — по ним
   в Метрике потом подбираем пороги под реальных заявителей. */
(() => {
  const C = 112782417;
  const T = { liveSec: 20, liveScroll: 35, deepSec: 60, deepScroll: 75, deepProjects: 2, leadSec: 20, callSec: 20, turns: 8, touches: 3, keys: 3 };
  const now = () => performance.now();
  const ua = navigator.userAgent || "";
  const bot = !!navigator.webdriver || /HeadlessChrome|PhantomJS|Lighthouse|bot|crawl|spider|slurp/i.test(ua)
    || !navigator.languages || navigator.languages.length === 0 || !screen.width || !screen.height;

  const s = { active: 0, lastInput: 0, lastTick: now(), moves: 0, turns: 0, dx: 0, dy: 0, touch: 0, keys: 0, zoom: false, scroll: 0, projects: new Set(), sent: {} };
  const input = () => { s.lastInput = now(); };

  // мышь: считаем смены направления — у скриптов траектория прямая или её нет вовсе
  addEventListener("mousemove", (e) => {
    const dx = Math.sign(e.movementX || 0), dy = Math.sign(e.movementY || 0);
    if ((dx && s.dx && dx !== s.dx) || (dy && s.dy && dy !== s.dy)) s.turns++;
    if (dx) s.dx = dx; if (dy) s.dy = dy;
    s.moves++; input();
  }, { passive: true });
  addEventListener("touchstart", () => { s.touch++; input(); }, { passive: true });
  addEventListener("touchmove", input, { passive: true });
  addEventListener("keydown", () => { s.keys++; input(); });
  addEventListener("wheel", input, { passive: true });
  if (window.visualViewport) visualViewport.addEventListener("resize", () => { if (visualViewport.scale > 1.05) { s.zoom = true; input(); } });
  addEventListener("scroll", () => {
    const h = document.documentElement.scrollHeight - innerHeight;
    if (h > 0) s.scroll = Math.max(s.scroll, Math.round(100 * scrollY / h));
  }, { passive: true });
  addEventListener("hashchange", () => { const id = location.hash.slice(1); if (id.startsWith("obekt-")) s.projects.add(id); });

  const human = () => !bot && (s.turns >= T.turns || s.touch >= T.touches || s.zoom || s.keys >= T.keys);
  const goal = (id) => {
    if (s.sent[id] || !window.ym) return;
    s.sent[id] = 1;
    ym(C, "reachGoal", id);
  };
  const snapshot = () => ({ sec: Math.round(s.active / 1000), scroll: s.scroll, turns: s.turns, touch: s.touch, zoom: s.zoom ? 1 : 0, keys: s.keys, projects: s.projects.size, human: human() ? 1 : 0, bot: bot ? 1 : 0 });

  // активное время: вкладка видна и был ввод за последние 20 секунд
  setInterval(() => {
    const t = now();
    if (!document.hidden && t - s.lastInput < 20000) s.active += t - s.lastTick;
    s.lastTick = t;
    const sec = s.active / 1000;
    if (human() && sec >= T.liveSec && s.scroll >= T.liveScroll) goal("q_live");
    if (s.sent.q_live && (s.projects.size >= T.deepProjects || (sec >= T.deepSec && s.scroll >= T.deepScroll))) goal("q_deep");
  }, 2000);

  // звонок с сайта — только от живого посетителя, побывшего на странице
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="tel:"]');
    if (a && human() && s.active / 1000 >= T.callSec) goal("q_call");
  });
  // заявка — site.js шлёт событие после успешной отправки
  document.addEventListener("lead:ok", () => {
    if (human() && s.active / 1000 >= T.leadSec) goal("q_lead");
  });

  // сигналы визита — для настройки порогов по реальным заявкам
  const flush = () => { if (window.ym) ym(C, "params", { q: snapshot() }); };
  addEventListener("pagehide", flush);
  document.addEventListener("visibilitychange", () => { if (document.hidden) flush(); });
})();
