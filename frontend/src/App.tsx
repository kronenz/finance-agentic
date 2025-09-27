import React from 'react';

const App: React.FC = () => {
  console.log('App component rendering');
  
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f5f5f5', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          fontWeight: 'bold', 
          color: '#1f2937', 
          marginBottom: '1rem' 
        }}>
          🚀 Crypto Trading Dashboard
        </h1>
        <p style={{ 
          fontSize: '1.25rem', 
          color: '#6b7280', 
          marginBottom: '2rem' 
        }}>
          프론트엔드가 정상적으로 로드되었습니다!
        </p>
        <div style={{ 
          backgroundColor: 'white', 
          padding: '1.5rem', 
          borderRadius: '0.5rem', 
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' 
        }}>
          <h2 style={{ 
            fontSize: '1.5rem', 
            fontWeight: '600', 
            color: '#1f2937', 
            marginBottom: '1rem' 
          }}>
            서비스 상태
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#6b7280' }}>프론트엔드:</span>
              <span style={{ color: '#059669', fontWeight: '600' }}>✅ 정상</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#6b7280' }}>백엔드 API:</span>
              <span style={{ color: '#059669', fontWeight: '600' }}>✅ 정상</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#6b7280' }}>데이터베이스:</span>
              <span style={{ color: '#059669', fontWeight: '600' }}>✅ 정상</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;