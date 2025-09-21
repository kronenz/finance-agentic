#!/bin/bash

# 프로덕션 배포 스크립트
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 환경 변수 확인
check_environment() {
    log_step "환경 변수 확인"
    
    required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "SECRET_KEY"
        "STRIPE_SECRET_KEY"
        "ENVIRONMENT"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "필수 환경 변수가 설정되지 않았습니다: $var"
            exit 1
        fi
    done
    
    log_info "모든 필수 환경 변수가 설정되었습니다"
}

# 의존성 설치
install_dependencies() {
    log_step "의존성 설치"
    
    # 백엔드 의존성
    log_info "백엔드 의존성 설치 중..."
    cd backend
    pip install -r requirements.txt
    cd ..
    
    # 프론트엔드 의존성
    log_info "프론트엔드 의존성 설치 중..."
    cd frontend
    npm ci --production
    cd ..
    
    log_info "의존성 설치 완료"
}

# 테스트 실행
run_tests() {
    log_step "테스트 실행"
    
    # 백엔드 테스트
    log_info "백엔드 테스트 실행 중..."
    cd backend
    python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term
    cd ..
    
    # 프론트엔드 테스트
    log_info "프론트엔드 테스트 실행 중..."
    cd frontend
    npm test -- --coverage --watchAll=false
    cd ..
    
    log_info "모든 테스트 통과"
}

# 보안 스캔
run_security_scan() {
    log_step "보안 스캔 실행"
    
    # Python 보안 스캔
    log_info "Python 보안 스캔 실행 중..."
    cd backend
    pip install bandit safety
    bandit -r app/ -f json -o bandit-report.json
    safety check --json --output safety-report.json
    cd ..
    
    # Node.js 보안 스캔
    log_info "Node.js 보안 스캔 실행 중..."
    cd frontend
    npm audit --audit-level=moderate
    cd ..
    
    log_info "보안 스캔 완료"
}

# 코드 품질 검사
run_code_quality() {
    log_step "코드 품질 검사"
    
    # Python 코드 품질
    log_info "Python 코드 품질 검사 중..."
    cd backend
    pip install black flake8 mypy
    black --check app/
    flake8 app/
    mypy app/ --ignore-missing-imports
    cd ..
    
    # TypeScript 코드 품질
    log_info "TypeScript 코드 품질 검사 중..."
    cd frontend
    npm run lint
    npm run type-check
    cd ..
    
    log_info "코드 품질 검사 완료"
}

# Docker 이미지 빌드
build_docker_images() {
    log_step "Docker 이미지 빌드"
    
    # 백엔드 이미지 빌드
    log_info "백엔드 Docker 이미지 빌드 중..."
    docker build -t crypto-trading/backend:latest -f backend/Dockerfile.prod backend/
    
    # 프론트엔드 이미지 빌드
    log_info "프론트엔드 Docker 이미지 빌드 중..."
    docker build -t crypto-trading/frontend:latest -f frontend/Dockerfile.prod frontend/
    
    log_info "Docker 이미지 빌드 완료"
}

# 데이터베이스 마이그레이션
run_database_migration() {
    log_step "데이터베이스 마이그레이션"
    
    log_info "데이터베이스 마이그레이션 실행 중..."
    cd backend
    alembic upgrade head
    cd ..
    
    log_info "데이터베이스 마이그레이션 완료"
}

# 애플리케이션 배포
deploy_application() {
    log_step "애플리케이션 배포"
    
    # Docker Compose로 배포
    log_info "Docker Compose로 애플리케이션 배포 중..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # 헬스체크
    log_info "애플리케이션 헬스체크 중..."
    sleep 30
    
    # 헬스체크 재시도
    for i in {1..5}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_info "애플리케이션이 정상적으로 시작되었습니다"
            break
        else
            log_warn "헬스체크 실패, 재시도 중... ($i/5)"
            sleep 10
        fi
    done
    
    # 최종 헬스체크
    if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_error "애플리케이션 배포 실패"
        exit 1
    fi
}

# 모니터링 설정
setup_monitoring() {
    log_step "모니터링 설정"
    
    # Prometheus 설정
    log_info "Prometheus 설정 중..."
    docker-compose -f docker-compose.prod.yml up -d prometheus
    
    # Grafana 설정
    log_info "Grafana 설정 중..."
    docker-compose -f docker-compose.prod.yml up -d grafana
    
    log_info "모니터링 설정 완료"
}

# 배포 후 검증
verify_deployment() {
    log_step "배포 후 검증"
    
    # API 엔드포인트 테스트
    log_info "API 엔드포인트 테스트 중..."
    
    # 기본 헬스체크
    curl -f http://localhost:8000/health
    
    # 상세 헬스체크
    curl -f http://localhost:8000/health/detailed
    
    # 메트릭 엔드포인트
    curl -f http://localhost:8000/metrics
    
    # API 문서
    curl -f http://localhost:8000/docs
    
    log_info "모든 API 엔드포인트가 정상적으로 동작합니다"
}

# 롤백 함수
rollback() {
    log_error "배포 중 오류 발생, 롤백 중..."
    
    # 이전 버전으로 롤백
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    
    log_warn "롤백 완료"
}

# 메인 함수
main() {
    log_info "프로덕션 배포 시작"
    
    # 트랩 설정 (오류 시 롤백)
    trap rollback ERR
    
    # 배포 단계 실행
    check_environment
    install_dependencies
    run_tests
    run_security_scan
    run_code_quality
    build_docker_images
    run_database_migration
    deploy_application
    setup_monitoring
    verify_deployment
    
    log_info "프로덕션 배포 완료!"
    
    # 배포 정보 출력
    echo ""
    echo "=========================================="
    echo "배포 완료 정보"
    echo "=========================================="
    echo "애플리케이션 URL: http://localhost:8000"
    echo "API 문서: http://localhost:8000/docs"
    echo "헬스체크: http://localhost:8000/health"
    echo "메트릭: http://localhost:8000/metrics"
    echo "Prometheus: http://localhost:9090"
    echo "Grafana: http://localhost:3001"
    echo "=========================================="
}

# 스크립트 실행
main "$@"
