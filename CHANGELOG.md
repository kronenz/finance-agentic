# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- **ccxt 버전 업데이트**: 4.5.5 → 4.5.6으로 업데이트하여 패키지 호환성 문제 해결
- **ta-lib 대안 제공**: 설치 어려운 ta-lib 대신 ta 패키지 사용
- **의존성 유연성 개선**: pandas, numpy 버전을 유연하게 설정 (>=)
- **불필요한 패키지 제거**: sqlite3 (Python 내장 모듈) 제거

### Changed
- **requirements.txt 최적화**: 패키지 설치 오류 해결을 위한 버전 조정
- **.gitignore 업데이트**: node_modules 및 프론트엔드 빌드 파일 제외

### Technical Details
- **ccxt 4.5.6**: 최신 안정 버전으로 업데이트
- **ta >= 0.10.2**: ta-lib의 대안으로 사용
- **pandas >= 2.1.4**: 유연한 버전 관리
- **numpy >= 1.24.3**: 유연한 버전 관리

### Installation
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

## [Previous Versions]

### [2024-09-27] - Frontend Port Change
- 프론트엔드 서버 포트를 3000에서 5000으로 변경
- Python HTTP 서버 대체 솔루션 추가 (포트 9000)
- AI 에이전트 기능 개선
- 백엔드 API 및 모니터링 강화
