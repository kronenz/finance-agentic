import React from 'react';
import PositionRisk from './PositionRisk';
import PortfolioRisk from './PortfolioRisk';

const RiskDashboard: React.FC = () => {
  return (
    <div className="p-4 bg-gray-900 text-white">
      <h1 className="text-2xl font-bold mb-4">Risk Management Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <PositionRisk />
        </div>
        <div>
          <PortfolioRisk />
        </div>
      </div>
    </div>
  );
};

export default RiskDashboard;
