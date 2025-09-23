// 구독 관리 컴포넌트
import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { SubscriptionResponse } from '../types/subscription';

const SubscriptionManagement: React.FC = () => {
  const [subscription, setSubscription] = useState<SubscriptionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCancelModal, setShowCancelModal] = useState(false);

  const { user } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (user) {
      fetchActiveSubscription();
    }
  }, [user]);

  const fetchActiveSubscription = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/subscriptions/active', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          setSubscription(null);
          return;
        }
        throw new Error('Failed to fetch subscription');
      }
      
      const data = await response.json();
      setSubscription(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!subscription) return;
    
    try {
      const response = await fetch(`/api/v1/subscriptions/${subscription.id}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to cancel subscription');
      }
      
      setShowCancelModal(false);
      await fetchActiveSubscription();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleReactivateSubscription = async () => {
    if (!subscription) return;
    
    try {
      const response = await fetch(`/api/v1/subscriptions/${subscription.id}/reactivate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to reactivate subscription');
      }
      
      await fetchActiveSubscription();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
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

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Error: {error}</p>
        <button
          onClick={fetchActiveSubscription}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
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
                  className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Cancel Subscription
                </button>
              )}
              
              {subscription.status === 'cancelled' && (
                <button
                  onClick={handleReactivateSubscription}
                  className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Reactivate Subscription
                </button>
              )}
              
              <button
                onClick={() => window.location.href = '/subscription/plans'}
                className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Change Plan
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
      {showCancelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Cancel Subscription
            </h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to cancel your subscription? This action cannot be undone.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowCancelModal(false)}
                className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
              >
                Keep Subscription
              </button>
              <button
                onClick={handleCancelSubscription}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Cancel Subscription
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionManagement;
