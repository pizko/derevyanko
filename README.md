# СК Деревянко — лендинг

Одностраничник для sk-derevyanko.ru в стиле dark editorial architecture.
Staging: https://pizko.github.io/derevyanko/ (noindex).

```
python3 src/media.py          # фото из orig/uploads → assets/img (AVIF + WebP)
python3 src/build.py          # staging: noindex, без Метрики
python3 src/build.py --prod   # для домена: index + Метрика
```

- Все тексты, цены и объекты — с текущего сайта; площади и сроки объектов не публикуются, пока их нет.
- Заявки уходят в отдельную форму Contact Form 7 (id 9421) на sk-derevyanko.ru.
  С github.io отправка упирается в защиту beget (cookie) — на сайте форма заработает на своём домене;
  на staging при ошибке показываются телефон и Telegram.
