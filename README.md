# Algocode

Python3 [Django](https://www.djangoproject.com) project to manage programming courses and create standings for [ejudge](https://ejudge.ru) and codeforces contests.

To setup, rename `configs/config_example.json` to `condfigs/config.json` and change needed fields there. 
After that algocode can be started the same way as any other django application.
Codeforces data can be loaded only manually with command `./manage.py load_codeforces` (Recommended to run it with cron).
