#!/usr/bin/env bash
# Cloud Agent install: 의존성 파일이 있을 때만 설치한다.
# 이 저장소는 강의노트/리포트 생성용이어서 requirements.txt 가 비어 있거나
# 아직 없는 브랜치에서도 부팅이 실패하면 안 된다.
set -euo pipefail

if [ -f requirements.txt ]; then
  python3 -m pip install --user --disable-pip-version-check -r requirements.txt
else
  echo "No requirements.txt found; skipping pip install"
fi
