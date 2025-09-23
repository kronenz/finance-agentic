#!/bin/bash

# 프로덕션 배포 스크립트
# Crypto Trading Subscription Service

set -e

echo "🚀 프로덕션 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 확인
check_env() {
    log_info "환경 변수 확인 중..."
    
    if [ ! -f "env.production" ]; then
        log_error "env.production 파일이 없습니다."
        exit 1
    fi
    
    log_success "환경 변수 파일 확인 완료"
}

# Docker 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 중..."
    
    # 백엔드 이미지 빌드
    log_info "백엔드 이미지 빌드 중..."
    docker-compose -f docker-compose.prod.yml build backend
    
    # 프론트엔드 이미지 빌드
    log_info "프론트엔드 이미지 빌드 중..."
    docker-compose -f docker-compose.prod.yml build frontend
    
    log_success "Docker 이미지 빌드 완료"
}

# 기존 컨테이너 정리
cleanup() {
    log_info "기존 컨테이너 정리 중..."
    
    # 기존 컨테이너 중지 및 제거
    docker-compose -f docker-compose.prod.yml down --volumes --remove-orphans
    
    # 사용하지 않는 이미지 정리
    docker image prune -f
    
    log_success "컨테이너 정리 완료"
}

# 데이터베이스 마이그레이션
migrate_database() {
    log_info "데이터베이스 마이그레이션 실행 중..."
    
    # PostgreSQL 컨테이너 시작
    docker-compose -f docker-compose.prod.yml up -d postgres
    
    # 데이터베이스 준비 대기
    log_info "데이터베이스 준비 대기 중..."
    sleep 30
    
    # 마이그레이션 실행
    docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
    
    log_success "데이터베이스 마이그레이션 완료"
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    # 모든 서비스 시작
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "서비스 시작 완료"
}

# 헬스 체크
health_check() {
    log_info "헬스 체크 실행 중..."
    
    # 백엔드 헬스 체크
    log_info "백엔드 헬스 체크 중..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "백엔드 헬스 체크 통과"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "백엔드 헬스 체크 실패"
            exit 1
        fi
        sleep 2
    done
    
    # 프론트엔드 헬스 체크
    log_info "프론트엔드 헬스 체크 중..."
    for i in {1..30}; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            log_success "프론트엔드 헬스 체크 통과"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "프론트엔드 헬스 체크 실패"
            exit 1
        fi
        sleep 2
    done
    
    log_success "모든 헬스 체크 통과"
}

# 배포 상태 확인
check_deployment() {
    log_info "배포 상태 확인 중..."
    
    # 컨테이너 상태 확인
    docker-compose -f docker-compose.prod.yml ps
    
    # 서비스 URL 확인
    log_info "서비스 URL:"
    echo "  - 프론트엔드: http://localhost:3000"
    echo "  - 백엔드 API: http://localhost:8000"
    echo "  - API 문서: http://localhost:8000/docs"
    echo "  - Grafana: http://localhost:3001"
    echo "  - Prometheus: http://localhost:9090"
}

# 메인 실행
main() {
    log_info "Crypto Trading Subscription Service 프로덕션 배포 시작"
    
    check_env
    cleanup
    build_images
    migrate_database
    start_services
    health_check
    check_deployment
    
    log_success "🎉 프로덕션 배포 완료!"
    log_info "서비스가 정상적으로 실행 중입니다."
}

# 스크립트 실행
main "$@"
