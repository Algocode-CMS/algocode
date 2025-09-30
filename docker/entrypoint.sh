#!/bin/sh

if [ ! -e /home/algocode/config.json ]; then
    cp configs/config_example.json /home/algocode/config.json
fi

source .venv/bin/activate
python3 manage.py migrate --noinput

python3 manage.py shell <<'PY'
import json, os
from django.contrib.auth import get_user_model

cfg = json.load(open("/home/algocode/config.json"))
su = cfg.get("secrets", {}).get("ejudge", {})
username = su.get("login", "admin")
password = su.get("password", "admin")

User = get_user_model()
u, created = User.objects.get_or_create(
    username=username,
    defaults={"is_staff": True, "is_superuser": True}
)

if created:
    u.set_password(password)
    u.save()
PY

python3 manage.py runserver 0.0.0.0:80
