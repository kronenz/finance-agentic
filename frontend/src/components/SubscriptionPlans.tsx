// 구독 플랜 선택 컴포넌트
import React, { useState, useEffect } from 'react';
// import { useSelector, useDispatch } from 'react-redux';
// import { RootState } from '../store';
import { SubscriptionPlanResponse } from '../types/subscription';

interface SubscriptionPlansProps {
  onPlanSelect: (planId: string) => void;
  selectedPlanId?: string;
}

const SubscriptionPlans: React.FC<SubscriptionPlansProps> = ({
  onPlanSelect,
  selectedPlanId
}) => {
  const [plans, setPlans] = useState<SubscriptionPlanResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/subscriptions/plans');
      if (!response.ok) {
        throw new Error('Failed to fetch plans');
      }
      const data = await response.json();
      setPlans(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handlePlanSelect = (planId: string) => {
    onPlanSelect(planId);
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
          onClick={fetchPlans}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
      {plans.map((plan) => (
        <div
          key={plan.id}
          className={`relative bg-white rounded-lg shadow-lg border-2 p-6 cursor-pointer transition-all duration-200 ${
            selectedPlanId === plan.id
              ? 'border-blue-600 ring-2 ring-blue-200'
              : 'border-gray-200 hover:border-gray-300'
          }`}
          onClick={() => handlePlanSelect(plan.id)}
        >
          {plan.id === 'premium' && (
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                Most Popular
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
            
            <button
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                selectedPlanId === plan.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
              }`}
              onClick={() => handlePlanSelect(plan.id)}
            >
              {selectedPlanId === plan.id ? 'Selected' : 'Select Plan'}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SubscriptionPlans;
