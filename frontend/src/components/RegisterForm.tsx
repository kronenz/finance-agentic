/**
 * 회원가입 폼 컴포넌트
 */

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useDispatch } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { AuthService } from '../services/auth';
import { loginSuccess } from '../store/authSlice';
import { RegisterRequest } from '../types/auth';

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
  agreeToTerms: boolean;
}

const RegisterForm: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>();

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const registerRequest: RegisterRequest = {
        email: data.email,
        password: data.password,
        first_name: data.first_name,
        last_name: data.last_name,
        agreeToTerms: data.agreeToTerms,
      };

      const response = await AuthService.register(registerRequest);

      dispatch(loginSuccess({
        user: response.user,
        token: response.access_token,
      }));

      // 회원가입 성공 시 대시보드로 이동
      navigate('/dashboard');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '회원가입에 실패했습니다.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="apple-h-screen apple-flex apple-items-center apple-justify-center apple-bg-gray-1 apple-py-32 apple-px-4">
      <div className="apple-w-full apple-max-w-md apple-mx-auto apple-animate-fade-in">
        <div className="apple-text-center apple-mb-12">
          <h2 className="apple-hero-title apple-text-6xl apple-text-gray-11 apple-mb-6">
            새 계정 만들기
          </h2>
          <p className="apple-text-2xl apple-text-gray-7 apple-mb-8">
            또는{' '}
            <Link
              to="/login"
              className="apple-text-primary apple-text-2xl apple-font-semibold apple-hover-scale"
            >
              기존 계정으로 로그인
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
                <div className="apple-grid apple-grid-2 apple-gap-4">
                  <div className="apple-input-group">
                    <label htmlFor="first_name" className="apple-input-label">
                      이름
                    </label>
                    <input
                      {...register('first_name', {
                        required: '이름을 입력해주세요.',
                        minLength: {
                          value: 2,
                          message: '이름은 최소 2자 이상이어야 합니다.',
                        },
                      })}
                      type="text"
                      className="apple-input-field"
                      placeholder="이름"
                    />
                    {errors.first_name && (
                      <p className="apple-input-error">{errors.first_name.message}</p>
                    )}
                  </div>

                  <div className="apple-input-group">
                    <label htmlFor="last_name" className="apple-input-label">
                      성
                    </label>
                    <input
                      {...register('last_name', {
                        required: '성을 입력해주세요.',
                        minLength: {
                          value: 2,
                          message: '성은 최소 2자 이상이어야 합니다.',
                        },
                      })}
                      type="text"
                      className="apple-input-field"
                      placeholder="성"
                    />
                    {errors.last_name && (
                      <p className="apple-input-error">{errors.last_name.message}</p>
                    )}
                  </div>
                </div>

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
                      pattern: {
                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
                        message: '비밀번호는 대문자, 소문자, 숫자, 특수문자를 포함해야 합니다.',
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

                <div className="apple-input-group">
                  <label htmlFor="confirmPassword" className="apple-input-label">
                    비밀번호 확인
                  </label>
                  <input
                    {...register('confirmPassword', {
                      required: '비밀번호 확인을 입력해주세요.',
                      validate: (value) =>
                        value === password || '비밀번호가 일치하지 않습니다.',
                    })}
                    type="password"
                    className="apple-input-field"
                    placeholder="비밀번호를 다시 입력하세요"
                  />
                  {errors.confirmPassword && (
                    <p className="apple-input-error">{errors.confirmPassword.message}</p>
                  )}
                </div>

                <div className="apple-checkbox-group">
                  <input
                    {...register('agreeToTerms', {
                      required: '이용 약관에 동의해야 합니다.',
                    })}
                    type="checkbox"
                    id="agreeToTerms"
                    className="apple-checkbox"
                  />
                  <label htmlFor="agreeToTerms" className="apple-checkbox-label">
                    이용 약관에 동의합니다.
                  </label>
                  {errors.agreeToTerms && (
                    <p className="apple-input-error">{errors.agreeToTerms.message}</p>
                  )}
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`apple-btn apple-btn-primary apple-w-full ${isLoading ? 'apple-btn-loading' : ''}`}
                >
                  {isLoading ? '회원가입 중...' : '회원가입'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;