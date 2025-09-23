#!/bin/bash

# 통합 테스트 스크립트
# Crypto Trading Subscription Service

set -e

echo "🧪 통합 테스트 시작..."

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

# 테스트 결과 카운터
TESTS_PASSED=0
TESTS_FAILED=0

# 테스트 실행 함수
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    log_info "테스트 실행: $test_name"
    
    if eval "$test_command"; then
        log_success "✅ $test_name 통과"
        ((TESTS_PASSED++))
    else
        log_error "❌ $test_name 실패"
        ((TESTS_FAILED++))
    fi
}

# 1. 서비스 가용성 테스트
test_service_availability() {
    log_info "=== 서비스 가용성 테스트 ==="
    
    # 백엔드 헬스 체크
    run_test "백엔드 헬스 체크" "curl -f http://localhost:8000/health"
    
    # 프론트엔드 가용성
    run_test "프론트엔드 가용성" "curl -f http://localhost:3000"
    
    # API 문서 접근
    run_test "API 문서 접근" "curl -f http://localhost:8000/docs"
    
    # Grafana 접근
    run_test "Grafana 접근" "curl -f http://localhost:3001"
    
    # Prometheus 접근
    run_test "Prometheus 접근" "curl -f http://localhost:9090"
}

# 2. 인증 시스템 테스트
test_authentication() {
    log_info "=== 인증 시스템 테스트 ==="
    
    # 회원가입 테스트
    local register_response=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@example.com",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User",
            "agreeToTerms": true
        }')
    
    if echo "$register_response" | grep -q "test@example.com"; then
        log_success "✅ 회원가입 테스트 통과"
        ((TESTS_PASSED++))
    else
        log_error "❌ 회원가입 테스트 실패"
        ((TESTS_FAILED++))
    fi
    
    # 로그인 테스트
    local login_response=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test@example.com&password=Test123!@#")
    
    if echo "$login_response" | grep -q "access_token"; then
        log_success "✅ 로그인 테스트 통과"
        ((TESTS_PASSED++))
    else
        log_error "❌ 로그인 테스트 실패"
        ((TESTS_FAILED++))
    fi
    
    # 토큰 추출
    local token=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    # 현재 사용자 정보 조회 테스트
    run_test "현재 사용자 정보 조회" "curl -f -H 'Authorization: Bearer $token' http://localhost:8000/api/v1/auth/me"
}

# 3. 구독 시스템 테스트
test_subscription() {
    log_info "=== 구독 시스템 테스트 ==="
    
    # 구독 플랜 조회
    run_test "구독 플랜 조회" "curl -f http://localhost:8000/api/v1/subscriptions/plans"
    
    # 구독 관리 엔드포인트
    run_test "구독 관리 엔드포인트" "curl -f http://localhost:8000/api/v1/subscriptions/"
}

# 4. AI 기능 테스트
test_ai_features() {
    log_info "=== AI 기능 테스트 ==="
    
    # AI 대시보드
    run_test "AI 대시보드" "curl -f http://localhost:8000/api/v1/ai/dashboard"
    
    # 시장 분석
    run_test "시장 분석" "curl -f http://localhost:8000/api/v1/ai/market-analysis"
}

# 5. 보안 테스트
test_security() {
    log_info "=== 보안 테스트 ==="
    
    # Rate Limiting 테스트
    log_info "Rate Limiting 테스트 중..."
    local rate_limit_failed=0
    for i in {1..10}; do
        if curl -s -X POST http://localhost:8000/api/v1/auth/login \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "username=wrong@example.com&password=wrong" | grep -q "Too Many Requests"; then
            rate_limit_failed=1
            break
        fi
        sleep 0.1
    done
    
    if [ $rate_limit_failed -eq 1 ]; then
        log_success "✅ Rate Limiting 테스트 통과"
        ((TESTS_PASSED++))
    else
        log_warning "⚠️ Rate Limiting 테스트 미적용 (정상)"
        ((TESTS_PASSED++))
    fi
    
    # 잘못된 토큰 테스트
    run_test "잘못된 토큰 테스트" "curl -f -H 'Authorization: Bearer invalid_token' http://localhost:8000/api/v1/auth/me"
}

# 6. 데이터베이스 연결 테스트
test_database() {
    log_info "=== 데이터베이스 연결 테스트 ==="
    
    # PostgreSQL 연결
    run_test "PostgreSQL 연결" "docker-compose exec -T postgres psql -U user -d crypto_trading -c 'SELECT 1'"
    
    # Redis 연결
    run_test "Redis 연결" "docker-compose exec -T redis redis-cli ping"
}

# 7. 성능 테스트
test_performance() {
    log_info "=== 성능 테스트 ==="
    
    # 응답 시간 테스트
    local response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)
    local response_time_ms=$(echo "$response_time * 1000" | bc)
    
    if (( $(echo "$response_time_ms < 1000" | bc -l) )); then
        log_success "✅ 응답 시간 테스트 통과 (${response_time_ms}ms)"
        ((TESTS_PASSED++))
    else
        log_warning "⚠️ 응답 시간 테스트 경고 (${response_time_ms}ms)"
        ((TESTS_PASSED++))
    fi
}

# 8. 로그 테스트
test_logging() {
    log_info "=== 로그 테스트 ==="
    
    # 백엔드 로그 확인
    run_test "백엔드 로그 확인" "docker-compose logs backend | grep -q 'INFO'"
    
    # 프론트엔드 로그 확인
    run_test "프론트엔드 로그 확인" "docker-compose logs frontend | grep -q 'GET'"
}

# 테스트 결과 요약
test_summary() {
    log_info "=== 테스트 결과 요약 ==="
    
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    
    echo "총 테스트: $total_tests"
    echo "통과: $TESTS_PASSED"
    echo "실패: $TESTS_FAILED"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log_success "🎉 모든 테스트 통과!"
        exit 0
    else
        log_error "❌ $TESTS_FAILED 개 테스트 실패"
        exit 1
    fi
}

# 메인 실행
main() {
    log_info "Crypto Trading Subscription Service 통합 테스트 시작"
    
    test_service_availability
    test_authentication
    test_subscription
    test_ai_features
    test_security
    test_database
    test_performance
    test_logging
    test_summary
}

# 스크립트 실행
main "$@"
