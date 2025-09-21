# 빠른 참조 가이드

## 프로젝트 핵심 정보

### 프로젝트명
Agentic AI 기반 암호화폐 자동화 거래 시스템

### 현재 상태
- ✅ Phase 1 (최소 기능) 완료
- ✅ 팀 협업 체계 구축 완료 (9개 역할)
- ✅ Phase 2 명세서 완료
- 🚧 Phase 2: 개인형 구독 서비스 개발 중

### 핵심 파일 위치
| 항목 | 파일 경로 |
|------|-----------|
| **프로젝트 전체 개요** | `PROJECT_INDEX.md` |
| **시작하기** | `docs/GETTING_STARTED.md` |
| **팀 협업 가이드** | `docs/team/TEAM_COLLABORATION_GUIDE.md` |
| **관리자 가이드** | `docs/human_manager/HUMAN_MANAGER_GUIDE.md` |
| **메인 실행 파일** | `src/main.py` |
| **시스템 설정** | `config/config.yaml` |

## 빠른 시작

### 1. 환경 설정
```bash
# 환경 설정 스크립트 실행
./scripts/setup.sh

# 환경변수 설정
cp env.example .env
# .env 파일에 Binance API 키 입력
```

### 2. 실행
```bash
# Python으로 실행
python src/main.py

# Docker로 실행
docker-compose up --build -d
```

### 3. 개발 참여
1. **역할 선택**: `docs/team/roles/` 에서 해당 역할 확인
2. **워크플로우**: `docs/team/SPEC_DRIVEN_WORKFLOW.md` 참조
3. **협업**: `docs/team/COMMUNICATION_PROTOCOL.md` 준수

## 주요 기능

### 거래 시스템 (Phase 1)
- **거래소**: Binance Futures API
- **전략**: 슈퍼트렌드, RSI 평균회귀
- **지표**: TA-Lib 기반 기술적 지표
- **데이터베이스**: SQLite

### 팀 협업
- **9개 AI 에이전트**: 각각 전문 역할
- **Spec Driven Development**: 명세서 우선 개발
- **의사소통 프로토콜**: 체계적 협업 규칙

### 관리자 지원
- **통합 대시보드**: 실시간 모니터링
- **AI 에이전트 관리**: 성과 추적 및 제어
- **품질 관리**: 자동 검사 및 보고서

## 자주 사용하는 명령어

### Git 작업
```bash
# 브랜치 전환
git checkout dev/stage/prod

# 변경사항 커밋
git add .
git commit -m "feat: 새로운 기능 추가"

# 브랜치 병합
git merge dev
```

### Docker 작업
```bash
# 컨테이너 실행
docker-compose up --build -d

# 로그 확인
docker-compose logs -f trading_bot

# 컨테이너 중지
docker-compose down
```

### 개발 작업
```bash
# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 코드 실행
python src/main.py
```

## 문제 해결

### 일반적인 문제
1. **API 키 오류**: `.env` 파일 확인
2. **의존성 오류**: `pip install -r requirements.txt`
3. **Docker 오류**: `docker-compose down && docker-compose up --build -d`

### 문서 참조
- **설치 문제**: `docs/GETTING_STARTED.md`
- **개발 문제**: 해당 역할 명세서
- **협업 문제**: `docs/team/COMMUNICATION_PROTOCOL.md`
- **관리 문제**: `docs/human_manager/HUMAN_MANAGER_GUIDE.md`

## 연락처

### 문서 참조
- **전체 개요**: `PROJECT_INDEX.md`
- **팀 협업**: `docs/team/TEAM_COLLABORATION_GUIDE.md`
- **관리자**: `docs/human_manager/HUMAN_MANAGER_GUIDE.md`

### 템플릿 활용
- **회의**: `docs/team/templates/MEETING_TEMPLATES.md`
- **문서**: `docs/team/templates/DOCUMENT_TEMPLATES.md`
- **체크리스트**: `docs/team/templates/CHECKLISTS.md`
- **실무**: `docs/human_manager/PRACTICAL_CHECKLISTS.md`
