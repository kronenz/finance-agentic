# 로컬 Docker 환경 배포 명령어

## 🚀 빠른 시작

### 1. 전체 시스템 배포 (개발 환경)
```bash
# 개발 환경으로 전체 시스템 배포
./scripts/deploy.sh development

# 또는 직접 docker-compose 사용
docker-compose -f docker-compose.dev.yml up -d --build
```

### 2. 프로덕션 환경 배포
```bash
# 프로덕션 환경으로 배포
./scripts/deploy.sh production

# 또는 직접 docker-compose 사용
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3. 기본 환경 배포 (모든 서비스 포함)
```bash
# 기본 docker-compose.yml 사용 (모든 서비스)
docker-compose up -d --build
```

## 📋 개별 서비스 배포

### 백엔드만 배포
```bash
# 개발 환경 백엔드
docker-compose -f docker-compose.dev.yml up backend -d --build

# 프로덕션 환경 백엔드
docker-compose up backend -d --build
```

### 프론트엔드만 배포
```bash
# 개발 환경 프론트엔드
docker-compose -f docker-compose.dev.yml up frontend -d --build

# 프로덕션 환경 프론트엔드
docker-compose up frontend -d --build
```

### 데이터베이스만 배포
```bash
# PostgreSQL + Redis
docker-compose up postgres redis -d
```

### 모니터링 스택만 배포
```bash
# Prometheus + Grafana + Elasticsearch + Kibana
docker-compose up prometheus grafana elasticsearch kibana -d
```

## 🔧 유용한 명령어

### 서비스 상태 확인
```bash
# 모든 서비스 상태
docker-compose ps

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 서비스 재시작
```bash
# 특정 서비스 재시작
docker-compose restart backend

# 모든 서비스 재시작
docker-compose restart
```

### 서비스 중지 및 정리
```bash
# 서비스 중지
docker-compose down

# 볼륨까지 삭제 (데이터 손실 주의!)
docker-compose down -v

# 이미지까지 삭제
docker-compose down --rmi all
```

### 데이터베이스 마이그레이션
```bash
# 백엔드가 실행된 후 마이그레이션 실행
docker-compose exec backend alembic upgrade head
```

## 🌐 접속 URL

배포 완료 후 다음 URL로 접속 가능:

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

## 🐛 문제 해결

### 포트 충돌 해결
```bash
# 사용 중인 포트 확인
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# 프로세스 종료
sudo kill -9 <PID>
```

### 컨테이너 재빌드
```bash
# 캐시 없이 재빌드
docker-compose build --no-cache

# 특정 서비스만 재빌드
docker-compose build --no-cache backend
```

### 로그 확인
```bash
# 실시간 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 볼륨 정리
```bash
# 사용하지 않는 볼륨 삭제
docker volume prune

# 모든 볼륨 삭제 (주의!)
docker volume rm $(docker volume ls -q)
```

## 📝 환경별 설정

### 개발 환경 (docker-compose.dev.yml)
- 핫 리로딩 활성화
- 디버그 모드
- 개발용 데이터베이스 포트 (5433, 6380)

### 프로덕션 환경 (docker-compose.prod.yml)
- 최적화된 빌드
- 보안 설정
- 리소스 제한

### 기본 환경 (docker-compose.yml)
- 모든 서비스 포함
- 모니터링 스택 포함
- 프로덕션 준비 상태
