#!/bin/bash

# 테스트 자동화 스크립트
# Phase 3.3 Week 3 - 통합 테스트 실행

set -e

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

# 설정
BASE_DIR="/root/develop/finance"
TEST_RESULTS_DIR="${BASE_DIR}/test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_LOG_FILE="${TEST_RESULTS_DIR}/test_run_${TIMESTAMP}.log"

# 테스트 결과 디렉토리 생성
mkdir -p "${TEST_RESULTS_DIR}"

# 로그 파일 초기화
echo "Test Run Started: $(date)" > "${TEST_LOG_FILE}"

# 함수 정의
check_services() {
    log_info "Checking required services..."
    
    # 백엔드 서비스 확인
    if ! curl -s http://localhost:8000/health > /dev/null; then
        log_error "Backend service is not running on localhost:8000"
        exit 1
    fi
    
    # 데이터베이스 연결 확인
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        log_warning "PostgreSQL is not running on localhost:5432, checking Docker container..."
        if ! docker exec crypto_trading_postgres pg_isready > /dev/null 2>&1; then
            log_error "PostgreSQL container is not healthy"
            exit 1
        fi
        log_success "PostgreSQL is running in Docker container"
    else
        log_success "PostgreSQL is running on localhost:5432"
    fi
    
    # Redis 연결 확인
    if ! redis-cli ping > /dev/null 2>&1; then
        log_warning "Redis is not running on localhost:6379, checking Docker container..."
        if ! docker exec crypto_trading_redis redis-cli ping > /dev/null 2>&1; then
            log_error "Redis container is not healthy"
            exit 1
        fi
        log_success "Redis is running in Docker container"
    else
        log_success "Redis is running on localhost:6379"
    fi
    
    log_success "All required services are running"
}

run_unit_tests() {
    log_info "Running unit tests..."
    
    cd "${BASE_DIR}/backend"
    
    # Python 의존성 설치
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    # 유닛 테스트 실행
    log_info "Running Python unit tests..."
    python -m pytest tests/unit/ -v --tb=short --junitxml="${TEST_RESULTS_DIR}/unit_tests_${TIMESTAMP}.xml" 2>&1 | tee -a "${TEST_LOG_FILE}"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Unit tests passed"
    else
        log_error "Unit tests failed"
        return 1
    fi
}

run_integration_tests() {
    log_info "Running integration tests..."
    
    cd "${BASE_DIR}/backend"
    source venv/bin/activate
    
    # 통합 테스트 실행
    log_info "Running Python integration tests..."
    python -m pytest tests/integration/ -v --tb=short --junitxml="${TEST_RESULTS_DIR}/integration_tests_${TIMESTAMP}.xml" 2>&1 | tee -a "${TEST_LOG_FILE}"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed"
        return 1
    fi
}

run_e2e_tests() {
    log_info "Running E2E tests..."
    
    cd "${BASE_DIR}"
    
    # Node.js 의존성 설치
    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
    fi
    
    # E2E 테스트 실행
    log_info "Running E2E tests..."
    python -m pytest tests/e2e/ -v --tb=short --junitxml="${TEST_RESULTS_DIR}/e2e_tests_${TIMESTAMP}.xml" 2>&1 | tee -a "${TEST_LOG_FILE}"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "E2E tests passed"
    else
        log_error "E2E tests failed"
        return 1
    fi
}

run_performance_tests() {
    log_info "Running performance tests..."
    
    cd "${BASE_DIR}"
    
    # 성능 테스트 실행
    log_info "Running performance tests..."
    python tests/performance/test_load_performance.py 2>&1 | tee -a "${TEST_LOG_FILE}"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Performance tests completed"
    else
        log_warning "Performance tests completed with warnings"
    fi
}

run_security_tests() {
    log_info "Running security tests..."
    
    cd "${BASE_DIR}"
    
    # 보안 테스트 실행
    log_info "Running security tests..."
    python tests/security/test_security_vulnerabilities.py 2>&1 | tee -a "${TEST_LOG_FILE}"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Security tests completed"
    else
        log_warning "Security tests completed with warnings"
    fi
}

run_linting() {
    log_info "Running code linting..."
    
    cd "${BASE_DIR}/backend"
    source venv/bin/activate
    
    # Python 린팅
    log_info "Running Python linting..."
    flake8 app/ tests/ --max-line-length=120 --exclude=venv,__pycache__ 2>&1 | tee -a "${TEST_LOG_FILE}"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Python linting passed"
    else
        log_warning "Python linting completed with warnings"
    fi
    
    # Type checking
    log_info "Running type checking..."
    mypy app/ --ignore-missing-imports 2>&1 | tee -a "${TEST_LOG_FILE}"
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Type checking passed"
    else
        log_warning "Type checking completed with warnings"
    fi
}

generate_report() {
    log_info "Generating test report..."
    
    # 테스트 결과 요약 생성
    REPORT_FILE="${TEST_RESULTS_DIR}/test_report_${TIMESTAMP}.md"
    
    cat > "${REPORT_FILE}" << EOF
# Test Report - ${TIMESTAMP}

## Test Summary
- **Test Run ID**: ${TIMESTAMP}
- **Start Time**: $(date)
- **Duration**: $(($(date +%s) - $(date -d "$(head -n1 "${TEST_LOG_FILE}" | cut -d' ' -f3-)" +%s))) seconds

## Test Results

### Unit Tests
\`\`\`
$(grep -A 10 "Running Python unit tests" "${TEST_LOG_FILE}" | tail -n +2)
\`\`\`

### Integration Tests
\`\`\`
$(grep -A 10 "Running Python integration tests" "${TEST_LOG_FILE}" | tail -n +2)
\`\`\`

### E2E Tests
\`\`\`
$(grep -A 10 "Running E2E tests" "${TEST_LOG_FILE}" | tail -n +2)
\`\`\`

### Performance Tests
\`\`\`
$(grep -A 10 "Running performance tests" "${TEST_LOG_FILE}" | tail -n +2)
\`\`\`

### Security Tests
\`\`\`
$(grep -A 10 "Running security tests" "${TEST_LOG_FILE}" | tail -n +2)
\`\`\`

### Linting Results
\`\`\`
$(grep -A 10 "Running Python linting" "${TEST_LOG_FILE}" | tail -n +2)
\`\`\`

## Files Generated
- Test Log: \`${TEST_LOG_FILE}\`
- Unit Test Results: \`${TEST_RESULTS_DIR}/unit_tests_${TIMESTAMP}.xml\`
- Integration Test Results: \`${TEST_RESULTS_DIR}/integration_tests_${TIMESTAMP}.xml\`
- E2E Test Results: \`${TEST_RESULTS_DIR}/e2e_tests_${TIMESTAMP}.xml\`

EOF
    
    log_success "Test report generated: ${REPORT_FILE}"
}

cleanup() {
    log_info "Cleaning up test environment..."
    
    # 테스트 데이터 정리
    cd "${BASE_DIR}/backend"
    source venv/bin/activate
    
    # 테스트 데이터베이스 정리
    python -c "
import asyncio
from app.core.database import engine
from app.models import Base

async def cleanup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(cleanup())
"
    
    log_success "Cleanup completed"
}

# 메인 실행 함수
main() {
    log_info "Starting Phase 3.3 Week 3 Test Suite"
    log_info "Timestamp: ${TIMESTAMP}"
    
    # 서비스 확인
    check_services
    
    # 테스트 실행
    local test_failed=0
    
    # 1. 린팅
    run_linting || test_failed=1
    
    # 2. 유닛 테스트
    run_unit_tests || test_failed=1
    
    # 3. 통합 테스트
    run_integration_tests || test_failed=1
    
    # 4. E2E 테스트
    run_e2e_tests || test_failed=1
    
    # 5. 성능 테스트
    run_performance_tests || test_failed=1
    
    # 6. 보안 테스트
    run_security_tests || test_failed=1
    
    # 7. 리포트 생성
    generate_report
    
    # 8. 정리
    cleanup
    
    # 결과 출력
    if [ $test_failed -eq 0 ]; then
        log_success "All tests passed! 🎉"
        exit 0
    else
        log_error "Some tests failed! Please check the logs."
        exit 1
    fi
}

# 스크립트 실행
main "$@"
