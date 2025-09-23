// 인증 서비스

import api from './api';
import { 
  AuthResponse, 
  RegisterRequest, 
  LoginRequest, 
  ForgotPasswordRequest, 
  ResetPasswordRequest 
} from '../types/auth';

export class AuthService {
  // 회원가입
  static async register(data: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await api.post<AuthResponse>('/auth/register', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '회원가입에 실패했습니다.');
    }
  }

  // 로그인
  static async login(data: LoginRequest): Promise<AuthResponse> {
    try {
      const formData = new FormData();
      formData.append('username', data.email);
      formData.append('password', data.password);

      const response = await api.post<AuthResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '로그인에 실패했습니다.');
    }
  }

  // 로그아웃
  static async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch (error: any) {
      console.error('로그아웃 에러:', error);
    } finally {
      // 로컬 스토리지에서 토큰 제거
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    }
  }

  // 토큰 갱신
  static async refreshToken(): Promise<AuthResponse> {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('리프레시 토큰이 없습니다.');
      }

      const response = await api.post<AuthResponse>('/auth/refresh', {
        refresh_token: refreshToken,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '토큰 갱신에 실패했습니다.');
    }
  }

  // 현재 사용자 정보 조회
  static async getCurrentUser(): Promise<AuthResponse['user']> {
    try {
      const response = await api.get<AuthResponse['user']>('/auth/me');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '사용자 정보 조회에 실패했습니다.');
    }
  }

  // 비밀번호 재설정 요청
  static async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    try {
      await api.post('/auth/forgot-password', data);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '비밀번호 재설정 요청에 실패했습니다.');
    }
  }

  // 비밀번호 재설정
  static async resetPassword(data: ResetPasswordRequest): Promise<void> {
    try {
      await api.post('/auth/reset-password', data);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '비밀번호 재설정에 실패했습니다.');
    }
  }

  // 이메일 인증
  static async verifyEmail(token: string): Promise<void> {
    try {
      await api.post('/auth/verify-email', { token });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || '이메일 인증에 실패했습니다.');
    }
  }

  // 토큰 유효성 검사
  static isTokenValid(): boolean {
    const token = localStorage.getItem('token');
    if (!token) return false;

    try {
      // JWT 토큰 디코딩 (간단한 검증)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      
      return payload.exp > currentTime;
    } catch (error) {
      return false;
    }
  }

  // 토큰 저장
  static saveTokens(authResponse: AuthResponse): void {
    localStorage.setItem('token', authResponse.access_token);
    // 리프레시 토큰이 있다면 저장
    if ((authResponse as any).refresh_token) {
      localStorage.setItem('refreshToken', (authResponse as any).refresh_token);
    }
  }

  // 토큰 제거
  static clearTokens(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }
}
