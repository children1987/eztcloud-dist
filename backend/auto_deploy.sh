#!/bin/sh

echo "stoping uwsgi ..."
cd /workspace/xjsy/backend
pipenv run uwsgi --stop ./uwsgi.pid
echo "stoping uwsgi finished."

echo "git configging ... "
git config core.filemode false
echo "git configging finished. "

echo "rm /static ... "
rm -rf /workspace/xjsy/backend/static
echo "rm /static finished. "

echo "git pulling code from oschina ... "
cd /workspace/xjsy
git pull
echo "git pulling code from oschina finished."

echo "chmoding ... "
chmod -R 777 /workspace/xjsy/backend
echo "chmoding finished."

echo "pack fronted static files..."
cd /workspace/xjsy/frontend_web/
cnpm i
cnpm run build
echo "packed finished"

echo "collectting static files ..."
cd /workspace/xjsy/backend
pipenv run python manage.py collectstatic --noinput
echo "collectting static files finished."

cd /workspace/xjsy/backend/backend
echo "restarting celery... "
pipenv run celery -A celery_tasks.main beat -l info
pipenv run celery multi restart w1 -A celery_tasks.main -l info
echo "restart celery finished."

echo "starting uwsgi ..."
pipenv run uwsgi --ini /workspace/xjsy/deploy/uwsgi/uwsgi_xjsy.ini
echo "starting uwsgi finished."
