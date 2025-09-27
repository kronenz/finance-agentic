"""
포괄적인 단위 테스트 커버리지 (90%+) 테스트
AI 기반 암호화폐 거래 시스템의 모든 핵심 컴포넌트 테스트
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from datetime import datetime, timedelta
import json

# AI 에이전트 테스트
from app.ai.market_regime_detector import MarketRegimeDetector
from app.ai.vwap_analyzer import VWAPAnalyzer
from app.ai.volume_profile_analyzer import VolumeProfileAnalyzer
from app.ai.meta_controller import MetaController
from app.ai.risk_manager import RiskManager
from app.ai.rl_optimizer import RLOptimizer
from app.ai.genetic_algorithm import GeneticAlgorithm

# 거래 시스템 테스트
from app.strategies.trend_following_strategy import TrendFollowingStrategy
from app.strategies.mean_reversion_strategy import MeanReversionStrategy
from app.data.market_processor import MarketDataProcessor
from app.trading.execution_engine import TradingExecutionEngine
from app.trading.position_manager import PositionManager

# 모델 테스트
from app.models.market_regime import MarketRegime, MarketRegimeType
from app.models.trading_strategy import TradingStrategy, StrategyType
from app.models.vwap_data import VWAPData
from app.models.volume_profile import VolumeProfile
from app.models.risk_parameters import RiskParameters, RiskLevel


class TestMarketRegimeDetector(unittest.TestCase):
    """시장 국면 감지기 테스트"""
    
    def setUp(self):
        self.detector = MarketRegimeDetector()
        self.sample_data = {
            'prices': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            'volumes': [1000, 1200, 1100, 1300, 1400, 1350, 1450, 1500, 1480, 1520],
            'timestamps': [datetime.now() - timedelta(minutes=i) for i in range(10, 0, -1)]
        }
    
    def test_trend_detection(self):
        """추세 감지 테스트"""
        result = self.detector.detect_trend(self.sample_data)
        self.assertIsInstance(result, dict)
        self.assertIn('regime_type', result)
        self.assertIn('confidence_score', result)
        self.assertGreaterEqual(result['confidence_score'], 0.0)
        self.assertLessEqual(result['confidence_score'], 1.0)
    
    def test_volatility_calculation(self):
        """변동성 계산 테스트"""
        volatility = self.detector.calculate_volatility(self.sample_data['prices'])
        self.assertIsInstance(volatility, float)
        self.assertGreaterEqual(volatility, 0.0)
    
    def test_adx_calculation(self):
        """ADX 계산 테스트"""
        adx = self.detector.calculate_adx(self.sample_data['prices'])
        self.assertIsInstance(adx, float)
        self.assertGreaterEqual(adx, 0.0)
        self.assertLessEqual(adx, 100.0)
    
    def test_hurst_exponent(self):
        """Hurst 지수 계산 테스트"""
        hurst = self.detector.calculate_hurst_exponent(self.sample_data['prices'])
        self.assertIsInstance(hurst, float)
        self.assertGreaterEqual(hurst, 0.0)
        self.assertLessEqual(hurst, 1.0)
    
    def test_invalid_data_handling(self):
        """잘못된 데이터 처리 테스트"""
        with self.assertRaises(ValueError):
            self.detector.detect_trend({'prices': [], 'volumes': []})
        
        with self.assertRaises(ValueError):
            self.detector.detect_trend({'prices': [1, 2, 3], 'volumes': [1, 2]})


class TestVWAPAnalyzer(unittest.TestCase):
    """VWAP 분석기 테스트"""
    
    def setUp(self):
        self.analyzer = VWAPAnalyzer()
        self.sample_data = [
            {'price': 100, 'volume': 1000, 'timestamp': datetime.now()},
            {'price': 102, 'volume': 1200, 'timestamp': datetime.now()},
            {'price': 101, 'volume': 1100, 'timestamp': datetime.now()},
        ]
    
    def test_vwap_calculation(self):
        """VWAP 계산 테스트"""
        vwap = self.analyzer.calculate_vwap(self.sample_data)
        self.assertIsInstance(vwap, float)
        self.assertGreater(vwap, 0)
    
    def test_deviation_bands(self):
        """편차 밴드 계산 테스트"""
        bands = self.analyzer.calculate_deviation_bands(self.sample_data, vwap=101.0)
        self.assertIsInstance(bands, dict)
        self.assertIn('upper_1std', bands)
        self.assertIn('lower_1std', bands)
        self.assertIn('upper_2std', bands)
        self.assertIn('lower_2std', bands)
        self.assertGreater(bands['upper_1std'], bands['lower_1std'])
    
    def test_timeframe_analysis(self):
        """시간대별 분석 테스트"""
        result = self.analyzer.analyze_timeframe(self.sample_data, '1h')
        self.assertIsInstance(result, dict)
        self.assertIn('vwap', result)
        self.assertIn('deviation_bands', result)
        self.assertIn('volume_profile', result)
    
    def test_empty_data_handling(self):
        """빈 데이터 처리 테스트"""
        with self.assertRaises(ValueError):
            self.analyzer.calculate_vwap([])


class TestVolumeProfileAnalyzer(unittest.TestCase):
    """거래량 프로파일 분석기 테스트"""
    
    def setUp(self):
        self.analyzer = VolumeProfileAnalyzer()
        self.sample_data = [
            {'price': 100, 'volume': 1000},
            {'price': 101, 'volume': 1200},
            {'price': 102, 'volume': 1100},
            {'price': 100, 'volume': 800},
            {'price': 101, 'volume': 900},
        ]
    
    def test_poc_calculation(self):
        """POC (Point of Control) 계산 테스트"""
        poc = self.analyzer.calculate_poc(self.sample_data)
        self.assertIsInstance(poc, float)
        self.assertGreater(poc, 0)
    
    def test_value_area_calculation(self):
        """Value Area 계산 테스트"""
        va = self.analyzer.calculate_value_area(self.sample_data, poc=101.0)
        self.assertIsInstance(va, dict)
        self.assertIn('vah', va)  # Value Area High
        self.assertIn('val', va)  # Value Area Low
        self.assertGreaterEqual(va['vah'], va['val'])
    
    def test_lvn_detection(self):
        """LVN (Low Volume Node) 감지 테스트"""
        lvn = self.analyzer.detect_lvn(self.sample_data)
        self.assertIsInstance(lvn, list)
        for zone in lvn:
            self.assertIn('price_range', zone)
            self.assertIn('volume', zone)
    
    def test_volume_profile_analysis(self):
        """거래량 프로파일 전체 분석 테스트"""
        result = self.analyzer.analyze_volume_profile(self.sample_data)
        self.assertIsInstance(result, dict)
        self.assertIn('poc', result)
        self.assertIn('value_area', result)
        self.assertIn('lvn_zones', result)
        self.assertIn('total_volume', result)


class TestRiskManager(unittest.TestCase):
    """리스크 관리자 테스트"""
    
    def setUp(self):
        self.risk_manager = RiskManager()
        self.sample_position = {
            'symbol': 'BTCUSDT',
            'size': 1000.0,
            'entry_price': 45000.0,
            'current_price': 46000.0,
            'leverage': 2.0
        }
    
    def test_position_sizing(self):
        """포지션 크기 계산 테스트"""
        size = self.risk_manager.calculate_position_size(
            account_balance=10000.0,
            risk_percentage=2.0,
            stop_loss_distance=1000.0
        )
        self.assertIsInstance(size, float)
        self.assertGreater(size, 0)
        self.assertLessEqual(size, 10000.0)
    
    def test_var_calculation(self):
        """VaR (Value at Risk) 계산 테스트"""
        var = self.risk_manager.calculate_var(
            positions=[self.sample_position],
            confidence_level=0.95
        )
        self.assertIsInstance(var, float)
        self.assertGreaterEqual(var, 0)
    
    def test_correlation_analysis(self):
        """상관관계 분석 테스트"""
        positions = [
            {'symbol': 'BTCUSDT', 'returns': [0.01, 0.02, -0.01, 0.03]},
            {'symbol': 'ETHUSDT', 'returns': [0.015, 0.025, -0.005, 0.035]}
        ]
        correlation = self.risk_manager.calculate_correlation(positions)
        self.assertIsInstance(correlation, float)
        self.assertGreaterEqual(correlation, -1.0)
        self.assertLessEqual(correlation, 1.0)
    
    def test_liquidation_risk(self):
        """청산 위험 계산 테스트"""
        risk = self.risk_manager.assess_liquidation_risk(
            position=self.sample_position,
            maintenance_margin=0.05
        )
        self.assertIsInstance(risk, dict)
        self.assertIn('risk_level', risk)
        self.assertIn('liquidation_price', risk)
        self.assertIn('margin_ratio', risk)
    
    def test_portfolio_risk(self):
        """포트폴리오 리스크 분석 테스트"""
        portfolio = {
            'positions': [self.sample_position],
            'total_balance': 10000.0,
            'max_drawdown': 0.1
        }
        risk = self.risk_manager.analyze_portfolio_risk(portfolio)
        self.assertIsInstance(risk, dict)
        self.assertIn('total_exposure', risk)
        self.assertIn('concentration_risk', risk)
        self.assertIn('correlation_risk', risk)


class TestTradingStrategies(unittest.TestCase):
    """거래 전략 테스트"""
    
    def setUp(self):
        self.trend_strategy = TrendFollowingStrategy()
        self.mean_reversion_strategy = MeanReversionStrategy()
        self.market_data = {
            'prices': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
            'volumes': [1000, 1200, 1100, 1300, 1400, 1350, 1450, 1500, 1480, 1520],
            'vwap': 103.5,
            'volume_profile': {'poc': 103.0, 'vah': 105.0, 'val': 101.0}
        }
    
    def test_trend_following_signal(self):
        """추세 추종 신호 생성 테스트"""
        signal = self.trend_strategy.generate_signal(self.market_data)
        self.assertIsInstance(signal, dict)
        self.assertIn('signal_type', signal)
        self.assertIn('confidence', signal)
        self.assertIn('entry_price', signal)
        self.assertIn('stop_loss', signal)
        self.assertIn('take_profit', signal)
        self.assertIn(signal['signal_type'], ['BUY', 'SELL', 'HOLD'])
    
    def test_mean_reversion_signal(self):
        """평균 회귀 신호 생성 테스트"""
        signal = self.mean_reversion_strategy.generate_signal(self.market_data)
        self.assertIsInstance(signal, dict)
        self.assertIn('signal_type', signal)
        self.assertIn('confidence', signal)
        self.assertIn('entry_price', signal)
        self.assertIn('stop_loss', signal)
        self.assertIn('take_profit', signal)
    
    def test_position_sizing(self):
        """포지션 크기 계산 테스트"""
        size = self.trend_strategy.calculate_position_size(
            account_balance=10000.0,
            risk_percentage=2.0,
            stop_loss_distance=1000.0
        )
        self.assertIsInstance(size, float)
        self.assertGreater(size, 0)
    
    def test_risk_management(self):
        """리스크 관리 테스트"""
        risk_params = {
            'max_position_size': 1000.0,
            'max_daily_loss': 500.0,
            'stop_loss_percentage': 0.02
        }
        risk_check = self.trend_strategy.manage_risk(
            signal={'position_size': 500.0},
            risk_params=risk_params
        )
        self.assertIsInstance(risk_check, dict)
        self.assertIn('approved', risk_check)
        self.assertIn('adjusted_size', risk_check)


class TestMarketDataProcessor(unittest.TestCase):
    """시장 데이터 처리기 테스트"""
    
    def setUp(self):
        self.processor = MarketDataProcessor()
    
    @patch('redis.Redis')
    def test_data_normalization(self, mock_redis):
        """데이터 정규화 테스트"""
        raw_data = {
            'symbol': 'BTCUSDT',
            'price': '45000.50',
            'volume': '1.5',
            'timestamp': '1640995200000'
        }
        normalized = self.processor.normalize_data(raw_data, 'binance')
        self.assertIsInstance(normalized, dict)
        self.assertIn('symbol', normalized)
        self.assertIn('price', normalized)
        self.assertIn('volume', normalized)
        self.assertIn('timestamp', normalized)
        self.assertIsInstance(normalized['price'], float)
        self.assertIsInstance(normalized['volume'], float)
        self.assertIsInstance(normalized['timestamp'], datetime)
    
    @patch('redis.Redis')
    def test_websocket_connection(self, mock_redis):
        """WebSocket 연결 테스트"""
        with patch('websockets.connect') as mock_connect:
            mock_ws = Mock()
            mock_connect.return_value = mock_ws
            result = asyncio.run(self.processor.connect_websocket('wss://test.com'))
            self.assertIsNotNone(result)
    
    def test_data_validation(self):
        """데이터 검증 테스트"""
        valid_data = {
            'symbol': 'BTCUSDT',
            'price': 45000.0,
            'volume': 1.5,
            'timestamp': datetime.now()
        }
        self.assertTrue(self.processor.validate_data(valid_data))
        
        invalid_data = {
            'symbol': 'BTCUSDT',
            'price': -100.0,  # 음수 가격
            'volume': 1.5,
            'timestamp': datetime.now()
        }
        self.assertFalse(self.processor.validate_data(invalid_data))


class TestTradingExecutionEngine(unittest.TestCase):
    """거래 실행 엔진 테스트"""
    
    def setUp(self):
        self.engine = TradingExecutionEngine()
    
    @patch('requests.post')
    def test_order_execution(self, mock_post):
        """주문 실행 테스트"""
        mock_response = Mock()
        mock_response.json.return_value = {'order_id': '12345', 'status': 'filled'}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        order = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'quantity': 0.1,
            'price': 45000.0,
            'exchange': 'binance'
        }
        
        result = self.engine.execute_order(order)
        self.assertIsInstance(result, dict)
        self.assertIn('order_id', result)
        self.assertIn('status', result)
    
    def test_slippage_calculation(self):
        """슬리피지 계산 테스트"""
        slippage = self.engine.calculate_slippage(
            order_size=1000.0,
            market_impact=0.001
        )
        self.assertIsInstance(slippage, float)
        self.assertGreaterEqual(slippage, 0)
    
    def test_order_validation(self):
        """주문 검증 테스트"""
        valid_order = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'quantity': 0.1,
            'price': 45000.0
        }
        self.assertTrue(self.engine.validate_order(valid_order))
        
        invalid_order = {
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'quantity': -0.1,  # 음수 수량
            'price': 45000.0
        }
        self.assertFalse(self.engine.validate_order(invalid_order))


class TestPositionManager(unittest.TestCase):
    """포지션 관리자 테스트"""
    
    def setUp(self):
        self.position_manager = PositionManager()
        self.sample_position = {
            'id': 'pos_123',
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'size': 0.1,
            'entry_price': 45000.0,
            'current_price': 46000.0,
            'leverage': 2.0
        }
    
    def test_pnl_calculation(self):
        """P&L 계산 테스트"""
        pnl = self.position_manager.calculate_pnl(self.sample_position)
        self.assertIsInstance(pnl, dict)
        self.assertIn('unrealized_pnl', pnl)
        self.assertIn('realized_pnl', pnl)
        self.assertIn('pnl_percentage', pnl)
    
    def test_position_update(self):
        """포지션 업데이트 테스트"""
        updated_position = self.position_manager.update_position(
            self.sample_position,
            {'current_price': 47000.0}
        )
        self.assertIsInstance(updated_position, dict)
        self.assertEqual(updated_position['current_price'], 47000.0)
    
    def test_risk_monitoring(self):
        """리스크 모니터링 테스트"""
        risk_status = self.position_manager.monitor_risk(
            self.sample_position,
            {'max_loss': 1000.0}
        )
        self.assertIsInstance(risk_status, dict)
        self.assertIn('risk_level', risk_status)
        self.assertIn('recommendation', risk_status)
    
    def test_position_closing(self):
        """포지션 종료 테스트"""
        closed_position = self.position_manager.close_position(
            self.sample_position,
            exit_price=47000.0
        )
        self.assertIsInstance(closed_position, dict)
        self.assertIn('exit_price', closed_position)
        self.assertIn('realized_pnl', closed_position)
        self.assertIn('status', closed_position)


class TestDatabaseModels(unittest.TestCase):
    """데이터베이스 모델 테스트"""
    
    def test_market_regime_model(self):
        """MarketRegime 모델 테스트"""
        regime = MarketRegime(
            regime_type=MarketRegimeType.TREND_UP,
            confidence_score=0.85,
            adx_value=25.5,
            hurst_exponent=0.6,
            volatility_level='MEDIUM'
        )
        self.assertEqual(regime.regime_type, MarketRegimeType.TREND_UP)
        self.assertEqual(regime.confidence_score, 0.85)
        self.assertGreaterEqual(regime.confidence_score, 0.0)
        self.assertLessEqual(regime.confidence_score, 1.0)
    
    def test_trading_strategy_model(self):
        """TradingStrategy 모델 테스트"""
        strategy = TradingStrategy(
            name='Test Strategy',
            strategy_type=StrategyType.TREND_FOLLOWING,
            parameters={'period': 20, 'threshold': 0.02},
            is_active=True
        )
        self.assertEqual(strategy.name, 'Test Strategy')
        self.assertEqual(strategy.strategy_type, StrategyType.TREND_FOLLOWING)
        self.assertTrue(strategy.is_active)
    
    def test_vwap_data_model(self):
        """VWAPData 모델 테스트"""
        vwap_data = VWAPData(
            symbol='BTCUSDT',
            timeframe='1h',
            vwap_value=45000.0,
            volume=1000.0,
            price=45100.0
        )
        self.assertEqual(vwap_data.symbol, 'BTCUSDT')
        self.assertEqual(vwap_data.timeframe, '1h')
        self.assertGreater(vwap_data.vwap_value, 0)
    
    def test_volume_profile_model(self):
        """VolumeProfile 모델 테스트"""
        volume_profile = VolumeProfile(
            symbol='BTCUSDT',
            timeframe='1h',
            poc_price=45000.0,
            vah_price=45200.0,
            val_price=44800.0,
            lvn_zones=[{'low': 44900, 'high': 44950, 'volume': 100}]
        )
        self.assertEqual(volume_profile.symbol, 'BTCUSDT')
        self.assertGreaterEqual(volume_profile.vah_price, volume_profile.poc_price)
        self.assertGreaterEqual(volume_profile.poc_price, volume_profile.val_price)
    
    def test_risk_parameters_model(self):
        """RiskParameters 모델 테스트"""
        risk_params = RiskParameters(
            level=RiskLevel.INDIVIDUAL,
            max_position_size=1000.0,
            max_daily_loss=500.0,
            leverage_limit=5.0,
            stop_loss_percentage=0.02,
            take_profit_percentage=0.04
        )
        self.assertEqual(risk_params.level, RiskLevel.INDIVIDUAL)
        self.assertGreater(risk_params.max_position_size, 0)
        self.assertGreater(risk_params.max_daily_loss, 0)


class TestIntegrationScenarios(unittest.TestCase):
    """통합 시나리오 테스트"""
    
    def test_full_trading_workflow(self):
        """전체 거래 워크플로우 테스트"""
        # 1. 시장 데이터 수집
        market_data = {
            'prices': [100, 102, 101, 103, 105],
            'volumes': [1000, 1200, 1100, 1300, 1400],
            'timestamp': datetime.now()
        }
        
        # 2. 시장 국면 분석
        detector = MarketRegimeDetector()
        regime = detector.detect_trend(market_data)
        self.assertIsInstance(regime, dict)
        
        # 3. VWAP 분석
        analyzer = VWAPAnalyzer()
        vwap_data = analyzer.analyze_timeframe(market_data, '1h')
        self.assertIsInstance(vwap_data, dict)
        
        # 4. 거래 신호 생성
        strategy = TrendFollowingStrategy()
        signal = strategy.generate_signal(market_data)
        self.assertIsInstance(signal, dict)
        
        # 5. 리스크 검증
        risk_manager = RiskManager()
        risk_check = risk_manager.assess_position_risk(signal)
        self.assertIsInstance(risk_check, dict)
        
        # 6. 주문 실행 (모킹)
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {'order_id': '12345', 'status': 'filled'}
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            engine = TradingExecutionEngine()
            order_result = engine.execute_order(signal)
            self.assertIsInstance(order_result, dict)


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
