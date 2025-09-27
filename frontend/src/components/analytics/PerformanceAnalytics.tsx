import React, { useState, useEffect } from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/solid';

interface PerformanceData {
  date: string;
  portfolioValue: number;
  benchmarkValue: number;
  dailyReturn: number;
  cumulativeReturn: number;
  volatility: number;
  sharpeRatio: number;
  maxDrawdown: number;
}

interface AssetAllocation {
  symbol: string;
  allocation: number;
  value: number;
  color: string;
}

const PerformanceAnalytics: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [assetAllocation, setAssetAllocation] = useState<AssetAllocation[]>([]);
  const [timeRange, setTimeRange] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('3M');

  // Generate mock performance data
  const generateMockPerformanceData = (): PerformanceData[] => {
    const data: PerformanceData[] = [];
    const now = new Date();
    const days = timeRange === '1M' ? 30 : timeRange === '3M' ? 90 : timeRange === '6M' ? 180 : timeRange === '1Y' ? 365 : 730;
    
    let portfolioValue = 100000;
    let benchmarkValue = 100000;
    let cumulativeReturn = 0;
    let maxValue = portfolioValue;
    let maxDrawdown = 0;

    for (let i = 0; i < days; i++) {
      const date = new Date(now.getTime() - (days - i) * 24 * 60 * 60 * 1000);
      const dailyReturn = (Math.random() - 0.5) * 0.05; // ±2.5% daily return
      const benchmarkReturn = (Math.random() - 0.5) * 0.03; // ±1.5% benchmark return
      
      portfolioValue *= (1 + dailyReturn);
      benchmarkValue *= (1 + benchmarkReturn);
      cumulativeReturn += dailyReturn;
      
      // Calculate max drawdown
      if (portfolioValue > maxValue) {
        maxValue = portfolioValue;
      }
      const currentDrawdown = (maxValue - portfolioValue) / maxValue;
      if (currentDrawdown > maxDrawdown) {
        maxDrawdown = currentDrawdown;
      }

      // Calculate volatility (simplified)
      const volatility = Math.abs(dailyReturn) * Math.sqrt(252); // Annualized
      const sharpeRatio = (dailyReturn * 252) / (volatility * Math.sqrt(252)); // Simplified Sharpe

      data.push({
        date: date.toISOString().split('T')[0],
        portfolioValue: Math.round(portfolioValue),
        benchmarkValue: Math.round(benchmarkValue),
        dailyReturn: Math.round(dailyReturn * 10000) / 100, // In basis points
        cumulativeReturn: Math.round(cumulativeReturn * 10000) / 100,
        volatility: Math.round(volatility * 10000) / 100,
        sharpeRatio: Math.round(sharpeRatio * 100) / 100,
        maxDrawdown: Math.round(maxDrawdown * 10000) / 100
      });
    }

    return data;
  };

  // Generate mock asset allocation
  const generateMockAssetAllocation = (): AssetAllocation[] => {
    const assets = [
      { symbol: 'BTC', allocation: 40, color: '#f59e0b' },
      { symbol: 'ETH', allocation: 25, color: '#3b82f6' },
      { symbol: 'BNB', allocation: 15, color: '#f97316' },
      { symbol: 'ADA', allocation: 10, color: '#8b5cf6' },
      { symbol: 'SOL', allocation: 10, color: '#10b981' }
    ];

    const totalValue = 100000;
    return assets.map(asset => ({
      ...asset,
      value: Math.round(totalValue * asset.allocation / 100)
    }));
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setPerformanceData(generateMockPerformanceData());
      setAssetAllocation(generateMockAssetAllocation());
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, [timeRange]);

  const currentValue = performanceData[performanceData.length - 1]?.portfolioValue || 0;
  const initialValue = performanceData[0]?.portfolioValue || 100000;
  const totalReturn = ((currentValue - initialValue) / initialValue) * 100;
  const benchmarkReturn = performanceData.length > 0 ? 
    ((performanceData[performanceData.length - 1]?.benchmarkValue - performanceData[0]?.benchmarkValue) / performanceData[0]?.benchmarkValue) * 100 : 0;
  const alpha = totalReturn - benchmarkReturn;
  const currentVolatility = performanceData[performanceData.length - 1]?.volatility || 0;
  const currentSharpe = performanceData[performanceData.length - 1]?.sharpeRatio || 0;
  const maxDrawdown = performanceData[performanceData.length - 1]?.maxDrawdown || 0;

  const formatNumber = (num: number, decimals: number = 2) => {
    if (num >= 1e9) return `$${(num / 1e9).toFixed(decimals)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(decimals)}M`;
    if (num >= 1e3) return `$${(num / 1e3).toFixed(decimals)}K`;
    return `$${num.toFixed(decimals)}`;
  };

  const getReturnColor = (returnValue: number) => {
    if (returnValue > 0) return 'text-green-600 dark:text-green-400';
    if (returnValue < 0) return 'text-red-600 dark:text-red-400';
    return 'text-neutral-600 dark:text-neutral-400';
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-neutral-600 dark:text-neutral-400">Loading performance analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="text-red-600 dark:text-red-400">Error: {error}</div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">
          Performance Analytics
        </h2>
        <div className="flex space-x-2">
          {['1M', '3M', '6M', '1Y', 'ALL'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range as any)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-600'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CurrencyDollarIcon className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Total Return</span>
          </div>
          <div className={`text-2xl font-bold ${getReturnColor(totalReturn)}`}>
            {totalReturn > 0 ? '+' : ''}{totalReturn.toFixed(2)}%
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ArrowTrendingUpIcon className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Alpha</span>
          </div>
          <div className={`text-2xl font-bold ${getReturnColor(alpha)}`}>
            {alpha > 0 ? '+' : ''}{alpha.toFixed(2)}%
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ChartBarIcon className="w-5 h-5 text-orange-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Sharpe Ratio</span>
          </div>
          <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            {currentSharpe.toFixed(2)}
          </div>
            </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ArrowTrendingDownIcon className="w-5 h-5 text-red-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Max Drawdown</span>
            </div>
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">
            -{maxDrawdown.toFixed(2)}%
            </div>
            </div>
            </div>

      {/* Performance Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            Portfolio vs Benchmark
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="benchmarkGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6b7280"
                  fontSize={12}
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis 
                  stroke="#6b7280"
                  fontSize={12}
                  tickFormatter={(value) => formatNumber(value)}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f9fafb'
                  }}
                  formatter={(value: any, name: string) => [
                    formatNumber(value),
                    name === 'portfolioValue' ? 'Portfolio' : 'Benchmark'
                  ]}
                  labelStyle={{ color: '#f9fafb' }}
                />
                <Area
                  type="monotone"
                  dataKey="portfolioValue"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#portfolioGradient)"
                  name="Portfolio"
                />
                <Area
                  type="monotone"
                  dataKey="benchmarkValue"
                  stroke="#10b981"
                  strokeWidth={2}
                  fill="url(#benchmarkGradient)"
                  name="Benchmark"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            Asset Allocation
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={assetAllocation}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="allocation"
                >
                  {assetAllocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f9fafb'
                  }}
                  formatter={(value: any, name: string) => [
                    `${value}%`,
                    name === 'allocation' ? 'Allocation' : 'Value'
                  ]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {assetAllocation.map((asset, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: asset.color }}
                  />
                  <span className="text-sm text-neutral-600 dark:text-neutral-400">
                    {asset.symbol}
                  </span>
                </div>
                <span className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                  {asset.allocation}%
                </span>
              </div>
            ))}
          </div>
        </div>
        </div>

      {/* Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <h4 className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-2">Volatility</h4>
          <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            {currentVolatility.toFixed(2)}%
          </div>
          <div className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
            Annualized
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <h4 className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-2">Beta</h4>
          <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            1.23
          </div>
          <div className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
            vs Market
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <h4 className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-2">VaR (95%)</h4>
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">
            -2.5%
          </div>
          <div className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
            Daily
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default PerformanceAnalytics;