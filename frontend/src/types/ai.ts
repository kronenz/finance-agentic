// AI/ML 관련 TypeScript 타입 정의

export enum MarketRegime {
  TRENDING = 'trending',
  MEAN_REVERSION = 'mean_reversion',
  UNKNOWN = 'unknown'
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high'
}

export enum StrategyType {
  TREND_FOLLOWING = 'trend_following',
  MEAN_REVERSION = 'mean_reversion',
  BREAKOUT = 'breakout',
  SCALPING = 'scalping'
}

export interface MarketAnalysisRequest {
  symbol: string;
  price_data: Array<{
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  update_model: boolean;
  regime_label?: string;
}

export interface MarketAnalysisResponse {
  symbol: string;
  regime: MarketRegime;
  confidence: number;
  probabilities: Record<string, number>;
  market_indicators: Record<string, number>;
  timestamp: string;
}

export interface StrategyRecommendationRequest {
  profile_updates?: Record<string, any>;
  market_conditions?: Record<string, any>;
  risk_preference?: RiskLevel;
}

export interface StrategyRecommendationResponse {
  strategy_id: string;
  strategy_name: string;
  score: number;
  confidence: number;
  description: string;
  risk_level: RiskLevel;
  strategy_type?: StrategyType;
  expected_return?: number;
  max_drawdown?: number;
}

export interface RiskAssessmentRequest {
  market_data: Record<string, any>;
  portfolio_data?: Record<string, any>;
  assessment_type: string;
}

export interface RiskAssessmentResponse {
  total_risk_score: number;
  risk_level: RiskLevel;
  market_risk: number;
  portfolio_risk: number;
  recommendations: string[];
  timestamp: string;
  risk_breakdown?: Record<string, number>;
  stress_test_results?: Record<string, any>;
}

export interface UserProfileUpdate {
  risk_tolerance?: number;
  trading_experience?: number;
  investment_horizon?: number;
  portfolio_size?: number;
  preferences?: Record<string, any>;
}

export interface UserProfileResponse {
  user_id: string;
  risk_tolerance: number;
  trading_experience: number;
  investment_horizon: number;
  portfolio_size: number;
  preferences: Record<string, any>;
  trading_history: Array<Record<string, any>>;
  created_at?: string;
  updated_at?: string;
}

export interface ModelTrainingRequest {
  model_type: string;
  training_data: Array<Record<string, any>>;
  hyperparameters?: Record<string, any>;
  validation_split: number;
}

export interface ModelTrainingResponse {
  model_type: string;
  training_status: string;
  accuracy?: number;
  loss?: number;
  training_samples: number;
  validation_samples: number;
  training_time: number;
  model_id: string;
}

export interface ABTestRequest {
  test_name: string;
  strategy_a: string;
  strategy_b: string;
  traffic_split: number;
  duration_days: number;
}

export interface ABTestResponse {
  test_id: string;
  test_name: string;
  status: string;
  strategy_a: string;
  strategy_b: string;
  traffic_split: number;
  start_date: string;
  end_date: string;
  results?: Record<string, any>;
}

export interface ModelPerformanceMetrics {
  model_type: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  auc_roc: number;
  training_samples: number;
  validation_samples: number;
  last_updated: string;
}

export interface SystemHealthMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  gpu_usage?: number;
  active_models: number;
  total_predictions: number;
  average_latency: number;
  error_rate: number;
  timestamp: string;
}

export interface AIAlertRequest {
  alert_type: string;
  message: string;
  priority: string;
  user_id?: string;
  metadata?: Record<string, any>;
}

export interface AIAlertResponse {
  alert_id: string;
  alert_type: string;
  message: string;
  priority: string;
  status: string;
  created_at: string;
  user_id?: string;
}

export interface BatchPredictionRequest {
  prediction_type: string;
  data: Array<Record<string, any>>;
  model_version?: string;
  output_format: string;
}

export interface BatchPredictionResponse {
  job_id: string;
  prediction_type: string;
  status: string;
  total_samples: number;
  processed_samples: number;
  results?: Array<Record<string, any>>;
  created_at: string;
  completed_at?: string;
}
