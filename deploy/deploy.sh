#!/bin/bash
# Выкладка на beget (vyache8m) в ~/sk-remont/public_html: сборка с Метрикой, затем обратно staging-сборка для git.
set -e
cd "$(dirname "$0")/.."
python3 src/build.py --prod
T=$(mktemp -d)
cp index.html politika.html robots.txt sitemap.xml "$T/"; cp *.txt "$T/" 2>/dev/null || true   # llms.txt и ключ IndexNow
cp deploy/send.php deploy/token.php deploy/captcha.php deploy/.htaccess "$T/"
cp -r msk spb "$T/"   # посадочные Москва/СПб — без этого rsync --delete их удалит
rsync -a --exclude '*.json' assets "$T/"
COPYFILE_DISABLE=1 rsync -rlt --delete --no-perms --exclude cgi-bin --exclude '._*' "$T/" vyache8m@vyache8m.beget.tech:sk-remont/public_html/
rm -rf "$T"
python3 src/build.py
