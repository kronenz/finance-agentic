#!/bin/bash

# AI 기반 암호화폐 자동화 거래 시스템 설정 스크립트

set -e

echo "🚀 AI 기반 암호화폐 자동화 거래 시스템 설정을 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Python 버전 확인
print_status "Python 버전 확인 중..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION 발견"
else
    print_error "Python 3이 설치되어 있지 않습니다. Python 3.9 이상을 설치해주세요."
    exit 1
fi

# 가상환경 생성
print_status "가상환경 생성 중..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "가상환경 생성 완료"
else
    print_warning "가상환경이 이미 존재합니다"
fi

# 가상환경 활성화
print_status "가상환경 활성화 중..."
source venv/bin/activate
print_success "가상환경 활성화 완료"

# pip 업그레이드
print_status "pip 업그레이드 중..."
pip install --upgrade pip
print_success "pip 업그레이드 완료"

# 의존성 설치
print_status "의존성 설치 중..."
pip install -r requirements.txt
print_success "의존성 설치 완료"

# 필요한 디렉토리 생성
print_status "필요한 디렉토리 생성 중..."
mkdir -p data/cache
mkdir -p logs
mkdir -p data/backup
print_success "디렉토리 생성 완료"

# 환경 변수 파일 생성
print_status "환경 변수 파일 생성 중..."
if [ ! -f ".env" ]; then
    cp env.example .env
    print_success "환경 변수 파일 생성 완료 (.env)"
    print_warning "실제 API 키를 .env 파일에 입력해주세요"
else
    print_warning ".env 파일이 이미 존재합니다"
fi

# 데이터베이스 초기화
print_status "데이터베이스 초기화 중..."
python -c "
from src.core.database import get_database
db = get_database()
print('데이터베이스 초기화 완료')
"
print_success "데이터베이스 초기화 완료"

# 테스트 실행
print_status "테스트 실행 중..."
if [ -d "tests" ]; then
    python -m pytest tests/ -v
    print_success "테스트 완료"
else
    print_warning "테스트 디렉토리가 없습니다"
fi

# 설정 검증
print_status "설정 검증 중..."
python -c "
from src.core.config import get_config
config = get_config()
print(f'설정 로드 성공: {config.trading.symbol}')
"
print_success "설정 검증 완료"

print_success "🎉 설정이 완료되었습니다!"
echo ""
echo "다음 단계:"
echo "1. .env 파일에 실제 API 키를 입력하세요"
echo "2. python src/main.py 명령으로 시스템을 실행하세요"
echo "3. 브라우저에서 http://localhost:8000 으로 대시보드에 접속하세요"
echo ""
echo "개발 모드 실행: python src/main.py --dev"
echo "프로덕션 모드 실행: python src/main.py --prod"
