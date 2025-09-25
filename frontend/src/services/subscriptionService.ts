// 구독 서비스 API 클라이언트
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  SubscriptionPlanResponse, 
  SubscriptionResponse, 
  SubscriptionCreate,
  SubscriptionHistoryResponse 
} from '../types/subscription';

class SubscriptionService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api/v1/subscriptions',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 요청 인터셉터 - 인증 토큰 자동 추가
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터 - 에러 처리
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          // 인증 실패 시 로그인 페이지로 리디렉션
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * 구독 플랜 목록 조회
   */
  async getSubscriptionPlans(): Promise<SubscriptionPlanResponse[]> {
    try {
      const response = await this.api.get<SubscriptionPlanResponse[]>('/plans');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch subscription plans:', error);
      throw new Error('구독 플랜을 불러오는데 실패했습니다.');
    }
  }

  /**
   * 활성 구독 조회
   */
  async getActiveSubscription(): Promise<SubscriptionResponse | null> {
    try {
      const response = await this.api.get<SubscriptionResponse>('/active');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null; // 활성 구독이 없는 경우
      }
      console.error('Failed to fetch active subscription:', error);
      throw new Error('구독 정보를 불러오는데 실패했습니다.');
    }
  }

  /**
   * 사용자의 모든 구독 조회
   */
  async getUserSubscriptions(): Promise<SubscriptionResponse[]> {
    try {
      const response = await this.api.get<SubscriptionResponse[]>('/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user subscriptions:', error);
      throw new Error('구독 목록을 불러오는데 실패했습니다.');
    }
  }

  /**
   * 구독 생성
   */
  async createSubscription(planId: string, billingCycle: string = 'monthly'): Promise<SubscriptionResponse> {
    try {
      const subscriptionData: SubscriptionCreate = {
        plan_id: planId,
        payment_method_id: 'default', // 임시 - 실제로는 Stripe 결제 후 받은 ID
        billing_cycle: billingCycle,
      };

      const response = await this.api.post<SubscriptionResponse>('/', subscriptionData);
      return response.data;
    } catch (error: any) {
      console.error('Failed to create subscription:', error);
      
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail || '구독 생성에 실패했습니다.');
      }
      
      throw new Error('구독 생성에 실패했습니다.');
    }
  }

  /**
   * 구독 업데이트
   */
  async updateSubscription(
    subscriptionId: string, 
    updates: { plan_id?: string; billing_cycle?: string }
  ): Promise<SubscriptionResponse> {
    try {
      const response = await this.api.put<SubscriptionResponse>(`/${subscriptionId}`, updates);
      return response.data;
    } catch (error: any) {
      console.error('Failed to update subscription:', error);
      
      if (error.response?.status === 404) {
        throw new Error('구독을 찾을 수 없습니다.');
      }
      
      throw new Error('구독 업데이트에 실패했습니다.');
    }
  }

  /**
   * 구독 취소
   */
  async cancelSubscription(subscriptionId: string): Promise<void> {
    try {
      await this.api.post(`/${subscriptionId}/cancel`);
    } catch (error: any) {
      console.error('Failed to cancel subscription:', error);
      
      if (error.response?.status === 404) {
        throw new Error('구독을 찾을 수 없습니다.');
      }
      
      throw new Error('구독 취소에 실패했습니다.');
    }
  }

  /**
   * 구독 재활성화
   */
  async reactivateSubscription(subscriptionId: string): Promise<void> {
    try {
      await this.api.post(`/${subscriptionId}/reactivate`);
    } catch (error: any) {
      console.error('Failed to reactivate subscription:', error);
      
      if (error.response?.status === 404) {
        throw new Error('구독을 찾을 수 없습니다.');
      }
      
      throw new Error('구독 재활성화에 실패했습니다.');
    }
  }

  /**
   * 구독 이력 조회
   */
  async getSubscriptionHistory(subscriptionId: string): Promise<SubscriptionHistoryResponse[]> {
    try {
      const response = await this.api.get<SubscriptionHistoryResponse[]>(`/${subscriptionId}/history`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch subscription history:', error);
      
      if (error.response?.status === 404) {
        throw new Error('구독을 찾을 수 없습니다.');
      }
      
      throw new Error('구독 이력을 불러오는데 실패했습니다.');
    }
  }
}

// 싱글톤 인스턴스 생성 및 내보내기
export const subscriptionService = new SubscriptionService();
export default subscriptionService;
