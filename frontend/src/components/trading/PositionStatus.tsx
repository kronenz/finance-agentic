import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  ChartBarIcon
} from '@heroicons/react/24/solid';

interface Position {
  id: string;
  symbol: string;
  side: 'LONG' | 'SHORT';
  size: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnl: number;
  unrealizedPnlPercent: number;
  margin: number;
  marginLevel: number;
  timestamp: Date;
  stopLoss?: number;
  takeProfit?: number;
}

const PositionStatus: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [sortBy, setSortBy] = useState<'pnl' | 'size' | 'symbol'>('pnl');

  // Generate mock positions
  const generateMockPositions = (): Position[] => {
    const symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'];
    const sides: ('LONG' | 'SHORT')[] = ['LONG', 'SHORT'];
    
    return Array.from({ length: 5 }, (_, i) => {
      const symbol = symbols[Math.floor(Math.random() * symbols.length)];
      const side = sides[Math.floor(Math.random() * sides.length)];
      const entryPrice = Math.random() * 100000 + 10000;
      const currentPrice = entryPrice * (0.95 + Math.random() * 0.1); // ±5% variation
      const size = Math.random() * 10 + 0.1;
      const unrealizedPnl = side === 'LONG' 
        ? (currentPrice - entryPrice) * size
        : (entryPrice - currentPrice) * size;
      const unrealizedPnlPercent = (unrealizedPnl / (entryPrice * size)) * 100;
      const margin = entryPrice * size * 0.1; // 10% margin
      const marginLevel = (entryPrice * size) / margin;

      return {
        id: `position-${i + 1}`,
        symbol,
        side,
        size,
        entryPrice,
        currentPrice,
        unrealizedPnl,
        unrealizedPnlPercent,
        margin,
        marginLevel,
        timestamp: new Date(Date.now() - Math.random() * 86400000), // Last 24 hours
        stopLoss: entryPrice * (side === 'LONG' ? 0.95 : 1.05),
        takeProfit: entryPrice * (side === 'LONG' ? 1.1 : 0.9)
      };
    });
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setPositions(generateMockPositions());
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  const sortedPositions = [...positions].sort((a, b) => {
    switch (sortBy) {
      case 'pnl':
        return b.unrealizedPnl - a.unrealizedPnl;
      case 'size':
        return b.size - a.size;
      case 'symbol':
        return a.symbol.localeCompare(b.symbol);
      default:
        return 0;
    }
  });

  const totalPnl = positions.reduce((sum, pos) => sum + pos.unrealizedPnl, 0);
  const totalMargin = positions.reduce((sum, pos) => sum + pos.margin, 0);
  const avgMarginLevel = positions.length > 0 
    ? positions.reduce((sum, pos) => sum + pos.marginLevel, 0) / positions.length 
    : 0;

  const getPnlColor = (pnl: number) => {
    if (pnl > 0) return 'text-green-600 dark:text-green-400';
    if (pnl < 0) return 'text-red-600 dark:text-red-400';
    return 'text-neutral-600 dark:text-neutral-400';
  };

  const getPnlBgColor = (pnl: number) => {
    if (pnl > 0) return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
    if (pnl < 0) return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
    return 'bg-neutral-50 dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700';
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-neutral-600 dark:text-neutral-400">Loading positions...</span>
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
          Position Status
        </h2>
        <div className="flex space-x-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1 rounded-md text-sm border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300"
          >
            <option value="pnl">Sort by P&L</option>
            <option value="size">Sort by Size</option>
            <option value="symbol">Sort by Symbol</option>
          </select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CurrencyDollarIcon className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Total P&L</span>
          </div>
          <div className={`text-2xl font-bold ${getPnlColor(totalPnl)}`}>
            ${totalPnl.toLocaleString()}
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ChartBarIcon className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Total Margin</span>
          </div>
          <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            ${totalMargin.toLocaleString()}
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Avg Margin Level</span>
          </div>
          <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            {avgMarginLevel.toFixed(2)}x
          </div>
        </div>
      </div>

      {/* Positions List */}
      <div className="space-y-3">
        <AnimatePresence>
          {sortedPositions.map((position, index) => (
            <motion.div
              key={position.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border ${getPnlBgColor(position.unrealizedPnl)}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    {position.side === 'LONG' ? (
                      <ArrowUpIcon className="w-5 h-5 text-green-500" />
                    ) : (
                      <ArrowDownIcon className="w-5 h-5 text-red-500" />
                    )}
                    <span className="font-semibold text-neutral-900 dark:text-neutral-100">
                      {position.symbol}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      position.side === 'LONG' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {position.side}
                    </span>
                  </div>
                  <div className="text-sm text-neutral-600 dark:text-neutral-400">
                    Size: {position.size.toFixed(4)}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${getPnlColor(position.unrealizedPnl)}`}>
                    ${position.unrealizedPnl.toLocaleString()}
                  </div>
                  <div className={`text-sm ${getPnlColor(position.unrealizedPnl)}`}>
                    {position.unrealizedPnlPercent.toFixed(2)}%
                  </div>
                </div>
              </div>
              
              <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-neutral-500 dark:text-neutral-400">Entry:</span>
                  <span className="ml-1 font-medium text-neutral-900 dark:text-neutral-100">
                    ${position.entryPrice.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-neutral-500 dark:text-neutral-400">Current:</span>
                  <span className="ml-1 font-medium text-neutral-900 dark:text-neutral-100">
                    ${position.currentPrice.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-neutral-500 dark:text-neutral-400">Margin:</span>
                  <span className="ml-1 font-medium text-neutral-900 dark:text-neutral-100">
                    ${position.margin.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-neutral-500 dark:text-neutral-400">Level:</span>
                  <span className={`ml-1 font-medium ${
                    position.marginLevel < 2 ? 'text-red-600 dark:text-red-400' : 'text-neutral-900 dark:text-neutral-100'
                  }`}>
                    {position.marginLevel.toFixed(2)}x
                  </span>
                </div>
              </div>

              {(position.stopLoss || position.takeProfit) && (
                <div className="mt-3 pt-3 border-t border-neutral-200 dark:border-neutral-700">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {position.stopLoss && (
                      <div>
                        <span className="text-neutral-500 dark:text-neutral-400">Stop Loss:</span>
                        <span className="ml-1 font-medium text-red-600 dark:text-red-400">
                          ${position.stopLoss.toLocaleString()}
                        </span>
                      </div>
                    )}
                    {position.takeProfit && (
                      <div>
                        <span className="text-neutral-500 dark:text-neutral-400">Take Profit:</span>
                        <span className="ml-1 font-medium text-green-600 dark:text-green-400">
                          ${position.takeProfit.toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {positions.length === 0 && (
        <div className="text-center py-8 text-neutral-500 dark:text-neutral-400">
          <ChartBarIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No active positions found.</p>
        </div>
      )}
    </motion.div>
  );
};

export default PositionStatus;