# AI 기반 암호화폐 자동화 거래 시스템

## 프로젝트 개요

본 프로젝트는 concept.md에 명시된 이론적 프레임워크를 바탕으로 한 AI 기반 암호화폐 자동화 거래 시스템입니다. Spec Driven Development 방법론을 통해 단계적으로 기능을 발전시켜 나가며, 여러 Agentic AI가 협력하여 지속적으로 시스템을 개선합니다.

## 개발 철학

- **Spec Driven Development**: 각 단계별로 명확한 명세서를 작성하고 이를 기반으로 개발
- **점진적 발전**: 최소 기능부터 시작하여 단계적으로 복잡성 증가
- **AI 협력**: 여러 Agentic AI가 Git을 통해 협력하여 시스템 발전
- **DevOps 중심**: dev/stage/prod 브랜치를 통한 체계적인 배포 관리

## 프로젝트 구조

```
finance/
├── docs/                    # 문서 및 명세서
│   ├── specs/              # 단계별 명세서
│   ├── architecture/       # 아키텍처 문서
│   └── design/             # 디자인 가이드라인
├── frontend/               # React 프론트엔드
│   ├── src/               # 소스 코드
│   │   ├── components/    # React 컴포넌트
│   │   ├── styles/        # CSS 스타일
│   │   └── services/      # API 서비스
│   └── public/            # 정적 파일
├── backend/                # FastAPI 백엔드
│   ├── app/               # 애플리케이션 코드
│   │   ├── api/           # API 엔드포인트
│   │   ├── models/        # 데이터베이스 모델
│   │   └── services/      # 비즈니스 로직
│   └── requirements.txt   # Python 의존성
├── src/                    # 레거시 소스 코드
│   ├── core/              # 핵심 로직
│   ├── strategies/        # 거래 전략
│   ├── data/              # 데이터 처리
│   └── ai/                # AI 에이전트
├── tests/                  # 테스트 코드
├── config/                 # 설정 파일
├── scripts/               # 유틸리티 스크립트
└── deployment/            # 배포 관련 파일
```

## 🎨 UI/UX 디자인 시스템

### 디자인 철학
- **Apple 홈페이지 스타일**: 깔끔하고 직관적인 사용자 경험
- **일관성**: 모든 컴포넌트에서 통일된 디자인 언어 사용
- **접근성**: 모든 사용자가 쉽게 접근할 수 있는 인터페이스
- **반응형**: 모든 디바이스에서 최적화된 경험 제공

### 주요 특징
- **색상 팔레트**: Apple의 시스템 색상을 기반으로 한 일관된 색상 체계
- **타이포그래피**: SF Pro 폰트를 사용한 명확하고 읽기 쉬운 텍스트
- **아이콘 시스템**: 12px~32px 크기의 일관된 아이콘 크기 체계
- **애니메이션**: 부드럽고 자연스러운 전환 효과
- **그림자**: 계층감을 표현하는 세련된 그림자 효과

### 디자인 가이드라인
자세한 디자인 가이드라인은 [웹 디자인 가이드라인 스펙](./docs/design/web_design_guidelines.md)을 참조하세요.

## 🛠️ 기술 스택

### Frontend
- **React 18**: 사용자 인터페이스 구축
- **TypeScript**: 타입 안전성 보장
- **Vite**: 빠른 개발 서버 및 빌드 도구
- **Redux Toolkit**: 상태 관리
- **React Router**: 클라이언트 사이드 라우팅
- **Tailwind CSS**: 유틸리티 우선 CSS 프레임워크
- **CSS3**: Apple 스타일 커스텀 스타일링

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **PostgreSQL**: 관계형 데이터베이스
- **SQLAlchemy**: ORM (Object-Relational Mapping)
- **Alembic**: 데이터베이스 마이그레이션
- **Redis**: 캐싱 및 세션 관리
- **JWT**: 인증 토큰 관리
- **Pydantic**: 데이터 검증 및 직렬화

### AI/ML
- **scikit-learn**: 머신러닝 라이브러리
- **pandas**: 데이터 분석 및 처리
- **numpy**: 수치 계산
- **python-binance**: 암호화폐 거래소 API

### DevOps & Infrastructure
- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 컨테이너 오케스트레이션
- **Nginx**: 웹 서버 및 리버스 프록시
- **Prometheus**: 메트릭 수집
- **Grafana**: 모니터링 대시보드
- **GitHub Actions**: CI/CD 파이프라인

### 개발 도구
- **ESLint**: JavaScript/TypeScript 린팅
- **Prettier**: 코드 포맷팅
- **Jest**: 테스트 프레임워크
- **pytest**: Python 테스트 프레임워크
- **Black**: Python 코드 포맷팅

## 개발 단계

### Phase 1: 기본 자동화 거래 (완료)
- 단순한 기술적 지표 기반 매매
- 기본적인 리스크 관리
- 실시간 가격 모니터링

### Phase 2: 개인형 구독 서비스 (현재 - 85% 완료)
- 사용자 인증 및 회원가입 시스템
- 구독 플랜 관리
- AI 기반 투자 추천
- 실시간 대시보드
- Apple 스타일 UI/UX 적용

### Phase 3: AI 에이전트 통합
- 머신러닝 기반 국면 분류
- 강화학습을 통한 전략 최적화
- 자가 학습 및 진화

### Phase 4: 고도화된 시장 분석
- VWAP 및 거래량 프로파일 분석
- 온체인 데이터 통합
- 다차원적 시장 심리 분석

## 브랜치 전략

- `dev`: 개발 브랜치 (기능 개발 및 테스트)
- `stage`: 스테이징 브랜치 (통합 테스트 및 검증)
- `prod`: 프로덕션 브랜치 (실제 거래 환경)

## 시작하기

1. 환경 설정: `pip install -r requirements.txt`
2. 설정 파일 구성: `config/config.yaml` 수정
3. 개발 서버 실행: `python src/main.py`

## 기여 가이드

각 AI 에이전트는 다음 규칙을 따라 기여해야 합니다:
1. 명세서를 먼저 작성하고 검토받기
2. dev 브랜치에서 기능 개발
3. 테스트 코드 작성 및 통과 확인
4. Pull Request를 통한 코드 리뷰
5. stage 브랜치에서 통합 테스트
6. prod 브랜치로의 배포 승인
