import React from 'react';

interface SettingsPageProps {
  onLogout: () => void;
}

const SettingsPage: React.FC<SettingsPageProps> = ({ onLogout }) => {
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
          <button
            onClick={() => window.history.back()}
            style={{
              padding: '0.5rem',
              backgroundColor: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: '#6b7280'
            }}
          >
            ←
          </button>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#1f2937' }}>
            ⚙️ Settings
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

      {/* Main Content */}
      <main style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '2rem' 
      }}>
        <div style={{ 
          backgroundColor: 'white', 
          padding: '2rem', 
          borderRadius: '0.5rem', 
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)' 
        }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1.5rem', color: '#1f2937' }}>
            🔧 Application Settings
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '0.5rem', color: '#374151' }}>
                Theme
              </h3>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Choose your preferred theme (Light/Dark)
              </p>
            </div>
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '0.5rem', color: '#374151' }}>
                Notifications
              </h3>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Configure notification preferences
              </p>
            </div>
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '0.5rem', color: '#374151' }}>
                Trading Settings
              </h3>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Set up your trading parameters and risk management
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;
