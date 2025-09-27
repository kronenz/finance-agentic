/**
 * 보호된 라우트 컴포넌트
 */

import React from 'react';
// import { useSelector } from 'react-redux';
import { Navigate, useLocation } from 'react-router-dom';
// import { RootState } from '../store';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // const { isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth);
  const isAuthenticated = true;
  const isLoading = false;
  const location = useLocation();

  // 로딩 중일 때
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  // 인증되지 않은 경우 로그인 페이지로 리다이렉트
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 인증된 경우 자식 컴포넌트 렌더링
  return <>{children}</>;
};

export default ProtectedRoute;
