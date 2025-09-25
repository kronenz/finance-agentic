import React, { useState, useEffect } from 'react';

const PositionStatus: React.FC = () => {
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
    return <div className="p-4 bg-gray-800 rounded-lg">Loading position status...</div>;
  }

  if (error) {
    return <div className="p-4 bg-red-800 rounded-lg">Error: {error}</div>;
  }

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-xl font-bold mb-2">Position Status</h2>
      {/* Placeholder for the actual position status */}
      <div className="space-y-2">
        <div className="p-2 bg-gray-700 rounded-lg">
          <p>Position 1: Long BTC @ $60,000</p>
        </div>
        <div className="p-2 bg-gray-700 rounded-lg">
          <p>Position 2: Short ETH @ $4,000</p>
        </div>
      </div>
    </div>
  );
};

export default PositionStatus;
