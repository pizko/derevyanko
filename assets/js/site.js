/* СК Деревянко — анимации, меню, галерея, форма. Без библиотек. */
(() => {
  const d = document, root = d.documentElement;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* появление: строки заголовков, блоки, фото через маску.
     Проверяем в обработчике прокрутки, а не IntersectionObserver: так надёжнее при быстрой прокрутке и якорях. */
  let pending = [...d.querySelectorAll(".rv, .giant, .hero-h, .mask")];
  if (reduce) { pending.forEach((t) => t.classList.add("in")); pending = []; }
  const onReveal = () => {
    if (!pending.length) return;
    const line = innerHeight * 0.94;
    pending = pending.filter((t) => {
      const r = t.getBoundingClientRect();
      if (r.top < line && r.bottom > -innerHeight) { t.classList.add("in"); return false; }
      if (r.bottom <= -innerHeight) { t.classList.add("in"); return false; }  // проскочили якорем — показываем сразу
      return true;
    });
  };

  /* шапка: фон после первого экрана, прячется при прокрутке вниз */
  const hdr = d.getElementById("hdr");
  let lastY = scrollY;
  const onHeader = () => {
    const y = scrollY;
    hdr.classList.toggle("solid", y > 40);
    hdr.classList.toggle("hide", y > 600 && y > lastY && !d.body.classList.contains("menu-open"));
    lastY = y;
  };

  /* активный пункт меню */
  const links = [...d.querySelectorAll(".nav a")];
  const secs = links.map((a) => d.querySelector(a.getAttribute("href")));
  const onNav = () => {
    const mid = innerHeight * 0.4;
    let cur = -1;
    secs.forEach((s, i) => { if (s && s.getBoundingClientRect().top < mid) cur = i; });
    links.forEach((a, i) => a.classList.toggle("act", i === cur));
  };

  /* параллакс и дрейф больших строк */
  const par = [...d.querySelectorAll("[data-speed]")];
  const drift = [...d.querySelectorAll("[data-drift]")];
  const onMotion = () => {
    if (reduce) return;
    const vh = innerHeight;
    par.forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      const k = parseFloat(el.dataset.speed) * (innerWidth < 600 ? 0.5 : 1);
      el.style.transform = `translate3d(0, ${((r.top + r.height / 2 - vh / 2) * -k).toFixed(1)}px, 0)`;
    });
    drift.forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const p = (r.top + r.height / 2 - vh / 2) / vh;
      el.style.transform = `translate3d(${(p * 60 * el.dataset.drift).toFixed(1)}px, 0, 0)`;
    });
  };

  /* процесс: номер текущего этапа краснеет */
  const steps = [...d.querySelectorAll(".step")];
  const onSteps = () => {
    const line = innerHeight * 0.55;
    let cur = -1;
    steps.forEach((s, i) => { if (s.getBoundingClientRect().top < line) cur = i; });
    steps.forEach((s, i) => s.classList.toggle("act", i === cur));
  };

  let ticking = false;
  const frame = () => { onReveal(); onHeader(); onNav(); onMotion(); onSteps(); ticking = false; };
  addEventListener("scroll", () => { onReveal(); if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true });
  addEventListener("resize", frame);
  frame();

  /* мобильное меню */
  const burger = d.querySelector(".burger"), menu = d.getElementById("menu");
  const setMenu = (open) => {
    burger.setAttribute("aria-expanded", open);
    menu.hidden = !open;
    d.body.classList.toggle("menu-open", open);
    if (open) hdr.classList.remove("hide");
    d.body.style.overflow = open ? "hidden" : "";
  };
  burger.addEventListener("click", () => setMenu(menu.hidden));
  menu.addEventListener("click", (ev) => { if (ev.target.closest("a")) setMenu(false); });
  addEventListener("keydown", (ev) => { if (ev.key === "Escape" && !menu.hidden) setMenu(false); });

  /* счётчики */
  d.querySelectorAll("[data-count]").forEach((el) => {
    const m = el.textContent.match(/^(\d+)(.*)$/);
    if (!m || reduce || !("IntersectionObserver" in window)) return;
    const to = +m[1], tail = m[2];
    const io = new IntersectionObserver(([x]) => {
      if (!x.isIntersecting) return;
      io.disconnect();
      const t0 = performance.now();
      const step = (t) => {
        const k = Math.min(1, (t - t0) / 1400);
        el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))) + tail;
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, { threshold: 0.3 });
    io.observe(el);
  });

  /* магнитные кнопки и курсор VIEW — только мышь */
  if (fine && !reduce) {
    d.querySelectorAll(".mag").forEach((b) => {
      b.addEventListener("pointermove", (ev) => {
        const r = b.getBoundingClientRect();
        b.style.transform = `translate(${(ev.clientX - r.left - r.width / 2) * 0.12}px, ${(ev.clientY - r.top - r.height / 2) * 0.2}px)`;
      });
      b.addEventListener("pointerleave", () => { b.style.transform = ""; });
    });
    const cur = d.querySelector(".cursor");
    addEventListener("pointermove", (ev) => {
      cur.style.left = ev.clientX + "px"; cur.style.top = ev.clientY + "px";
      cur.classList.toggle("on", !!ev.target.closest("[data-view]"));
    }, { passive: true });
  }

  /* страницы объектов: #obekt-… открывает полноэкранный объект, назад — кнопкой браузера или «Все проекты» */
  const views = [...d.querySelectorAll(".pv")];
  let openView = null;
  const route = () => {
    const id = location.hash.slice(1);
    const v = id.startsWith("obekt-") ? d.getElementById(id) : null;
    views.forEach((x) => { if (x !== v) x.hidden = true; });
    if (v) {
      v.hidden = false; v.scrollTop = 0; openView = v;
      d.body.style.overflow = "hidden"; hdr.classList.add("hide");
      v.querySelector(".pv-back").focus({ preventScroll: true });
      if (window.ym) ym(112782417, "hit", location.href);
    } else if (openView) {
      openView = null; d.body.style.overflow = ""; hdr.classList.remove("hide");
      const t = d.getElementById(id) || d.getElementById("projects");
      requestAnimationFrame(() => t.scrollIntoView({ behavior: "instant" }));
    }
  };
  addEventListener("hashchange", route);
  route();

  /* просмотр фото на весь экран */
  const lb = d.querySelector(".lb"), lbImg = lb.querySelector("img"), lbCap = lb.querySelector("figcaption");
  let list = [], idx = 0, opener = null;
  const show = (i) => {
    idx = (i + list.length) % list.length;
    lbImg.src = list[idx].s; lbImg.alt = list[idx].a;
    lbCap.textContent = `${String(idx + 1).padStart(2, "0")} / ${String(list.length).padStart(2, "0")} — ${list[idx].a}`;
  };
  const close = () => { lb.hidden = true; if (!openView) d.body.style.overflow = ""; opener && opener.focus(); };
  views.forEach((v) => {
    const btns = [...v.querySelectorAll(".pv-ph")];
    btns.forEach((b, i) => b.addEventListener("click", () => {
      list = btns.map((x) => ({ s: x.dataset.full, a: x.dataset.alt })); opener = b;
      show(i); lb.hidden = false; d.body.style.overflow = "hidden"; lb.querySelector(".lb-x").focus();
    }));
  });
  lb.querySelector(".lb-x").addEventListener("click", close);
  lb.querySelector(".lb-p").addEventListener("click", () => show(idx - 1));
  lb.querySelector(".lb-n").addEventListener("click", () => show(idx + 1));
  lb.addEventListener("click", (ev) => { if (ev.target === lb) close(); });
  addEventListener("keydown", (ev) => {
    if (!lb.hidden) {
      if (ev.key === "Escape") close();
      if (ev.key === "ArrowLeft") show(idx - 1);
      if (ev.key === "ArrowRight") show(idx + 1);
    } else if (openView && ev.key === "Escape") location.hash = "projects";
  });
  let tx = null;
  lb.addEventListener("touchstart", (ev) => { tx = ev.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", (ev) => {
    if (tx === null) return;
    const dx = ev.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
    tx = null;
  });
  /* «Обсудить проект» со страницы объекта — закрываем объект и едем к форме */
  views.forEach((v) => v.querySelectorAll('a[href="#form"]').forEach((a) => a.addEventListener("click", () => { v.hidden = true; openView = null; d.body.style.overflow = ""; })));

  /* форма: телефон — только допустимые символы, отправка в Contact Form 7 */
  const form = d.querySelector(".lead"), msg = form.querySelector(".form-msg");
  const phone = form.querySelector("[name=your-phone]");
  phone.addEventListener("input", () => { phone.value = phone.value.replace(/[^\d+()\-\s]/g, ""); });

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const name = form.querySelector("[name=your-name]");
    const digits = phone.value.replace(/\D/g, "");
    name.closest(".fld").classList.toggle("err", !name.value.trim());
    phone.closest(".fld").classList.toggle("err", digits.length < 10);
    if (!name.value.trim() || digits.length < 10) {
      msg.className = "form-msg bad"; msg.textContent = "Укажите имя и телефон — перезвоним.";
      return;
    }
    const fd = new FormData(form);
    fd.append("page", location.href);
    form.classList.add("sending"); msg.className = "form-msg"; msg.textContent = "Отправляем…";
    try {
      const r = await fetch(form.action, { method: "POST", body: fd, headers: { "X-Requested-With": "XMLHttpRequest" } });
      const j = await r.json();
      if (j.ok) {
        form.reset(); msg.className = "form-msg ok"; msg.textContent = j.message || "Спасибо! Перезвоним в течение рабочего дня.";
        if (window.ym) ym(112782417, "reachGoal", "landing_form");
      } else throw new Error(j.error || "fail");
    } catch (err) {
      msg.className = "form-msg bad";
      msg.innerHTML = 'Не получилось отправить. Позвоните <a href="tel:+79265886968">+7 926 588 69 68</a> или напишите на <a href="mailto:info@sk-derevyanko.ru">info@sk-derevyanko.ru</a>.';
    } finally { form.classList.remove("sending"); }
  });

  root.classList.remove("no-js");
})();
