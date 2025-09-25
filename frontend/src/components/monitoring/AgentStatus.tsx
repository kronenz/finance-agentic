import React, { useState, useEffect } from 'react';

const AgentStatus: React.FC = () => {
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
    return <div className="p-4 bg-gray-800 rounded-lg">Loading agent status...</div>;
  }

  if (error) {
    return <div className="p-4 bg-red-800 rounded-lg">Error: {error}</div>;
  }

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-xl font-bold mb-2">Agent Status</h2>
      {/* Placeholder for the actual agent status */}
      <div className="space-y-2">
        <div className="p-2 bg-gray-700 rounded-lg">
          <p>Agent 1: Running</p>
        </div>
        <div className="p-2 bg-gray-700 rounded-lg">
          <p>Agent 2: Idle</p>
        </div>
      </div>
    </div>
  );
};

export default AgentStatus;
