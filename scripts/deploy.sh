#!/bin/bash

# 배포 스크립트
# 환경별 배포를 위한 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수 정의
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 확인
ENVIRONMENT=${1:-development}

if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    log_error "Invalid environment. Use: development, staging, or production"
    exit 1
fi

log_info "Deploying to $ENVIRONMENT environment..."

# 환경별 설정
case $ENVIRONMENT in
    development)
        COMPOSE_FILE="docker-compose.dev.yml"
        LOG_LEVEL="DEBUG"
        ;;
    staging)
        COMPOSE_FILE="docker-compose.yml"
        LOG_LEVEL="INFO"
        ;;
    production)
        COMPOSE_FILE="docker-compose.prod.yml"
        LOG_LEVEL="WARNING"
        ;;
esac

# 기존 컨테이너 정리
log_info "Cleaning up existing containers..."
docker-compose -f $COMPOSE_FILE down --remove-orphans

# 이미지 빌드
log_info "Building images..."
docker-compose -f $COMPOSE_FILE build --no-cache

# 서비스 시작
log_info "Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# 헬스체크
log_info "Waiting for services to be healthy..."
sleep 30

# 백엔드 헬스체크
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log_info "Backend is healthy"
else
    log_error "Backend health check failed"
    exit 1
fi

# 프론트엔드 헬스체크
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    log_info "Frontend is healthy"
else
    log_error "Frontend health check failed"
    exit 1
fi

# 데이터베이스 마이그레이션 (백엔드가 실행된 후)
log_info "Running database migrations..."
docker-compose -f $COMPOSE_FILE exec backend alembic upgrade head

log_info "Deployment completed successfully!"

# 서비스 상태 확인
log_info "Service status:"
docker-compose -f $COMPOSE_FILE ps

# 포트 정보
log_info "Service URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3001"
echo "  Kibana: http://localhost:5601"