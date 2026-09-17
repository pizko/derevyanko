#!/bin/bash
# Выкладка на beget (vyache8m) в ~/sk-remont/public_html: сборка с Метрикой, затем обратно staging-сборка для git.
set -e
cd "$(dirname "$0")/.."
python3 src/build.py --prod
T=$(mktemp -d)
cp index.html robots.txt "$T/"; cp deploy/send.php deploy/.htaccess "$T/"
rsync -a --exclude '*.json' assets "$T/"
COPYFILE_DISABLE=1 rsync -rlt --delete --no-perms --exclude cgi-bin --exclude '._*' "$T/" vyache8m@vyache8m.beget.tech:sk-remont/public_html/
rm -rf "$T"
python3 src/build.py
