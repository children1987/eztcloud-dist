#!/bin/sh

echo "stoping uwsgi ..."
cd /workspace/rslz/backend
pipenv run uwsgi --stop ./uwsgi.pid
echo "stoping uwsgi finished."

echo "git configging ... "
git config core.filemode false
echo "git configging finished. "

echo "git pulling code from oschina ... "
cd /workspace/rslz
git pull
echo "git pulling code from oschina finished."

echo "chmoding ... "
chmod -R 777 /workspace/rslz/backend
echo "chmoding finished."

cd /workspace/rslz/backend

echo "starting uwsgi ..."
pipenv run uwsgi --ini /workspace/rslz/deploy/uwsgi/uwsgi_arch.ini
echo "starting uwsgi finished."
