// 인증 관련 타입 정의

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  country?: string;
  timezone: string;
  isActive: boolean;
  emailVerified: boolean;
  phoneVerified: boolean;
  twoFactorEnabled: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface RegisterRequest {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  agreeToTerms: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
  confirmPassword: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (data: ResetPasswordRequest) => Promise<void>;
  clearError: () => void;
}
