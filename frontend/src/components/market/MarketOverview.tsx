import React from 'react';

interface CryptoData {
  name: string;
  symbol: string;
  price: number;
  change24h: number;
  marketCap: string;
  volume: string;
}

const dummyData: CryptoData[] = [
  { name: 'Bitcoin', symbol: 'BTC', price: 68000.00, change24h: 2.5, marketCap: '$1.3T', volume: '$45B' },
  { name: 'Ethereum', symbol: 'ETH', price: 3500.00, change24h: -1.2, marketCap: '$420B', volume: '$20B' },
  { name: 'Solana', symbol: 'SOL', price: 170.00, change24h: 5.8, marketCap: '$78B', volume: '$3B' },
  { name: 'Cardano', symbol: 'ADA', price: 0.45, change24h: 0.5, marketCap: '$16B', volume: '$500M' },
];

const MarketOverview: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h2 className="text-2xl font-bold mb-4">Market Overview</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200">
          <thead>
            <tr className="bg-gray-100">
              <th className="py-2 px-4 border-b">Name</th>
              <th className="py-2 px-4 border-b">Price</th>
              <th className="py-2 px-4 border-b">24h Change</th>
              <th className="py-2 px-4 border-b">Market Cap</th>
              <th className="py-2 px-4 border-b">Volume (24h)</th>
            </tr>
          </thead>
          <tbody>
            {dummyData.map((crypto) => (
              <tr key={crypto.symbol} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">{crypto.name} ({crypto.symbol})</td>
                <td className="py-2 px-4 border-b">${crypto.price.toLocaleString()}</td>
                <td className={`py-2 px-4 border-b ${crypto.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {crypto.change24h.toFixed(2)}%
                </td>
                <td className="py-2 px-4 border-b">{crypto.marketCap}</td>
                <td className="py-2 px-4 border-b">{crypto.volume}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MarketOverview;