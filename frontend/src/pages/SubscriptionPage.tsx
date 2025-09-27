import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { CheckIcon } from '@heroicons/react/24/outline';

const plans = [
  {
    name: 'Basic',
    price: '$29',
    features: [
      'Basic Trading Signals',
      'Limited to 1 Strategy',
      'Email Support',
      'Community Access',
    ],
    cta: 'Choose Basic',
    current: false,
  },
  {
    name: 'Premium',
    price: '$79',
    features: [
      'Advanced Trading Signals',
      'Up to 5 Strategies',
      'Priority Email Support',
      'Exclusive Community Access',
      'Basic Analytics',
    ],
    cta: 'Choose Premium',
    current: true,
  },
  {
    name: 'Pro',
    price: '$199',
    features: [
      'All Premium Features',
      'Unlimited Strategies',
      'Real-time Market Analysis',
      'API Access',
      'Dedicated Support',
    ],
    cta: 'Choose Pro',
    current: false,
  },
];

const SubscriptionPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800">Subscription Plans</h1>
        <p className="mt-2 text-lg text-gray-600">
          Choose the plan that's right for your trading needs.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.current ? 'border-primary-500 border-2' : ''}>
            <CardHeader className="text-center">
              <CardTitle className="text-xl font-semibold">{plan.name}</CardTitle>
              <CardDescription className="text-4xl font-bold text-gray-800">
                {plan.price}
                <span className="text-sm font-normal text-gray-500">/month</span>
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center">
                    <CheckIcon className="h-5 w-5 text-green-500 mr-3" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button
                variant={plan.current ? 'secondary' : 'primary'}
                className="w-full"
                disabled={plan.current}
              >
                {plan.current ? 'Current Plan' : plan.cta}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default SubscriptionPage;