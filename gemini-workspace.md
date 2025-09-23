# Gemini CLI 협동 워크스페이스

## 프로젝트 개요
이 워크스페이스는 Gemini CLI와 협동하여 암호화폐 거래 플랫폼을 개발하는 공간입니다.

## 현재 프로젝트 상태
- **Phase 1**: 기본 거래 시스템 (완료)
- **Phase 2**: AI 통합 및 구독 서비스 (85% 완료)
- **현재 브랜치**: `prod`

## 주요 컴포넌트

### 백엔드 (FastAPI)
- 위치: `./backend/`
- 주요 기능: 사용자 인증, 구독 관리, API 엔드포인트
- 상태: 개발 중 (일부 API 오류 있음)

### 프론트엔드 (React + TypeScript)
- 위치: `./frontend/`
- 주요 기능: 사용자 인터페이스, 대시보드, 인증 폼
- 상태: 개발 중

### AI 모듈
- 위치: `./src/ai/`
- 주요 기능: 거래 전략, 시장 분석
- 상태: Phase 1에서 구현됨

## 현재 이슈
1. **인증 시스템 오류**: 백엔드 API에서 필드명 불일치 (first_name vs firstName)
2. **비밀번호 검증**: 대문자 요구사항 추가 필요
3. **백엔드 헬스체크**: unhealthy 상태

## Gemini CLI 협동 포인트

### 1. 코드 리뷰 및 최적화
```bash
# 특정 파일 리뷰 요청
gemini "backend/app/api/v1/auth.py 파일을 리뷰하고 개선점을 제안해줘"
```

### 2. 버그 수정
```bash
# 인증 API 오류 수정
gemini "사용자 등록 API에서 first_name 필드 오류를 수정해줘"
```

### 3. 테스트 코드 작성
```bash
# 인증 서비스 테스트 작성
gemini "AuthService 클래스에 대한 포괄적인 테스트 코드를 작성해줘"
```

### 4. 문서화 개선
```bash
# API 문서 개선
gemini "FastAPI 엔드포인트에 대한 상세한 문서를 작성해줘"
```

## 협동 워크플로우

### 1. 문제 식별
- 현재 이슈를 Gemini CLI에 설명
- 관련 파일들을 컨텍스트로 제공

### 2. 해결책 제안
- Gemini CLI가 문제 분석 및 해결책 제안
- 코드 수정안 검토

### 3. 구현 및 테스트
- 제안된 해결책 구현
- 테스트 실행 및 검증

### 4. 문서화
- 변경사항 문서화
- 다음 단계 계획 수립

## 유용한 명령어

### 프로젝트 상태 확인
```bash
# Docker 컨테이너 상태
docker-compose ps

# 백엔드 로그 확인
docker-compose logs backend

# 프론트엔드 빌드
cd frontend && npm run build
```

### 개발 서버 실행
```bash
# 전체 서비스 실행
docker-compose up -d

# 개발 모드 실행
docker-compose -f docker-compose.dev.yml up -d
```

### 테스트 실행
```bash
# 백엔드 테스트
cd backend && pytest

# 프론트엔드 테스트
cd frontend && npm test
```

## 다음 단계
1. 인증 시스템 오류 수정
2. 백엔드 헬스체크 문제 해결
3. 프론트엔드-백엔드 통합 테스트
4. AI 모듈 통합
5. 구독 서비스 완성

## Gemini CLI 사용 팁
- 구체적인 질문을 하세요
- 관련 파일 경로를 명시하세요
- 현재 오류 메시지를 포함하세요
- 단계별로 접근하세요
