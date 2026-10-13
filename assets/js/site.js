/* СК-Ремонт — анимации, меню, галерея, форма. Без библиотек. */
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

  /* мобильная панель «Позвонить / Обсудить проект»: висит внизу, прячется у самой формы */
  const mCta = d.querySelector(".m-bar"), formSec = d.getElementById("form"), heroBtn = d.querySelector(".hero-act .btn");
  const inView = (el) => { if (!el) return false; const r = el.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; };
  const onCta = () => { if (mCta) mCta.classList.toggle("off", inView(heroBtn) || inView(formSec)); };

  let ticking = false;
  const frame = () => { onReveal(); onCta(); onHeader(); onNav(); onMotion(); onSteps(); ticking = false; };
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

  /* ── заявки ───────────────────────────────────────────────────────────
     Две формы с одинаковой механикой: полная в секции «Заявка» и короткая
     в модальном окне (имя + телефон). Вместо картинки с кодом — невидимый
     одноразовый токен из token.php. После успеха форма заменяется заметным
     подтверждением, и повторная отправка блокируется на 5 минут. */
  const LEAD_KEY = "skr_lead_at", LEAD_LOCK = 5 * 60 * 1000;
  const leadSentAt = () => { try { return +localStorage.getItem(LEAD_KEY) || 0; } catch (e) { return 0; } };
  const leadLocked = () => Date.now() - leadSentAt() < LEAD_LOCK;

  const doneHTML = (text) =>
    '<div class="lead-done" role="status">' +
    '<p class="lead-done-mark" aria-hidden="true">✓</p>' +
    '<h3>Заявка принята</h3>' +
    `<p>${text}</p>` +
    '<p class="lead-done-alt">Если срочно — звоните <a href="tel:+79167314907">+7 916 731 49 07</a></p>' +
    '</div>';

  const showDone = (form, text) => {
    const done = d.createElement("div");
    done.className = "lead-wrap-done";
    done.innerHTML = doneHTML(text || "Перезвоним в течение рабочего дня.");
    form.replaceWith(done);
    return done;
  };

  /* маска телефона: +7 висит всегда, цифры раскладываются в +7 (916) 731-49-07 */
  const fmtPhone = (v) => {
    let n = v.replace(/\D/g, "");
    if (n[0] === "7") n = n.slice(1);                        // префикс +7 самого поля
    if (n.length > 10 && /^[78]/.test(n)) n = n.slice(1);    // вставили 8916… или 7916…
    n = n.slice(0, 10);
    let out = "+7 ";
    if (n.length) out += "(" + n.slice(0, 3);
    if (n.length >= 3) out += ")";
    if (n.length > 3) out += " " + n.slice(3, 6);
    if (n.length > 6) out += "-" + n.slice(6, 8);
    if (n.length > 8) out += "-" + n.slice(8, 10);
    return out;
  };

  const wireLead = (form) => {
    if (!form) return;
    const msg = form.querySelector(".form-msg");
    const phone = form.querySelector("[name=your-phone]");
    const tokenField = form.querySelector("[name=t]");

    /* код с картинки: есть только на боевой сборке, где работает PHP */
    const capImg = form.querySelector(".cap-img"), capIn = form.querySelector("[name=captcha]");
    const newCap = () => { if (capImg) { capImg.src = "captcha.php?t=" + Date.now(); capIn.value = ""; } };
    const capBtn = form.querySelector(".cap-new");
    if (capBtn) capBtn.addEventListener("click", () => { newCap(); capIn.focus(); });

    const toEnd = () => requestAnimationFrame(() => phone.setSelectionRange(phone.value.length, phone.value.length));
    phone.addEventListener("input", () => { phone.value = fmtPhone(phone.value); toEnd(); });
    phone.addEventListener("keydown", (ev) => {
      if (ev.key !== "Backspace") return;
      ev.preventDefault();                                    // стираем цифру, а не скобку или дефис
      const n = phone.value.replace(/\D/g, "").slice(1, -1);
      phone.value = fmtPhone("7" + n); toEnd();
    });
    phone.addEventListener("focus", () => { if (!phone.value.startsWith("+7")) phone.value = "+7 "; toEnd(); });

    /* токен берём при первом касании формы: к моменту отправки ему уже есть пара секунд */
    let tokenReq = null;
    const getToken = (force) => {
      if (force || !tokenReq) {
        tokenReq = fetch("token.php", { cache: "no-store" })
          .then((r) => r.json()).then((j) => { tokenField.value = j.t || ""; return j.t; })
          .catch(() => { tokenReq = null; return ""; });
      }
      return tokenReq;
    };
    ["focusin", "input"].forEach((ev) => form.addEventListener(ev, () => getToken(false), { once: true }));

    const post = async () => {
      const fd = new FormData(form);
      fd.append("page", location.href);
      fd.append("src", form.dataset.src || "");
      const r = await fetch(form.action, { method: "POST", body: fd, headers: { "X-Requested-With": "XMLHttpRequest" } });
      return r.json();
    };

    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      if (leadLocked()) {
        showDone(form, "Мы уже получили вашу заявку и скоро перезвоним.");
        return;
      }
      const name = form.querySelector("[name=your-name]");
      const digits = phone.value.replace(/\D/g, "");
      name.closest(".fld").classList.toggle("err", !name.value.trim());
      phone.closest(".fld").classList.toggle("err", digits.length < 11);
      const capBad = !!capIn && capIn.value.trim().length < 5;
      if (capIn) capIn.closest(".fld").classList.toggle("err", capBad);
      if (!name.value.trim() || digits.length < 11) {
        msg.className = "form-msg bad"; msg.textContent = "Укажите имя и телефон — перезвоним.";
        return;
      }
      if (capBad) { msg.className = "form-msg bad"; msg.textContent = "Введите код с картинки."; return; }

      form.classList.add("sending");
      msg.className = "form-msg"; msg.textContent = "Отправляем…";
      try {
        await getToken(!tokenField.value);
        let j = await post();
        if (j && j.captcha) {
          newCap();
          capIn.closest(".fld").classList.add("err");
          form.classList.remove("sending");
          msg.className = "form-msg bad"; msg.textContent = j.error;
          capIn.focus();
          return;
        }
        if (j && j.token) {
          // токен протух: берём новый и ждём, иначе сервер сочтёт мгновенную отправку ботом
          await getToken(true);
          await new Promise((r) => setTimeout(r, 2600));
          j = await post();
          if (j && j.captcha) {
            newCap();
            capIn.closest(".fld").classList.add("err");
            form.classList.remove("sending");
            msg.className = "form-msg bad"; msg.textContent = j.error;
            return;
          }
        }
        if (!j || !j.ok) throw new Error((j && j.error) || "fail");

        try { localStorage.setItem(LEAD_KEY, String(Date.now())); } catch (e) { /* приватный режим */ }
        if (!j.duplicate) {
          if (window.ym) ym(112782417, "reachGoal", "landing_form");
          d.dispatchEvent(new Event("lead:ok"));
        }
        const done = showDone(form, j.message);
        done.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" });
      } catch (err) {
        form.classList.remove("sending");
        newCap();
        msg.className = "form-msg bad";
        msg.innerHTML = 'Не получилось отправить. Позвоните <a href="tel:+79167314907">+7 916 731 49 07</a>.';
      }
    });

    /* заявку уже отправляли пять минут назад — форму не показываем */
    if (leadLocked()) showDone(form, "Мы уже получили вашу заявку и скоро перезвоним.");
  };

  wireLead(d.querySelector(".form-sec .lead"));

  /* модальное окно с короткой формой: открывается всеми кнопками «Обсудить проект» */
  const lm = d.getElementById("lead-modal");
  if (lm && typeof lm.showModal === "function") {
    const lmForm = lm.querySelector(".lead");
    wireLead(lmForm);
    const typeField = lm.querySelector("[name=interest]");
    let lastOpener = null;

    const openLead = (opener, type) => {
      lastOpener = opener || null;
      if (typeField) typeField.value = type || "";
      const view = d.querySelector(".pv:not([hidden])");
      if (view) { view.hidden = true; openView = null; }      // ушли со страницы объекта
      lm.showModal();
      d.body.style.overflow = "hidden";
      const first = lm.querySelector("input:not([type=hidden]):not([tabindex])");
      if (first) first.focus({ preventScroll: true });
    };
    const closeLead = () => lm.close();

    lm.addEventListener("close", () => {
      d.body.style.overflow = "";
      if (lastOpener && d.contains(lastOpener)) lastOpener.focus();
    });
    lm.querySelector(".lm-x").addEventListener("click", closeLead);
    lm.addEventListener("click", (ev) => { if (ev.target === lm) closeLead(); });

    d.addEventListener("click", (ev) => {
      const t = ev.target.closest('a[href="#form"], [data-lead]');
      if (!t || lm.open) return;
      ev.preventDefault();
      openLead(t, t.dataset.type || "");
    });
  }

  root.classList.remove("no-js");
})();
