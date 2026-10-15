#!/usr/bin/env bash
# Render 빌드 스크립트
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
# 환경변수로 관리자 계정 만들기/비밀번호 맞추기 (값이 없으면 경고만)
python manage.py ensure_superuser
# 로그인 잠금(axes) 모두 풀기
python manage.py axes_reset
# CSV를 DB에 넣기 (여러 번 실행해도 중복 없음)
python manage.py import_creatures ../먹이를찾아라_50종.csv
