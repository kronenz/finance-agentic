# XGBoost 모델 구현
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from typing import Tuple, List, Dict, Any, Optional
import structlog
import joblib
import os

logger = structlog.get_logger()

class XGBoostModel:
    """XGBoost 기반 거래 신호 분류 모델"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 6, learning_rate: float = 0.1):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.is_trained = False
        
    def build_model(self, **kwargs):
        """XGBoost 모델 구축"""
        try:
            # 기본 파라미터 설정
            params = {
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth,
                'learning_rate': self.learning_rate,
                'random_state': 42,
                'n_jobs': -1
            }
            
            # 추가 파라미터 적용
            params.update(kwargs)
            
            self.model = xgb.XGBClassifier(**params)
            
            logger.info(f"XGBoost model built with parameters: {params}")
            
        except Exception as e:
            logger.error(f"Error building XGBoost model: {e}")
            raise
            
    def prepare_data(self, df: pd.DataFrame, target_column: str = 'signal') -> Tuple[np.ndarray, np.ndarray]:
        """데이터 전처리 및 특성 선택"""
        try:
            # 특성 컬럼 선택 (기술적 지표들)
            feature_columns = [
                'rsi', 'macd', 'macd_signal', 'macd_histogram',
                'sma_20', 'sma_50', 'ema_12', 'ema_26',
                'bb_upper', 'bb_middle', 'bb_lower',
                'stoch_k', 'stoch_d', 'volatility'
            ]
            
            # 실제 존재하는 컬럼만 선택
            available_features = [col for col in feature_columns if col in df.columns]
            self.feature_columns = available_features
            
            if not available_features:
                raise ValueError("No valid feature columns found")
                
            # 특성 데이터 추출
            X = df[available_features].fillna(0).values
            
            # 타겟 데이터 처리
            if target_column in df.columns:
                y = df[target_column].values
            else:
                # 타겟이 없는 경우 가격 변화 기반으로 생성
                y = self._generate_signals(df)
                
            # 레이블 인코딩 (문자열 레이블인 경우)
            if y.dtype == 'object':
                y = self.label_encoder.fit_transform(y)
                
            logger.info(f"Data prepared: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise
            
    def _generate_signals(self, df: pd.DataFrame) -> np.ndarray:
        """가격 변화 기반 거래 신호 생성"""
        try:
            signals = []
            
            for i in range(len(df)):
                if i < 5:  # 초기 데이터는 보유
                    signals.append('HOLD')
                    continue
                    
                # 최근 5일간의 가격 변화율 계산
                current_price = df['close'].iloc[i]
                past_price = df['close'].iloc[i-5]
                price_change = (current_price - past_price) / past_price
                
                # RSI 기반 신호 (있는 경우)
                rsi = df.get('rsi', pd.Series([50] * len(df))).iloc[i]
                
                # 신호 생성 로직
                if price_change > 0.05 and rsi < 70:  # 5% 이상 상승, RSI 과매수 아님
                    signals.append('BUY')
                elif price_change < -0.05 and rsi > 30:  # 5% 이상 하락, RSI 과매도 아님
                    signals.append('SELL')
                else:
                    signals.append('HOLD')
                    
            return np.array(signals)
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return np.array(['HOLD'] * len(df))
            
    def train(self, X: np.ndarray, y: np.ndarray, 
              validation_split: float = 0.2, test_size: float = 0.2) -> Dict[str, Any]:
        """모델 훈련"""
        try:
            if self.model is None:
                self.build_model()
                
            # 데이터 분할
            X_train, X_temp, y_train, y_temp = train_test_split(
                X, y, test_size=validation_split + test_size, random_state=42, stratify=y
            )
            
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=test_size/(validation_split + test_size), 
                random_state=42, stratify=y_temp
            )
            
            # 훈련 실행
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                early_stopping_rounds=10,
                verbose=False
            )
            
            self.is_trained = True
            
            # 훈련 결과 평가
            train_score = self.model.score(X_train, y_train)
            val_score = self.model.score(X_val, y_val)
            test_score = self.model.score(X_test, y_test)
            
            training_results = {
                'train_accuracy': train_score,
                'val_accuracy': val_score,
                'test_accuracy': test_score,
                'n_estimators_used': self.model.n_estimators
            }
            
            logger.info(f"XGBoost model training completed: {training_results}")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training XGBoost model: {e}")
            raise
            
    def predict(self, X: np.ndarray) -> np.ndarray:
        """예측 수행"""
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before making predictions")
                
            predictions = self.model.predict(X)
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            raise
            
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """예측 확률 반환"""
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before making predictions")
                
            probabilities = self.model.predict_proba(X)
            return probabilities
            
        except Exception as e:
            logger.error(f"Error making probability predictions: {e}")
            raise
            
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """모델 평가"""
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before evaluation")
                
            # 예측 수행
            predictions = self.predict(X)
            
            # 평가 지표 계산
            accuracy = accuracy_score(y, predictions)
            precision = precision_score(y, predictions, average='weighted')
            recall = recall_score(y, predictions, average='weighted')
            f1 = f1_score(y, predictions, average='weighted')
            
            # 혼동 행렬
            cm = confusion_matrix(y, predictions)
            
            evaluation_results = {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'confusion_matrix': cm.tolist()
            }
            
            logger.info(f"XGBoost model evaluation: {evaluation_results}")
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating XGBoost model: {e}")
            raise
            
    def get_feature_importance(self) -> Dict[str, float]:
        """특성 중요도 반환"""
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before getting feature importance")
                
            importance = self.model.feature_importances_
            feature_importance = dict(zip(self.feature_columns, importance))
            
            # 중요도 순으로 정렬
            sorted_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
            
            return sorted_importance
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
            
    def save_model(self, filepath: str):
        """모델 저장"""
        try:
            # 모델 디렉토리 생성
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 모델 저장
            if self.model:
                joblib.dump(self.model, filepath)
                
            # 레이블 인코더 저장
            encoder_path = filepath.replace('.pkl', '_encoder.pkl')
            joblib.dump(self.label_encoder, encoder_path)
            
            # 특성 컬럼 저장
            features_path = filepath.replace('.pkl', '_features.pkl')
            joblib.dump(self.feature_columns, features_path)
            
            logger.info(f"XGBoost model saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving XGBoost model: {e}")
            raise
            
    def load_model(self, filepath: str):
        """모델 로드"""
        try:
            # 모델 로드
            self.model = joblib.load(filepath)
            
            # 레이블 인코더 로드
            encoder_path = filepath.replace('.pkl', '_encoder.pkl')
            self.label_encoder = joblib.load(encoder_path)
            
            # 특성 컬럼 로드
            features_path = filepath.replace('.pkl', '_features.pkl')
            self.feature_columns = joblib.load(features_path)
            
            self.is_trained = True
            logger.info(f"XGBoost model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading XGBoost model: {e}")
            raise
            
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        if self.model is None:
            return {"status": "Model not built"}
            
        return {
            "n_estimators": self.model.n_estimators,
            "max_depth": self.model.max_depth,
            "learning_rate": self.model.learning_rate,
            "feature_count": len(self.feature_columns),
            "is_trained": self.is_trained
        }
