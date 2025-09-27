import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine
} from 'recharts';
import { motion } from 'framer-motion';

interface VolumeProfileData {
  price: number;
  volume: number;
  percentage: number;
  color: string;
}

const VolumeProfileChart: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [volumeData, setVolumeData] = useState<VolumeProfileData[]>([]);
  const [selectedSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1H');

  // Generate mock volume profile data
  const generateMockVolumeData = (): VolumeProfileData[] => {
    const data: VolumeProfileData[] = [];
    const basePrice = 60000;
    const priceRange = 2000; // ±$2000 range
    const maxVolume = 1000000;
    
    // Generate price levels
    for (let i = 0; i < 20; i++) {
      const price = basePrice - priceRange + (i * (priceRange * 2) / 19);
      const volume = Math.random() * maxVolume;
      const percentage = (volume / maxVolume) * 100;
      
      // Color based on volume intensity
      let color = '#3b82f6'; // Default blue
      if (percentage > 80) color = '#ef4444'; // High volume - red
      else if (percentage > 60) color = '#f59e0b'; // Medium-high - orange
      else if (percentage > 40) color = '#10b981'; // Medium - green
      else if (percentage > 20) color = '#3b82f6'; // Low-medium - blue
      else color = '#6b7280'; // Low - gray
      
      data.push({
        price: Math.round(price),
        volume: Math.round(volume),
        percentage: Math.round(percentage),
        color
      });
    }
    
    return data.sort((a, b) => a.price - b.price);
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setVolumeData(generateMockVolumeData());
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-neutral-600 dark:text-neutral-400">Loading volume profile...</span>
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

  // const maxVolume = Math.max(...volumeData.map(d => d.volume));
  const totalVolume = volumeData.reduce((sum, d) => sum + d.volume, 0);
  const avgPrice = volumeData.reduce((sum, d) => sum + (d.price * d.volume), 0) / totalVolume;
  const vwap = avgPrice;

  // Find POC (Point of Control) - highest volume
  const poc = volumeData.reduce((max, d) => d.volume > max.volume ? d : max, volumeData[0]);

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
            Volume Profile - {selectedSymbol}
          </h2>
          <div className="flex items-center space-x-4 mt-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">High Volume</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Normal Volume</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Low Volume</span>
            </div>
          </div>
        </div>
        <div className="flex space-x-2">
          {['1H', '4H', '1D'].map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                timeframe === tf
                  ? 'bg-blue-600 text-white'
                  : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-600'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Volume Profile Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3">
          <div className="text-sm text-neutral-600 dark:text-neutral-400">VWAP</div>
          <div className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            ${vwap.toLocaleString()}
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3">
          <div className="text-sm text-neutral-600 dark:text-neutral-400">POC (Point of Control)</div>
          <div className="text-lg font-semibold text-red-600 dark:text-red-400">
            ${poc.price.toLocaleString()}
          </div>
        </div>
        <div className="bg-neutral-50 dark:bg-neutral-700 rounded-lg p-3">
          <div className="text-sm text-neutral-600 dark:text-neutral-400">Total Volume</div>
          <div className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            {totalVolume.toLocaleString()}
          </div>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={volumeData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              type="number"
              domain={[0, 'dataMax']}
              stroke="#6b7280"
              fontSize={12}
              tickFormatter={(value) => value.toLocaleString()}
            />
            <YAxis 
              type="number"
              dataKey="price"
              stroke="#6b7280"
              fontSize={12}
              tickFormatter={(value) => `$${value.toLocaleString()}`}
              width={80}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#f9fafb'
              }}
              formatter={(value: any, name: string) => [
                name === 'volume' ? value.toLocaleString() : value,
                name === 'volume' ? 'Volume' : 'Price'
              ]}
              labelStyle={{ color: '#f9fafb' }}
              labelFormatter={(value) => `Price: $${value.toLocaleString()}`}
            />
            
            <Bar dataKey="volume" radius={[0, 4, 4, 0]}>
              {volumeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
            
            {/* VWAP Reference Line */}
            <ReferenceLine 
              y={vwap} 
              stroke="#10b981" 
              strokeDasharray="2 2"
              label={{ value: "VWAP", position: "top" }}
            />
            
            {/* POC Reference Line */}
            <ReferenceLine 
              y={poc.price} 
              stroke="#ef4444" 
              strokeDasharray="2 2"
              label={{ value: "POC", position: "top" }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Distribution Table */}
      <div className="mt-4">
        <h3 className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Volume Distribution</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-700">
                <th className="text-left py-2 text-neutral-600 dark:text-neutral-400">Price Level</th>
                <th className="text-right py-2 text-neutral-600 dark:text-neutral-400">Volume</th>
                <th className="text-right py-2 text-neutral-600 dark:text-neutral-400">% of Total</th>
                <th className="text-right py-2 text-neutral-600 dark:text-neutral-400">Intensity</th>
              </tr>
            </thead>
            <tbody>
              {volumeData
                .sort((a, b) => b.volume - a.volume)
                .slice(0, 10)
                .map((data, index) => (
                <tr key={index} className="border-b border-neutral-100 dark:border-neutral-800">
                  <td className="py-2 font-medium text-neutral-900 dark:text-neutral-100">
                    ${data.price.toLocaleString()}
                  </td>
                  <td className="py-2 text-right text-neutral-600 dark:text-neutral-400">
                    {data.volume.toLocaleString()}
                  </td>
                  <td className="py-2 text-right text-neutral-600 dark:text-neutral-400">
                    {data.percentage.toFixed(1)}%
                  </td>
                  <td className="py-2 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: data.color }}
                      />
                      <span className="text-xs text-neutral-500 dark:text-neutral-500">
                        {data.percentage > 80 ? 'Very High' :
                         data.percentage > 60 ? 'High' :
                         data.percentage > 40 ? 'Medium' :
                         data.percentage > 20 ? 'Low' : 'Very Low'}
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
};

export default VolumeProfileChart;