# Gemini → Cursor 작업 전달 #1

## 작업 개요
**제목**: 구독 서비스 API 연동 및 상태 관리 통합  
**우선순위**: 최고  
**예상 소요시간**: 2-3시간  
**담당자**: Cursor Agent  

## 작업 배경
Phase 2 구독 서비스의 85% 완성 상태에서 프론트엔드와 백엔드 API의 완전한 연동이 필요한 상황입니다. 현재 프론트엔드 컴포넌트들이 독립적으로 API를 호출하는 기본 형태만 갖추고 있어, 사용자 플로우가 완성되지 않았습니다.

## 1단계: API 서비스 모듈 생성 및 리팩토링

### 작업 목표
API 요청 로직을 컴포넌트에서 분리하여 중앙에서 관리하고 재사용성을 높입니다.

### 구체적 작업 내용

#### 1.1 구독 서비스 모듈 생성
**파일**: `frontend/src/services/subscriptionService.ts`

**요구사항**:
- Axios 기반 HTTP 클라이언트 설정
- 인증 토큰 자동 추가 인터셉터 구현
- Redux 상태에서 토큰 가져오기
- 백엔드 API와 매핑되는 함수들 구현

**구현할 함수들**:
```typescript
// 구독 플랜 목록 조회
getSubscriptionPlans(): Promise<SubscriptionPlanResponse[]>

// 활성 구독 조회
getActiveSubscription(): Promise<SubscriptionResponse | null>

// 구독 생성
createSubscription(planId: string, billingCycle: string): Promise<SubscriptionResponse>

// 구독 취소
cancelSubscription(subscriptionId: string): Promise<void>

// 구독 재활성화
reactivateSubscription(subscriptionId: string): Promise<void>

// 구독 이력 조회
getSubscriptionHistory(subscriptionId: string): Promise<SubscriptionHistoryResponse[]>
```

#### 1.2 컴포넌트 리팩토링
**대상 파일들**:
- `frontend/src/components/SubscriptionPlans.tsx`
- `frontend/src/components/SubscriptionManagement.tsx`

**작업 내용**:
- 기존 `fetch` 로직을 새 서비스 함수 호출로 교체
- 에러 처리 로직 개선
- 로딩 상태 관리 개선

### 기술적 요구사항
- TypeScript 타입 안전성 보장
- 에러 핸들링 표준화
- API 응답 데이터 검증
- 로깅 및 디버깅 지원

### 완료 기준
- [ ] `subscriptionService.ts` 파일 생성 및 모든 함수 구현
- [ ] `SubscriptionPlans.tsx`에서 새 서비스 사용
- [ ] `SubscriptionManagement.tsx`에서 새 서비스 사용
- [ ] API 호출 시 인증 토큰 자동 추가 확인
- [ ] 에러 처리 및 로딩 상태 정상 작동 확인

### 다음 단계 준비
1단계 완료 후 2단계(Redux 상태 관리 연동) 작업을 진행할 예정입니다.

---
**작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**승인자**: Human Manager
