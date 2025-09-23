/**
 * 로그인 폼 컴포넌트
 */

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useDispatch } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { AuthService } from '../services/auth';
import { loginStart, loginSuccess, loginFailure } from '../store/authSlice';
import { LoginRequest } from '../types/auth';

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

const LoginForm: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(null);
    dispatch(loginStart());

    try {
      const loginRequest: LoginRequest = {
        email: data.email,
        password: data.password,
      };

      const response = await AuthService.login(loginRequest);
      
      dispatch(loginSuccess({
        user: response.user,
        token: response.access_token,
      }));

      // 로그인 성공 시 대시보드로 이동
      navigate('/dashboard');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '로그인에 실패했습니다.';
      setError(errorMessage);
      dispatch(loginFailure(errorMessage));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="apple-h-screen apple-flex apple-items-center apple-justify-center apple-bg-gray-1 apple-py-32 apple-px-4">
      <div className="apple-w-full apple-max-w-md apple-mx-auto apple-animate-fade-in">
        <div className="apple-text-center apple-mb-12">
          <h2 className="apple-hero-title apple-text-6xl apple-text-gray-11 apple-mb-6">
            계정에 로그인
          </h2>
          <p className="apple-text-2xl apple-text-gray-7 apple-mb-8">
            또는{' '}
            <Link
              to="/register"
              className="apple-text-primary apple-text-2xl apple-font-semibold apple-hover-scale"
            >
              새 계정 만들기
            </Link>
          </p>
        </div>

        <div className="apple-card apple-animate-scale-in apple-hover-shadow">
          <div className="apple-card-body">
            <form className="apple-space-y-6" onSubmit={handleSubmit(onSubmit)}>
              {error && (
                <div className="apple-alert apple-alert-error apple-animate-shake">
                  <svg className="apple-w-4 apple-h-4 apple-mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  {error}
                </div>
              )}

              <div className="apple-space-y-6">
                <div className="apple-input-group">
                  <label htmlFor="email" className="apple-input-label">
                    이메일 주소
                  </label>
                  <input
                    {...register('email', {
                      required: '이메일을 입력해주세요.',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: '올바른 이메일 형식이 아닙니다.',
                      },
                    })}
                    type="email"
                    className="apple-input-field"
                    placeholder="이메일 주소를 입력하세요"
                  />
                  {errors.email && (
                    <p className="apple-input-error">{errors.email.message}</p>
                  )}
                </div>

                <div className="apple-input-group">
                  <label htmlFor="password" className="apple-input-label">
                    비밀번호
                  </label>
                  <input
                    {...register('password', {
                      required: '비밀번호를 입력해주세요.',
                      minLength: {
                        value: 8,
                        message: '비밀번호는 최소 8자 이상이어야 합니다.',
                      },
                    })}
                    type="password"
                    className="apple-input-field"
                    placeholder="비밀번호를 입력하세요"
                  />
                  {errors.password && (
                    <p className="apple-input-error">{errors.password.message}</p>
                  )}
                </div>

                <div className="apple-flex apple-items-center apple-justify-between">
                  <div className="apple-checkbox-group">
                    <input
                      {...register('rememberMe')}
                      type="checkbox"
                      id="rememberMe"
                      className="apple-checkbox"
                    />
                    <label htmlFor="rememberMe" className="apple-checkbox-label">
                      로그인 상태 유지
                    </label>
                  </div>

                  <div className="apple-text-sm">
                    <Link
                      to="/forgot-password"
                      className="apple-text-primary apple-hover-scale"
                    >
                      비밀번호를 잊으셨나요?
                    </Link>
                  </div>
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`apple-btn apple-btn-primary apple-w-full ${isLoading ? 'apple-btn-loading' : ''}`}
                >
                  {isLoading ? '로그인 중...' : '로그인'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
