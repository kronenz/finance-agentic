import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store/store';
import TradingDashboard from './components/trading/TradingDashboard';
import SignalMonitoring from './components/monitoring/SignalMonitoring';
import RiskDashboard from './components/risk/RiskDashboard';
import VwapChart from './components/charts/VwapChart';
import VolumeProfileChart from './components/charts/VolumeProfileChart';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <div className="bg-gray-900 min-h-screen">
        <TradingDashboard />
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <VwapChart />
            <VolumeProfileChart />
          </div>
        </div>
        <SignalMonitoring />
        <RiskDashboard />
      </div>
    </Provider>
  );
};

export default App;