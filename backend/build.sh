#!/usr/bin/env bash
# Render 빌드 스크립트
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# CSV를 DB에 넣기 (여러 번 실행해도 중복 없음)
python manage.py import_creatures ../먹이를찾아라_50종.csv
