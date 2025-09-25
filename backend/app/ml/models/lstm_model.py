# LSTM 모델 구현
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, List, Dict, Any
import structlog
import joblib
import os

logger = structlog.get_logger()

class LSTMModel:
    """LSTM 기반 가격 예측 모델"""
    
    def __init__(self, sequence_length: int = 60, features: int = 10):
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        
    def build_model(self, lstm_units: List[int] = [128, 64], dropout_rate: float = 0.2):
        """LSTM 모델 구축"""
        try:
            self.model = Sequential()
            
            # 첫 번째 LSTM 레이어
            self.model.add(LSTM(
                lstm_units[0], 
                return_sequences=True, 
                input_shape=(self.sequence_length, self.features)
            ))
            self.model.add(Dropout(dropout_rate))
            
            # 두 번째 LSTM 레이어
            self.model.add(LSTM(lstm_units[1], return_sequences=False))
            self.model.add(Dropout(dropout_rate))
            
            # Dense 레이어
            self.model.add(Dense(32, activation='relu'))
            self.model.add(Dense(1, activation='linear'))
            
            # 컴파일
            self.model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            logger.info(f"LSTM model built with {self.model.count_params()} parameters")
            
        except Exception as e:
            logger.error(f"Error building LSTM model: {e}")
            raise
            
    def prepare_data(self, df: pd.DataFrame, target_column: str = 'close') -> Tuple[np.ndarray, np.ndarray]:
        """데이터 전처리 및 시퀀스 생성"""
        try:
            # 필요한 컬럼 선택
            feature_columns = ['open', 'high', 'low', 'close', 'volume']
            if len(df.columns) > 5:
                # 추가 특성 컬럼이 있는 경우
                additional_features = [col for col in df.columns if col not in feature_columns and col != 'timestamp']
                feature_columns.extend(additional_features[:5])  # 최대 5개 추가 특성
            
            # 데이터 정규화
            scaled_data = self.scaler.fit_transform(df[feature_columns])
            
            # 시퀀스 데이터 생성
            X, y = [], []
            for i in range(self.sequence_length, len(scaled_data)):
                X.append(scaled_data[i-self.sequence_length:i])
                y.append(scaled_data[i, feature_columns.index(target_column)])
                
            return np.array(X), np.array(y)
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise
            
    def train(self, X: np.ndarray, y: np.ndarray, 
              validation_split: float = 0.2, epochs: int = 100, 
              batch_size: int = 32) -> Dict[str, Any]:
        """모델 훈련"""
        try:
            if self.model is None:
                self.build_model()
                
            # 콜백 설정
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ModelCheckpoint(
                    'models/lstm_best_model.h5', 
                    save_best_only=True, 
                    monitor='val_loss'
                )
            ]
            
            # 훈련 실행
            history = self.model.fit(
                X, y,
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
            
            self.is_trained = True
            
            # 훈련 결과 반환
            training_results = {
                'final_loss': history.history['loss'][-1],
                'final_val_loss': history.history['val_loss'][-1],
                'final_mae': history.history['mae'][-1],
                'final_val_mae': history.history['val_mae'][-1],
                'epochs_trained': len(history.history['loss'])
            }
            
            logger.info(f"LSTM model training completed: {training_results}")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
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
            
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """모델 평가"""
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before evaluation")
                
            # 예측 수행
            predictions = self.predict(X)
            
            # 평가 지표 계산
            mse = np.mean((y - predictions.flatten()) ** 2)
            mae = np.mean(np.abs(y - predictions.flatten()))
            rmse = np.sqrt(mse)
            
            # R² 점수 계산
            ss_res = np.sum((y - predictions.flatten()) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            evaluation_results = {
                'mse': float(mse),
                'mae': float(mae),
                'rmse': float(rmse),
                'r2': float(r2)
            }
            
            logger.info(f"LSTM model evaluation: {evaluation_results}")
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating LSTM model: {e}")
            raise
            
    def save_model(self, filepath: str):
        """모델 저장"""
        try:
            # 모델 디렉토리 생성
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 모델 저장
            if self.model:
                self.model.save(filepath)
                
            # 스케일러 저장
            scaler_path = filepath.replace('.h5', '_scaler.pkl')
            joblib.dump(self.scaler, scaler_path)
            
            logger.info(f"LSTM model saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving LSTM model: {e}")
            raise
            
    def load_model(self, filepath: str):
        """모델 로드"""
        try:
            # 모델 로드
            self.model = tf.keras.models.load_model(filepath)
            
            # 스케일러 로드
            scaler_path = filepath.replace('.h5', '_scaler.pkl')
            self.scaler = joblib.load(scaler_path)
            
            self.is_trained = True
            logger.info(f"LSTM model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading LSTM model: {e}")
            raise
            
    def get_model_summary(self) -> str:
        """모델 구조 요약"""
        if self.model is None:
            return "Model not built yet"
            
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        self.model.summary()
        sys.stdout = old_stdout
        
        return buffer.getvalue()
