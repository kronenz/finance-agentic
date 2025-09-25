# AI 에이전트 배포 가이드

**Version**: 1.0.0  
**Date**: 2024-12-19  
**Platform**: Docker + Kubernetes

## 개요

AI 에이전트 시스템의 배포, 설정, 운영을 위한 종합 가이드입니다. Docker 컨테이너와 Kubernetes를 사용한 마이크로서비스 아키텍처를 기반으로 합니다.

## 시스템 요구사항

### 최소 요구사항

- **CPU**: 8 cores
- **Memory**: 16GB RAM
- **Storage**: 100GB SSD
- **Network**: 1Gbps

### 권장 요구사항

- **CPU**: 16 cores
- **Memory**: 32GB RAM
- **Storage**: 500GB NVMe SSD
- **Network**: 10Gbps

### 소프트웨어 요구사항

- Docker 20.10+
- Kubernetes 1.21+
- Redis 6.0+
- PostgreSQL 13+
- Python 3.9+

## 아키텍처 개요

### 컨테이너 구성

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Meta-     │  │   Market    │  │    VWAP     │        │
│  │ Controller  │  │   Regime    │  │  Analyzer   │        │
│  │             │  │  Detector   │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Volume    │  │    Risk     │  │      RL     │        │
│  │   Profile   │  │   Manager   │  │  Optimizer  │        │
│  │  Analyzer   │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Genetic   │  │   Trading   │  │   Market    │        │
│  │ Algorithm   │  │   Engine    │  │   Data      │        │
│  │             │  │             │  │ Processor   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Docker 설정

### 1. 기본 Dockerfile

```dockerfile
FROM python:3.9-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 실행 명령
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 에이전트별 Dockerfile

```dockerfile
# AI 에이전트 전용 Dockerfile
FROM python:3.9-slim

WORKDIR /app

# AI/ML 라이브러리 설치
COPY requirements-ai.txt .
RUN pip install --no-cache-dir -r requirements-ai.txt

# 에이전트 코드 복사
COPY app/ai/ ./app/ai/
COPY app/core/ ./app/core/

# 에이전트 실행
CMD ["python", "-m", "app.ai.agent_runner", "--agent", "${AGENT_NAME}"]
```

## Kubernetes 설정

### 1. 네임스페이스

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-trading
  labels:
    name: ai-trading
```

### 2. ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-agents-config
  namespace: ai-trading
data:
  # Redis 설정
  REDIS_URL: "redis://redis-service:6379"
  
  # 데이터베이스 설정
  DATABASE_URL: "postgresql://user:password@postgres-service:5432/ai_trading"
  
  # 에이전트 설정
  AGENT_UPDATE_INTERVAL: "60"
  CONFIDENCE_THRESHOLD: "0.7"
  
  # 로깅 설정
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
```

### 3. Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-agents-secrets
  namespace: ai-trading
type: Opaque
data:
  # Base64 인코딩된 값들
  SECRET_KEY: "eW91ci1zZWNyZXQta2V5LWhlcmU="
  DATABASE_PASSWORD: "cGFzc3dvcmQ="
  REDIS_PASSWORD: "cmVkaXNwYXNzd29yZA=="
```

### 4. Meta-Controller 배포

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: meta-controller
  namespace: ai-trading
spec:
  replicas: 1
  selector:
    matchLabels:
      app: meta-controller
  template:
    metadata:
      labels:
        app: meta-controller
    spec:
      containers:
      - name: meta-controller
        image: ai-trading/meta-controller:latest
        ports:
        - containerPort: 8000
        env:
        - name: AGENT_NAME
          value: "meta_controller"
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: ai-agents-config
              key: REDIS_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ai-agents-secrets
              key: SECRET_KEY
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: meta-controller-service
  namespace: ai-trading
spec:
  selector:
    app: meta-controller
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 5. Market Regime Detector 배포

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: market-regime-detector
  namespace: ai-trading
spec:
  replicas: 2
  selector:
    matchLabels:
      app: market-regime-detector
  template:
    metadata:
      labels:
        app: market-regime-detector
    spec:
      containers:
      - name: market-regime-detector
        image: ai-trading/market-regime-detector:latest
        env:
        - name: AGENT_NAME
          value: "market_regime_detector"
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: ai-agents-config
              key: REDIS_URL
        resources:
          requests:
            memory: "256Mi"
            cpu: "125m"
          limits:
            memory: "512Mi"
            cpu: "250m"
```

## 환경별 설정

### 1. 개발 환경

```yaml
# development-values.yaml
replicas:
  meta_controller: 1
  market_regime_detector: 1
  vwap_analyzer: 1
  volume_profile_analyzer: 1
  risk_manager: 1
  rl_optimizer: 1
  genetic_algorithm: 1

resources:
  requests:
    memory: "128Mi"
    cpu: "50m"
  limits:
    memory: "256Mi"
    cpu: "100m"

logging:
  level: "DEBUG"
  format: "text"
```

### 2. 스테이징 환경

```yaml
# staging-values.yaml
replicas:
  meta_controller: 1
  market_regime_detector: 2
  vwap_analyzer: 2
  volume_profile_analyzer: 2
  risk_manager: 1
  rl_optimizer: 1
  genetic_algorithm: 1

resources:
  requests:
    memory: "256Mi"
    cpu: "125m"
  limits:
    memory: "512Mi"
    cpu: "250m"

logging:
  level: "INFO"
  format: "json"
```

### 3. 프로덕션 환경

```yaml
# production-values.yaml
replicas:
  meta_controller: 2
  market_regime_detector: 4
  vwap_analyzer: 4
  volume_profile_analyzer: 4
  risk_manager: 2
  rl_optimizer: 2
  genetic_algorithm: 2

resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"

logging:
  level: "WARNING"
  format: "json"

# 고가용성 설정
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values: [meta-controller]
        topologyKey: kubernetes.io/hostname
```

## 배포 스크립트

### 1. 배포 스크립트 (deploy.sh)

```bash
#!/bin/bash

set -e

# 환경 변수 설정
ENVIRONMENT=${1:-development}
NAMESPACE="ai-trading"

echo "Deploying AI Agents to $ENVIRONMENT environment..."

# 네임스페이스 생성
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# ConfigMap 적용
kubectl apply -f k8s/configmap.yaml -n $NAMESPACE

# Secret 적용
kubectl apply -f k8s/secret.yaml -n $NAMESPACE

# 에이전트 배포
kubectl apply -f k8s/agents/ -n $NAMESPACE

# 서비스 배포
kubectl apply -f k8s/services/ -n $NAMESPACE

# Ingress 배포
kubectl apply -f k8s/ingress/ -n $NAMESPACE

# 배포 상태 확인
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

echo "Deployment completed successfully!"
```

### 2. 롤백 스크립트 (rollback.sh)

```bash
#!/bin/bash

set -e

NAMESPACE="ai-trading"
REVISION=${1:-previous}

echo "Rolling back to revision $REVISION..."

# 이전 리비전으로 롤백
kubectl rollout undo deployment/meta-controller -n $NAMESPACE --to-revision=$REVISION
kubectl rollout undo deployment/market-regime-detector -n $NAMESPACE --to-revision=$REVISION
kubectl rollout undo deployment/vwap-analyzer -n $NAMESPACE --to-revision=$REVISION
kubectl rollout undo deployment/volume-profile-analyzer -n $NAMESPACE --to-revision=$REVISION
kubectl rollout undo deployment/risk-manager -n $NAMESPACE --to-revision=$REVISION
kubectl rollout undo deployment/rl-optimizer -n $NAMESPACE --to-revision=$REVISION
kubectl rollout undo deployment/genetic-algorithm -n $NAMESPACE --to-revision=$REVISION

# 롤백 상태 확인
kubectl rollout status deployment/meta-controller -n $NAMESPACE
kubectl rollout status deployment/market-regime-detector -n $NAMESPACE

echo "Rollback completed successfully!"
```

## 모니터링 설정

### 1. Prometheus 설정

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: ai-trading
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'ai-agents'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - ai-trading
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

### 2. Grafana 대시보드

```json
{
  "dashboard": {
    "title": "AI Agents Monitoring",
    "panels": [
      {
        "title": "Agent Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"ai-agents\"}",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{namespace=\"ai-trading\"}[5m])",
            "legendFormat": "{{pod}}"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{namespace=\"ai-trading\"}",
            "legendFormat": "{{pod}}"
          }
        ]
      }
    ]
  }
}
```

## 로깅 설정

### 1. Fluentd 설정

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: ai-trading
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*ai-trading*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
      time_key time
      time_format %Y-%m-%dT%H:%M:%S.%NZ
    </source>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      index_name ai-agents
      type_name _doc
    </match>
```

### 2. 로그 수집 스크립트

```bash
#!/bin/bash

# 로그 수집 및 분석
kubectl logs -f deployment/meta-controller -n ai-trading | \
  jq -r '.timestamp + " " + .level + " " + .message' | \
  tee /var/log/ai-agents/meta-controller.log

# 에러 로그 필터링
kubectl logs deployment/meta-controller -n ai-trading | \
  jq 'select(.level == "ERROR")' | \
  tee /var/log/ai-agents/errors.log
```

## 백업 및 복구

### 1. 데이터베이스 백업

```bash
#!/bin/bash

# PostgreSQL 백업
kubectl exec -it postgres-0 -n ai-trading -- \
  pg_dump -U user ai_trading > backup_$(date +%Y%m%d_%H%M%S).sql

# Redis 백업
kubectl exec -it redis-0 -n ai-trading -- \
  redis-cli BGSAVE
```

### 2. 설정 백업

```bash
#!/bin/bash

# Kubernetes 리소스 백업
kubectl get all -n ai-trading -o yaml > k8s-backup-$(date +%Y%m%d_%H%M%S).yaml

# ConfigMap 백업
kubectl get configmap -n ai-trading -o yaml > configmap-backup-$(date +%Y%m%d_%H%M%S).yaml
```

## 보안 설정

### 1. 네트워크 정책

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-agents-network-policy
  namespace: ai-trading
spec:
  podSelector:
    matchLabels:
      app: ai-agent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ai-trading
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: ai-trading
    ports:
    - protocol: TCP
      port: 6379
    - protocol: TCP
      port: 5432
```

### 2. RBAC 설정

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: ai-trading
  name: ai-agent-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
```

## 성능 튜닝

### 1. 리소스 최적화

```yaml
# HPA 설정
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: market-regime-detector-hpa
  namespace: ai-trading
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: market-regime-detector
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. 네트워크 최적화

```yaml
# Service Mesh 설정 (Istio)
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: ai-agents-destination-rule
  namespace: ai-trading
spec:
  host: meta-controller-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 10
    circuitBreaker:
      consecutiveErrors: 3
      interval: 30s
      baseEjectionTime: 30s
```

## 문제 해결

### 1. 일반적인 문제

```bash
# Pod 상태 확인
kubectl get pods -n ai-trading

# 로그 확인
kubectl logs -f deployment/meta-controller -n ai-trading

# 이벤트 확인
kubectl get events -n ai-trading --sort-by='.lastTimestamp'

# 리소스 사용량 확인
kubectl top pods -n ai-trading
```

### 2. 디버깅 스크립트

```bash
#!/bin/bash

echo "=== AI Agents Debug Information ==="
echo "Date: $(date)"
echo ""

echo "=== Pod Status ==="
kubectl get pods -n ai-trading -o wide

echo ""
echo "=== Service Status ==="
kubectl get services -n ai-trading

echo ""
echo "=== ConfigMap Status ==="
kubectl get configmap -n ai-trading

echo ""
echo "=== Recent Events ==="
kubectl get events -n ai-trading --sort-by='.lastTimestamp' | tail -20

echo ""
echo "=== Resource Usage ==="
kubectl top pods -n ai-trading

echo ""
echo "=== Network Policy ==="
kubectl get networkpolicy -n ai-trading
```

## 결론

이 배포 가이드는 AI 에이전트 시스템을 Kubernetes 환경에서 안정적으로 운영하기 위한 모든 필요한 설정과 절차를 포함합니다. 환경별 설정, 모니터링, 보안, 성능 튜닝까지 종합적으로 다루어 프로덕션 환경에서의 안정적인 서비스 운영을 보장합니다.