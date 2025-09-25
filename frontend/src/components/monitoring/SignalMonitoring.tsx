import React from 'react';
import AgentStatus from './AgentStatus';
import Alerts from './Alerts';

const SignalMonitoring: React.FC = () => {
  return (
    <div className="p-4 bg-gray-900 text-white">
      <h1 className="text-2xl font-bold mb-4">Signal Monitoring</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <AgentStatus />
        </div>
        <div>
          <Alerts />
        </div>
      </div>
    </div>
  );
};

export default SignalMonitoring;
