#!/usr/bin/env python3
"""Лендинг СК Деревянко (одна страница) → index.html в корне репозитория.

Все факты — с sk-derevyanko.ru: тарифы, FAQ, этапы, контакты, объекты портфолио.
Площади, сроки и годы по объектам на сайте не указаны — поэтому их здесь нет.

  python3 src/media.py          # фото (один раз)
  python3 src/build.py          # staging для GitHub Pages: без Метрики
  python3 src/build.py --prod   # для beget (папка sk-remont): Метрика + заявки через send.php

Сайт ведётся только под Директ — закрыт от индексации в обоих режимах (meta, robots.txt, X-Robots-Tag).
"""
import hashlib, html, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROD = "--prod" in sys.argv
META = json.loads((ROOT / "assets/img/meta.json").read_text())
VER = hashlib.md5((ROOT / "assets/css/site.css").read_bytes() + (ROOT / "assets/js/site.js").read_bytes() + (ROOT / "assets/js/goals.js").read_bytes()).hexdigest()[:8]
e = html.escape

SITE = "https://sk-derevyanko.ru/"
PHONE, TEL = "+7 926 588 69 68", "tel:+79265886968"
PHONE2, TEL2 = "+7 926 588 69 62", "tel:+79265886962"
EMAIL = "info@sk-derevyanko.ru"
ADDRESS = "Москва, Партийный переулок, 1, корп. 58, стр. 3"
YMAPS = "https://yandex.ru/maps/org/derevyanko/121687699078/"
SOCIAL = [("Дзен", "https://dzen.ru/id/66869490deb14e765dcd9429"), ("Яндекс Карты", YMAPS)]
PF = json.loads((ROOT / "assets/img/pf.json").read_text())
FORM_URL = "send.php"   # PHP на beget → Telegram-бот заявок (конфиг вне webroot: ~/sk-remont/lead_config.php)
METRIKA = 112782417  # счётчик лендинга sk-remont (18.09.2026); 104567459 — старый сайт sk-derevyanko.ru


def pic(name, alt, sizes="100vw", cls="", eager=False):
    m = META[name]
    ws = [640, 1280] if m["w"] > 640 else [480]
    if name == "osnovatel":
        ws = [480]
    srcset = lambda ext: ", ".join(f"assets/img/{name}-{w}.{ext} {min(w, m['w'])}w" for w in ws)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture class="{cls}"><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img src="assets/img/{name}-{ws[-1]}.webp" width="{m["w"]}" height="{m["h"]}" alt="{e(alt)}" {load}></picture>')


# ── объекты ─────────────────────────────────────────────────────────────────
PROJECTS = [
    {"id": "prime-park", "name": "ЖК Прайм парк", "lat": "PRIME PARK", "type": "Квартира", "cover": "prime-vannaya",
     "photos": [("prime-vannaya", "ванная"), ("prime-spalnya", "спальня"), ("prime-zerkalo", "мастер-ванная"),
                ("prime-dush", "душевая"), ("prime-shkaf", "встроенный шкаф с подсветкой")]},
    {"id": "sky-house", "name": "ЖК Скай Хаус", "lat": "SKY HOUSE", "type": "Квартира", "cover": "sky-gostinaya",
     "photos": [("sky-gostinaya", "гостиная"), ("sky-kuhnya", "кухня-столовая"), ("sky-sanuzel", "санузел"),
                ("sky-kollektor", "коллекторный шкаф")]},
    {"id": "eniteo", "name": "ЖК Энитео", "lat": "ENITEO", "type": "Квартира", "cover": "eni-vannaya",
     "photos": [("eni-vannaya", "ванная"), ("eni-koridor", "коридор"), ("eni-komnata", "комната"), ("eni-pol", "укладка пола")]},
    {"id": "shelepiha", "name": "Шелепиха", "lat": "SHELEPIKHA", "type": "Квартира", "cover": "shel-stolovaya",
     "photos": [("shel-gostinaya", "гостиная-кухня"), ("shel-stolovaya", "столовая"), ("shel-koridor", "коридор"),
                ("shel-spalnya", "спальня"), ("shel-spalnya-2", "спальня")]},
    {"id": "ochakovskaya", "name": "Большая Очаковская 2", "lat": "OCHAKOVSKAYA", "type": "Квартира", "cover": "ochak-tv",
     "photos": [("ochak-tv", "гостиная"), ("ochak-stolovaya", "столовая")]},
    {"id": "detsky-centr", "name": "Детский центр", "lat": "KIDS CENTER", "type": "Коммерческое помещение", "cover": "detsky-karta",
     "photos": [("detsky-karta", "игровой зал"), ("detsky-holl", "холл")]},
    {"id": "novokuznetskaya", "name": "Новокузнецкая", "lat": "NOVOKUZNETSKAYA", "type": "Квартира", "cover": "novok-komnata",
     "photos": [("novok-komnata", "комната"), ("novok-vannaya", "ванная")]},
]

DESIGN = [
    ("01", "Технический дизайн-проект", 1000,
     "Комплект рабочих чертежей с учётом ваших пожеланий и технической реализации: по нему бригада делает ремонт без импровизаций.",
     "plan"),
    ("02", "Полный дизайн-проект с 3D-визуализацией", 3000,
     "Технические чертежи и 3D-модели пространства. Вы видите готовый интерьер ещё до начала работ.",
     "axo"),
]
TARIFFS = [
    ("03", "Стандарт", 35000, [
        ("Полы", "стяжка, ламинат, кварцвинил, МДФ-плинтус"),
        ("Стены", "перегородки, штукатурка, шпаклёвка, обои или обои под покраску"),
        ("Санузел", "плитка размером до 60×60 см"),
        ("Инженерия", "электрика, сантехника, водопровод, канализация"),
        ("Потолки", "натяжные стандартные")]),
    ("04", "Дизайнерский", 45000, [
        ("Полы", "стяжка, инженерная доска, микро- или дюрополимерный плинтус"),
        ("Стены", "перегородки, штукатурка, шпаклёвка под покраску, покраска"),
        ("Санузел", "плитка размером до 60×120 см"),
        ("Инженерия", "улучшенный монтаж электрики, сантехники, водопровода и канализации"),
        ("Потолки", "ГКЛ, натяжные с теневым профилем, парящие")]),
    ("05", "Индивидуальный", 60000, [
        ("Полы", "стяжка, инженерная доска или паркет ёлочкой, теневой плинтус"),
        ("Стены", "шпаклёвка под лампу, безвоздушная покраска, молдинги и стеновые панели"),
        ("Санузел", "плитка нестандартного размера"),
        ("Инженерия", "улучшенный монтаж всех систем, умный дом"),
        ("Потолки", "ГКЛ и натяжные, многоуровневые, парящие, лепнина")]),
]

STEPS = [
    ("Знакомство", "Оставляете заявку — перезваниваем, обсуждаем задачу и договариваемся о встрече."),
    ("Замер и смета", "Бесплатно выезжаем на объект и готовим расчёт за 3 рабочих дня. Погрешность сметы — 5–10%."),
    ("Договор", "Фиксируем состав работ, сроки, стоимость и этапы оплаты."),
    ("Проект", "Работаем по вашему дизайн-проекту или разрабатываем новый."),
    ("Материалы", "Подбираем и закупаем всё необходимое у проверенных поставщиков — или вы закупаете сами."),
    ("Ремонт", "Выполняем работы по плану. Каждую неделю — фото- и видеоотчёт с объекта."),
    ("Сдача", "Принимаем объект вместе, устраняем замечания и передаём готовое пространство."),
]

FAQ = [
    ("Сколько стоит ремонт?", "Стоимость ремонта под ключ зависит от сложности проекта и рассчитывается индивидуально. "
     "Минимальная стоимость — от 35 000 ₽ за квадратный метр по тарифу «Стандарт»."),
    ("Какие сроки ремонта?", "Сроки зависят от сложности работ и площади. Обычно — от двух месяцев до полугода. "
     "Точный срок фиксируется в договоре после замера."),
    ("Как происходит оплата?", "Оплата делится на этапы, каждый зафиксирован в договоре. Перед очередным этапом вносится "
     "предоплата — так вы прозрачно контролируете весь процесс."),
    ("Как выполняется закупка материалов?", "Можно закупать самостоятельно или доверить закупку нам. Мы работаем с проверенными "
     "поставщиками, наценка прозрачна и согласуется заранее. Перед покупкой вы утверждаете счёт, доставки фиксируются фотоотчётом."),
    ("Можно посмотреть другие объекты?", "Да. Позвоните — договоримся о встрече на одном из текущих объектов и покажем, как мы работаем."),
    ("Как проверить порядочность строителей?", "Мы работаем открыто: еженедельные отчёты, фото и видео с объекта. "
     "Готовы к любым проверкам, включая технадзор."),
    ("Что, если я в другом городе?", "Есть опыт работы с удалёнными клиентами: постоянная связь, фото и видео — вы всегда в курсе событий."),
    ("Есть ли гарантия?", "Да, 3 года с момента сдачи объекта. Если в этот период возникнут дефекты, бесплатно их устраним. "
     "Гарантийные обязательства прописаны в договоре."),
]

SVG = {
    "plan": '<svg viewBox="0 0 160 120" aria-hidden="true"><path d="M8 8h144v104H8z"/><path d="M8 58h56v54M64 8v34M64 58h40M104 8v74h48M104 96v16M22 58v-8M120 82h-16"/><path d="M64 42a16 16 0 0 1 16 16" class="t"/><path d="M104 82a14 14 0 0 0 14 14" class="t"/><circle cx="34" cy="30" r="2"/></svg>',
    "axo": '<svg viewBox="0 0 160 120" aria-hidden="true"><path d="M80 10l62 34v48l-62 26-62-26V44z"/><path d="M80 10v60l62 22M80 70L18 92M18 44l62 26 62-26" class="t"/><path d="M48 60v26M112 60v26" class="t"/></svg>',
}

H = []
w = H.append


def label(t):
    return f'<p class="lbl"><i></i>{t}</p>'


def rub(n):
    return f"{n:,}".replace(",", " ")


# ── head ────────────────────────────────────────────────────────────────────
TITLE = "Ремонт квартир и помещений под ключ в Москве — СК Деревянко"
DESC = ("Ремонт квартир, домов и коммерческих помещений под ключ в Москве: дизайн-проект, инженерия, отделка и контроль. "
        "От 35 000 ₽/м², смета с погрешностью 5–10%, гарантия 3 года.")

org = {
    "@type": ["HomeAndConstructionBusiness", "GeneralContractor"], "@id": SITE + "#org",
    "name": "СК Деревянко", "url": SITE, "image": SITE + "wp-content/uploads/2025/09/photo_2025-09-03_14-50-56.jpg",
    "telephone": ["+79265886968", "+79265886962"], "email": EMAIL, "priceRange": "от 35 000 ₽/м²",
    "address": {"@type": "PostalAddress", "streetAddress": "Партийный переулок, 1, корп. 58, стр. 3",
                "addressLocality": "Москва", "postalCode": "115093", "addressCountry": "RU"},
    "areaServed": {"@type": "City", "name": "Москва"},
    "founder": {"@type": "Person", "name": "Сергей Деревянко", "jobTitle": "Основатель"},
    "sameAs": [SOCIAL[0][1], YMAPS],
    "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Услуги и цены", "itemListElement": [
        *[{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t},
           "priceSpecification": {"@type": "UnitPriceSpecification", "price": p, "priceCurrency": "RUB",
                                  "unitCode": "MTK", "unitText": "м²", "minPrice": p}} for _, t, p, _, _ in DESIGN],
        *[{"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"Ремонт квартиры под ключ — тариф «{t}»"},
           "priceSpecification": {"@type": "UnitPriceSpecification", "price": p, "priceCurrency": "RUB",
                                  "unitCode": "MTK", "unitText": "м²", "minPrice": p}} for _, t, p, _ in TARIFFS]]},
}
graph = [
    org,
    {"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": "СК Деревянко", "inLanguage": "ru", "publisher": {"@id": SITE + "#org"}},
    {"@type": "WebPage", "@id": SITE + "#page", "url": SITE, "name": TITLE, "description": DESC, "isPartOf": {"@id": SITE + "#site"},
     "about": {"@id": SITE + "#org"}, "inLanguage": "ru"},
    {"@type": "FAQPage", "@id": SITE + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    {"@type": "ItemList", "@id": SITE + "#projects", "name": "Наши проекты", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {"@type": "CreativeWork", "name": f"Ремонт: {p['name']}",
                                                         "genre": p["type"], "locationCreated": "Москва"}}
        for i, p in enumerate(PROJECTS)]},
]

w('<!doctype html><html lang="ru" class="no-js"><head><meta charset="utf-8">')
w('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
w(f"<title>{e(TITLE)}</title><meta name=\"description\" content=\"{e(DESC)}\">")
w('<meta name="robots" content="noindex, nofollow"><meta name="yandex" content="noindex, nofollow"><meta name="theme-color" content="#08090A">')
w(f'<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="СК Деревянко">'
  f'<meta property="og:title" content="{e(TITLE)}"><meta property="og:description" content="{e(DESC)}">'
  f'<meta property="og:image" content="assets/img/og.jpg"><meta name="twitter:card" content="summary_large_image">')
w('<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">')
w('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
w('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alumni+Sans:wght@500;600;700;800&family=Manrope:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')
w('<link rel="preload" as="image" type="image/avif" imagesrcset="assets/img/prime-spalnya-640.avif 640w, assets/img/prime-spalnya-1280.avif 1280w" imagesizes="(max-width: 760px) 100vw, 55vw">')
w(f'<link rel="stylesheet" href="assets/css/site.css?v={VER}">')
w(f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>')
if PROD:
    w(f'<script type="text/javascript">(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();'
      f'for(var j=0;j<document.scripts.length;j++){{if(document.scripts[j].src===r){{return;}}}}'
      f'k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})'
      f'(window,document,"script","https://mc.yandex.ru/metrika/tag.js?id={METRIKA}","ym");'
      f'ym({METRIKA},"init",{{ssr:true,webvisor:true,clickmap:true,ecommerce:"dataLayer",referrer:document.referrer,url:location.href,accurateTrackBounce:true,trackLinks:true}});</script>'
      f'<noscript><div><img src="https://mc.yandex.ru/watch/{METRIKA}" style="position:absolute;left:-9999px" alt=""></div></noscript>')
w('</head><body>')
w('<a class="skip" href="#main">Перейти к содержимому</a>')

# ── header ──────────────────────────────────────────────────────────────────
NAV = [("projects", "Проекты"), ("services", "Услуги"), ("about", "О компании"), ("process", "Процесс"), ("contacts", "Контакты")]
w('<header class="hdr" id="hdr"><div class="hdr-in">')
w('<a class="logo" href="#top" aria-label="СК Деревянко — наверх"><i></i><b>СК Деревянко</b></a>')
w('<nav class="nav" aria-label="Разделы">' + "".join(f'<a href="#{a}">{t}</a>' for a, t in NAV) + '</nav>')
w(f'<a class="hdr-tel" href="{TEL}">{PHONE}</a>')
w('<a class="btn btn-s mag" href="#form">Обсудить проект <span>→</span></a>')
w('<button class="burger" type="button" aria-label="Меню" aria-expanded="false" aria-controls="menu"><i></i><i></i></button>')
w('</div></header>')
w('<div class="menu" id="menu" hidden><nav>' + "".join(f'<a href="#{a}"><em>0{i+1}</em>{t}</a>' for i, (a, t) in enumerate(NAV)) +
  f'</nav><div class="menu-foot"><a href="{TEL}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>')

w('<main id="main">')

# ── hero ────────────────────────────────────────────────────────────────────
w('<section class="hero" id="top">')
w('<div class="hero-img" data-speed="0.12">' + pic("prime-spalnya", "Спальня в ЖК Прайм парк после ремонта СК Деревянко", "(max-width: 760px) 100vw, 55vw", "mask", True) +
  '<p class="cap"><span>PROJECT / 001</span><span>ЖК ПРАЙМ ПАРК</span><span>RESIDENTIAL</span></p></div>')
w('<div class="hero-top"><p class="lbl"><i></i>СК Деревянко — renovation studio</p><p class="coord">55.7558° N<br>37.6173° E<br>MOSCOW / 2026</p></div>')
w('<h1 class="hero-h"><span class="big"><span class="ln"><span>Ремонт</span></span><span class="ln"><span>интерьеров</span></span></span>'
  '<span class="sub">квартир и помещений под ключ в Москве</span></h1>')
w('<div class="hero-foot">')
w('<p class="hero-txt">Квартиры, дома и коммерческие пространства. Проектируем и реализуем под ключ — от чертежа до полностью готового интерьера.</p>')
w('<p class="gift"><i></i>Технический дизайн-проект — в подарок</p>')
w('<div class="hero-act"><a class="btn mag" href="#form">Обсудить проект <span>→</span></a><a class="lnk" href="#projects">Смотреть работы <span>↓</span></a></div>')
w('</div><div class="scroll-line" aria-hidden="true"><i></i></div></section>')

# ── statement ───────────────────────────────────────────────────────────────
w('<section class="stmt" aria-labelledby="stmt-h">')
for n, (img, t, cls) in enumerate([("sky-kollektor", "Инженерия", "s1"), ("eni-pol", "Полы", "s2"),
                                   ("prime-shkaf", "Отделка", "s3"), ("shel-spalnya-2", "Интерьер", "s4")]):
    w(f'<figure class="stmt-pic {cls}" data-speed="{[0.18, -0.1, 0.24, -0.16][n]}">' + pic(img, f"Этап ремонта: {t.lower()}", "20vw", "mask") +
      f'<figcaption>0{n+1} / {t}</figcaption></figure>')
w('<h2 class="giant" id="stmt-h"><span class="ln" data-drift="-1"><span>От бетона</span></span><span class="ln ind" data-drift="1"><span>до готового</span></span>'
  '<span class="ln" data-drift="-1"><span>интерьера</span></span></h2>')
w('<p class="stmt-txt rv">Берём на себя проектирование, инженерные работы, отделку и контроль реализации. '
  'Ремонт квартир в Москве, ремонт домов и отделка коммерческих помещений — одна команда отвечает за результат от первого замера до сдачи.</p>')
w('</section>')

# ── projects ────────────────────────────────────────────────────────────────
w('<section class="sec prj" id="projects" aria-labelledby="prj-h">')
w('<div class="sec-head">' + label("Selected projects / 01") +
  '<h2 class="giant" id="prj-h"><span class="ln"><span>Наши</span></span><span class="ln"><span>проекты</span></span></h2>'
  f'<p class="sec-note rv">Москва — квартиры и коммерческие помещения.</p></div>')
w('<div class="prj-grid">')
# Шелепиха показана ниже отдельным кейсом — в сетке её нет
for i, p in enumerate([x for x in PROJECTS if x["id"] != "shelepiha"]):
    n = len(PF[p["id"]])
    w(f'<article class="card rv" data-view>')
    w(f'<a class="card-open" href="#obekt-{p["id"]}" aria-label="Открыть объект {e(p["name"])}: {n} фото">'
      + pic(p["cover"], f"Ремонт: {p['name']}", "(max-width: 760px) 100vw, 50vw", "mask") + '<i class="dot"></i></a>')
    w(f'<div class="card-meta"><p class="num">{i+1:02d} / {p["lat"]}</p><h3><a href="#obekt-{p["id"]}">{e(p["name"])}</a></h3>'
      f'<ul><li>Москва</li><li>{e(p["type"])}</li><li>{n} фото</li></ul></div></article>')
w('</div></section>')

# ── case study ──────────────────────────────────────────────────────────────
w('<section class="sec case" aria-labelledby="case-h">')
w('<div class="case-head">' + label("Case study / 02") +
  '<h2 class="giant" id="case-h"><span class="ln"><span>Шелепиха</span></span></h2></div>')
w('<figure class="case-main" data-view><a class="card-open" href="#obekt-shelepiha" aria-label="Все фото объекта Шелепиха">' +
  pic("shel-gostinaya", "Гостиная-кухня в квартире на Шелепихе", "(max-width: 760px) 100vw, 66vw", "mask") + '</a></figure>')
w('<dl class="case-spec rv">'
  '<div><dt>Объект</dt><dd>Квартира</dd></div>'
  '<div><dt>Локация</dt><dd>Москва, Шелепиха</dd></div>'
  '<div><dt>Помещения</dt><dd>Гостиная-кухня, спальня, коридор</dd></div></dl>')
w(f'<p class="case-row-link rv"><a class="lnk" href="#obekt-shelepiha">Все фото объекта — {len(PF["shelepiha"])} <span>→</span></a></p>')
w('<p class="case-txt rv">Тёплое дерево, серый камень и мягкий текстиль: спокойный интерьер, в котором всё решает точность — '
  'ровные плоскости, аккуратные примыкания, продуманный свет. Так выглядит объект, когда проект, инженерия и отделка сделаны одной командой.</p>')
w('<div class="case-row">')
for n, (img, t) in enumerate([("shel-stolovaya", "Столовая"), ("shel-koridor", "Коридор"), ("shel-spalnya", "Спальня")]):
    w(f'<figure class="rv">' + pic(img, f"Шелепиха — {t.lower()}", "(max-width: 760px) 100vw, 33vw", "mask") +
      f'<figcaption><span>ZONE / 0{n+1}</span>{t}</figcaption></figure>')
w('</div></section>')

# ── services ────────────────────────────────────────────────────────────────
w('<section class="sec svc" id="services" aria-labelledby="svc-h">')
w('<div class="sec-head">' + label("Services / 03") +
  '<h2 class="giant" id="svc-h"><span class="ln"><span>Наши</span></span><span class="ln"><span>услуги</span></span></h2>'
  '<p class="sec-note rv">Дизайн интерьера и ремонт квартир под ключ.<br>Цены — за квадратный метр.</p></div>')
w('<div class="svc-design">')
for n, t, p, d, art in DESIGN:
    w(f'<article class="box rv"><div class="art">{SVG[art]}</div><p class="num">{n}</p><h3>{t}</h3><p>{d}</p>'
      f'<p class="price">от {rub(p)} ₽<small>/м²</small></p><a class="lnk" href="#form" data-type="{e(t)}">Обсудить <span>→</span></a></article>')
w('</div>')
w('<h3 class="svc-sub rv"><i></i>Ремонт под ключ — три тарифа</h3><div class="svc-tariffs">')
for n, t, p, rows in TARIFFS:
    w(f'<article class="box tariff rv"><p class="num">{n}</p><h3>{t}</h3><dl>' +
      "".join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in rows) +
      f'</dl><p class="price">от {rub(p)} ₽<small>/м²</small></p><a class="lnk" href="#form">Рассчитать <span>→</span></a></article>')
w('</div><p class="svc-foot rv">Точную стоимость считаем бесплатно за 3 рабочих дня после замера — по вашему проекту и выбранным материалам.</p></section>')

# ── numbers ─────────────────────────────────────────────────────────────────
w('<section class="sec nums" aria-label="Цифры">')
NUMS = [("5+", "лет в ремонте"), ("50+", "реализованных проектов"), ("5–10%", "погрешность сметы"),
        ("3 года", "гарантия по договору"), ("Каждую неделю", "фото- и видеоотчёт")]
w('<ul class="nums-list">' + "".join(f'<li class="rv{" wide" if i == 4 else ""}"><b data-count>{v}</b><span>{t}</span></li>' for i, (v, t) in enumerate(NUMS)) + '</ul>')
w('<ul class="nums-facts rv"><li>Сроки фиксируем в договоре</li><li>Бесплатный расчёт за 3 рабочих дня</li>'
  '<li>Покажем текущий объект вживую</li><li>Узкопрофильные специалисты и опытные бригады</li></ul></section>')

# ── about ───────────────────────────────────────────────────────────────────
w('<section class="sec about" id="about" aria-labelledby="about-h">')
w('<div class="about-head">' + label("The company / 04") +
  '<h2 class="giant" id="about-h"><span class="ln"><span>СК</span></span><span class="ln ind"><span>Деревянко</span></span></h2></div>')
w('<figure class="about-pic rv">' + pic("osnovatel", "Сергей Деревянко, основатель СК Деревянко", "(max-width: 760px) 80vw, 30vw", "mask") +
  '<figcaption><span>FOUNDER</span>Сергей Деревянко</figcaption></figure>')
w('<div class="about-txt"><blockquote class="rv"><p>Мы создаём интерьер целиком — от чертежей до последней детали. '
  'За каждым объектом стоит команда специалистов и персональный контроль качества.</p>'
  '<footer><b>Сергей Деревянко</b><span>Основатель</span></footer></blockquote>'
  '<p class="rv">Более 5 лет в ремонте и более 50 реализованных проектов: квартиры, дома и коммерческие помещения. '
  'Дизайнерский ремонт квартир, дизайн интерьера и инженерные системы — в одних руках, поэтому результат совпадает с проектом.</p></div>')
w('</section>')

# ── process ─────────────────────────────────────────────────────────────────
w('<section class="sec proc" id="process" aria-labelledby="proc-h">')
w('<div class="proc-head">' + label("Process / 05") +
  '<h2 class="giant" id="proc-h"><span class="ln"><span>Как мы</span></span><span class="ln"><span>работаем</span></span></h2>'
  '<p class="sec-note rv">Семь этапов — от первого звонка до ключей.</p></div>')
w('<ol class="steps">' + "".join(f'<li class="step"><span class="step-n">{i+1:02d}</span><div><h3>{t}</h3><p>{d}</p></div></li>'
                                 for i, (t, d) in enumerate(STEPS)) + '</ol></section>')

# ── faq ─────────────────────────────────────────────────────────────────────
w('<section class="sec faq" aria-labelledby="faq-h"><div class="faq-head">' + label("Questions / 06") +
  '<h2 class="mid" id="faq-h">Частые вопросы</h2></div><div class="faq-list">')
for q, a in FAQ:
    w(f'<details class="rv"><summary>{q}<i></i></summary><p>{a}</p></details>')
w('</div></section>')

# ── cta + form ──────────────────────────────────────────────────────────────
w('<section class="cta" id="contacts" aria-labelledby="cta-h">')
w('<div class="cta-glow" aria-hidden="true"></div>')
w(label("Contact / 07"))
w('<h2 class="giant cta-h" id="cta-h"><span class="ln" data-drift="-1"><span>Есть</span></span><span class="ln ind" data-drift="1"><span>объект?</span></span></h2>')
w('<div class="cta-side"><p class="rv">Расскажите о помещении — подготовим предварительную оценку стоимости.</p>'
  f'<a class="cta-tel rv" href="{TEL}">{PHONE}</a><a class="btn mag rv" href="#form">Получить расчёт <span>→</span></a></div>')
w('</section>')

w('<section class="sec form-sec" id="form" aria-labelledby="form-h">')
w('<div class="form-head">' + label("Заявка") + '<h2 class="mid" id="form-h">Обсудить проект</h2>'
  '<p>Перезвоним, ответим на вопросы и договоримся о бесплатном замере.</p>'
  f'<ul class="form-alt"><li><a href="{TEL}">{PHONE}</a></li><li><a href="{TEL2}">{PHONE2}</a></li>'
  f'<li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>')
w(f'<form class="lead" action="{FORM_URL}" method="post" novalidate>')
w('<label class="hp" aria-hidden="true">Не заполняйте<input name="website" tabindex="-1" autocomplete="off"></label>')
w('<label class="fld"><span>Имя</span><input name="your-name" autocomplete="name" required></label>')
w('<label class="fld"><span>Телефон</span><input name="your-phone" type="tel" inputmode="tel" autocomplete="tel" required placeholder="+7"></label>')
w('<fieldset class="fld types"><legend>Тип объекта</legend><div>' +
  "".join(f'<label><input type="radio" name="object-type" value="{t}"{" checked" if i == 0 else ""}><span>{t}</span></label>'
          for i, t in enumerate(["Квартира", "Дом", "Офис", "Коммерческое помещение", "Другое"])) + '</div></fieldset>')
w('<label class="fld"><span>Площадь, м²</span><input name="object-area" type="number" inputmode="numeric" min="1" max="100000"></label>')
if PROD:
    w('<div class="fld capf"><span>Код с картинки</span><div class="cap-row">'
      '<img class="cap-img" src="captcha.php" width="160" height="52" alt="Код с картинки">'
      '<button class="cap-new" type="button" aria-label="Показать другой код">↻</button>'
      '<input name="captcha" autocomplete="off" autocapitalize="characters" spellcheck="false" maxlength="5" required></div></div>')
w('<div class="form-act"><button class="btn mag" type="submit">Обсудить проект <span>→</span></button>'
  f'<p class="consent">Нажимая кнопку, вы соглашаетесь с <a href="{SITE}privacy-policy/" target="_blank" rel="noopener">политикой конфиденциальности</a>.</p></div>')
w('<p class="form-msg" role="status" aria-live="polite"></p></form></section>')

w('</main>')

# ── страницы объектов: «проваливаемся» в объект, как в портфолио на основном сайте ──
for i, p in enumerate(PROJECTS):
    nxt = PROJECTS[(i + 1) % len(PROJECTS)]
    ph = PF[p["id"]]
    w(f'<section class="pv" id="obekt-{p["id"]}" hidden aria-labelledby="pv-h-{p["id"]}">')
    w(f'<div class="pv-bar"><a class="lnk pv-back" href="#projects"><span>←</span> Все проекты</a><p class="num">Project / {i+1:03d}</p></div>')
    w(f'<div class="pv-head"><p class="lbl"><i></i>{p["lat"]}</p><h2 class="giant" id="pv-h-{p["id"]}">{e(p["name"])}</h2>'
      f'<ul class="pv-meta"><li><span>Локация</span>Москва</li><li><span>Объект</span>{e(p["type"])}</li><li><span>Фото</span>{len(ph)}</li></ul></div>')
    w('<div class="pv-grid">')
    for k, f in enumerate(ph):
        alt = f"{p['name']} — фото {k+1}"
        w(f'<button class="pv-ph" type="button" data-view data-full="assets/img/{f["n"]}-1280.webp" data-alt="{e(alt)}">'
          f'<picture><source type="image/avif" srcset="assets/img/{f["n"]}-640.avif 640w, assets/img/{f["n"]}-1280.avif 1280w" sizes="(max-width: 760px) 100vw, 33vw">'
          f'<img src="assets/img/{f["n"]}-640.webp" srcset="assets/img/{f["n"]}-640.webp 640w, assets/img/{f["n"]}-1280.webp 1280w" sizes="(max-width: 760px) 100vw, 33vw" '
          f'width="{f["w"]}" height="{f["h"]}" alt="{e(alt)}" loading="lazy" decoding="async"></picture><span>{k+1:02d}</span></button>')
    w('</div>')
    w(f'<a class="pv-next" href="#obekt-{nxt["id"]}"><span class="lbl"><i></i>Следующий проект</span><b>{e(nxt["name"])} <em>→</em></b></a>')
    w(f'<div class="pv-cta"><p>Хотите так же? Обсудим ваш объект.</p><a class="btn mag" href="#form">Обсудить проект <span>→</span></a></div>')
    w('</section>')

# ── footer ──────────────────────────────────────────────────────────────────
w('<footer class="ftr">')
w('<p class="ftr-word" aria-hidden="true">СК Деревянко</p>')
w('<div class="ftr-grid">')
w(f'<div><p class="lbl"><i></i>Контакты</p><p><a href="{TEL}">{PHONE}</a><br><a href="{TEL2}">{PHONE2}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>')
w(f'<div><p class="lbl"><i></i>Адрес</p><p>{ADDRESS}</p></div>')
w('<div><p class="lbl"><i></i>Мы на площадках</p><p>' + "<br>".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for t, u in SOCIAL) + '</p></div>')
w('<div><p class="lbl"><i></i>Разделы</p><p>' + "<br>".join(f'<a href="#{a}">{t}</a>' for a, t in NAV) + '</p></div>')
w('</div><div class="ftr-bot"><span>© 2026 СК Деревянко</span><span>RENOVATION / DESIGN / CONSTRUCTION</span>'
  f'<a href="{SITE}privacy-policy/" target="_blank" rel="noopener">Политика конфиденциальности</a></div>')
w('</footer>')

w('<div class="lb" hidden role="dialog" aria-modal="true" aria-label="Фото объекта"><button class="lb-x" type="button" aria-label="Закрыть">Закрыть ✕</button>'
  '<button class="lb-p" type="button" aria-label="Предыдущее фото">←</button><figure><img alt=""><figcaption></figcaption></figure>'
  '<button class="lb-n" type="button" aria-label="Следующее фото">→</button></div>')
w('<div class="cursor" aria-hidden="true">View</div>')
w(f'<script src="assets/js/goals.js?v={VER}" defer></script>')
w(f'<script src="assets/js/site.js?v={VER}" defer></script></body></html>')

(ROOT / "index.html").write_text("\n".join(H))
(ROOT / "assets/img/favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#08090A"/>'
    '<rect x="14" y="14" width="14" height="14" fill="#A70F27"/><path d="M14 36h36v14H14z" fill="#F3F2EE"/></svg>')
(ROOT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
print("index.html", len("\n".join(H)) // 1024, "KB", "PROD" if PROD else "staging")
