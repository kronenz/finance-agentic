import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowUpIcon,
  ArrowDownIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/solid';

interface Trade {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  total: number;
  pnl: number;
  pnlPercent: number;
  timestamp: Date;
  status: 'OPEN' | 'CLOSED' | 'PARTIAL';
  strategy: string;
}

const TradingHistory: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'BUY' | 'SELL' | 'OPEN' | 'CLOSED'>('ALL');
  const [sortBy, setSortBy] = useState<'timestamp' | 'pnl' | 'total'>('timestamp');

  // Generate mock trading data
  const generateMockTrades = (): Trade[] => {
    const symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'];
    const strategies = ['Momentum', 'Mean Reversion', 'Breakout', 'Scalping', 'Swing'];
    const trades: Trade[] = [];

    for (let i = 0; i < 50; i++) {
      const symbol = symbols[Math.floor(Math.random() * symbols.length)];
      const type = Math.random() > 0.5 ? 'BUY' : 'SELL';
      const quantity = Math.random() * 10 + 0.1;
      const price = Math.random() * 100000 + 10000;
      const total = quantity * price;
      const pnl = (Math.random() - 0.5) * total * 0.1; // ±10% PnL
      const pnlPercent = (pnl / total) * 100;
      const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000); // Last 7 days
      const status = Math.random() > 0.3 ? 'CLOSED' : 'OPEN';
      const strategy = strategies[Math.floor(Math.random() * strategies.length)];

      trades.push({
        id: `trade-${i + 1}`,
        symbol,
        type,
        quantity: Math.round(quantity * 1000) / 1000,
        price: Math.round(price * 100) / 100,
        total: Math.round(total * 100) / 100,
        pnl: Math.round(pnl * 100) / 100,
        pnlPercent: Math.round(pnlPercent * 100) / 100,
        timestamp,
        status,
        strategy
      });
    }

    return trades.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setTrades(generateMockTrades());
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  const filteredTrades = trades.filter(trade => {
    if (filter === 'ALL') return true;
    if (filter === 'BUY' || filter === 'SELL') return trade.type === filter;
    return trade.status === filter;
  });

  const sortedTrades = [...filteredTrades].sort((a, b) => {
    switch (sortBy) {
      case 'timestamp':
        return b.timestamp.getTime() - a.timestamp.getTime();
      case 'pnl':
        return b.pnl - a.pnl;
      case 'total':
        return b.total - a.total;
      default:
        return 0;
    }
  });

  const totalPnL = trades.reduce((sum, trade) => sum + trade.pnl, 0);
  const totalVolume = trades.reduce((sum, trade) => sum + trade.total, 0);
  const winRate = trades.filter(trade => trade.pnl > 0).length / trades.length * 100;
  const avgPnL = totalPnL / trades.length;

  const formatNumber = (num: number, decimals: number = 2) => {
    if (num >= 1e9) return `$${(num / 1e9).toFixed(decimals)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(decimals)}M`;
    if (num >= 1e3) return `$${(num / 1e3).toFixed(decimals)}K`;
    return `$${num.toFixed(decimals)}`;
  };

  const getPnLColor = (pnl: number) => {
    if (pnl > 0) return 'text-green-600 dark:text-green-400';
    if (pnl < 0) return 'text-red-600 dark:text-red-400';
    return 'text-neutral-600 dark:text-neutral-400';
  };

  const getPnLBgColor = (pnl: number) => {
    if (pnl > 0) return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
    if (pnl < 0) return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
    return 'bg-neutral-50 dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700';
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-neutral-600 dark:text-neutral-400">Loading trading history...</span>
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
          Trading History
        </h2>
        <div className="flex space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="px-3 py-1 rounded-md text-sm border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300"
          >
            <option value="ALL">All Trades</option>
            <option value="BUY">Buy Orders</option>
            <option value="SELL">Sell Orders</option>
            <option value="OPEN">Open Positions</option>
            <option value="CLOSED">Closed Positions</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1 rounded-md text-sm border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300"
          >
            <option value="timestamp">Time</option>
            <option value="pnl">PnL</option>
            <option value="total">Volume</option>
          </select>
        </div>
      </div>

      {/* Trading Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CurrencyDollarIcon className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Total P&L</span>
          </div>
          <div className={`text-2xl font-bold ${getPnLColor(totalPnL)}`}>
            {formatNumber(totalPnL)}
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ChartBarIcon className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Total Volume</span>
          </div>
          <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
            {formatNumber(totalVolume)}
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ArrowTrendingUpIcon className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Win Rate</span>
          </div>
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {winRate.toFixed(1)}%
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <ArrowTrendingDownIcon className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Avg P&L</span>
          </div>
          <div className={`text-2xl font-bold ${getPnLColor(avgPnL)}`}>
            {formatNumber(avgPnL)}
          </div>
        </div>
      </div>

      {/* Trades Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-200 dark:border-neutral-700">
              <th className="text-left py-3 text-neutral-600 dark:text-neutral-400">Time</th>
              <th className="text-left py-3 text-neutral-600 dark:text-neutral-400">Symbol</th>
              <th className="text-left py-3 text-neutral-600 dark:text-neutral-400">Type</th>
              <th className="text-right py-3 text-neutral-600 dark:text-neutral-400">Quantity</th>
              <th className="text-right py-3 text-neutral-600 dark:text-neutral-400">Price</th>
              <th className="text-right py-3 text-neutral-600 dark:text-neutral-400">Total</th>
              <th className="text-right py-3 text-neutral-600 dark:text-neutral-400">P&L</th>
              <th className="text-left py-3 text-neutral-600 dark:text-neutral-400">Strategy</th>
              <th className="text-center py-3 text-neutral-600 dark:text-neutral-400">Status</th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {sortedTrades.map((trade, index) => (
                <motion.tr
                  key={trade.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.02 }}
                  className={`border-b border-neutral-100 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700/50 ${getPnLBgColor(trade.pnl)}`}
                >
                  <td className="py-3 text-neutral-600 dark:text-neutral-400">
                    <div className="flex items-center space-x-2">
                      <ClockIcon className="w-4 h-4" />
                      <span>{trade.timestamp.toLocaleTimeString()}</span>
                    </div>
                  </td>
                  <td className="py-3 font-medium text-neutral-900 dark:text-neutral-100">
                    {trade.symbol}
                  </td>
                  <td className="py-3">
                    <div className="flex items-center space-x-2">
                      {trade.type === 'BUY' ? (
                        <ArrowUpIcon className="w-4 h-4 text-green-500" />
                      ) : (
                        <ArrowDownIcon className="w-4 h-4 text-red-500" />
                      )}
                      <span className={`font-medium ${
                        trade.type === 'BUY' 
                          ? 'text-green-600 dark:text-green-400' 
                          : 'text-red-600 dark:text-red-400'
                      }`}>
                        {trade.type}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 text-right text-neutral-600 dark:text-neutral-400">
                    {trade.quantity.toFixed(3)}
                  </td>
                  <td className="py-3 text-right text-neutral-600 dark:text-neutral-400">
                    {formatNumber(trade.price)}
                  </td>
                  <td className="py-3 text-right text-neutral-600 dark:text-neutral-400">
                    {formatNumber(trade.total)}
                  </td>
                  <td className="py-3 text-right">
                    <div className="flex flex-col items-end">
                      <span className={`font-medium ${getPnLColor(trade.pnl)}`}>
                        {formatNumber(trade.pnl)}
                      </span>
                      <span className={`text-xs ${getPnLColor(trade.pnl)}`}>
                        {trade.pnlPercent > 0 ? '+' : ''}{trade.pnlPercent.toFixed(2)}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3 text-neutral-600 dark:text-neutral-400">
                    {trade.strategy}
                  </td>
                  <td className="py-3 text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      trade.status === 'OPEN' 
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        : trade.status === 'CLOSED'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                    }`}>
                      {trade.status}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {sortedTrades.length === 0 && (
        <div className="text-center py-8 text-neutral-500 dark:text-neutral-400">
          <ChartBarIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No trades found for the selected filter.</p>
        </div>
      )}
    </motion.div>
  );
};

export default TradingHistory;