import React, { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { InformationCircleIcon } from '@heroicons/react/24/outline';

// API 응답 타입 정의
interface PortfolioRiskResponse {
  value_at_risk: number;
  sharpe_ratio: number;
  max_drawdown: number;
  risk_breakdown: { [key: string]: number };
}

// API 호출 함수
const fetchPortfolioRisk = async (assets: { [key: string]: number }): Promise<PortfolioRiskResponse> => {
  const { data } = await axios.post('/api/v1/ai/portfolio-risk', { assets });
  return data;
};

// 리스크 지표를 설명하는 툴팁 텍스트
const METRIC_DEFINITIONS = {
  var: 'Value at Risk (VaR)는 주어진 신뢰 수준(95%)에서 특정 기간(1일) 동안 포트폴리오가 입을 수 있는 최대 손실 추정치입니다.',
  sharpe: '샤프 비율은 위험 대비 수익률을 측정합니다. 무위험 수익률을 초과하는 수익을 포트폴리오 변동성으로 나눈 값입니다. 높을수록 좋습니다.',
  mdd: '최대 낙폭(MDD)은 특정 기간 동안 포트폴리오의 최고점에서 최저점까지의 최대 손실률을 나타냅니다.',
};

// 차트 색상
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

// 개별 리스크 지표를 표시하는 카드 컴포넌트
const RiskCard: React.FC<{ title: string; value: string; tooltip: string }> = ({ title, value, tooltip }) => (
  <div className="bg-gray-800 p-4 rounded-lg shadow-md flex flex-col justify-between">
    <div className="flex items-center justify-between mb-2">
      <h3 className="text-md font-semibold text-gray-300">{title}</h3>
      <div className="relative group">
        <InformationCircleIcon className="h-5 w-5 text-gray-500" />
        <div className="absolute bottom-full mb-2 w-64 bg-gray-900 text-white text-xs rounded py-2 px-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10">
          {tooltip}
        </div>
      </div>
    </div>
    <p className="text-3xl font-bold text-white">{value}</p>
  </div>
);

const PortfolioRisk: React.FC = () => {
  // 초기 포트폴리오 상태 (실제 앱에서는 props나 Redux/Context에서 가져올 수 있음)
  const [portfolio] = useState({
    "BTCUSDT": 0.4,
    "ETHUSDT": 0.3,
    "SOLUSDT": 0.2,
    "ADAUSDT": 0.1,
  });

  const { data, isLoading, error } = useQuery<PortfolioRiskResponse, Error>(
    ['portfolioRisk', portfolio],
    () => fetchPortfolioRisk(portfolio),
    {
      staleTime: 1000 * 60 * 5, // 5분
    }
  );

  if (isLoading) {
    return (
      <div className="p-6 bg-gray-900 rounded-lg shadow-lg h-full flex items-center justify-center">
        <p className="text-white">리스크 데이터를 불러오는 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-900 text-white rounded-lg shadow-lg h-full flex items-center justify-center">
        <p>오류가 발생했습니다: {error.message}</p>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const chartData = Object.entries(data.risk_breakdown).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="p-6 bg-gray-900 rounded-lg shadow-lg text-white h-full">
      <h2 className="text-2xl font-bold mb-6">포트폴리오 리스크 분석</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <RiskCard 
          title="VaR (1일, 95%)" 
          value={`${(data.value_at_risk * 100).toFixed(2)}%`}
          tooltip={METRIC_DEFINITIONS.var}
        />
        <RiskCard 
          title="샤프 비율" 
          value={data.sharpe_ratio.toFixed(2)}
          tooltip={METRIC_DEFINITIONS.sharpe}
        />
        <RiskCard 
          title="최대 낙폭 (MDD)" 
          value={`${(data.max_drawdown * 100).toFixed(2)}%`}
          tooltip={METRIC_DEFINITIONS.mdd}
        />
      </div>

      <div>
        <h3 className="text-xl font-semibold mb-4">자산별 리스크 기여도</h3>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => `${(value * 100).toFixed(2)}%`}
                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '0.5rem' }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default PortfolioRisk;