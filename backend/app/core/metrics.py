from prometheus_client import Counter, Histogram, Gauge, start_http_server
from app.core.config import settings

# Trading metrics
trading_signals_total = Counter(
    'trading_signals_total',
    'Total number of trading signals generated',
    ['signal_type', 'strategy']
)

trading_executions_total = Counter(
    'trading_executions_total',
    'Total number of trading executions',
    ['symbol', 'side']
)

trading_errors_total = Counter(
    'trading_errors_total',
    'Total number of trading errors',
    ['error_type']
)

# Performance metrics
api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

ai_analysis_duration = Histogram(
    'ai_analysis_duration_seconds',
    'AI analysis duration',
    ['analysis_type']
)

# System metrics
active_strategies = Gauge(
    'active_strategies',
    'Number of active trading strategies'
)

market_regime_confidence = Gauge(
    'market_regime_confidence',
    'Current market regime confidence score',
    ['regime_type']
)

def start_metrics_server():
    """Start Prometheus metrics server"""
    if settings.ENABLE_METRICS:
        start_http_server(8001)