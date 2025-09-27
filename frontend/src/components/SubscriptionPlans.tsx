// 구독 플랜 선택 컴포넌트
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { AppDispatch } from '../store';
import toast from 'react-hot-toast';
// import { RootState } from '../store'; // 사용하지 않음
// import { SubscriptionPlanResponse } from '../types/subscription'; // 사용하지 않음
import { 
  fetchSubscriptionPlans, 
  subscribeToPlan,
  selectSubscriptionPlans,
  // selectSubscriptionStatus, // 사용하지 않음
  selectSubscriptionError,
  selectIsLoading,
  selectHasError,
  clearError
} from '../store/slices/subscriptionSlice';
import { SubscriptionPlanSkeleton } from './ui/SkeletonLoader';

interface SubscriptionPlansProps {
  onPlanSelect: (planId: string) => void;
  selectedPlanId?: string;
  onSubscribe?: (planId: string, billingCycle: string) => void;
}

const SubscriptionPlans: React.FC<SubscriptionPlansProps> = ({
  onPlanSelect,
  selectedPlanId,
  onSubscribe
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [subscribing, setSubscribing] = useState<string | null>(null);

  // Redux 상태 구독
  const plans = useSelector(selectSubscriptionPlans);
  // const status = useSelector(selectSubscriptionStatus); // 사용하지 않음
  const error = useSelector(selectSubscriptionError);
  const isLoading = useSelector(selectIsLoading);
  const hasError = useSelector(selectHasError);

  useEffect(() => {
    dispatch(fetchSubscriptionPlans());
  }, [dispatch]);

  // 에러 초기화
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        dispatch(clearError());
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, dispatch]);

  const handlePlanSelect = (planId: string) => {
    onPlanSelect(planId);
  };

  const handleSubscribe = async (planId: string, billingCycle: string = 'monthly') => {
    try {
      setSubscribing(planId);
      await dispatch(subscribeToPlan({ planId, billingCycle })).unwrap();
      
      // 구독 성공 토스트
      toast.success('구독이 성공적으로 완료되었습니다!');
      
      // 구독 성공 시 콜백 호출
      if (onSubscribe) {
        onSubscribe(planId, billingCycle);
      }
    } catch (error) {
      console.error('Subscription failed:', error);
      toast.error('구독 처리 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setSubscribing(null);
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
        {[...Array(3)].map((_, index) => (
          <SubscriptionPlanSkeleton key={index} />
        ))}
      </div>
    );
  }

  if (hasError && error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">오류: {error}</p>
        <button
          onClick={() => dispatch(fetchSubscriptionPlans())}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          다시 시도
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
      {plans.map((plan) => (
        <div
          key={plan.id}
          className={`relative bg-white rounded-lg shadow-lg border-2 p-6 cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-105 ${
            selectedPlanId === plan.id
              ? 'border-blue-600 ring-2 ring-blue-200'
              : 'border-gray-200 hover:border-gray-300'
          }`}
          onClick={() => handlePlanSelect(plan.id)}
        >
          {plan.id === 'premium' && (
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium shadow-lg">
                추천
              </span>
            </div>
          )}
          
          <div className="text-center">
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              {plan.name}
            </h3>
            <p className="text-gray-600 mb-4">{plan.description}</p>
            
            <div className="mb-6">
              <span className="text-4xl font-bold text-gray-900">
                ${plan.price}
              </span>
              <span className="text-gray-600 ml-1">
                /{plan.billing_cycle}
              </span>
            </div>
            
            <ul className="space-y-3 mb-6">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-center">
                  <svg
                    className="w-5 h-5 text-green-500 mr-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span className="text-gray-700">{feature}</span>
                </li>
              ))}
            </ul>
            
            <div className="space-y-2">
              <button
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                  selectedPlanId === plan.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                }`}
                onClick={() => handlePlanSelect(plan.id)}
              >
                {selectedPlanId === plan.id ? '선택됨' : '플랜 선택'}
              </button>
              
              {onSubscribe && selectedPlanId === plan.id && (
                <button
                  className="w-full py-3 px-4 rounded-lg font-medium bg-gradient-to-r from-green-600 to-green-700 text-white hover:from-green-700 hover:to-green-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
                  onClick={() => handleSubscribe(plan.id, plan.billing_cycle)}
                  disabled={subscribing === plan.id}
                >
                  {subscribing === plan.id ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      구독 중...
                    </div>
                  ) : (
                    '구독하기'
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SubscriptionPlans;
