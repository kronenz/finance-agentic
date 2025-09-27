import React, { useState, useEffect } from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine,
  Legend
} from 'recharts';
import { motion } from 'framer-motion';

interface VWAPData {
  time: string;
  price: number;
  vwap: number;
  volume: number;
  upperBand: number;
  lowerBand: number;
  deviation: number;
}

const VwapChart: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [vwapData, setVwapData] = useState<VWAPData[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');

  // Generate mock VWAP data
  const generateMockVWAPData = (): VWAPData[] => {
    const data: VWAPData[] = [];
    const now = new Date();
    let basePrice = 60000;
    let cumulativeVolume = 0;
    let cumulativeVolumePrice = 0;
    
    for (let i = 0; i < 100; i++) {
      const time = new Date(now.getTime() - (99 - i) * 60000);
      const change = (Math.random() - 0.5) * 1000;
      basePrice += change;
      
      const volume = Math.random() * 1000000 + 100000;
      const price = basePrice;
      
      cumulativeVolume += volume;
      cumulativeVolumePrice += price * volume;
      const vwap = cumulativeVolumePrice / cumulativeVolume;
      
      const deviation = 0.02; // 2% deviation
      const upperBand = vwap * (1 + deviation);
      const lowerBand = vwap * (1 - deviation);
      
      data.push({
        time: time.toISOString().substr(11, 5),
        price: Math.round(price),
        vwap: Math.round(vwap),
        volume: Math.round(volume),
        upperBand: Math.round(upperBand),
        lowerBand: Math.round(lowerBand),
        deviation: ((price - vwap) / vwap) * 100
      });
    }
    return data;
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setVwapData(generateMockVWAPData());
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-neutral-600 dark:text-neutral-400">Loading VWAP chart...</span>
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

  const currentVWAP = vwapData[vwapData.length - 1]?.vwap || 0;
  const currentPrice = vwapData[vwapData.length - 1]?.price || 0;
  const currentDeviation = vwapData[vwapData.length - 1]?.deviation || 0;

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
            VWAP Analysis - {selectedSymbol}
          </h2>
          <div className="flex items-center space-x-4 mt-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Price</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">VWAP</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Bands</span>
            </div>
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

      {/* VWAP Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3">
          <div className="text-sm text-neutral-600 dark:text-neutral-400">Current VWAP</div>
          <div className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            ${currentVWAP.toLocaleString()}
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3">
          <div className="text-sm text-neutral-600 dark:text-neutral-400">Price Deviation</div>
          <div className={`text-lg font-semibold ${
            currentDeviation > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            {currentDeviation > 0 ? '+' : ''}{currentDeviation.toFixed(2)}%
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3">
          <div className="text-sm text-neutral-600 dark:text-neutral-400">Price vs VWAP</div>
          <div className={`text-lg font-semibold ${
            currentPrice > currentVWAP ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            ${(currentPrice - currentVWAP).toLocaleString()}
          </div>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={vwapData}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="vwapGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
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
                name === 'price' ? 'Price' : 
                name === 'vwap' ? 'VWAP' :
                name === 'upperBand' ? 'Upper Band' :
                name === 'lowerBand' ? 'Lower Band' : name
              ]}
              labelStyle={{ color: '#f9fafb' }}
            />
            <Legend />
            
            {/* Price Area */}
            <Area
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#priceGradient)"
              name="Price"
            />
            
            {/* VWAP Line */}
            <Area
              type="monotone"
              dataKey="vwap"
              stroke="#10b981"
              strokeWidth={2}
              fill="#10b981"
              fillOpacity={0.1}
              dot={false}
              name="VWAP"
            />
            
            {/* Upper Band */}
            <Area
              type="monotone"
              dataKey="upperBand"
              stroke="#ef4444"
              strokeWidth={1}
              strokeDasharray="5 5"
              fill="transparent"
              dot={false}
              name="Upper Band"
            />
            
            {/* Lower Band */}
            <Area
              type="monotone"
              dataKey="lowerBand"
              stroke="#ef4444"
              strokeWidth={1}
              strokeDasharray="5 5"
              fill="transparent"
              dot={false}
              name="Lower Band"
            />
            
            {/* Current VWAP Reference Line */}
            <ReferenceLine 
              y={currentVWAP} 
              stroke="#10b981" 
              strokeDasharray="2 2"
              label={{ value: "Current VWAP", position: "top" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Profile */}
      <div className="mt-4">
        <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Volume Distribution</h3>
        <div className="h-16 bg-neutral-50 dark:bg-neutral-700 rounded-lg p-2">
          <div className="flex items-end h-full space-x-1">
            {vwapData.slice(-20).map((data, index) => (
              <div
                key={index}
                className="flex-1 bg-blue-200 dark:bg-blue-800 rounded-sm"
                style={{ 
                  height: `${(data.volume / Math.max(...vwapData.map(d => d.volume))) * 100}%` 
                }}
                title={`Volume: ${data.volume.toLocaleString()}`}
              />
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default VwapChart;