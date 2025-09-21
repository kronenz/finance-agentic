/**
 * 메인 App 컴포넌트
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="App">
          <Routes>
            {/* 공개 라우트 */}
            <Route path="/login" element={<LoginForm />} />
            <Route path="/register" element={<RegisterForm />} />
            
            {/* 보호된 라우트 */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            
            {/* 기본 리다이렉트 */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* 404 페이지 */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </Provider>
  );
}

export default App;
