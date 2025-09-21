# Phase 2 인프라 설정 명세서

## 개요
**작성자**: AI Agent - DevOps Engineer  
**작성일**: 2024년 12월 19일  
**버전**: 1.0  
**상태**: 🚧 설계 중

## 목적
Phase 2 개인형 구독 서비스를 위한 확장 가능하고 안정적인 인프라를 구축하여, 고가용성과 성능을 보장합니다.

## 인프라 아키텍처

### 전체 아키텍처
```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 2 Infrastructure                   │
├─────────────────────────────────────────────────────────────┤
│  Load Balancer (ALB)                                       │
│  ├─ SSL Termination                                        │
│  ├─ Health Checks                                          │
│  └─ Auto Scaling                                           │
├─────────────────────────────────────────────────────────────┤
│  Application Layer (ECS Fargate)                           │
│  ├─ Frontend (React)                                       │
│  ├─ Backend API (FastAPI)                                  │
│  └─ Background Jobs (Celery)                               │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                │
│  ├─ PostgreSQL (RDS)                                       │
│  ├─ Redis (ElastiCache)                                    │
│  └─ S3 (File Storage)                                      │
├─────────────────────────────────────────────────────────────┤
│  External Services                                         │
│  ├─ Binance API                                            │
│  ├─ Stripe API                                             │
│  ├─ SendGrid API                                           │
│  └─ Twilio API                                             │
├─────────────────────────────────────────────────────────────┤
│  Monitoring & Logging                                      │
│  ├─ CloudWatch                                             │
│  ├─ Prometheus + Grafana                                   │
│  └─ ELK Stack                                              │
└─────────────────────────────────────────────────────────────┘
```

## 클라우드 인프라 (AWS)

### 1. 컴퓨팅 서비스

#### Amazon ECS Fargate
```yaml
# ECS Cluster 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: ecs-cluster-config
data:
  cluster_name: "crypto-trading-cluster"
  capacity_providers: "FARGATE,FARGATE_SPOT"
  default_capacity_provider_strategy: |
    - capacity_provider: "FARGATE"
      weight: 1
    - capacity_provider: "FARGATE_SPOT"
      weight: 1
```

#### ECS 서비스 정의
```yaml
# Frontend Service
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
---
# Backend Service
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### 2. 데이터베이스 서비스

#### Amazon RDS PostgreSQL
```yaml
# RDS 인스턴스 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: rds-config
data:
  engine: "postgres"
  engine_version: "14.7"
  instance_class: "db.t3.medium"
  allocated_storage: "100"
  max_allocated_storage: "1000"
  storage_encrypted: "true"
  backup_retention_period: "7"
  multi_az: "true"
  publicly_accessible: "false"
  vpc_security_group_ids: "sg-xxxxxxxxx"
  db_subnet_group_name: "crypto-trading-db-subnet-group"
```

#### Amazon ElastiCache Redis
```yaml
# Redis 클러스터 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
data:
  engine: "redis"
  engine_version: "7.0"
  node_type: "cache.t3.micro"
  num_cache_nodes: "2"
  parameter_group_name: "default.redis7"
  port: "6379"
  subnet_group_name: "crypto-trading-redis-subnet-group"
  security_group_ids: "sg-xxxxxxxxx"
```

### 3. 스토리지 서비스

#### Amazon S3
```yaml
# S3 버킷 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: s3-config
data:
  bucket_name: "crypto-trading-storage"
  region: "ap-northeast-2"
  versioning: "Enabled"
  encryption: "AES256"
  public_access_block: "true"
  cors_configuration: |
    - AllowedHeaders: ["*"]
      AllowedMethods: ["GET", "PUT", "POST", "DELETE"]
      AllowedOrigins: ["https://crypto-trading.com"]
      MaxAgeSeconds: 3000
```

### 4. 네트워킹

#### VPC 설정
```yaml
# VPC 구성
apiVersion: v1
kind: ConfigMap
metadata:
  name: vpc-config
data:
  vpc_cidr: "10.0.0.0/16"
  availability_zones: "ap-northeast-2a,ap-northeast-2c"
  public_subnets: "10.0.1.0/24,10.0.2.0/24"
  private_subnets: "10.0.11.0/24,10.0.12.0/24"
  database_subnets: "10.0.21.0/24,10.0.22.0/24"
```

#### 보안 그룹
```yaml
# Application Security Group
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-groups
data:
  frontend_sg: |
    - Type: "ingress"
      FromPort: 80
      ToPort: 80
      Protocol: "tcp"
      Source: "0.0.0.0/0"
    - Type: "ingress"
      FromPort: 443
      ToPort: 443
      Protocol: "tcp"
      Source: "0.0.0.0/0"
  backend_sg: |
    - Type: "ingress"
      FromPort: 8000
      ToPort: 8000
      Protocol: "tcp"
      Source: "sg-frontend"
  database_sg: |
    - Type: "ingress"
      FromPort: 5432
      ToPort: 5432
      Protocol: "tcp"
      Source: "sg-backend"
```

## 컨테이너화

### 1. Docker 설정

#### Frontend Dockerfile
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Backend Dockerfile
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

#### 개발 환경
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/crypto_trading
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=crypto_trading
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

#### 프로덕션 환경
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=https://api.crypto-trading.com

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - frontend
      - backend
```

## CI/CD 파이프라인

### 1. GitHub Actions

#### Frontend CI/CD
```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD

on:
  push:
    branches: [main, develop]
    paths: ['frontend/**']
  pull_request:
    branches: [main]
    paths: ['frontend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
      
      - name: Run linting
        run: |
          cd frontend
          npm run lint
      
      - name: Build
        run: |
          cd frontend
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster crypto-trading-cluster \
            --service frontend-service \
            --force-new-deployment
```

#### Backend CI/CD
```yaml
# .github/workflows/backend.yml
name: Backend CI/CD

on:
  push:
    branches: [main, develop]
    paths: ['backend/**']
  pull_request:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster crypto-trading-cluster \
            --service backend-service \
            --force-new-deployment
```

### 2. 배포 전략

#### Blue-Green 배포
```yaml
# Blue-Green 배포 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: blue-green-deployment
data:
  strategy: "blue-green"
  blue_service: "crypto-trading-blue"
  green_service: "crypto-trading-green"
  load_balancer: "crypto-trading-alb"
  health_check_path: "/health"
  rollback_timeout: "300"
```

#### Canary 배포
```yaml
# Canary 배포 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: canary-deployment
data:
  strategy: "canary"
  canary_percentage: "10"
  canary_duration: "300"
  success_threshold: "95"
  failure_threshold: "5"
```

## 모니터링 및 로깅

### 1. CloudWatch 설정

#### 로그 그룹
```yaml
# CloudWatch Log Groups
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudwatch-logs
data:
  frontend_log_group: "/aws/ecs/crypto-trading/frontend"
  backend_log_group: "/aws/ecs/crypto-trading/backend"
  retention_days: "30"
  log_stream_prefix: "crypto-trading"
```

#### 메트릭 알림
```yaml
# CloudWatch Alarms
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudwatch-alarms
data:
  high_cpu_alarm: |
    - AlarmName: "HighCPUUtilization"
      MetricName: "CPUUtilization"
      Namespace: "AWS/ECS"
      Statistic: "Average"
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: "GreaterThanThreshold"
  
  high_memory_alarm: |
    - AlarmName: "HighMemoryUtilization"
      MetricName: "MemoryUtilization"
      Namespace: "AWS/ECS"
      Statistic: "Average"
      Period: 300
      EvaluationPeriods: 2
      Threshold: 85
      ComparisonOperator: "GreaterThanThreshold"
```

### 2. Prometheus + Grafana

#### Prometheus 설정
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'crypto-trading-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'crypto-trading-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 5s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Grafana 대시보드
```json
{
  "dashboard": {
    "title": "Crypto Trading System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ]
  }
}
```

### 3. ELK Stack

#### Elasticsearch 설정
```yaml
# elasticsearch.yml
cluster.name: crypto-trading-cluster
node.name: crypto-trading-node-1
network.host: 0.0.0.0
discovery.type: single-node
xpack.security.enabled: false
```

#### Logstash 설정
```yaml
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "backend" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "crypto-trading-%{+YYYY.MM.dd}"
  }
}
```

## 보안 설정

### 1. SSL/TLS 인증서

#### Let's Encrypt 자동 갱신
```yaml
# certbot 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: certbot-config
data:
  email: "admin@crypto-trading.com"
  domains: "crypto-trading.com,api.crypto-trading.com"
  renew_cron: "0 12 * * *"
```

### 2. 보안 그룹 및 네트워크 ACL

#### 네트워크 보안
```yaml
# Network ACL 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: network-security
data:
  public_nacl: |
    - RuleNumber: 100
      Protocol: "tcp"
      RuleAction: "allow"
      PortRange: "80,443"
      CidrBlock: "0.0.0.0/0"
  
  private_nacl: |
    - RuleNumber: 100
      Protocol: "tcp"
      RuleAction: "allow"
      PortRange: "5432"
      CidrBlock: "10.0.0.0/16"
```

### 3. 시크릿 관리

#### AWS Secrets Manager
```yaml
# 시크릿 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: secrets-config
data:
  database_secret: "crypto-trading/database"
  stripe_secret: "crypto-trading/stripe"
  jwt_secret: "crypto-trading/jwt"
  api_keys_secret: "crypto-trading/api-keys"
```

## 자동 스케일링

### 1. ECS Auto Scaling

#### Target Tracking Scaling
```yaml
# Auto Scaling 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: autoscaling-config
data:
  frontend_scaling: |
    - MetricType: "ECSServiceAverageCPUUtilization"
      TargetValue: 70
      ScaleOutCooldown: 300
      ScaleInCooldown: 300
      MinCapacity: 2
      MaxCapacity: 10
  
  backend_scaling: |
    - MetricType: "ECSServiceAverageCPUUtilization"
      TargetValue: 70
      ScaleOutCooldown: 300
      ScaleInCooldown: 300
      MinCapacity: 2
      MaxCapacity: 20
```

### 2. 데이터베이스 스케일링

#### RDS Auto Scaling
```yaml
# RDS Auto Scaling 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: rds-autoscaling
data:
  storage_autoscaling: |
    - MinStorageSize: 100
      MaxStorageSize: 1000
      TargetValue: 70
      ScaleInCooldown: 300
      ScaleOutCooldown: 300
```

## 재해 복구

### 1. 백업 전략

#### 데이터베이스 백업
```yaml
# 백업 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: backup-config
data:
  rds_backup: |
    - BackupRetentionPeriod: 7
      PreferredBackupWindow: "03:00-04:00"
      PreferredMaintenanceWindow: "sun:04:00-sun:05:00"
      MultiAZ: true
      StorageEncrypted: true
  
  s3_backup: |
    - LifecycleConfiguration:
        - Status: "Enabled"
          Transitions:
            - Days: 30
              StorageClass: "STANDARD_IA"
            - Days: 90
              StorageClass: "GLACIER"
```

### 2. 재해 복구 계획

#### RTO/RPO 목표
- **RTO (Recovery Time Objective)**: 4시간
- **RPO (Recovery Point Objective)**: 1시간
- **백업 주기**: 일일 백업
- **복구 테스트**: 월간 실행

## 비용 최적화

### 1. 리소스 최적화

#### 인스턴스 타입 최적화
```yaml
# 비용 최적화 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: cost-optimization
data:
  instance_types: |
    - Development: "t3.micro"
    - Staging: "t3.small"
    - Production: "t3.medium"
  
  spot_instances: |
    - Enabled: true
      MaxPrice: "0.05"
      InstanceTypes: ["t3.medium", "t3.large"]
```

### 2. 모니터링 및 알림

#### 비용 알림
```yaml
# 비용 알림 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: cost-alerts
data:
  monthly_budget: "1000"
  alert_thresholds: |
    - 50%: "warning"
    - 80%: "critical"
    - 100%: "emergency"
```

## 다음 단계

### 1. 즉시 실행
- [ ] AWS 인프라 구축
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인 설정
- [ ] 모니터링 시스템 구축

### 2. 단기 목표 (1주일)
- [ ] 개발/스테이징 환경 구축
- [ ] 자동 배포 파이프라인 완성
- [ ] 기본 모니터링 설정
- [ ] 보안 설정 완료

### 3. 중기 목표 (2주일)
- [ ] 프로덕션 환경 구축
- [ ] 고급 모니터링 설정
- [ ] 자동 스케일링 구현
- [ ] 재해 복구 계획 수립

## 결론

이 인프라 설정 명세서는 Phase 2 개인형 구독 서비스를 위한 확장 가능하고 안정적인 클라우드 인프라를 구축하기 위한 완전한 가이드입니다. AWS 기반의 마이크로서비스 아키텍처를 통해 고가용성, 성능, 보안을 모두 고려한 현대적인 인프라를 제공합니다.
