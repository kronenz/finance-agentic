// 구독 관리 컴포넌트
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import toast from 'react-hot-toast';
import { RootState } from '../store';
import { SubscriptionResponse } from '../types/subscription';
import { 
  fetchUserSubscription,
  cancelCurrentUserSubscription,
  reactivateUserSubscription,
  selectUserSubscription,
  selectSubscriptionStatus,
  selectSubscriptionError,
  selectIsLoading,
  selectHasError,
  clearError
} from '../store/slices/subscriptionSlice';
import { SubscriptionManagementSkeleton } from './ui/SkeletonLoader';
import ConfirmationModal from './ui/ConfirmationModal';

const SubscriptionManagement: React.FC = () => {
  const dispatch = useDispatch();
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const { user } = useSelector((state: RootState) => state.auth);
  
  // Redux 상태 구독
  const subscription = useSelector(selectUserSubscription);
  const status = useSelector(selectSubscriptionStatus);
  const error = useSelector(selectSubscriptionError);
  const isLoading = useSelector(selectIsLoading);
  const hasError = useSelector(selectHasError);

  useEffect(() => {
    if (user) {
      dispatch(fetchUserSubscription());
    }
  }, [user, dispatch]);

  // 에러 초기화
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        dispatch(clearError());
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, dispatch]);

  const handleCancelSubscription = async () => {
    if (!subscription) return;
    
    try {
      setIsProcessing(true);
      await dispatch(cancelCurrentUserSubscription(subscription.id)).unwrap();
      setShowCancelModal(false);
      toast.success('구독이 성공적으로 취소되었습니다.');
    } catch (err) {
      console.error('Cancel subscription failed:', err);
      toast.error('구독 취소 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReactivateSubscription = async () => {
    if (!subscription) return;
    
    try {
      setIsProcessing(true);
      await dispatch(reactivateUserSubscription(subscription.id)).unwrap();
      toast.success('구독이 성공적으로 재활성화되었습니다.');
    } catch (err) {
      console.error('Reactivate subscription failed:', err);
      toast.error('구독 재활성화 중 오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100';
      case 'cancelled':
        return 'text-red-600 bg-red-100';
      case 'expired':
        return 'text-gray-600 bg-gray-100';
      case 'suspended':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return <SubscriptionManagementSkeleton />;
  }

  if (hasError && error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">오류: {error}</p>
        <button
          onClick={() => dispatch(fetchUserSubscription())}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          No Active Subscription
        </h2>
        <p className="text-gray-600 mb-6">
          You don't have an active subscription. Choose a plan to get started.
        </p>
        <button
          onClick={() => window.location.href = '/subscription/plans'}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          View Plans
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {subscription.plan_name}
            </h2>
            <p className="text-gray-600">
              ${subscription.price} / {subscription.billing_cycle}
            </p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
              subscription.status
            )}`}
          >
            {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Subscription Details
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Start Date:</span>
                <span className="font-medium">
                  {formatDate(subscription.start_date)}
                </span>
              </div>
              {subscription.end_date && (
                <div className="flex justify-between">
                  <span className="text-gray-600">End Date:</span>
                  <span className="font-medium">
                    {formatDate(subscription.end_date)}
                  </span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600">Billing Cycle:</span>
                <span className="font-medium capitalize">
                  {subscription.billing_cycle}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Currency:</span>
                <span className="font-medium uppercase">
                  {subscription.currency}
                </span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Actions
            </h3>
            <div className="space-y-3">
              {subscription.status === 'active' && (
                <button
                  onClick={() => setShowCancelModal(true)}
                  disabled={isProcessing}
                  className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  구독 취소
                </button>
              )}
              
              {subscription.status === 'cancelled' && (
                <button
                  onClick={handleReactivateSubscription}
                  disabled={isProcessing}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isProcessing ? '재활성화 중...' : '구독 재활성화'}
                </button>
              )}
              
              <button
                onClick={() => window.location.href = '/subscription/plans'}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                플랜 변경
              </button>
            </div>
          </div>
        </div>

        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Subscription History
          </h3>
          <button
            onClick={() => window.location.href = `/subscription/${subscription.id}/history`}
            className="text-blue-600 hover:text-blue-700 underline"
          >
            View Full History
          </button>
        </div>
      </div>

      {/* Cancel Confirmation Modal */}
      <ConfirmationModal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        onConfirm={handleCancelSubscription}
        title="구독 취소"
        message="정말로 구독을 취소하시겠습니까? 이 작업은 되돌릴 수 없습니다."
        confirmText="구독 취소"
        cancelText="구독 유지"
        confirmButtonColor="red"
        isLoading={isProcessing}
      />
    </div>
  );
};

export default SubscriptionManagement;
