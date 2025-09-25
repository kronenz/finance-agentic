import React, { useState, useEffect } from 'react';

const Alerts: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate data fetching
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <div className="p-4 bg-gray-800 rounded-lg">Loading alerts...</div>;
  }

  if (error) {
    return <div className="p-4 bg-red-800 rounded-lg">Error: {error}</div>;
  }

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-xl font-bold mb-2">Alerts</h2>
      {/* Placeholder for the actual alerts */}
      <div className="space-y-2">
        <div className="p-2 bg-yellow-700 rounded-lg">
          <p>Alert 1: High volatility detected in BTC/USD</p>
        </div>
        <div className="p-2 bg-red-700 rounded-lg">
          <p>Alert 2: Margin call on ETH position</p>
        </div>
      </div>
    </div>
  );
};

export default Alerts;
