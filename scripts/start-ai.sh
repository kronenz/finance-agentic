#!/bin/bash

# AI 개발 환경 시작 스크립트

echo "🚀 Starting AI Development Environment..."

# 환경 변수 설정
export PYTHONPATH=/app
export JUPYTER_ENABLE_LAB=yes

# 데이터 디렉토리 생성
mkdir -p /app/data/{raw,processed,models}
mkdir -p /app/notebooks
mkdir -p /app/logs

# Jupyter Lab과 FastAPI를 동시에 실행
echo "📊 Starting Jupyter Lab on port 8888..."
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root &

echo "🔧 Starting FastAPI on port 8000..."
cd /app && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# 프로세스 대기
wait
