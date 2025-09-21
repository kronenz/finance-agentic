# AI/ML 서비스
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import os

from app.core.config import settings

# 로거 설정
logger = structlog.get_logger()

class MarketRegimeDetector:
    """시장 국면 감지 모델"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, price_data: pd.DataFrame) -> np.ndarray:
        """가격 데이터에서 특성 추출"""
        try:
            features = []
            
            # 기본 가격 특성
            features.extend([
                price_data['close'].pct_change().mean(),  # 평균 수익률
                price_data['close'].pct_change().std(),   # 수익률 변동성
                price_data['close'].pct_change().skew(),  # 수익률 왜도
                price_data['close'].pct_change().kurt(),  # 수익률 첨도
            ])
            
            # 이동평균 특성
            for window in [5, 10, 20, 50]:
                ma = price_data['close'].rolling(window=window).mean()
                features.extend([
                    (price_data['close'] / ma - 1).mean(),  # MA 대비 가격
                    (price_data['close'] / ma - 1).std(),   # MA 대비 변동성
                ])
            
            # RSI 특성
            rsi = self._calculate_rsi(price_data['close'])
            features.extend([
                rsi.mean(),
                rsi.std(),
                (rsi > 70).sum() / len(rsi),  # 과매수 비율
                (rsi < 30).sum() / len(rsi),  # 과매도 비율
            ])
            
            # 볼린저 밴드 특성
            bb_upper, bb_lower = self._calculate_bollinger_bands(price_data['close'])
            bb_position = (price_data['close'] - bb_lower) / (bb_upper - bb_lower)
            features.extend([
                bb_position.mean(),
                bb_position.std(),
                (bb_position > 0.8).sum() / len(bb_position),  # 상단 밴드 근접
                (bb_position < 0.2).sum() / len(bb_position),  # 하단 밴드 근접
            ])
            
            # 거래량 특성
            if 'volume' in price_data.columns:
                volume_ma = price_data['volume'].rolling(window=20).mean()
                features.extend([
                    (price_data['volume'] / volume_ma).mean(),  # 거래량 비율
                    (price_data['volume'] / volume_ma).std(),   # 거래량 변동성
                ])
            else:
                features.extend([0, 0])  # 거래량 데이터가 없는 경우
            
            return np.array(features)
            
        except Exception as e:
            logger.error("Failed to extract features", error=str(e))
            return np.zeros(20)  # 기본 특성 수
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series]:
        """볼린저 밴드 계산"""
        ma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        return upper, lower
    
    def train(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """모델 훈련"""
        try:
            # 데이터 준비
            X = []
            y = []
            
            for data in historical_data:
                price_df = pd.DataFrame(data['price_data'])
                features = self.extract_features(price_df)
                X.append(features)
                y.append(data['regime'])  # 'trending' 또는 'mean_reversion'
            
            X = np.array(X)
            y = np.array(y)
            
            # 특성 정규화
            X_scaled = self.scaler.fit_transform(X)
            
            # 훈련/검증 분할
            X_train, X_val, y_train, y_val = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # 모델 훈련
            self.model.fit(X_train, y_train)
            
            # 성능 평가
            y_pred = self.model.predict(X_val)
            accuracy = accuracy_score(y_val, y_pred)
            
            self.is_trained = True
            
            # 모델 저장
            self._save_model()
            
            logger.info(
                "Market regime detector trained successfully",
                accuracy=accuracy,
                training_samples=len(X_train),
                validation_samples=len(X_val)
            )
            
            return {
                'accuracy': accuracy,
                'training_samples': len(X_train),
                'validation_samples': len(X_val)
            }
            
        except Exception as e:
            logger.error("Failed to train market regime detector", error=str(e))
            raise
    
    def predict(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """시장 국면 예측"""
        try:
            if not self.is_trained:
                self._load_model()
            
            features = self.extract_features(price_data)
            features_scaled = self.scaler.transform([features])
            
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # 특성 중요도
            feature_importance = self.model.feature_importances_
            
            return {
                'regime': prediction,
                'confidence': float(max(probabilities)),
                'probabilities': {
                    'trending': float(probabilities[0]),
                    'mean_reversion': float(probabilities[1])
                },
                'feature_importance': feature_importance.tolist()
            }
            
        except Exception as e:
            logger.error("Failed to predict market regime", error=str(e))
            return {
                'regime': 'unknown',
                'confidence': 0.0,
                'probabilities': {'trending': 0.5, 'mean_reversion': 0.5},
                'feature_importance': []
            }
    
    def _save_model(self):
        """모델 저장"""
        try:
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, 'models/market_regime_detector.pkl')
            joblib.dump(self.scaler, 'models/market_regime_scaler.pkl')
        except Exception as e:
            logger.error("Failed to save model", error=str(e))
    
    def _load_model(self):
        """모델 로드"""
        try:
            self.model = joblib.load('models/market_regime_detector.pkl')
            self.scaler = joblib.load('models/market_regime_scaler.pkl')
            self.is_trained = True
        except Exception as e:
            logger.error("Failed to load model", error=str(e))
            self.is_trained = False

class PersonalizedStrategyRecommender:
    """개인화된 전략 추천 시스템"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_user_features(self, user_profile: Dict[str, Any]) -> np.ndarray:
        """사용자 프로필에서 특성 추출"""
        try:
            features = []
            
            # 기본 사용자 특성
            features.extend([
                user_profile.get('risk_tolerance', 0.5),  # 리스크 허용도
                user_profile.get('trading_experience', 0.5),  # 거래 경험
                user_profile.get('investment_horizon', 0.5),  # 투자 기간
                user_profile.get('portfolio_size', 0.0),  # 포트폴리오 크기
            ])
            
            # 거래 패턴 특성
            trading_history = user_profile.get('trading_history', [])
            if trading_history:
                features.extend([
                    len(trading_history),  # 거래 횟수
                    np.mean([t.get('profit_loss', 0) for t in trading_history]),  # 평균 수익
                    np.std([t.get('profit_loss', 0) for t in trading_history]),  # 수익 변동성
                    np.mean([t.get('holding_period', 1) for t in trading_history]),  # 평균 보유 기간
                ])
            else:
                features.extend([0, 0, 0, 1])
            
            # 선호도 특성
            preferences = user_profile.get('preferences', {})
            features.extend([
                preferences.get('prefers_trend_following', 0.5),
                preferences.get('prefers_mean_reversion', 0.5),
                preferences.get('prefers_short_term', 0.5),
                preferences.get('prefers_long_term', 0.5),
            ])
            
            return np.array(features)
            
        except Exception as e:
            logger.error("Failed to extract user features", error=str(e))
            return np.zeros(12)  # 기본 특성 수
    
    def train(self, user_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """모델 훈련"""
        try:
            # 데이터 준비
            X = []
            y = []
            
            for data in user_data:
                user_features = self.extract_user_features(data['user_profile'])
                X.append(user_features)
                y.append(data['strategy_performance'])  # 전략 성과 점수
            
            X = np.array(X)
            y = np.array(y)
            
            # 특성 정규화
            X_scaled = self.scaler.fit_transform(X)
            
            # 훈련/검증 분할
            X_train, X_val, y_train, y_val = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # 모델 훈련
            self.model.fit(X_train, y_train)
            
            # 성능 평가
            y_pred = self.model.predict(X_val)
            mse = mean_squared_error(y_val, y_pred)
            r2_score = self.model.score(X_val, y_val)
            
            self.is_trained = True
            
            # 모델 저장
            self._save_model()
            
            logger.info(
                "Personalized strategy recommender trained successfully",
                mse=mse,
                r2_score=r2_score,
                training_samples=len(X_train),
                validation_samples=len(X_val)
            )
            
            return {
                'mse': mse,
                'r2_score': r2_score,
                'training_samples': len(X_train),
                'validation_samples': len(X_val)
            }
            
        except Exception as e:
            logger.error("Failed to train personalized strategy recommender", error=str(e))
            raise
    
    def recommend_strategies(self, user_profile: Dict[str, Any], available_strategies: List[str]) -> List[Dict[str, Any]]:
        """전략 추천"""
        try:
            if not self.is_trained:
                self._load_model()
            
            user_features = self.extract_user_features(user_profile)
            features_scaled = self.scaler.transform([user_features])
            
            # 각 전략에 대한 성과 예측
            strategy_scores = []
            for strategy in available_strategies:
                # 전략별 특성 추가 (실제로는 더 복잡한 로직)
                strategy_features = np.concatenate([features_scaled[0], [hash(strategy) % 100 / 100]])
                strategy_features = strategy_features.reshape(1, -1)
                
                score = self.model.predict(strategy_features)[0]
                strategy_scores.append({
                    'strategy': strategy,
                    'score': float(score),
                    'confidence': 0.8  # 기본 신뢰도
                })
            
            # 점수순 정렬
            strategy_scores.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(
                "Strategies recommended",
                user_id=user_profile.get('user_id'),
                strategies_count=len(strategy_scores)
            )
            
            return strategy_scores
            
        except Exception as e:
            logger.error("Failed to recommend strategies", error=str(e))
            return []
    
    def _save_model(self):
        """모델 저장"""
        try:
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.model, 'models/strategy_recommender.pkl')
            joblib.dump(self.scaler, 'models/strategy_recommender_scaler.pkl')
        except Exception as e:
            logger.error("Failed to save model", error=str(e))
    
    def _load_model(self):
        """모델 로드"""
        try:
            self.model = joblib.load('models/strategy_recommender.pkl')
            self.scaler = joblib.load('models/strategy_recommender_scaler.pkl')
            self.is_trained = True
        except Exception as e:
            logger.error("Failed to load model", error=str(e))
            self.is_trained = False

class RiskAssessmentModel:
    """리스크 평가 모델"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def assess_risk(self, market_data: Dict[str, Any], portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """리스크 평가"""
        try:
            # 시장 리스크 지표
            market_risk = self._calculate_market_risk(market_data)
            
            # 포트폴리오 리스크 지표
            portfolio_risk = self._calculate_portfolio_risk(portfolio_data)
            
            # 전체 리스크 점수 계산
            total_risk = (market_risk * 0.6 + portfolio_risk * 0.4)
            
            # 리스크 등급 결정
            if total_risk < 0.3:
                risk_level = 'low'
            elif total_risk < 0.6:
                risk_level = 'medium'
            else:
                risk_level = 'high'
            
            # 권장사항 생성
            recommendations = self._generate_recommendations(total_risk, market_risk, portfolio_risk)
            
            return {
                'total_risk_score': float(total_risk),
                'risk_level': risk_level,
                'market_risk': float(market_risk),
                'portfolio_risk': float(portfolio_risk),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error("Failed to assess risk", error=str(e))
            return {
                'total_risk_score': 0.5,
                'risk_level': 'medium',
                'market_risk': 0.5,
                'portfolio_risk': 0.5,
                'recommendations': ['Unable to assess risk']
            }
    
    def _calculate_market_risk(self, market_data: Dict[str, Any]) -> float:
        """시장 리스크 계산"""
        try:
            # VIX 지수 (변동성 지수)
            vix = market_data.get('vix', 20)
            vix_risk = min(vix / 50, 1.0)  # 50 이상이면 최대 리스크
            
            # 시장 변동성
            volatility = market_data.get('volatility', 0.2)
            vol_risk = min(volatility * 5, 1.0)  # 0.2 이상이면 최대 리스크
            
            # 시장 트렌드
            trend = market_data.get('trend', 0)
            trend_risk = abs(trend)  # 트렌드가 강할수록 리스크
            
            return (vix_risk + vol_risk + trend_risk) / 3
            
        except Exception as e:
            logger.error("Failed to calculate market risk", error=str(e))
            return 0.5
    
    def _calculate_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> float:
        """포트폴리오 리스크 계산"""
        try:
            # 포트폴리오 집중도
            concentration = portfolio_data.get('concentration', 0.5)
            
            # 레버리지 비율
            leverage = portfolio_data.get('leverage', 1.0)
            leverage_risk = min(leverage / 3, 1.0)  # 3배 이상이면 최대 리스크
            
            # 포지션 크기
            position_size = portfolio_data.get('position_size', 0.1)
            position_risk = min(position_size * 10, 1.0)  # 10% 이상이면 최대 리스크
            
            return (concentration + leverage_risk + position_risk) / 3
            
        except Exception as e:
            logger.error("Failed to calculate portfolio risk", error=str(e))
            return 0.5
    
    def _generate_recommendations(self, total_risk: float, market_risk: float, portfolio_risk: float) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        if total_risk > 0.7:
            recommendations.append("Consider reducing position sizes")
            recommendations.append("Increase diversification")
        
        if market_risk > 0.7:
            recommendations.append("Market volatility is high - consider hedging")
            recommendations.append("Monitor market conditions closely")
        
        if portfolio_risk > 0.7:
            recommendations.append("Portfolio is highly concentrated")
            recommendations.append("Consider rebalancing positions")
        
        if total_risk < 0.3:
            recommendations.append("Risk level is low - consider increasing exposure")
        
        return recommendations

class AIService:
    """AI 서비스 통합 클래스"""
    
    def __init__(self):
        self.market_regime_detector = MarketRegimeDetector()
        self.strategy_recommender = PersonalizedStrategyRecommender()
        self.risk_assessor = RiskAssessmentModel()
    
    async def analyze_market(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """시장 분석"""
        try:
            # 시장 국면 감지
            regime_analysis = self.market_regime_detector.predict(price_data)
            
            # 추가 시장 지표 계산
            market_indicators = self._calculate_market_indicators(price_data)
            
            return {
                'regime_analysis': regime_analysis,
                'market_indicators': market_indicators,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to analyze market", error=str(e))
            return {
                'regime_analysis': {'regime': 'unknown', 'confidence': 0.0},
                'market_indicators': {},
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def recommend_strategies(self, user_id: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """전략 추천"""
        try:
            available_strategies = [
                'supertrend_trend_following',
                'rsi_mean_reversion',
                'bollinger_bands_squeeze',
                'macd_crossover',
                'moving_average_crossover'
            ]
            
            recommendations = self.strategy_recommender.recommend_strategies(
                user_profile, available_strategies
            )
            
            logger.info(
                "Strategies recommended for user",
                user_id=user_id,
                recommendations_count=len(recommendations)
            )
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to recommend strategies", error=str(e))
            return []
    
    async def assess_risk(self, user_id: str, market_data: Dict[str, Any], portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """리스크 평가"""
        try:
            risk_assessment = self.risk_assessor.assess_risk(market_data, portfolio_data)
            
            logger.info(
                "Risk assessed for user",
                user_id=user_id,
                risk_level=risk_assessment['risk_level'],
                risk_score=risk_assessment['total_risk_score']
            )
            
            return risk_assessment
            
        except Exception as e:
            logger.error("Failed to assess risk", error=str(e))
            return {
                'total_risk_score': 0.5,
                'risk_level': 'medium',
                'market_risk': 0.5,
                'portfolio_risk': 0.5,
                'recommendations': ['Unable to assess risk']
            }
    
    def _calculate_market_indicators(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """시장 지표 계산"""
        try:
            indicators = {}
            
            # 기본 지표
            indicators['price_change'] = float(price_data['close'].pct_change().iloc[-1])
            indicators['volatility'] = float(price_data['close'].pct_change().std())
            indicators['volume_ratio'] = float(price_data['volume'].iloc[-1] / price_data['volume'].mean())
            
            # 기술적 지표
            rsi = self.market_regime_detector._calculate_rsi(price_data['close'])
            indicators['rsi'] = float(rsi.iloc[-1])
            
            bb_upper, bb_lower = self.market_regime_detector._calculate_bollinger_bands(price_data['close'])
            bb_position = (price_data['close'] - bb_lower) / (bb_upper - bb_lower)
            indicators['bollinger_position'] = float(bb_position.iloc[-1])
            
            return indicators
            
        except Exception as e:
            logger.error("Failed to calculate market indicators", error=str(e))
            return {}

# 전역 AI 서비스 인스턴스
ai_service = AIService()
