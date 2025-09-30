#! /bin/bash

set -x

localedef -v -c -i ru_RU -f UTF-8 ru_RU.UTF-8

set -e

#RELEASE=
RELEASE='RELEASE=1'

rm -rf .git

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt pymemcache

sed -i "s|MemcachedCache|PyMemcacheCache|" /app/configs/config_example.json
sed -i "s|127.0.0.1:11211|memcached:11211|" /app/configs/config_example.json
sed -i "s|exec_res = os.path.join(BASE_DIR, 'db.sqlite3')|exec_res = /home/algocode/db.sqlite3|" /app/configs/config_example.json
sed -i "s|"connection_string": ""|"connection_string": "127.0.0.1:27017"|" /app/configs/config_example.json
sed -i "s|http://some_ejudge_url.com|http://ejudge|" /app/configs/config_example.json
sed -i "s|ejudge_admin_login|ejudge|" /app/configs/config_example.json
sed -i "s|ejudge_admin_password|ejudge|" /app/configs/config_example.json
sed -i "s|<path to ejudge bin/serve-control>|/home/judges/bin/ejudge-control|" /app/configs/config_example.json
sed -i "s|os.path.join(BASE_DIR, 'configs/config.json')|'/home/algocode/config.json'|" /app/algocode/settings.py
sed -i "s|sql.log|/home/algocode/sql.log|" /app/algocode/settings.py
sed -i "s|os.path.join(BASE_DIR, 'files')|'/home/algocode/files'|" /app/algocode/settings.py
sed -i "s|ru-RU|en-US|" /app/algocode/settings.py
sed -i "s|os.path.join(BASE_DIR, 'static')|os.path.join(BASE_DIR, 'courses/static')|" /app/algocode/settings.py
sed -i "s|(os.path.join(BASE_DIR,  'templates'),)|(os.path.join(BASE_DIR,  'courses/templates'),)|" /app/algocode/settings.py
