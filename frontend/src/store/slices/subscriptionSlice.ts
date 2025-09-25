// 구독 관련 Redux Slice
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { 
  SubscriptionPlanResponse, 
  SubscriptionResponse, 
  SubscriptionCreate 
} from '../../types/subscription';
import { subscriptionService } from '../../services/subscriptionService';

// 상태 인터페이스 정의
interface SubscriptionState {
  plans: SubscriptionPlanResponse[];
  userSubscription: SubscriptionResponse | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

// 초기 상태
const initialState: SubscriptionState = {
  plans: [],
  userSubscription: null,
  status: 'idle',
  error: null,
};

// Async Thunks 정의

// 구독 플랜 목록 조회
export const fetchSubscriptionPlans = createAsyncThunk(
  'subscription/fetchPlans',
  async (_, { rejectWithValue }) => {
    try {
      const plans = await subscriptionService.getSubscriptionPlans();
      return plans;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '구독 플랜을 불러오는데 실패했습니다.';
      return rejectWithValue(errorMessage);
    }
  }
);

// 사용자 활성 구독 조회
export const fetchUserSubscription = createAsyncThunk(
  'subscription/fetchUserSubscription',
  async (_, { rejectWithValue }) => {
    try {
      const subscription = await subscriptionService.getActiveSubscription();
      return subscription;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '구독 정보를 불러오는데 실패했습니다.';
      return rejectWithValue(errorMessage);
    }
  }
);

// 구독 생성
export const subscribeToPlan = createAsyncThunk(
  'subscription/subscribeToPlan',
  async ({ planId, billingCycle }: { planId: string; billingCycle: string }, { rejectWithValue }) => {
    try {
      const subscription = await subscriptionService.createSubscription(planId, billingCycle);
      return subscription;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '구독 생성에 실패했습니다.';
      return rejectWithValue(errorMessage);
    }
  }
);

// 구독 취소
export const cancelCurrentUserSubscription = createAsyncThunk(
  'subscription/cancelSubscription',
  async (subscriptionId: string, { rejectWithValue }) => {
    try {
      await subscriptionService.cancelSubscription(subscriptionId);
      return subscriptionId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '구독 취소에 실패했습니다.';
      return rejectWithValue(errorMessage);
    }
  }
);

// 구독 재활성화
export const reactivateUserSubscription = createAsyncThunk(
  'subscription/reactivateSubscription',
  async (subscriptionId: string, { rejectWithValue }) => {
    try {
      await subscriptionService.reactivateSubscription(subscriptionId);
      return subscriptionId;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '구독 재활성화에 실패했습니다.';
      return rejectWithValue(errorMessage);
    }
  }
);

// 구독 업데이트
export const updateUserSubscription = createAsyncThunk(
  'subscription/updateSubscription',
  async ({ subscriptionId, updates }: { subscriptionId: string; updates: Partial<SubscriptionCreate> }, { rejectWithValue }) => {
    try {
      const subscription = await subscriptionService.updateSubscription(subscriptionId, updates);
      return subscription;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '구독 업데이트에 실패했습니다.';
      return rejectWithValue(errorMessage);
    }
  }
);

// Slice 생성
const subscriptionSlice = createSlice({
  name: 'subscription',
  initialState,
  reducers: {
    // 에러 초기화
    clearError: (state) => {
      state.error = null;
    },
    // 상태 초기화
    resetSubscriptionState: (state) => {
      state.plans = [];
      state.userSubscription = null;
      state.status = 'idle';
      state.error = null;
    },
    // 구독 상태 업데이트 (로컬 상태 변경용)
    updateSubscriptionStatus: (state, action: PayloadAction<{ status: string }>) => {
      if (state.userSubscription) {
        state.userSubscription.status = action.payload.status as any;
      }
    },
  },
  extraReducers: (builder) => {
    // fetchSubscriptionPlans
    builder
      .addCase(fetchSubscriptionPlans.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchSubscriptionPlans.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.plans = action.payload;
        state.error = null;
      })
      .addCase(fetchSubscriptionPlans.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
      });

    // fetchUserSubscription
    builder
      .addCase(fetchUserSubscription.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchUserSubscription.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.userSubscription = action.payload;
        state.error = null;
      })
      .addCase(fetchUserSubscription.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
      });

    // subscribeToPlan
    builder
      .addCase(subscribeToPlan.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(subscribeToPlan.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.userSubscription = action.payload;
        state.error = null;
      })
      .addCase(subscribeToPlan.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
      });

    // cancelCurrentUserSubscription
    builder
      .addCase(cancelCurrentUserSubscription.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(cancelCurrentUserSubscription.fulfilled, (state) => {
        state.status = 'succeeded';
        if (state.userSubscription) {
          state.userSubscription.status = 'cancelled' as any;
        }
        state.error = null;
      })
      .addCase(cancelCurrentUserSubscription.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
      });

    // reactivateUserSubscription
    builder
      .addCase(reactivateUserSubscription.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(reactivateUserSubscription.fulfilled, (state) => {
        state.status = 'succeeded';
        if (state.userSubscription) {
          state.userSubscription.status = 'active' as any;
        }
        state.error = null;
      })
      .addCase(reactivateUserSubscription.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
      });

    // updateUserSubscription
    builder
      .addCase(updateUserSubscription.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(updateUserSubscription.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.userSubscription = action.payload;
        state.error = null;
      })
      .addCase(updateUserSubscription.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
      });
  },
});

// 액션 내보내기
export const { clearError, resetSubscriptionState, updateSubscriptionStatus } = subscriptionSlice.actions;

// 리듀서 내보내기
export default subscriptionSlice.reducer;

// 셀렉터 함수들
export const selectSubscriptionPlans = (state: { subscription: SubscriptionState }) => state.subscription.plans;
export const selectUserSubscription = (state: { subscription: SubscriptionState }) => state.subscription.userSubscription;
export const selectSubscriptionStatus = (state: { subscription: SubscriptionState }) => state.subscription.status;
export const selectSubscriptionError = (state: { subscription: SubscriptionState }) => state.subscription.error;
export const selectIsLoading = (state: { subscription: SubscriptionState }) => state.subscription.status === 'loading';
export const selectHasError = (state: { subscription: SubscriptionState }) => state.subscription.status === 'failed';
