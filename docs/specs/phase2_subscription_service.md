# Phase 2: 개인형 구독 서비스 명세서

## 개요
**목표**: Phase 1의 기본 자동화 거래 시스템을 개인형 구독 서비스로 발전  
**기간**: 3-4개월  
**팀 구성**: 기존 7개 역할 + Frontend Developer + UI/UX Designer

## 비즈니스 요구사항

### 1. 구독 모델
- **개인 사용자 대상**: 개인 투자자를 위한 맞춤형 서비스
- **계층화된 구독 플랜**: Basic, Premium, Pro 3단계
- **월간/연간 구독**: 유연한 구독 주기 선택
- **무료 체험**: 14일 무료 체험 제공

### 2. 구독 플랜 상세
#### Basic Plan ($29/월)
- **기본 거래 전략**: 슈퍼트렌드, RSI 평균회귀
- **실시간 모니터링**: 기본 대시보드
- **알림**: 이메일 알림
- **지원**: 이메일 지원

#### Premium Plan ($79/월)
- **고급 거래 전략**: AI 기반 전략 포함
- **고급 분석**: 시장 국면 분석, 리스크 분석
- **실시간 알림**: 이메일 + SMS + 푸시 알림
- **지원**: 우선 지원 + 채팅 지원

#### Pro Plan ($199/월)
- **모든 전략**: 모든 거래 전략 접근
- **AI 맞춤화**: 개인화된 AI 전략
- **고급 시각화**: 커스텀 차트, 백테스팅
- **전용 지원**: 전용 계정 매니저
- **API 접근**: REST API 접근 권한

### 3. 사용자 인증 및 권한
- **JWT 기반 인증**: 안전한 사용자 인증
- **소셜 로그인**: Google, Apple, GitHub 로그인
- **2FA 지원**: 2단계 인증 보안
- **세션 관리**: 안전한 세션 관리

## 기능 요구사항

### 1. 사용자 관리 시스템
#### 사용자 등록 및 인증
- **회원가입**: 이메일, 소셜 로그인 지원
- **이메일 인증**: 회원가입 시 이메일 인증
- **비밀번호 재설정**: 안전한 비밀번호 재설정
- **프로필 관리**: 사용자 프로필 정보 관리

#### 구독 관리
- **구독 플랜 선택**: 플랜 비교 및 선택
- **결제 처리**: Stripe 기반 안전한 결제
- **구독 변경**: 플랜 업그레이드/다운그레이드
- **구독 취소**: 구독 취소 및 환불 처리

### 2. 개인화된 대시보드
#### 기본 대시보드
- **포트폴리오 개요**: 현재 포지션 및 성과
- **실시간 차트**: 거래 데이터 실시간 시각화
- **알림 센터**: 중요 이벤트 알림
- **빠른 액션**: 주요 기능 빠른 접근

#### 고급 대시보드 (Premium/Pro)
- **AI 인사이트**: AI 기반 시장 분석
- **백테스팅 도구**: 전략 성과 백테스팅
- **리스크 분석**: 포트폴리오 리스크 분석
- **커스텀 위젯**: 사용자 정의 대시보드

### 3. 거래 전략 관리
#### 전략 라이브러리
- **전략 목록**: 사용 가능한 모든 전략
- **전략 상세**: 전략 설명, 성과, 리스크
- **전략 비교**: 여러 전략 성과 비교
- **전략 추천**: AI 기반 전략 추천

#### 전략 설정
- **파라미터 조정**: 전략별 파라미터 설정
- **리스크 설정**: 손절매, 익절 설정
- **알림 설정**: 전략별 알림 설정
- **백테스팅**: 설정된 파라미터로 백테스팅

### 4. 실시간 모니터링
#### 거래 모니터링
- **실시간 포지션**: 현재 포지션 상태
- **수익/손실**: 실시간 P&L 표시
- **거래 내역**: 거래 기록 및 상세 정보
- **성과 분석**: 일간/주간/월간 성과

#### 시장 모니터링
- **시장 상황**: 현재 시장 상태
- **뉴스 피드**: 관련 뉴스 및 이벤트
- **경제 지표**: 주요 경제 지표
- **시장 분석**: AI 기반 시장 분석

### 5. 알림 시스템
#### 알림 유형
- **거래 알림**: 포지션 진입/청산 알림
- **성과 알림**: 목표 달성/손실 알림
- **시장 알림**: 중요한 시장 이벤트
- **시스템 알림**: 시스템 상태 및 업데이트

#### 알림 채널
- **이메일**: 상세한 이메일 알림
- **SMS**: 긴급한 SMS 알림
- **푸시 알림**: 모바일 앱 푸시 알림
- **웹 알림**: 웹 브라우저 알림

## 비기능 요구사항

### 1. 성능 요구사항
- **응답 시간**: 페이지 로딩 3초 이하
- **동시 사용자**: 1,000명 동시 접속 지원
- **데이터 처리**: 실시간 데이터 1초 이내 처리
- **API 응답**: API 응답 500ms 이하

### 2. 보안 요구사항
- **데이터 암호화**: 모든 민감 데이터 암호화
- **HTTPS**: 모든 통신 HTTPS 사용
- **인증**: JWT 기반 안전한 인증
- **권한 관리**: 역할 기반 접근 제어

### 3. 사용성 요구사항
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 대응
- **접근성**: WCAG 2.1 AA 수준 준수
- **다국어**: 영어, 한국어 지원
- **사용자 경험**: 직관적이고 사용하기 쉬운 인터페이스

### 4. 확장성 요구사항
- **마이크로서비스**: 확장 가능한 마이크로서비스 아키텍처
- **데이터베이스**: 수평적 확장 가능한 데이터베이스
- **캐싱**: Redis 기반 효율적인 캐싱
- **CDN**: 전 세계 빠른 콘텐츠 전송

## 기술 스택

### 프론트엔드
- **프레임워크**: React 18+ with TypeScript
- **상태 관리**: Redux Toolkit
- **라우팅**: React Router v6
- **스타일링**: Styled-components + Tailwind CSS
- **차트**: Recharts + D3.js
- **UI 라이브러리**: Ant Design
- **테스트**: Jest + React Testing Library + Cypress

### 백엔드
- **언어**: Python 3.9+ with FastAPI
- **데이터베이스**: PostgreSQL + Redis
- **ORM**: SQLAlchemy
- **인증**: JWT + OAuth2
- **결제**: Stripe API
- **이메일**: SendGrid
- **SMS**: Twilio

### 인프라
- **컨테이너**: Docker + Kubernetes
- **클라우드**: AWS
- **CDN**: CloudFront
- **모니터링**: Prometheus + Grafana
- **로깅**: ELK Stack
- **CI/CD**: GitHub Actions

## 데이터베이스 설계

### 사용자 관련 테이블
```sql
-- 사용자 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 구독 테이블
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL, -- active, cancelled, expired
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    stripe_subscription_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 결제 내역 테이블
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    subscription_id UUID REFERENCES subscriptions(id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) NOT NULL, -- pending, completed, failed, refunded
    stripe_payment_intent_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 거래 관련 테이블
```sql
-- 사용자 거래 설정 테이블
CREATE TABLE user_trading_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    strategy_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    parameters JSONB,
    risk_settings JSONB,
    notification_settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 포지션 테이블
CREATE TABLE user_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- long, short
    entry_price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    current_price DECIMAL(20,8),
    unrealized_pnl DECIMAL(20,8),
    strategy_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'open', -- open, closed
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);
```

## API 설계

### 인증 API
```typescript
// 사용자 인증
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
POST /api/auth/forgot-password
POST /api/auth/reset-password

// 소셜 로그인
POST /api/auth/google
POST /api/auth/apple
POST /api/auth/github
```

### 구독 API
```typescript
// 구독 관리
GET /api/subscriptions/plans
POST /api/subscriptions/subscribe
PUT /api/subscriptions/change-plan
DELETE /api/subscriptions/cancel
GET /api/subscriptions/current
GET /api/subscriptions/history
```

### 거래 API
```typescript
// 거래 설정
GET /api/trading/settings
POST /api/trading/settings
PUT /api/trading/settings/:id
DELETE /api/trading/settings/:id

// 포지션 관리
GET /api/trading/positions
GET /api/trading/positions/:id
POST /api/trading/positions/close
GET /api/trading/history
```

### 대시보드 API
```typescript
// 대시보드 데이터
GET /api/dashboard/overview
GET /api/dashboard/performance
GET /api/dashboard/positions
GET /api/dashboard/alerts
```

## 보안 고려사항

### 1. 데이터 보호
- **개인정보 암호화**: 사용자 개인정보 AES-256 암호화
- **결제정보 보호**: PCI DSS 준수
- **API 보안**: Rate Limiting, CORS 설정
- **데이터 백업**: 정기적 데이터 백업

### 2. 인증 및 권한
- **JWT 토큰**: 안전한 JWT 토큰 사용
- **세션 관리**: 세션 타임아웃 및 갱신
- **권한 검증**: 모든 API 엔드포인트 권한 검증
- **2FA**: 2단계 인증 지원

### 3. 거래 보안
- **API 키 암호화**: 거래소 API 키 암호화 저장
- **거래 승인**: 중요한 거래는 사용자 승인 필요
- **리스크 관리**: 사용자 설정된 리스크 한도 준수
- **감사 로그**: 모든 거래 활동 감사 로그

## 성과 지표 (KPI)

### 비즈니스 지표
- **월간 반복 수익 (MRR)**: $50,000 (6개월 목표)
- **고객 획득 비용 (CAC)**: $50 이하
- **고객 생애 가치 (LTV)**: $500 이상
- **이탈률**: 5% 이하 (월간)
- **전환율**: 15% 이상 (체험 → 유료)

### 기술 지표
- **시스템 가용성**: 99.9% 이상
- **응답 시간**: 평균 500ms 이하
- **에러율**: 0.1% 이하
- **사용자 만족도**: 4.5/5.0 이상

### 사용자 지표
- **일간 활성 사용자 (DAU)**: 500명 (6개월 목표)
- **월간 활성 사용자 (MAU)**: 2,000명 (6개월 목표)
- **사용자 참여도**: 평균 세션 시간 10분 이상
- **기능 사용률**: 핵심 기능 80% 이상 사용

## 구현 로드맵

### Phase 2.1: 기본 인프라 (1개월)
- [ ] 사용자 인증 시스템 구축
- [ ] 구독 관리 시스템 구축
- [ ] 기본 데이터베이스 설계
- [ ] API 기본 구조 구축

### Phase 2.2: 프론트엔드 개발 (1.5개월)
- [ ] React 앱 기본 구조
- [ ] 사용자 인증 UI
- [ ] 구독 관리 UI
- [ ] 기본 대시보드

### Phase 2.3: 거래 기능 통합 (1개월)
- [ ] 기존 거래 시스템 통합
- [ ] 사용자별 거래 설정
- [ ] 실시간 모니터링
- [ ] 알림 시스템

### Phase 2.4: 고급 기능 (0.5개월)
- [ ] 고급 대시보드
- [ ] 백테스팅 도구
- [ ] AI 인사이트
- [ ] 모바일 최적화

## 위험 요소 및 대응 방안

### 기술적 위험
- **확장성 문제**: 마이크로서비스 아키텍처로 대응
- **보안 취약점**: 정기적 보안 검토 및 패치
- **성능 저하**: 캐싱 및 CDN 활용
- **데이터 손실**: 다중 백업 및 복구 시스템

### 비즈니스 위험
- **경쟁사 대응**: 차별화된 기능 개발
- **규제 변화**: 규제 모니터링 및 대응
- **사용자 이탈**: 지속적인 사용자 피드백 수집
- **기술 부채**: 정기적 코드 리뷰 및 리팩토링

## 결론

Phase 2는 기본 자동화 거래 시스템을 개인형 구독 서비스로 발전시키는 중요한 단계입니다. 사용자 중심의 설계와 안전한 거래 환경을 제공하여 지속 가능한 비즈니스 모델을 구축할 수 있습니다.
