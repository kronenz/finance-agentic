import React, { useState } from 'react';

interface MainDashboardProps {
  onLogout: () => void;
}

const MainDashboard: React.FC<MainDashboardProps> = ({ onLogout }) => {
  const [activeView, setActiveView] = useState('dashboard');

  const navigation = [
    { name: 'Dashboard', id: 'dashboard' },
    { name: 'Trading', id: 'trading' },
    { name: 'Analytics', id: 'analytics' },
    { name: 'Risk Management', id: 'risk' },
    { name: 'Monitoring', id: 'monitoring' },
  ];

  const renderContent = () => {
    switch (activeView) {
      case 'dashboard':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ 
              backgroundColor: 'white', 
              padding: '1.5rem', 
              borderRadius: '0.5rem', 
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' 
            }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
                📊 Market Overview
              </h2>
              <p style={{ color: '#6b7280' }}>Real-time market data and analysis</p>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
              <div style={{ 
                backgroundColor: 'white', 
                padding: '1.5rem', 
                borderRadius: '0.5rem', 
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' 
              }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
                  📈 Price Chart
                </h3>
                <p style={{ color: '#6b7280' }}>Interactive price charts and technical indicators</p>
              </div>
              <div style={{ 
                backgroundColor: 'white', 
                padding: '1.5rem', 
                borderRadius: '0.5rem', 
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' 
              }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
                  🎯 Trading Signals
                </h3>
                <p style={{ color: '#6b7280' }}>AI-generated trading signals and recommendations</p>
              </div>
            </div>
          </div>
        );
      case 'trading':
        return (
          <div style={{ 
            backgroundColor: 'white', 
            padding: '1.5rem', 
            borderRadius: '0.5rem', 
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' 
          }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
              💼 Trading Dashboard
            </h2>
            <p style={{ color: '#6b7280' }}>Manage your trading positions and execute trades</p>
          </div>
        );
      case 'analytics':
        return (
          <div style={{ 
            backgroundColor: 'white', 
            padding: '1.5rem', 
            borderRadius: '0.5rem', 
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' 
          }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
              📊 Performance Analytics
            </h2>
            <p style={{ color: '#6b7280' }}>Detailed performance metrics and analytics</p>
          </div>
        );
      case 'risk':
        return (
          <div style={{ 
            backgroundColor: 'white', 
            padding: '1.5rem', 
            borderRadius: '0.5rem', 
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' 
          }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
              ⚠️ Risk Management
            </h2>
            <p style={{ color: '#6b7280' }}>Portfolio risk analysis and position management</p>
          </div>
        );
      case 'monitoring':
        return (
          <div style={{ 
            backgroundColor: 'white', 
            padding: '1.5rem', 
            borderRadius: '0.5rem', 
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' 
          }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
              🔍 System Monitoring
            </h2>
            <p style={{ color: '#6b7280' }}>Real-time system status and alerts</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <header style={{ 
        backgroundColor: 'white', 
        padding: '1rem 2rem', 
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937' }}>
            🚀 AI Trading Dashboard
          </h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={onLogout}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}
          >
            Logout
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <div style={{ 
        position: 'fixed', 
        left: 0, 
        top: '73px', 
        width: '250px', 
        height: 'calc(100vh - 73px)', 
        backgroundColor: 'white', 
        boxShadow: '2px 0 5px rgba(0, 0, 0, 0.1)',
        padding: '1rem'
      }}>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              style={{
                padding: '0.75rem 1rem',
                textAlign: 'left',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500',
                backgroundColor: activeView === item.id ? '#dbeafe' : 'transparent',
                color: activeView === item.id ? '#1d4ed8' : '#374151',
                transition: 'all 0.2s'
              }}
            >
              {item.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <main style={{ 
        marginLeft: '250px', 
        padding: '2rem',
        minHeight: 'calc(100vh - 73px)'
      }}>
        {renderContent()}
      </main>
    </div>
  );
};

export default MainDashboard;