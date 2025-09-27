import React, { useState, useEffect } from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine
} from 'recharts';
import { motion } from 'framer-motion';

interface PriceData {
  time: string;
  price: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  close: number;
}

const PriceChart: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');

  // Generate mock data for demonstration
  const generateMockData = () => {
    const data: PriceData[] = [];
    const now = new Date();
    let basePrice = 60000; // BTC starting price
    
    for (let i = 0; i < 100; i++) {
      const time = new Date(now.getTime() - (99 - i) * 60000); // 1 minute intervals
      const change = (Math.random() - 0.5) * 1000; // Random price change
      basePrice += change;
      
      const high = basePrice + Math.random() * 200;
      const low = basePrice - Math.random() * 200;
      const open = i === 0 ? basePrice : data[i - 1].close;
      const close = basePrice;
      const volume = Math.random() * 1000000;
      
      data.push({
        time: time.toISOString().substr(11, 5),
        price: Math.round(basePrice),
        volume: Math.round(volume),
        high: Math.round(high),
        low: Math.round(low),
        open: Math.round(open),
        close: Math.round(close)
      });
    }
    return data;
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setPriceData(generateMockData());
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-neutral-600 dark:text-neutral-400">Loading price chart...</span>
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

  const currentPrice = priceData[priceData.length - 1]?.price || 0;
  const previousPrice = priceData[priceData.length - 2]?.price || 0;
  const priceChange = currentPrice - previousPrice;
  const priceChangePercent = previousPrice ? (priceChange / previousPrice) * 100 : 0;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6"
    >
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">
            {selectedSymbol}
          </h2>
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              ${currentPrice.toLocaleString()}
            </span>
            <span className={`text-sm font-medium ${
              priceChange >= 0 
                ? 'text-green-600 dark:text-green-400' 
                : 'text-red-600 dark:text-red-400'
            }`}>
              {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
            </span>
          </div>
        </div>
        <div className="flex space-x-2">
          {['BTC/USDT', 'ETH/USDT', 'BNB/USDT'].map((symbol) => (
            <button
              key={symbol}
              onClick={() => setSelectedSymbol(symbol)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                selectedSymbol === symbol
                  ? 'bg-blue-600 text-white'
                  : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-600'
              }`}
            >
              {symbol}
            </button>
          ))}
        </div>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={priceData}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="time" 
              stroke="#6b7280"
              fontSize={12}
            />
            <YAxis 
              domain={['dataMin - 1000', 'dataMax + 1000']}
              stroke="#6b7280"
              fontSize={12}
              tickFormatter={(value) => `$${value.toLocaleString()}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#f9fafb'
              }}
              formatter={(value: any, name: string) => [
                `$${value.toLocaleString()}`,
                name === 'price' ? 'Price' : name
              ]}
              labelStyle={{ color: '#f9fafb' }}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#priceGradient)"
            />
                   <ReferenceLine
                     y={currentPrice}
                     stroke="#10b981"
                     strokeDasharray="2 2"
                     label={{ value: "Current", position: "top" }}
                   />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};

export default PriceChart;
