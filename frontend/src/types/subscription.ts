// 구독 관련 TypeScript 타입 정의

export interface SubscriptionPlanResponse {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  billing_cycle: string;
  features: string[];
  max_trades_per_day: number;
  max_portfolio_value: number;
  is_active: boolean;
}

export interface SubscriptionResponse {
  id: string;
  user_id: string;
  plan_id: string;
  plan_name: string;
  status: SubscriptionStatus;
  start_date: string;
  end_date?: string;
  billing_cycle: string;
  price: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export enum SubscriptionStatus {
  ACTIVE = 'active',
  CANCELLED = 'cancelled',
  EXPIRED = 'expired',
  SUSPENDED = 'suspended',
  PENDING = 'pending'
}

export interface SubscriptionCreate {
  plan_id: string;
  payment_method_id: string;
  billing_cycle: string;
}

export interface SubscriptionUpdate {
  plan_id?: string;
  payment_method_id?: string;
  billing_cycle?: string;
}

export interface SubscriptionHistoryResponse {
  id: string;
  subscription_id: string;
  action: string;
  old_status?: SubscriptionStatus;
  new_status: SubscriptionStatus;
  description: string;
  created_at: string;
}

export interface PaymentMethodResponse {
  id: string;
  user_id: string;
  stripe_payment_method_id: string;
  card_last_four: string;
  card_brand: string;
  card_exp_month: number;
  card_exp_year: number;
  is_default: boolean;
  created_at: string;
}

export interface BillingInfoResponse {
  subscription: SubscriptionResponse;
  next_billing_date?: string;
  amount_due: number;
  currency: string;
  payment_method?: PaymentMethodResponse;
  billing_address?: any;
}

export interface UsageStatsResponse {
  trades_used: number;
  trades_limit: number;
  portfolio_value: number;
  portfolio_limit: number;
  api_calls_used: number;
  api_calls_limit: number;
  storage_used: number;
  storage_limit: number;
}
