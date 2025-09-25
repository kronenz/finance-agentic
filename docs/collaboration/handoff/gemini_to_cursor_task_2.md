# Gemini → Cursor 작업 전달 #2

## 작업 개요
**제목**: Redux 상태 관리 연동  
**우선순위**: 최고  
**예상 소요시간**: 2-3시간  
**담당자**: Cursor Agent  

## 작업 배경
1단계에서 구독 서비스 API 모듈이 완성되었습니다. 이제 Redux를 통해 전역 상태 관리를 구현하여 컴포넌트의 복잡도를 낮추고 상태 관리 일관성을 확보해야 합니다.

## 2단계: Redux 상태 관리 연동

### 작업 목표
- `subscriptionService.ts`를 사용하여 백엔드와 통신하는 비동기 로직을 Redux Thunk를 통해 관리
- 구독 플랜, 사용자 구독 상태, API 호출 상태를 전역 Redux 스토어에서 관리
- 컴포넌트의 복잡도 낮추고 상태 관리 일관성 확보

### 구체적 작업 내용

#### 2.1 Redux Slice 생성
**파일**: `frontend/src/store/slices/subscriptionSlice.ts`

**상태 구조**:
```typescript
interface SubscriptionState {
  plans: SubscriptionPlanResponse[];
  userSubscription: SubscriptionResponse | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}
```

**구현할 Async Thunks**:
- `fetchSubscriptionPlans`: 구독 플랜 목록 조회
- `fetchUserSubscription`: 사용자 활성 구독 조회
- `subscribeToPlan`: 구독 생성
- `cancelCurrentUserSubscription`: 구독 취소
- `reactivateUserSubscription`: 구독 재활성화

#### 2.2 Redux Store 통합
**파일**: `frontend/src/store/store.ts`
- `subscriptionSlice.reducer`를 store에 추가

#### 2.3 컴포넌트 리팩토링

**SubscriptionPlans.tsx**:
- `useState` 제거하고 `useSelector` 사용
- `useEffect`에서 `fetchSubscriptionPlans` Thunk dispatch
- '구독하기' 버튼에서 `subscribeToPlan` Thunk dispatch

**SubscriptionManagement.tsx**:
- `useState` 제거하고 `useSelector` 사용
- `useEffect`에서 `fetchUserSubscription` Thunk dispatch
- 구독 취소/재활성화에서 해당 Thunk dispatch

### 기술적 요구사항
- Redux Toolkit의 `createSlice`와 `createAsyncThunk` 사용
- TypeScript 타입 안전성 보장
- 에러 처리 및 로딩 상태 관리
- 컴포넌트에서 로컬 상태 최소화

### 완료 기준
- [ ] `subscriptionSlice.ts` 생성 및 모든 Async Thunk 구현
- [ ] Redux store에 subscriptionSlice 통합
- [ ] `SubscriptionPlans.tsx` Redux 연동 완료
- [ ] `SubscriptionManagement.tsx` Redux 연동 완료
- [ ] 모든 기능 정상 작동 확인
- [ ] 로딩 및 에러 상태 UI 반영 확인

### 다음 단계 준비
2단계 완료 후 3단계(UI/UX 개선) 작업을 진행할 예정입니다.

---
**작성자**: Gemini CLI  
**작성일**: 2024-12-23  
**승인자**: Human Manager
