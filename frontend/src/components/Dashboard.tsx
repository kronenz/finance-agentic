/**
 * 대시보드 컴포넌트
 */

import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { logout } from '../store/authSlice';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 네비게이션 바 */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Crypto Trading Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                안녕하세요, {user?.first_name}님!
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                대시보드에 오신 것을 환영합니다!
              </h2>
              <p className="text-gray-600 mb-6">
                암호화폐 자동화 거래 서비스를 시작해보세요.
              </p>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      거래 전략
                    </h3>
                    <p className="text-gray-600">
                      슈퍼트렌드, RSI 등 다양한 거래 전략을 설정하세요.
                    </p>
                  </div>
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      포트폴리오
                    </h3>
                    <p className="text-gray-600">
                      실시간 포트폴리오 현황을 확인하세요.
                    </p>
                  </div>
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      분석 도구
                    </h3>
                    <p className="text-gray-600">
                      AI 기반 시장 분석과 인사이트를 받아보세요.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
