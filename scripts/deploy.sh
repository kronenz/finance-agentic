#!/bin/bash

# AI 기반 암호화폐 자동화 거래 시스템 배포 스크립트

set -e

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

# 환경 변수 확인
ENVIRONMENT=${1:-dev}
if [[ ! "$ENVIRONMENT" =~ ^(dev|stage|prod)$ ]]; then
    print_error "올바른 환경을 지정해주세요: dev, stage, prod"
    exit 1
fi

print_status "배포 환경: $ENVIRONMENT"

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
print_status "현재 브랜치: $CURRENT_BRANCH"

# 환경별 브랜치 검증
case $ENVIRONMENT in
    dev)
        if [ "$CURRENT_BRANCH" != "dev" ]; then
            print_warning "dev 환경 배포를 위해 dev 브랜치로 전환합니다"
            git checkout dev
        fi
        ;;
    stage)
        if [ "$CURRENT_BRANCH" != "stage" ]; then
            print_warning "stage 환경 배포를 위해 stage 브랜치로 전환합니다"
            git checkout stage
        fi
        ;;
    prod)
        if [ "$CURRENT_BRANCH" != "prod" ]; then
            print_error "prod 환경 배포는 prod 브랜치에서만 가능합니다"
            exit 1
        fi
        ;;
esac

# 가상환경 활성화
print_status "가상환경 활성화 중..."
if [ -d "venv" ]; then
    source venv/bin/activate
    print_success "가상환경 활성화 완료"
else
    print_error "가상환경이 없습니다. 먼저 setup.sh를 실행해주세요"
    exit 1
fi

# 의존성 업데이트
print_status "의존성 업데이트 중..."
pip install -r requirements.txt
print_success "의존성 업데이트 완료"

# 테스트 실행
print_status "테스트 실행 중..."
if [ -d "tests" ]; then
    python -m pytest tests/ -v --tb=short
    if [ $? -eq 0 ]; then
        print_success "테스트 통과"
    else
        print_error "테스트 실패"
        exit 1
    fi
else
    print_warning "테스트 디렉토리가 없습니다"
fi

# 코드 품질 검사
print_status "코드 품질 검사 중..."
if command -v black &> /dev/null; then
    black --check src/
    print_success "코드 포맷 검사 완료"
fi

if command -v flake8 &> /dev/null; then
    flake8 src/ --max-line-length=100 --ignore=E203,W503
    print_success "린트 검사 완료"
fi

# 환경별 설정 적용
print_status "환경별 설정 적용 중..."
case $ENVIRONMENT in
    dev)
        export TRADING_ENV=development
        export LOG_LEVEL=DEBUG
        ;;
    stage)
        export TRADING_ENV=staging
        export LOG_LEVEL=INFO
        ;;
    prod)
        export TRADING_ENV=production
        export LOG_LEVEL=WARNING
        ;;
esac

# 데이터베이스 마이그레이션 (필요한 경우)
print_status "데이터베이스 마이그레이션 확인 중..."
python -c "
from src.core.database import get_database
db = get_database()
print('데이터베이스 연결 확인 완료')
"

# 백업 생성 (prod 환경인 경우)
if [ "$ENVIRONMENT" = "prod" ]; then
    print_status "프로덕션 백업 생성 중..."
    BACKUP_DIR="data/backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [ -f "data/trading.db" ]; then
        cp data/trading.db "$BACKUP_DIR/"
        print_success "데이터베이스 백업 완료: $BACKUP_DIR"
    fi
    
    # 로그 백업
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/"
        print_success "로그 백업 완료"
    fi
fi

# 서비스 중지 (이미 실행 중인 경우)
print_status "기존 서비스 중지 확인 중..."
if pgrep -f "python.*main.py" > /dev/null; then
    print_warning "기존 서비스가 실행 중입니다. 중지합니다..."
    pkill -f "python.*main.py" || true
    sleep 2
fi

# 서비스 시작
print_status "서비스 시작 중..."
case $ENVIRONMENT in
    dev)
        print_status "개발 모드로 시작합니다..."
        nohup python src/main.py > logs/dev.log 2>&1 &
        ;;
    stage)
        print_status "스테이징 모드로 시작합니다..."
        nohup python src/main.py > logs/stage.log 2>&1 &
        ;;
    prod)
        print_status "프로덕션 모드로 시작합니다..."
        # 프로덕션에서는 systemd 서비스로 실행하는 것을 권장
        nohup python src/main.py > logs/prod.log 2>&1 &
        ;;
esac

# 서비스 상태 확인
sleep 3
if pgrep -f "python.*main.py" > /dev/null; then
    print_success "서비스가 성공적으로 시작되었습니다"
    echo "프로세스 ID: $(pgrep -f 'python.*main.py')"
    echo "로그 파일: logs/${ENVIRONMENT}.log"
else
    print_error "서비스 시작에 실패했습니다"
    echo "로그를 확인해주세요: logs/${ENVIRONMENT}.log"
    exit 1
fi

# 헬스체크
print_status "헬스체크 수행 중..."
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "헬스체크 통과"
else
    print_warning "헬스체크 실패 (웹 서버가 설정되지 않았을 수 있음)"
fi

print_success "🎉 $ENVIRONMENT 환경 배포가 완료되었습니다!"
echo ""
echo "배포 정보:"
echo "- 환경: $ENVIRONMENT"
echo "- 브랜치: $CURRENT_BRANCH"
echo "- 프로세스 ID: $(pgrep -f 'python.*main.py')"
echo "- 로그 파일: logs/${ENVIRONMENT}.log"
echo ""
echo "서비스 중지: pkill -f 'python.*main.py'"
echo "로그 확인: tail -f logs/${ENVIRONMENT}.log"
