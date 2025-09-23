/**
 * 대시보드 컴포넌트
 */

import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { logoutUser } from '../store/authSlice';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logoutUser() as any);
    navigate('/login');
  };

  return (
    <div className="apple-h-screen apple-bg-white">
      {/* Apple 스타일 네비게이션 바 */}
      <nav className="apple-navbar">
        <div className="apple-px-16">
          <div className="apple-flex apple-justify-between apple-items-center apple-h-16">
            <div className="apple-flex apple-items-center">
              <div className="apple-navbar-brand apple-animate-fade-in">
                <span className="apple-text-2xl apple-font-semibold apple-text-gray-11">
                  Crypto Trading Dashboard
                </span>
              </div>
            </div>
            <div className="apple-flex apple-items-center apple-gap-4 apple-animate-fade-in">
              <span className="apple-text-base apple-text-gray-7">
                안녕하세요, <span className="apple-text-primary apple-font-semibold">{user?.first_name}</span>님!
              </span>
              <button
                onClick={handleLogout}
                className="apple-btn apple-btn-outline apple-hover-scale"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Apple 스타일 메인 콘텐츠 */}
      <main className="apple-py-20">
        <div className="apple-px-16">
          <div className="apple-animate-fade-in">
            <h2 className="apple-hero-title apple-text-6xl apple-text-gray-11 apple-mb-8 apple-text-center">
              대시보드에 오신 것을 환영합니다! 🎉
            </h2>
            
            <div className="apple-grid apple-grid-3 apple-gap-8 apple-mb-16">
              {/* 환영 카드 */}
              <div className="apple-card apple-hover-scale apple-hover-shadow">
                <div className="apple-card-body apple-text-center">
                  <div className="apple-text-6xl apple-mb-6">👋</div>
                  <h3 className="apple-card-title">환영합니다!</h3>
                  <p className="apple-text-gray-7 apple-text-lg">
                    암호화폐 자동화 거래 시스템에 오신 것을 환영합니다.
                  </p>
                </div>
              </div>

              {/* 사용자 정보 카드 */}
              <div className="apple-card apple-hover-scale apple-hover-shadow">
                <div className="apple-card-header">
                  <h3 className="apple-card-title">사용자 정보</h3>
                </div>
                <div className="apple-card-body">
                  <dl className="apple-space-y-4">
                    <div className="apple-flex apple-justify-between">
                      <dt className="apple-text-gray-7 apple-font-medium">이메일</dt>
                      <dd className="apple-text-gray-11 apple-font-semibold">{user?.email}</dd>
                    </div>
                    <div className="apple-flex apple-justify-between">
                      <dt className="apple-text-gray-7 apple-font-medium">이름</dt>
                      <dd className="apple-text-gray-11 apple-font-semibold">{user?.first_name}</dd>
                    </div>
                    <div className="apple-flex apple-justify-between">
                      <dt className="apple-text-gray-7 apple-font-medium">성</dt>
                      <dd className="apple-text-gray-11 apple-font-semibold">{user?.last_name}</dd>
                    </div>
                    <div className="apple-flex apple-justify-between">
                      <dt className="apple-text-gray-7 apple-font-medium">가입일</dt>
                      <dd className="apple-text-gray-11 apple-font-semibold">
                        {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>

              {/* 기능 카드 */}
              <div className="apple-card apple-hover-scale apple-hover-shadow">
                <div className="apple-card-body apple-text-center">
                  <div className="apple-text-6xl apple-mb-6">🚀</div>
                  <h3 className="apple-card-title">시작하기</h3>
                  <p className="apple-text-gray-7 apple-text-lg apple-mb-6">
                    AI 기반 거래 전략을 설정하고 자동화된 거래를 시작하세요.
                  </p>
                  <button className="apple-btn apple-btn-primary">
                    거래 시작하기
                  </button>
                </div>
              </div>
            </div>

            {/* 추가 기능 섹션 */}
            <div className="apple-grid apple-grid-2 apple-gap-8">
              <div className="apple-card apple-hover-shadow">
                <div className="apple-card-header">
                  <h3 className="apple-card-title">AI 분석</h3>
                  <p className="apple-card-subtitle">시장 분석 및 전략 추천</p>
                </div>
                <div className="apple-card-body">
                  <p className="apple-text-gray-7 apple-text-lg apple-mb-6">
                    AI가 시장을 분석하고 최적의 거래 전략을 추천해드립니다.
                  </p>
                  <button className="apple-btn apple-btn-secondary">
                    분석 시작하기
                  </button>
                </div>
              </div>

              <div className="apple-card apple-hover-shadow">
                <div className="apple-card-header">
                  <h3 className="apple-card-title">구독 관리</h3>
                  <p className="apple-card-subtitle">플랜 선택 및 결제 관리</p>
                </div>
                <div className="apple-card-body">
                  <p className="apple-text-gray-7 apple-text-lg apple-mb-6">
                    다양한 구독 플랜을 선택하고 결제를 관리하세요.
                  </p>
                  <button className="apple-btn apple-btn-outline">
                    구독 관리
                  </button>
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