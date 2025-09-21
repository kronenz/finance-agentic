# 프로젝트 전체 인덱스

## 프로젝트 개요
**프로젝트명**: Agentic AI 기반 암호화폐 자동화 거래 시스템  
**개발 방법론**: Spec Driven Development  
**팀 구성**: 9개 AI 에이전트 + 인간 관리자  
**현재 단계**: Phase 1 (최소 기능 구현) 완료, Phase 2 (개인형 구독 서비스) 진행 중

## 프로젝트 구조

### 📁 소스 코드 (`src/`)
```
src/
├── core/                    # 핵심 유틸리티
│   ├── config.py           # 설정 관리 (Pydantic 기반)
│   ├── logger.py           # 로깅 시스템 (Rich 라이브러리)
│   └── database.py         # 데이터베이스 (SQLAlchemy + SQLite)
├── data/                   # 데이터 처리
│   ├── market_data.py      # Binance API 연동
│   └── indicators.py       # 기술적 지표 (TA-Lib)
├── strategies/             # 거래 전략
│   ├── base_strategy.py    # 전략 인터페이스
│   ├── supertrend.py       # 슈퍼트렌드 전략
│   └── rsi_mean_reversion.py # RSI 평균회귀 전략
└── main.py                 # 메인 실행 파일
```

### 📁 설정 파일 (`config/`)
```
config/
└── config.yaml            # 시스템 설정 (YAML)
```

### 📁 문서 (`docs/`)
```
docs/
├── GETTING_STARTED.md      # 시작하기 가이드
├── specs/                  # 기능 명세서
│   └── phase1_minimal_trading.md
├── team/                   # 팀 협업 가이드
│   ├── TEAM_STRUCTURE.md
│   ├── COMMUNICATION_PROTOCOL.md
│   ├── SPEC_DRIVEN_WORKFLOW.md
│   ├── TEAM_COLLABORATION_GUIDE.md
│   ├── roles/              # 역할별 명세서
│   │   ├── ARCHITECT_SPEC.md
│   │   ├── STRATEGY_DEVELOPER_SPEC.md
│   │   ├── DATA_ENGINEER_SPEC.md
│   │   ├── AI_ML_ENGINEER_SPEC.md
│   │   ├── DEVOPS_ENGINEER_SPEC.md
│   │   ├── QA_ENGINEER_SPEC.md
│   │   └── PRODUCT_MANAGER_SPEC.md
│   └── templates/          # 템플릿 모음
│       ├── MEETING_TEMPLATES.md
│       ├── DOCUMENT_TEMPLATES.md
│       └── CHECKLISTS.md
└── human_manager/          # 인간 관리자 가이드
    ├── HUMAN_MANAGER_GUIDE.md
    ├── SERVICE_IMPLEMENTATION_GUIDE.md
    └── PRACTICAL_CHECKLISTS.md
```

### 📁 스크립트 (`scripts/`)
```
scripts/
├── setup.sh               # 환경 설정 스크립트
└── deploy.sh              # 배포 스크립트
```

## 핵심 기능

### 1. 자동화 거래 시스템 (Phase 1)
- **거래소 연동**: Binance Futures API
- **기술적 지표**: 슈퍼트렌드, RSI, 이동평균선
- **거래 전략**: 
  - 전략 A: 슈퍼트렌드 기반 추세추종
  - 전략 C: RSI 기반 평균회귀
- **리스크 관리**: 포지션 크기, 손절매, 익절
- **데이터베이스**: SQLite 기반 거래 기록 저장

### 2. 팀 협업 체계
- **9개 AI 에이전트 역할**:
  - 시스템 아키텍트: 전체 시스템 설계
  - 전략 개발자: 거래 전략 개발
  - 데이터 엔지니어: 데이터 파이프라인
  - AI/ML 엔지니어: 머신러닝 모델
  - DevOps 엔지니어: 인프라 및 배포
  - QA 엔지니어: 테스트 및 품질보증
  - 프로덕트 매니저: 제품 요구사항 관리
  - 프론트엔드 개발자: 사용자 인터페이스 개발
  - UI/UX 디자이너: 사용자 경험 설계

### 3. Spec Driven Development
- **명세서 우선 개발**: 모든 작업은 명세서 작성부터 시작
- **6단계 워크플로우**: 명세서 작성 → 검토 → 개발 → 검증 → 배포 → 운영
- **품질 게이트**: 각 단계별 품질 기준 설정
- **협업 프로토콜**: 역할별 의사소통 규칙

### 4. 개인형 구독 서비스 (Phase 2)
- **구독 모델**: Basic, Premium, Pro 3단계 플랜
- **사용자 인증**: JWT 기반 안전한 인증 시스템
- **개인화 대시보드**: 사용자별 맞춤형 인터페이스
- **실시간 모니터링**: 거래 성과 및 시장 상황 실시간 표시
- **알림 시스템**: 이메일, SMS, 푸시 알림

### 5. 인간 관리자 지원 시스템
- **통합 대시보드**: 실시간 모니터링 + 의사결정 지원
- **AI 에이전트 관리**: 성과 추적, 설정 제어
- **품질 관리**: 자동 검사, 보고서 생성
- **의사결정 지원**: 데이터 분석, 시나리오 시뮬레이션

## 기술 스택

### 백엔드
- **언어**: Python 3.9+
- **프레임워크**: FastAPI (예정)
- **데이터베이스**: SQLite → PostgreSQL (확장)
- **ORM**: SQLAlchemy
- **API**: Binance Futures API

### 데이터 분석
- **라이브러리**: Pandas, NumPy
- **기술적 지표**: TA-Lib
- **시각화**: Matplotlib, Plotly (예정)

### 인프라
- **컨테이너**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **모니터링**: Prometheus, Grafana (예정)
- **로깅**: Rich 라이브러리

### 프론트엔드
- **프레임워크**: React 18+ with TypeScript
- **상태관리**: Redux Toolkit
- **라우팅**: React Router v6
- **스타일링**: Styled-components + Tailwind CSS
- **차트**: Recharts + D3.js
- **UI 라이브러리**: Ant Design
- **테스트**: Jest + React Testing Library + Cypress

## 주요 파일 설명

### 핵심 소스 파일
| 파일 | 설명 | 주요 기능 |
|------|------|-----------|
| `src/main.py` | 메인 실행 파일 | 트레이딩 봇 오케스트레이션 |
| `src/core/config.py` | 설정 관리 | Pydantic 기반 설정 로딩 |
| `src/core/logger.py` | 로깅 시스템 | Rich 기반 콘솔 로깅 |
| `src/core/database.py` | 데이터베이스 | SQLAlchemy 모델 정의 |
| `src/data/market_data.py` | 시장 데이터 | Binance API 연동 |
| `src/data/indicators.py` | 기술적 지표 | TA-Lib 기반 지표 계산 |
| `src/strategies/base_strategy.py` | 전략 인터페이스 | 추상 기본 클래스 |
| `src/strategies/supertrend.py` | 슈퍼트렌드 전략 | 추세추종 전략 구현 |
| `src/strategies/rsi_mean_reversion.py` | RSI 전략 | 평균회귀 전략 구현 |

### 설정 파일
| 파일 | 설명 | 주요 설정 |
|------|------|-----------|
| `config/config.yaml` | 시스템 설정 | API 키, 거래 파라미터, 전략 설정 |
| `requirements.txt` | Python 의존성 | 필요한 패키지 목록 |
| `env.example` | 환경변수 예시 | API 키 설정 가이드 |

### 문서 파일
| 파일 | 설명 | 주요 내용 |
|------|------|-----------|
| `docs/GETTING_STARTED.md` | 시작 가이드 | 설치 및 실행 방법 |
| `docs/specs/phase1_minimal_trading.md` | Phase 1 명세서 | 최소 기능 요구사항 |
| `docs/team/TEAM_STRUCTURE.md` | 팀 구조 | 7개 역할 정의 |
| `docs/team/COMMUNICATION_PROTOCOL.md` | 의사소통 규칙 | 협업 프로토콜 |
| `docs/team/SPEC_DRIVEN_WORKFLOW.md` | SDD 워크플로우 | 6단계 개발 프로세스 |
| `docs/human_manager/HUMAN_MANAGER_GUIDE.md` | 관리자 가이드 | 인간 관리자 역할 |

### 템플릿 파일
| 파일 | 설명 | 주요 템플릿 |
|------|------|-----------|
| `docs/team/templates/MEETING_TEMPLATES.md` | 회의 템플릿 | 5가지 회의 유형 |
| `docs/team/templates/DOCUMENT_TEMPLATES.md` | 문서 템플릿 | 5가지 문서 유형 |
| `docs/team/templates/CHECKLISTS.md` | 체크리스트 | 8가지 업무 영역 |
| `docs/human_manager/PRACTICAL_CHECKLISTS.md` | 실무 체크리스트 | 일일/주간/월간 체크 |

## 개발 상태

### ✅ 완료된 기능
- [x] Phase 1 기본 자동화 거래 시스템
- [x] 팀 구조 및 역할 정의 (9개 역할)
- [x] Spec Driven Development 워크플로우
- [x] 의사소통 프로토콜
- [x] 인간 관리자 가이드
- [x] 서비스 구현 방안
- [x] 실무 체크리스트 및 템플릿
- [x] Phase 2 개인형 구독 서비스 명세서

### 🚧 진행 중인 작업
- [ ] Phase 2: 개인형 구독 서비스 개발
- [ ] 사용자 인증 시스템 구축
- [ ] 프론트엔드 개발 환경 구축
- [ ] UI/UX 디자인 시스템 구축

### 📋 예정된 작업
- [ ] Phase 3: 시장 국면 감지
- [ ] Phase 4: 적응형 전략 전환
- [ ] Phase 5: 고급 AI 기능
- [ ] Phase 6: 모바일 앱 개발

## 사용 방법

### 1. 프로젝트 시작
```bash
# 환경 설정
./scripts/setup.sh

# 환경변수 설정
cp env.example .env
# .env 파일에 API 키 입력

# 실행
python src/main.py
```

### 2. Docker 실행
```bash
# Docker Compose로 실행
docker-compose up --build -d

# 로그 확인
docker-compose logs -f trading_bot
```

### 3. 개발 참여
1. **역할 선택**: `docs/team/roles/` 에서 해당 역할 명세서 확인
2. **워크플로우**: `docs/team/SPEC_DRIVEN_WORKFLOW.md` 참조
3. **협업**: `docs/team/COMMUNICATION_PROTOCOL.md` 준수
4. **템플릿**: `docs/team/templates/` 활용

### 4. 관리자 가이드
1. **기본 가이드**: `docs/human_manager/HUMAN_MANAGER_GUIDE.md`
2. **서비스 구현**: `docs/human_manager/SERVICE_IMPLEMENTATION_GUIDE.md`
3. **실무 체크리스트**: `docs/human_manager/PRACTICAL_CHECKLISTS.md`

## 브랜치 전략

### 브랜치 구조
- **`prod`**: 프로덕션 환경 (안정화된 코드)
- **`stage`**: 스테이징 환경 (테스트 완료된 코드)
- **`dev`**: 개발 환경 (개발 중인 코드)

### 배포 프로세스
1. **개발**: `dev` 브랜치에서 개발
2. **테스트**: `stage` 브랜치에서 테스트
3. **배포**: `prod` 브랜치로 배포

## 성과 지표

### 시스템 KPI
- **가용성**: 99.9% 이상
- **응답시간**: 평균 100ms 이하
- **거래 성과**: 월간 5% 이상 수익률
- **품질**: 테스트 커버리지 90% 이상

### 팀 KPI
- **개발 속도**: 스프린트 완료율 90% 이상
- **품질**: 버그율 1% 이하
- **협업**: 팀 만족도 4.5/5.0 이상
- **학습**: 월간 개선사항 10개 이상

## 연락처 및 지원

### 문서 참조
- **전체 가이드**: `docs/GETTING_STARTED.md`
- **팀 협업**: `docs/team/TEAM_COLLABORATION_GUIDE.md`
- **관리자 가이드**: `docs/human_manager/HUMAN_MANAGER_GUIDE.md`

### 문제 해결
- **설치 문제**: `docs/GETTING_STARTED.md` 참조
- **개발 문제**: 해당 역할 명세서 참조
- **협업 문제**: `docs/team/COMMUNICATION_PROTOCOL.md` 참조

---

**마지막 업데이트**: 2024년 12월 19일  
**버전**: 1.0.0  
**상태**: Phase 1 완료, 팀 협업 체계 구축 완료
