// AI 대시보드 컴포넌트
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { MarketAnalysisResponse, StrategyRecommendationResponse, RiskAssessmentResponse } from '../types/ai';

const AIDashboard: React.FC = () => {
  const [marketAnalysis, setMarketAnalysis] = useState<MarketAnalysisResponse | null>(null);
  const [strategyRecommendations, setStrategyRecommendations] = useState<StrategyRecommendationResponse[]>([]);
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessmentResponse | null>(null);
  const [loading, setLoading] = useState({
    market: false,
    strategies: false,
    risk: false
  });
  const [error, setError] = useState<string | null>(null);

  const { user } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (user) {
      loadAIData();
    }
  }, [user]);

  const loadAIData = async () => {
    await Promise.all([
      analyzeMarket(),
      recommendStrategies(),
      assessRisk()
    ]);
  };

  const analyzeMarket = async () => {
    try {
      setLoading(prev => ({ ...prev, market: true }));
      
      // 샘플 가격 데이터 (실제로는 API에서 가져옴)
      const samplePriceData = generateSamplePriceData();
      
      const response = await fetch('/api/v1/ai/market/analyze', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          symbol: 'BTCUSDT',
          price_data: samplePriceData,
          update_model: false
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze market');
      }
      
      const data = await response.json();
      setMarketAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze market');
    } finally {
      setLoading(prev => ({ ...prev, market: false }));
    }
  };

  const recommendStrategies = async () => {
    try {
      setLoading(prev => ({ ...prev, strategies: true }));
      
      const response = await fetch('/api/v1/ai/strategies/recommend', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          profile_updates: null,
          market_conditions: null,
          risk_preference: 'medium'
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to get strategy recommendations');
      }
      
      const data = await response.json();
      setStrategyRecommendations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get strategy recommendations');
    } finally {
      setLoading(prev => ({ ...prev, strategies: false }));
    }
  };

  const assessRisk = async () => {
    try {
      setLoading(prev => ({ ...prev, risk: true }));
      
      const response = await fetch('/api/v1/ai/risk/assess', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          market_data: {
            vix: 25,
            volatility: 0.15,
            trend: 0.3
          },
          portfolio_data: {
            concentration: 0.3,
            leverage: 1.0,
            position_size: 0.1
          }
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to assess risk');
      }
      
      const data = await response.json();
      setRiskAssessment(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assess risk');
    } finally {
      setLoading(prev => ({ ...prev, risk: false }));
    }
  };

  const generateSamplePriceData = () => {
    // 샘플 가격 데이터 생성 (실제로는 API에서 가져옴)
    const data = [];
    let price = 50000;
    for (let i = 0; i < 100; i++) {
      const change = (Math.random() - 0.5) * 0.02;
      price *= (1 + change);
      data.push({
        open: price,
        high: price * (1 + Math.random() * 0.01),
        low: price * (1 - Math.random() * 0.01),
        close: price,
        volume: Math.random() * 1000000
      });
    }
    return data;
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'high':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case 'trending':
        return 'text-blue-600 bg-blue-100';
      case 'mean_reversion':
        return 'text-purple-600 bg-purple-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Error: {error}</p>
        <button
          onClick={loadAIData}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Trading Dashboard</h1>
        <p className="text-gray-600">AI-powered market analysis and strategy recommendations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* 시장 분석 카드 */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Market Analysis</h2>
            {loading.market && (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            )}
          </div>
          
          {marketAnalysis ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Regime:</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRegimeColor(marketAnalysis.regime)}`}>
                  {marketAnalysis.regime}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Confidence:</span>
                <span className="font-medium">
                  {(marketAnalysis.confidence * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-700">Probabilities:</h3>
                {Object.entries(marketAnalysis.probabilities).map(([regime, prob]) => (
                  <div key={regime} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 capitalize">{regime}:</span>
                    <span className="text-sm font-medium">{(prob * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
              
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-700">Market Indicators:</h3>
                {Object.entries(marketAnalysis.market_indicators).map(([indicator, value]) => (
                  <div key={indicator} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 capitalize">{indicator}:</span>
                    <span className="text-sm font-medium">{value.toFixed(4)}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">No market analysis available</p>
            </div>
          )}
        </div>

        {/* 리스크 평가 카드 */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Risk Assessment</h2>
            {loading.risk && (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            )}
          </div>
          
          {riskAssessment ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Risk Level:</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(riskAssessment.risk_level)}`}>
                  {riskAssessment.risk_level}
                </span>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Total Risk:</span>
                  <span className="font-medium">{(riskAssessment.total_risk_score * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Market Risk:</span>
                  <span className="font-medium">{(riskAssessment.market_risk * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Portfolio Risk:</span>
                  <span className="font-medium">{(riskAssessment.portfolio_risk * 100).toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-700">Recommendations:</h3>
                <ul className="space-y-1">
                  {riskAssessment.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm text-gray-600">• {rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">No risk assessment available</p>
            </div>
          )}
        </div>

        {/* AI 모델 상태 카드 */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Models Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Market Regime Detector:</span>
              <span className="text-green-600 font-medium">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Strategy Recommender:</span>
              <span className="text-green-600 font-medium">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Risk Assessor:</span>
              <span className="text-green-600 font-medium">Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* 전략 추천 섹션 */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Recommended Strategies</h2>
          {loading.strategies && (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          )}
        </div>
        
        {strategyRecommendations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {strategyRecommendations.map((strategy, index) => (
              <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{strategy.strategy_name}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(strategy.risk_level)}`}>
                    {strategy.risk_level}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{strategy.description}</p>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Score:</span>
                    <span className="font-medium">{(strategy.score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Confidence:</span>
                    <span className="font-medium">{(strategy.confidence * 100).toFixed(1)}%</span>
                  </div>
                </div>
                
                <button className="w-full mt-3 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                  Apply Strategy
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">No strategy recommendations available</p>
          </div>
        )}
      </div>

      {/* 새로고침 버튼 */}
      <div className="mt-6 text-center">
        <button
          onClick={loadAIData}
          disabled={Object.values(loading).some(l => l)}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Refresh AI Analysis
        </button>
      </div>
    </div>
  );
};

export default AIDashboard;
