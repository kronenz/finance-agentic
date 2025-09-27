import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import {
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const stats = [
  { name: 'Total Balance', stat: '$12,345.67', icon: CurrencyDollarIcon },
  { name: '24h P&L', stat: '+$583.21', icon: ArrowTrendingUpIcon },
  { name: 'Active Strategies', stat: '3', icon: CheckCircleIcon },
  { name: 'Last Trade', stat: '2h ago', icon: ClockIcon },
];

const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <Card key={item.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">{item.name}</CardTitle>
              <item.icon className="h-5 w-5 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{item.stat}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Performance Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">[Performance Chart Placeholder]</p>
          </div>
        </CardContent>
      </Card>

      {/* Recent Trades */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Trades</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-60 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">[Recent Trades List Placeholder]</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardPage;