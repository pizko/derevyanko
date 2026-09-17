# СК Деревянко — лендинг

Одностраничник для sk-derevyanko.ru в стиле dark editorial architecture.
Staging: https://pizko.github.io/derevyanko/ (noindex).

```
python3 src/media.py          # фото из orig/uploads → assets/img (AVIF + WebP)
python3 src/build.py          # staging (GitHub Pages), без Метрики
./deploy/deploy.sh            # боевой: beget vyache8m ~/sk-remont/public_html, с Метрикой
```

Сайт работает только под Яндекс.Директ и закрыт от индексации: meta robots, robots.txt, X-Robots-Tag.

- Все тексты, цены и объекты — с текущего сайта; площади и сроки объектов не публикуются, пока их нет.
- Заявки: `send.php` → Telegram-бот заявок. Токен в `~/sk-remont/lead_config.php` (вне webroot),
  копия каждой заявки — `~/sk-remont/leads.log`. На staging PHP нет — форма покажет телефон.
