import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowUpIcon,
  ArrowDownIcon,
  ExclamationTriangleIcon,
  ClockIcon
} from '@heroicons/react/24/solid';

interface TradingSignal {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL' | 'HOLD';
  price: number;
  confidence: number;
  strength: 'WEAK' | 'MEDIUM' | 'STRONG';
  timestamp: Date;
  reason: string;
  targetPrice?: number;
  stopLoss?: number;
}

const TradingSignals: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'BUY' | 'SELL' | 'HOLD'>('ALL');

  // Generate mock signals
  const generateMockSignals = (): TradingSignal[] => {
    const symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'];
    const types: ('BUY' | 'SELL' | 'HOLD')[] = ['BUY', 'SELL', 'HOLD'];
    const strengths: ('WEAK' | 'MEDIUM' | 'STRONG')[] = ['WEAK', 'MEDIUM', 'STRONG'];
    const reasons = [
      'RSI oversold condition detected',
      'Moving average crossover signal',
      'Volume spike with price breakout',
      'Support level bounce confirmed',
      'Resistance level rejection',
      'MACD bullish divergence',
      'Bollinger Bands squeeze',
      'Fibonacci retracement level'
    ];

    return Array.from({ length: 8 }, (_, i) => ({
      id: `signal-${i + 1}`,
      symbol: symbols[Math.floor(Math.random() * symbols.length)],
      type: types[Math.floor(Math.random() * types.length)],
      price: Math.random() * 100000 + 10000,
      confidence: Math.random() * 40 + 60, // 60-100%
      strength: strengths[Math.floor(Math.random() * strengths.length)],
      timestamp: new Date(Date.now() - Math.random() * 3600000), // Last hour
      reason: reasons[Math.floor(Math.random() * reasons.length)],
      targetPrice: Math.random() * 100000 + 10000,
      stopLoss: Math.random() * 100000 + 10000
    }));
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setSignals(generateMockSignals());
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  const filteredSignals = signals.filter(signal => 
    filter === 'ALL' || signal.type === filter
  );

  const getSignalIcon = (type: string) => {
    switch (type) {
      case 'BUY':
        return <ArrowUpIcon className="w-5 h-5 text-green-500" />;
      case 'SELL':
        return <ArrowDownIcon className="w-5 h-5 text-red-500" />;
      case 'HOLD':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      default:
        return null;
    }
  };

  const getStrengthColor = (strength: string) => {
    switch (strength) {
      case 'WEAK':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'MEDIUM':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'STRONG':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600 dark:text-green-400';
    if (confidence >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-neutral-600 dark:text-neutral-400">Loading signals...</span>
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
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">
          Trading Signals
        </h2>
        <div className="flex space-x-1">
          {['ALL', 'BUY', 'SELL', 'HOLD'].map((filterType) => (
            <button
              key={filterType}
              onClick={() => setFilter(filterType as any)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                filter === filterType
                  ? 'bg-blue-600 text-white'
                  : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-600'
              }`}
            >
              {filterType}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        <AnimatePresence>
          {filteredSignals.map((signal, index) => (
            <motion.div
              key={signal.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-l-4 ${
                signal.type === 'BUY' 
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
                  : signal.type === 'SELL'
                  ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                  : 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  {getSignalIcon(signal.type)}
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-neutral-900 dark:text-neutral-100">
                        {signal.symbol}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStrengthColor(signal.strength)}`}>
                        {signal.strength}
                      </span>
                    </div>
                    <div className="text-sm text-neutral-600 dark:text-neutral-400">
                      {signal.type} @ ${signal.price.toLocaleString()}
                    </div>
                    <div className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
                      {signal.reason}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-medium ${getConfidenceColor(signal.confidence)}`}>
                    {signal.confidence.toFixed(0)}% confidence
                  </div>
                  <div className="text-xs text-neutral-500 dark:text-neutral-500">
                    {signal.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
              
              {(signal.targetPrice || signal.stopLoss) && (
                <div className="mt-3 pt-3 border-t border-neutral-200 dark:border-neutral-700">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {signal.targetPrice && (
                      <div>
                        <span className="text-neutral-500 dark:text-neutral-400">Target:</span>
                        <span className="ml-1 font-medium text-green-600 dark:text-green-400">
                          ${signal.targetPrice.toLocaleString()}
                        </span>
                      </div>
                    )}
                    {signal.stopLoss && (
                      <div>
                        <span className="text-neutral-500 dark:text-neutral-400">Stop Loss:</span>
                        <span className="ml-1 font-medium text-red-600 dark:text-red-400">
                          ${signal.stopLoss.toLocaleString()}
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

      {filteredSignals.length === 0 && (
        <div className="text-center py-8 text-neutral-500 dark:text-neutral-400">
          <ExclamationTriangleIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No signals found for the selected filter.</p>
        </div>
      )}
    </motion.div>
  );
};

export default TradingSignals;
