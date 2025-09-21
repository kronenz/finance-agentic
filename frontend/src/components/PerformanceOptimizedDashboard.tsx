// 성능 최적화된 대시보드 컴포넌트
import React, { useState, useEffect, useMemo, useCallback, lazy, Suspense } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';

// 코드 스플리팅을 위한 지연 로딩
const AIDashboard = lazy(() => import('./AIDashboard'));
const SubscriptionManagement = lazy(() => import('./SubscriptionManagement'));
const TradingChart = lazy(() => import('./TradingChart'));

// 메모이제이션된 컴포넌트
const MemoizedCard = React.memo(({ title, value, loading }: { title: string; value: string | number; loading: boolean }) => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
    {loading ? (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded"></div>
      </div>
    ) : (
      <p className="text-3xl font-bold text-blue-600">{value}</p>
    )}
  </div>
));

const MemoizedChart = React.memo(({ data, type }: { data: any[]; type: string }) => {
  // 차트 렌더링 로직 (실제로는 차트 라이브러리 사용)
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Chart: {type}</h3>
      <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
        <p className="text-gray-500">Chart placeholder ({data.length} data points)</p>
      </div>
    </div>
  );
});

const PerformanceOptimizedDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState({
    totalValue: 0,
    dailyChange: 0,
    activeStrategies: 0,
    riskScore: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { user } = useSelector((state: RootState) => state.auth);

  // 메모이제이션된 데이터 처리
  const processedData = useMemo(() => {
    return {
      totalValue: dashboardData.totalValue.toLocaleString('en-US', {
        style: 'currency',
        currency: 'USD'
      }),
      dailyChange: dashboardData.dailyChange > 0 ? `+${dashboardData.dailyChange.toFixed(2)}%` : `${dashboardData.dailyChange.toFixed(2)}%`,
      changeColor: dashboardData.dailyChange >= 0 ? 'text-green-600' : 'text-red-600'
    };
  }, [dashboardData]);

  // 메모이제이션된 차트 데이터
  const chartData = useMemo(() => {
    // 실제로는 API에서 가져온 데이터를 처리
    return Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      value: Math.random() * 1000 + 50000
    }));
  }, []);

  // 메모이제이션된 이벤트 핸들러
  const handleTabChange = useCallback((tab: string) => {
    setActiveTab(tab);
  }, []);

  const handleRefresh = useCallback(async () => {
    setLoading(true);
    try {
      // 실제로는 API 호출
      await new Promise(resolve => setTimeout(resolve, 1000));
      setDashboardData({
        totalValue: Math.random() * 100000 + 50000,
        dailyChange: (Math.random() - 0.5) * 10,
        activeStrategies: Math.floor(Math.random() * 5) + 1,
        riskScore: Math.random() * 100
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh data');
    } finally {
      setLoading(false);
    }
  }, []);

  // 초기 데이터 로드
  useEffect(() => {
    if (user) {
      handleRefresh();
    }
  }, [user, handleRefresh]);

  // 탭별 컴포넌트 렌더링
  const renderTabContent = () => {
    switch (activeTab) {
      case 'ai':
        return (
          <Suspense fallback={<div className="animate-pulse h-64 bg-gray-200 rounded"></div>}>
            <AIDashboard />
          </Suspense>
        );
      case 'subscriptions':
        return (
          <Suspense fallback={<div className="animate-pulse h-64 bg-gray-200 rounded"></div>}>
            <SubscriptionManagement />
          </Suspense>
        );
      case 'trading':
        return (
          <Suspense fallback={<div className="animate-pulse h-64 bg-gray-200 rounded"></div>}>
            <TradingChart data={chartData} />
          </Suspense>
        );
      default:
        return (
          <div className="space-y-6">
            {/* 개요 카드들 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MemoizedCard
                title="Total Portfolio Value"
                value={processedData.totalValue}
                loading={loading}
              />
              <MemoizedCard
                title="Daily Change"
                value={processedData.dailyChange}
                loading={loading}
              />
              <MemoizedCard
                title="Active Strategies"
                value={dashboardData.activeStrategies}
                loading={loading}
              />
              <MemoizedCard
                title="Risk Score"
                value={`${dashboardData.riskScore.toFixed(1)}%`}
                loading={loading}
              />
            </div>

            {/* 차트 섹션 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <MemoizedChart data={chartData} type="Portfolio Value" />
              <MemoizedChart data={chartData} type="Risk Metrics" />
            </div>

            {/* 최근 활동 */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {loading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="animate-pulse flex items-center space-x-3">
                      <div className="h-4 bg-gray-200 rounded w-4"></div>
                      <div className="h-4 bg-gray-200 rounded flex-1"></div>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-500">No recent activity</div>
                )}
              </div>
            </div>
          </div>
        );
    }
  };

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Error: {error}</p>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Trading Dashboard</h1>
        <p className="text-gray-600">AI-powered cryptocurrency trading platform</p>
      </div>

      {/* 탭 네비게이션 */}
      <div className="mb-6">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', name: 'Overview' },
            { id: 'ai', name: 'AI Analysis' },
            { id: 'subscriptions', name: 'Subscriptions' },
            { id: 'trading', name: 'Trading' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* 탭 컨텐츠 */}
      <div className="min-h-96">
        {renderTabContent()}
      </div>

      {/* 새로고침 버튼 */}
      <div className="mt-6 text-center">
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>
    </div>
  );
};

export default PerformanceOptimizedDashboard;
